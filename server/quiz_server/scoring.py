"""搶答判定規則（buzz-answering D2；docs/trd-game-modes.md T-02 預留）。

結果只由規則產生：view、結果畫面與匯出都經 `Activity.rule`，不在別處重算。
"""
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class Submission:
    team: str
    question: int
    answers: tuple[str, ...]
    seq: int  # 伺服器在活動鎖內配發的接收序（順位唯一依據）
    elapsed_ms: int  # 自開始搶答起的伺服器單調時鐘毫秒數（時間計分模式預留）


@dataclass(frozen=True)
class Ranked:
    team: str
    answers: tuple[str, ...]
    seq: int
    rank: int
    is_winner: bool
    score: int


class ScoringRule(Protocol):
    name: str

    def rank(self, submissions: Sequence[Submission], judgments: Mapping[str, bool] | None = None,
             attrs: Mapping[str, Any] | None = None) -> list[Ranked]: ...

    def team_scores(self, teams: Sequence[str], ranked: Sequence[Sequence[Ranked]]) -> dict[str, int]: ...


class ClassicBuzzRule:
    """經典搶答：伺服器接收序最小者得該題（R-10），得 1 分；不判對錯。"""

    name = "classic"

    def rank(self, submissions: Sequence[Submission], judgments: Mapping[str, bool] | None = None,
             attrs: Mapping[str, Any] | None = None) -> list[Ranked]:
        ordered = sorted(submissions, key=lambda s: s.seq)
        return [
            Ranked(s.team, s.answers, s.seq, i, i == 1, 1 if i == 1 else 0)
            for i, s in enumerate(ordered, 1)
        ]

    def team_scores(self, teams: Sequence[str], ranked: Sequence[Sequence[Ranked]]) -> dict[str, int]:
        scores = dict.fromkeys(teams, 0)
        for per_question in ranked:
            for r in per_question:
                if r.team in scores:
                    scores[r.team] += r.score
        return scores
