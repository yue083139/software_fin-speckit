"""活動狀態：唯一的狀態來源（app-skeleton D2）。

所有改變狀態的方法都在 `_lock` 內執行，檢查與寫入之間以 `_checkpoint()` 讓出一次控制權——
讓並發測試真的交錯執行，拿掉鎖時測試必紅（app-skeleton v1.1 D2）。改變後遞增 `version`
並喚醒 `changed`，由各 WebSocket 連線自己的送出迴圈重算 view（app-skeleton D4）。
"""
import asyncio
import secrets
import time
import unicodedata
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from .guided_notes import ParsedNotes, Question, parse_workbook
from .judging import suggest
from .modes import DEFAULT_MODE, MODES, Mode, ModeError
from .phases import Phase, PhaseError, check_transition
from .scoring import QuestionAttrs, Ranked, ScoringRule, Submission

MIN_TEAMS, MAX_TEAMS, DEFAULT_TEAMS = 2, 50, 4
MAX_ANSWER_CHARS = 200


class TeamTakenError(Exception):
    """該組已有裝置持有組別憑證；API 層轉成 409。"""


class InviteCodeError(Exception):
    """組隊時加入已有裝置的組別但邀請碼不符；API 層轉成 403（team-mode D2）。"""


class AlreadySubmittedError(Exception):
    """本組本題已送出，不可修改；API 層轉成 409。"""


class SettingsError(ValueError):
    """題目設定值不合規；API 層轉成 422。"""


MULTIPLIERS = (1, 2)
MAX_DEVICES = 6  # 組隊時每組裝置上限（team-mode D2）
CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # 去掉易混淆的 I、O、0、1
CODE_LENGTH = 6
TIME_LIMIT_RANGE = (5, 120)


@dataclass
class Round:
    """時間計分的一個回合（mode-timed-scoring D3）。

    `opened_at` 為伺服器單調時鐘；`deadline_epoch_ms` 只供前端倒數。
    """

    number: int
    opened_at: float
    deadline_epoch_ms: int
    limit: int
    closed: bool = False
    revealed: bool = False


class AnswerError(ValueError):
    """答案內容不合規；API 層轉成 422。訊息為固定文字，不回顯答案（作答隔離）。"""


def clean_answers(answers: list[str], expected: int) -> tuple[str, ...]:
    if len(answers) != expected:
        raise AnswerError(f"此題有 {expected} 個子題，必須一次送出全部答案")
    cleaned = []
    for a in answers:
        text = a.strip() if isinstance(a, str) else ""
        if not text:
            raise AnswerError("答案不可空白")
        if len(text) > MAX_ANSWER_CHARS:
            raise AnswerError(f"每個答案最多 {MAX_ANSWER_CHARS} 字")
        if any(unicodedata.category(ch) == "Cc" for ch in text):
            raise AnswerError("答案含有不允許的控制字元")
        cleaned.append(text)
    return tuple(cleaned)


def clean_draft(answers: list[str], expected: int) -> tuple[str, ...]:
    """草稿可空白（組員清掉）；其餘限制同送出，訊息固定不回顯（team-mode D4）。"""
    if len(answers) != expected:
        raise AnswerError(f"此題有 {expected} 個子題")
    cleaned = []
    for a in answers:
        if not isinstance(a, str):
            raise AnswerError("草稿格式不正確")
        if len(a) > MAX_ANSWER_CHARS:
            raise AnswerError(f"每個答案最多 {MAX_ANSWER_CHARS} 字")
        if any(unicodedata.category(ch) == "Cc" for ch in a):
            raise AnswerError("答案含有不允許的控制字元")
        cleaned.append(a)
    return tuple(cleaned)


def normalize_code(code: str | None) -> bytes:
    """全形轉半形（NFKC）、去空白、轉大寫；比對一律用位元組，非 ASCII 只會比對失敗不會拋例外。"""
    return "".join(unicodedata.normalize("NFKC", code or "").split()).upper().encode()


def team_names(n: int) -> list[str]:
    return [f"第{i}組" for i in range(1, n + 1)]


class Activity:
    def __init__(self, team_count: int = DEFAULT_TEAMS, clock: Callable[[], float] = time.monotonic,
                 wall: Callable[[], float] = time.time,
                 sleep: Callable[[float], Awaitable[None]] = asyncio.sleep) -> None:
        self._lock = asyncio.Lock()
        self.changed = asyncio.Condition()
        self.phase = Phase.PREPARING
        self.teams = team_names(team_count)
        self.version = 0
        self._tokens: dict[str, str] = {}  # 組別憑證 → 組別（app-skeleton D6）；組隊時多對一
        self.team_play = False  # 組隊：與模式正交的活動設定（team-mode D1）
        self._codes: dict[str, str] = {}  # 組別 → 邀請碼（team-mode D2）
        self.drafts: dict[str, dict[int, tuple[str, ...]]] = {}  # 組別 → 題號 → 組內草稿（team-mode D4）
        self.notes: ParsedNotes | None = None
        self.source_bytes: bytes | None = None  # 匯入當下的原檔，供匯出寫回（guided-notes-import D6）
        self.source_name: str | None = None
        self.public_url: str | None = None  # 通道公開網址（student-qr）；伺服器設定，重置與重新匯入都保留
        self.tunnel_state = "off"  # 手機連線 off／starting／on（easy-setup D3）；重置與重新匯入都保留
        # Google 來源時為匯入時建立的副本 id（guided-notes-sheets-sync D3）；上傳 xlsx 為 None
        self.source_sheet_id: str | None = None
        # Google 來源：{Google 分頁名: xlsx 備援檔分頁名}（xlsx 不允許 / : 等字元，實作輪評審）
        self.source_xlsx_sheets: dict[str, str] | None = None
        # 上次寫回 Google 副本時寫過答案的題號（answer-review D5 v1.1）：這次沒得主就以原標籤還原。
        # 隨副本走：重新匯入（新副本）清空；重置保留（同一份副本，上一場寫過的格仍在副本裡）
        self.sheet_written: frozenset[int] = frozenset()
        self.mode: Mode = MODES[DEFAULT_MODE]
        self.submissions: dict[int, list[Submission]] = {}
        self.judgments: dict[int, dict[str, bool]] = {}  # 題號 → 組別 → 正確否（game-mode-framework D3）
        self.attrs: dict[int, QuestionAttrs] = {}  # 題號 → 題目屬性（question-settings D2）
        self._seq = 0
        self._started_at = 0.0
        self.rounds: dict[int, Round] = {}  # 題號 → 回合（只有逐題模式）
        self._timer: asyncio.Task | None = None
        self._clock, self._wall, self._sleep = clock, wall, sleep

    @property
    def rule(self) -> ScoringRule:
        """結果、view 與匯出一律經此取得規則（game-mode-framework D1）。"""
        return self.mode.rule

    @property
    def questions(self) -> tuple[Question, ...]:
        return self.notes.questions if self.notes else ()

    @staticmethod
    async def _checkpoint() -> None:
        await asyncio.sleep(0)

    async def set_tunnel(self, state: str, url: str | None) -> None:
        """手機連線狀態與公開網址（easy-setup D3）；只給老師 view，學生 view 不帶。"""
        async with self._lock:
            self.tunnel_state = state
            self.public_url = url
            await self._bump()

    async def _bump(self) -> None:
        self.version += 1
        async with self.changed:
            self.changed.notify_all()

    def _require(self, *phases: Phase) -> None:
        if self.phase not in phases:
            allowed = "、".join(p.value for p in phases)
            raise PhaseError(f"此操作只能在 {allowed} 階段進行（目前 {self.phase.value}）")

    # ---- 組別與憑證 ----
    def team_of(self, token: str | None) -> str | None:
        """由組別憑證反查組別；無效回 None。不採信客戶端自報的組別名稱。"""
        if not token:
            return None
        for known, team in self._tokens.items():
            if secrets.compare_digest(known.encode(), token.encode()):
                return team
        return None

    def joined_teams(self) -> list[str]:
        return [t for t in self.teams if t in self._tokens.values()]

    def devices(self, team: str) -> int:
        return sum(1 for v in self._tokens.values() if v == team)

    def invite_code(self, team: str) -> str | None:
        return self._codes.get(team)

    @staticmethod
    def _new_code() -> str:
        return "".join(secrets.choice(CODE_ALPHABET) for _ in range(CODE_LENGTH))

    def _revoke_all(self) -> None:
        self._tokens.clear()
        self._codes.clear()
        self.drafts = {}

    async def join(self, team: str, code: str | None = None) -> str:
        async with self._lock:
            if team not in self.teams:
                raise KeyError(team)
            count = self.devices(team)
            if count and not self.team_play:
                raise TeamTakenError("此組已有裝置加入，請老師釋放後再加入")
            known = self._codes.get(team) if self.team_play else None
            if count and known is None:
                raise InviteCodeError("邀請碼不正確")  # 防禦：組隊時有裝置的組必有邀請碼
            if known is not None:
                # 該組有邀請碼（已有裝置，或被老師釋放過）就必須帶碼；先比對邀請碼再檢查上限：
                # 沒有正確邀請碼的人不該知道該組有幾台（team-mode v1.1 D2）
                if not secrets.compare_digest(normalize_code(code), known.encode()):
                    raise InviteCodeError("邀請碼不正確")
                if count >= MAX_DEVICES:
                    raise TeamTakenError(f"此組裝置已滿（最多 {MAX_DEVICES} 台）")
            await self._checkpoint()  # 讓出點必須夾在「檢查」與「寫入」之間，拿掉鎖時並發測試才會紅
            token = secrets.token_urlsafe(16)
            self._tokens[token] = team
            if self.team_play and known is None:
                self._codes[team] = self._new_code()
            await self._bump()
            return token

    async def release(self, team: str) -> None:
        async with self._lock:
            if team not in self.teams:
                raise KeyError(team)
            self._tokens = {k: v for k, v in self._tokens.items() if v != team}
            # 組隊時釋放即換新碼（只顯示在老師畫面）：被踢的冒用者不能搶先以「第一台」
            # 重新佔住該組（team-mode v1.1 D2）
            if self.team_play:
                self._codes[team] = self._new_code()
            self.drafts.pop(team, None)
            await self._bump()

    async def set_team_play(self, enabled: bool) -> None:
        async with self._lock:
            self._require(Phase.PREPARING)
            if enabled == self.team_play:
                return  # 值不變不撤銷（team-mode D1）
            await self._checkpoint()
            self.team_play = enabled
            self._revoke_all()
            await self._bump()

    async def configure_teams(self, count: int) -> None:
        if not MIN_TEAMS <= count <= MAX_TEAMS:
            raise ValueError(f"組數須介於 {MIN_TEAMS} 到 {MAX_TEAMS}")
        async with self._lock:
            self._require(Phase.PREPARING)
            await self._checkpoint()
            self.teams = team_names(count)
            self._revoke_all()  # 改組數即撤銷所有組別憑證與邀請碼
            await self._bump()

    def require_preparing(self) -> None:
        self._require(Phase.PREPARING)

    # ---- 模式（game-mode-framework D1） ----
    async def set_mode(self, key: str) -> None:
        if key not in MODES:
            raise ModeError("不支援的模式")
        async with self._lock:
            self._require(Phase.PREPARING)
            await self._checkpoint()
            self.mode = MODES[key]
            await self._bump()

    # ---- 題目 ----
    async def load_questions(self, data: bytes, name: str, notes: ParsedNotes | None = None,
                             sheet_id: str | None = None, xlsx_sheets: dict[str, str] | None = None) -> None:
        """`notes` 已由呼叫端解析時（Google 來源）直接採用；`sheet_id` 為副本 id，上傳 xlsx 為 None。"""
        async with self._lock:
            self._require(Phase.PREPARING)
            if notes is None:
                notes = parse_workbook(data)  # 解析失敗拋 GuidedNotesError，狀態不變
            await self._checkpoint()
            self.notes, self.source_bytes, self.source_name = notes, data, name
            self.source_sheet_id = sheet_id
            self.source_xlsx_sheets = xlsx_sheets
            self.sheet_written = frozenset()
            self.attrs = {q.number: QuestionAttrs() for q in notes.questions}  # 新題目清單：設定歸零
            self._clear_answers()
            await self._bump()

    def _clear_answers(self) -> None:
        self.submissions = {q.number: [] for q in self.questions}
        self.judgments = {q.number: {} for q in self.questions}
        self._seq = 0
        self.drafts = {}
        self.rounds = {}
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None

    def attrs_of(self, number: int) -> QuestionAttrs:
        return self.attrs.get(number, QuestionAttrs())

    async def set_question(self, number: int, multiplier: int | None = None,
                           time_limit: int | None = None) -> QuestionAttrs:
        """只在準備階段（question-settings D2）：搶答中改設定會改變已作答組別的期望分數。

        兩欄皆可選、至少一欄（mode-timed-scoring D2）；只給一欄時另一欄不動。
        """
        if multiplier is None and time_limit is None:
            raise SettingsError("至少要設定倍率或時限其中一項")
        if multiplier is not None and multiplier not in MULTIPLIERS:
            raise SettingsError("倍率只能是 1 或 2")
        low, high = TIME_LIMIT_RANGE
        if time_limit is not None and not low <= time_limit <= high:
            raise SettingsError(f"時限須介於 {low} 到 {high} 秒")
        async with self._lock:
            self._require(Phase.PREPARING)
            self.question(number)
            old = self.attrs_of(number)
            await self._checkpoint()
            self.attrs[number] = QuestionAttrs(
                old.multiplier if multiplier is None else multiplier,
                old.time_limit if time_limit is None else time_limit,
            )
            await self._bump()
            return self.attrs[number]

    def question(self, number: int) -> Question:
        for q in self.questions:
            if q.number == number:
                return q
        raise KeyError(number)

    # ---- 作答（buzz-answering D1） ----
    async def submit(self, team: str, number: int, answers: list[str]) -> Submission:
        async with self._lock:
            self._require(Phase.ANSWERING)
            q = self.question(number)
            # 只讀一次時鐘：截止比對與作答毫秒用同一個值，且在讓出點之前（mode-timed-scoring D3）
            now = self._clock()
            opened_at = self._started_at
            if self.mode.sequential:
                rnd = self.current
                if rnd is None or rnd.number != number or rnd.closed:
                    raise PhaseError("這一題目前沒有開放作答")
                if now - rnd.opened_at > rnd.limit:
                    raise PhaseError("本題作答時間已到")
                opened_at = rnd.opened_at
            if any(s.team == team for s in self.submissions[number]):
                raise AlreadySubmittedError("本組已送出這一題，不可修改")
            cleaned = clean_answers(answers, len(q.slots))
            next_seq = self._seq + 1
            # 讓出點夾在「讀序號」與「寫序號／寫紀錄」之間：拿掉鎖時並發測試必紅（buzz-answering v1.1 D1）
            await self._checkpoint()
            self._seq = next_seq
            elapsed = int((now - opened_at) * 1000)
            sub = Submission(team, number, cleaned, next_seq, elapsed)
            self.submissions[number].append(sub)
            self.drafts.get(team, {}).pop(number, None)  # 送出即清該組該題草稿（team-mode D3）
            await self._bump()
            return sub

    # ---- 組內草稿（team-mode D4） ----
    async def set_draft(self, team: str, number: int, answers: list[str]) -> None:
        async with self._lock:
            if not self.team_play:
                raise PhaseError("只有組隊模式可以共用草稿")
            self._require(Phase.ANSWERING)
            q = self.question(number)
            if self.mode.sequential:
                rnd = self.current
                if rnd is None or rnd.number != number or rnd.closed:
                    raise PhaseError("這一題目前沒有開放作答")
            if any(s.team == team for s in self.submissions[number]):
                raise AlreadySubmittedError("本組已送出這一題，不可修改")
            cleaned = clean_draft(answers, len(q.slots))
            await self._checkpoint()
            self.drafts.setdefault(team, {})[number] = cleaned
            await self._bump()

    def own_submissions(self, team: str) -> list[Submission]:
        return [s for subs in self.submissions.values() for s in subs if s.team == team]

    # ---- 階段 ----
    async def _transition(self, target: Phase) -> None:
        check_transition(self.phase, target)
        await self._checkpoint()
        self.phase = target

    async def start(self) -> None:
        async with self._lock:
            if not self.questions:
                raise PhaseError("尚未匯入題目，不能開始搶答")
            await self._transition(Phase.ANSWERING)
            self._started_at = self._clock()
            # 開始搶答即換新邀請碼：準備階段被瞄到的碼在搶答中失效，
            # 搶答中加入只能向老師索取（team-mode v1.1 D2）
            for team in self._codes:
                self._codes[team] = self._new_code()
            await self._bump()

    async def end(self) -> None:
        async with self._lock:
            # 明寫「結束搶答只在搶答中」；判定模式另由轉移表擋 judging → judging（game-mode-framework v1.2）
            self._require(Phase.ANSWERING)
            if self.mode.sequential and self.current is not None:
                raise PhaseError("請先揭曉目前這一題，再結束活動")
            await self._transition(Phase.JUDGING if self.mode.judged else Phase.ENDED)
            await self._bump()

    # ---- 判定（game-mode-framework D3、D4） ----
    def _submission(self, number: int, team: str) -> Submission:
        self.question(number)
        for s in self.submissions.get(number, []):
            if s.team == team:
                return s
        raise KeyError(team)

    def suggestion(self, number: int, team: str) -> bool | None:
        return suggest(self._submission(number, team).answers, self.question(number).slots)

    def pending_judgments(self) -> int:
        return sum(1 for n, subs in self.submissions.items() for s in subs
                   if s.team not in self.judgments.get(n, {}))

    def _require_judgeable(self, number: int) -> None:
        """全部同時開放的模式在 judging 判定；逐題模式只能判定已關閉、尚未揭曉的那一題。"""
        if not self.mode.sequential:
            self._require(Phase.JUDGING)
            return
        self._require(Phase.ANSWERING)
        rnd = self.rounds.get(number)
        if rnd is None or not rnd.closed or rnd.revealed:
            raise PhaseError("只能判定已關閉、尚未揭曉的題目")

    def pending_for(self, number: int) -> int:
        judged = self.judgments.get(number, {})
        return sum(1 for s in self.submissions.get(number, []) if s.team not in judged)

    async def judge(self, number: int, team: str, correct: bool) -> None:
        async with self._lock:
            self._require_judgeable(number)
            self._submission(number, team)
            await self._checkpoint()
            self.judgments.setdefault(number, {})[team] = correct
            await self._bump()

    async def accept_suggestions(self) -> int:
        """只寫入「尚未判定且有建議」者；老師已判定的不覆蓋。"""
        async with self._lock:
            if self.mode.sequential:
                rnd = self.current
                if rnd is None:
                    raise PhaseError("沒有可判定的題目")
                self._require_judgeable(rnd.number)
                targets = {rnd.number: self.submissions.get(rnd.number, [])}
            else:
                self._require(Phase.JUDGING)
                targets = self.submissions
            todo = []
            for number, subs in targets.items():
                for s in subs:
                    if s.team in self.judgments.get(number, {}):
                        continue
                    hint = suggest(s.answers, self.question(number).slots)
                    if hint is not None:
                        todo.append((number, s.team, hint))
            await self._checkpoint()
            for number, team, hint in todo:
                self.judgments.setdefault(number, {})[team] = hint
            if todo:
                await self._bump()
            return len(todo)

    # ---- 經典搶答結束後依順位檢查（answer-review D1–D3） ----
    def _require_reviewable(self, number: int) -> None:
        if self.mode.key != "classic":
            raise PhaseError("只有經典搶答可以檢查")
        if self.phase is not Phase.ENDED:
            raise PhaseError("搶答結束後才能檢查")
        self.question(number)  # 題號不存在 ⇒ KeyError ⇒ 404

    def review_candidate(self, number: int) -> Ranked | None:
        """目前候選＝規則產生的得主（依順位第一個未被判錯者）；全部判錯或無送出為 None。"""
        ranked = self.rule.rank(self.submissions.get(number, []), self.judgments.get(number, {}),
                                self.attrs_of(number))
        return next((r for r in ranked if r.is_winner), None)

    async def review(self, number: int, team: str, correct: bool) -> None:
        async with self._lock:
            self._require_reviewable(number)
            cand = self.review_candidate(number)
            if cand is not None and cand.correct is True:
                raise PhaseError("本題已鎖定，請先重設本題")
            if cand is None:
                raise PhaseError("本題沒有可檢查的答案")
            # 老師端帶上畫面上的候選；不符（例：連點第二下）即拒，不會跳過一組
            if cand.team != team:
                raise PhaseError("這一組不是目前要檢查的答案，請重新整理")
            await self._checkpoint()
            self.judgments.setdefault(number, {})[team] = correct
            await self._bump()

    async def review_reset(self, number: int) -> None:
        async with self._lock:
            self._require_reviewable(number)
            if not self.judgments.get(number):
                raise PhaseError("本題尚未檢查")
            await self._checkpoint()
            self.judgments[number] = {}
            await self._bump()

    # ---- Google 副本寫回紀錄（answer-review D5 v1.1） ----
    async def mark_sheet_written(self, sheet_id: str, numbers: frozenset[int]) -> None:
        """寫回成功後記下這次寫過答案的題號；寫回期間若已換了副本（重新匯入）就不記。"""
        async with self._lock:
            if self.source_sheet_id == sheet_id:
                self.sheet_written = numbers

    async def reveal(self) -> None:
        async with self._lock:
            self._require(Phase.JUDGING)
            pending = self.pending_judgments()
            if pending:
                raise PhaseError(f"尚有 {pending} 筆未判定，全部判定後才能揭曉")
            await self._transition(Phase.ENDED)
            await self._bump()

    # ---- 逐題回合（mode-timed-scoring D3） ----
    @property
    def current(self) -> Round | None:
        """唯一一個尚未揭曉的回合。"""
        return next((r for r in self.rounds.values() if not r.revealed), None)

    async def open_next(self) -> int:
        async with self._lock:
            self._require(Phase.ANSWERING)
            if not self.mode.sequential:
                raise PhaseError("此模式不逐題開放")
            if self.current is not None:
                raise PhaseError("請先揭曉目前這一題")
            number = next((q.number for q in self.questions if q.number not in self.rounds), None)
            if number is None:
                raise PhaseError("所有題目都已開放過")
            limit = self.attrs_of(number).time_limit
            await self._checkpoint()
            rnd = Round(number, self._clock(), int((self._wall() + limit) * 1000), limit)
            self.rounds[number] = rnd
            self._timer = asyncio.create_task(self._run_timer(rnd))
            await self._bump()
            return number

    async def _run_timer(self, rnd: Round) -> None:
        # 迴圈直到關閉：Windows 上 asyncio 計時可能提早約一個解析度（15.6 毫秒）醒來，單次睡眠會漏關
        while not rnd.closed and self.rounds.get(rnd.number) is rnd:
            remaining = rnd.opened_at + rnd.limit - self._clock()
            if remaining > 0:
                await self._sleep(remaining)
            await self.close_due()

    async def close_due(self) -> None:
        """計時器呼叫：目前回合已到時限才關閉（可重入；送出路徑另有自己的截止比對）。"""
        async with self._lock:
            rnd = self.current
            if rnd is None or rnd.closed or self._clock() - rnd.opened_at < rnd.limit:
                return
            await self._checkpoint()
            rnd.closed = True
            await self._bump()

    async def close_question(self) -> int:
        async with self._lock:
            rnd = self.current
            if rnd is None or rnd.closed:
                raise PhaseError("沒有進行中的題目")
            await self._checkpoint()
            rnd.closed = True
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None
            await self._bump()
            return rnd.number

    async def reveal_question(self) -> int:
        async with self._lock:
            rnd = self.current
            if rnd is None or not rnd.closed:
                raise PhaseError("本題尚未關閉")
            pending = self.pending_for(rnd.number)
            if pending:
                raise PhaseError(f"尚有 {pending} 筆未判定，全部判定後才能揭曉")
            await self._checkpoint()
            rnd.revealed = True
            await self._bump()
            return rnd.number

    async def reset(self) -> None:
        async with self._lock:
            await self._transition(Phase.PREPARING)
            self._clear_answers()
            await self._bump()
