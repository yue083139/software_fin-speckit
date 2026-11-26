"""活動階段狀態機（app-skeleton D3）。

`judging` 為遊戲模式預留（docs/trd-game-modes.md T-03）；經典模式結束時由 answering 直接到 ended。
"""
from enum import StrEnum


class Phase(StrEnum):
    PREPARING = "preparing"
    ANSWERING = "answering"
    JUDGING = "judging"
    ENDED = "ended"


TRANSITIONS: dict[Phase, frozenset[Phase]] = {
    Phase.PREPARING: frozenset({Phase.ANSWERING}),
    Phase.ANSWERING: frozenset({Phase.ENDED, Phase.JUDGING}),
    Phase.JUDGING: frozenset({Phase.ENDED}),
    Phase.ENDED: frozenset({Phase.PREPARING}),
}


class PhaseError(Exception):
    """要求的階段轉移或操作與目前階段不符；API 層轉成 409。"""


def check_transition(current: Phase, target: Phase) -> None:
    if target not in TRANSITIONS[current]:
        raise PhaseError(f"目前階段 {current.value} 不能轉到 {target.value}")
