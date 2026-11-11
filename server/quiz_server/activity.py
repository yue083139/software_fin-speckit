"""活動狀態：唯一的狀態來源（app-skeleton D2）。

所有改變狀態的方法都在 `_lock` 內執行，檢查與寫入之間以 `_checkpoint()` 讓出一次控制權——
讓並發測試真的交錯執行，拿掉鎖時測試必紅（app-skeleton v1.1 D2）。改變後遞增 `version`
並喚醒 `changed`，由各 WebSocket 連線自己的送出迴圈重算 view（app-skeleton D4）。
"""
import asyncio
import secrets

from .guided_notes import ParsedNotes, Question, parse_workbook
from .phases import Phase, PhaseError, check_transition

MIN_TEAMS, MAX_TEAMS, DEFAULT_TEAMS = 2, 12, 4


class TeamTakenError(Exception):
    """該組已有裝置持有組別憑證；API 層轉成 409。"""


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
        """清除作答紀錄；作答由 buzz-answering 卡加入。"""

    # ---- 階段 ----
    async def _transition(self, target: Phase) -> None:
        check_transition(self.phase, target)
        await self._checkpoint()
        self.phase = target

    async def start(self) -> None:
        async with self._lock:
            await self._transition(Phase.ANSWERING)
            await self._bump()

    async def end(self) -> None:
        async with self._lock:
            await self._transition(Phase.ENDED)
            await self._bump()

    async def reset(self) -> None:
        async with self._lock:
            await self._transition(Phase.PREPARING)
            await self._bump()
