"""遊戲模式登記表（game-mode-framework D1；docs/trd-game-modes.md T-01）。

模式只決定「用哪條判定規則」與「結束搶答後是否進入判定」；匯入與匯出不受模式影響。
"""
from dataclasses import dataclass

from .scoring import AccuracyRule, ClassicBuzzRule, ScoringRule, TimedRule


@dataclass(frozen=True)
class Mode:
    key: str
    label: str
    judged: bool  # 結束搶答後是否進入 judging
    rule: ScoringRule
    sequential: bool = False  # 逐題開放；判定在每題關閉後、仍在 answering 內（mode-timed-scoring D1）


MODES: dict[str, Mode] = {
    m.key: m for m in (
        Mode("classic", "經典搶答", False, ClassicBuzzRule()),
        Mode("accuracy", "只計對錯", True, AccuracyRule()),
        Mode("timed", "時間計分", False, TimedRule(), sequential=True),
    )
}
DEFAULT_MODE = "classic"


class ModeError(ValueError):
    """未知的模式鍵；API 層轉成 422。"""
