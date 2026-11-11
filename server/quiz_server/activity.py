"""活動狀態：唯一的狀態來源（app-skeleton D2）。

所有改變狀態的方法都在 `_lock` 內執行，檢查與寫入之間以 `_checkpoint()` 讓出一次控制權——
讓並發測試真的交錯執行，拿掉鎖時測試必紅（app-skeleton v1.1 D2）。改變後遞增 `version`
並喚醒 `changed`，由各 WebSocket 連線自己的送出迴圈重算 view（app-skeleton D4）。
"""
import asyncio
import secrets
import time
import unicodedata

from .guided_notes import ParsedNotes, Question, parse_workbook
from .phases import Phase, PhaseError, check_transition
from .scoring import ClassicBuzzRule, ScoringRule, Submission

MIN_TEAMS, MAX_TEAMS, DEFAULT_TEAMS = 2, 12, 4
MAX_ANSWER_CHARS = 200


class TeamTakenError(Exception):
    """該組已有裝置持有組別憑證；API 層轉成 409。"""


class AlreadySubmittedError(Exception):
    """本組本題已送出，不可修改；API 層轉成 409。"""


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


def team_names(n: int) -> list[str]:
    return [f"第{i}組" for i in range(1, n + 1)]


class Activity:
    def __init__(self, team_count: int = DEFAULT_TEAMS) -> None:
        self._lock = asyncio.Lock()
        self.changed = asyncio.Condition()
        self.phase = Phase.PREPARING
        self.teams = team_names(team_count)
        self.version = 0
        self._tokens: dict[str, str] = {}  # 組別憑證 → 組別（app-skeleton D6）
        self.notes: ParsedNotes | None = None
        self.source_bytes: bytes | None = None  # 匯入當下的原檔，供匯出寫回（guided-notes-import D6）
        self.source_name: str | None = None
        self.rule: ScoringRule = ClassicBuzzRule()
        self.submissions: dict[int, list[Submission]] = {}
        self._seq = 0
        self._started_at = 0.0

    @property
    def questions(self) -> tuple[Question, ...]:
        return self.notes.questions if self.notes else ()

    @staticmethod
    async def _checkpoint() -> None:
        await asyncio.sleep(0)

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

    async def join(self, team: str) -> str:
        async with self._lock:
            if team not in self.teams:
                raise KeyError(team)
            if team in self._tokens.values():
                raise TeamTakenError("此組已有裝置加入，請老師釋放後再加入")
            await self._checkpoint()  # 讓出點必須夾在「檢查」與「寫入」之間，拿掉鎖時並發測試才會紅
            token = secrets.token_urlsafe(16)
            self._tokens[token] = team
            await self._bump()
            return token

    async def release(self, team: str) -> None:
        async with self._lock:
            if team not in self.teams:
                raise KeyError(team)
            self._tokens = {k: v for k, v in self._tokens.items() if v != team}
            await self._bump()

    async def configure_teams(self, count: int) -> None:
        if not MIN_TEAMS <= count <= MAX_TEAMS:
            raise ValueError(f"組數須介於 {MIN_TEAMS} 到 {MAX_TEAMS}")
        async with self._lock:
            self._require(Phase.PREPARING)
            await self._checkpoint()
            self.teams = team_names(count)
            self._tokens.clear()  # 改組數即撤銷所有組別憑證
            await self._bump()

    def require_preparing(self) -> None:
        self._require(Phase.PREPARING)

    # ---- 題目 ----
    async def load_questions(self, data: bytes, name: str) -> None:
        async with self._lock:
            self._require(Phase.PREPARING)
            notes = parse_workbook(data)  # 解析失敗拋 GuidedNotesError，狀態不變
            await self._checkpoint()
            self.notes, self.source_bytes, self.source_name = notes, data, name
            self._clear_answers()
            await self._bump()

    def _clear_answers(self) -> None:
        self.submissions = {q.number: [] for q in self.questions}
        self._seq = 0

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
            if any(s.team == team for s in self.submissions[number]):
                raise AlreadySubmittedError("本組已送出這一題，不可修改")
            cleaned = clean_answers(answers, len(q.slots))
            next_seq = self._seq + 1
            # 讓出點夾在「讀序號」與「寫序號／寫紀錄」之間：拿掉鎖時並發測試必紅（buzz-answering v1.1 D1）
            await self._checkpoint()
            self._seq = next_seq
            elapsed = int((time.monotonic() - self._started_at) * 1000)
            sub = Submission(team, number, cleaned, next_seq, elapsed)
            self.submissions[number].append(sub)
            await self._bump()
            return sub

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
            self._started_at = time.monotonic()
            await self._bump()

    async def end(self) -> None:
        async with self._lock:
            await self._transition(Phase.ENDED)
            await self._bump()

    async def reset(self) -> None:
        async with self._lock:
            await self._transition(Phase.PREPARING)
            self._clear_answers()
            await self._bump()
