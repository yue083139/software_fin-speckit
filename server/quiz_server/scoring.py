"""搶答判定規則（buzz-answering D2；docs/trd-game-modes.md T-02 預留）。

結果只由規則產生：view、結果畫面與匯出都經 `Activity.rule`，不在別處重算。
"""
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Submission:
    team: str
    question: int
    answers: tuple[str, ...]
    seq: int  # 伺服器在活動鎖內配發的接收序（順位唯一依據）
    elapsed_ms: int  # 自開始搶答起的伺服器單調時鐘毫秒數（時間計分模式預留）


@dataclass(frozen=True)
class QuestionAttrs:
    """題目屬性（question-settings D1；TRD T-05）：老師在準備階段設定，不寫回 Guided Notes。"""

    multiplier: int = 1  # 1 或 2（雙倍分數題）


DEFAULT_ATTRS = QuestionAttrs()


@dataclass(frozen=True)
class Ranked:
    team: str
    answers: tuple[str, ...]
    seq: int
    rank: int
    is_winner: bool
    score: int
    correct: bool | None = None  # None＝本模式不判定或尚未判定（game-mode-framework D2）


class ScoringRule(Protocol):
    name: str

    def rank(self, submissions: Sequence[Submission], judgments: Mapping[str, bool] | None = None,
             attrs: QuestionAttrs | None = None) -> list[Ranked]:
        """`judgments`：該題「組別 → 是否正確」。"""
        ...

    def team_scores(self, teams: Sequence[str], ranked: Sequence[Sequence[Ranked]]) -> dict[str, int]: ...


class ClassicBuzzRule:
    """經典搶答：伺服器接收序最小者得該題（R-10），得 1 × 倍率分；不判對錯。"""

    name = "classic"

    def rank(self, submissions: Sequence[Submission], judgments: Mapping[str, bool] | None = None,
             attrs: QuestionAttrs | None = None) -> list[Ranked]:
        m = (attrs or DEFAULT_ATTRS).multiplier
        ordered = sorted(submissions, key=lambda s: s.seq)
        return [
            Ranked(s.team, s.answers, s.seq, i, i == 1, m if i == 1 else 0)
            for i, s in enumerate(ordered, 1)
        ]

    def team_scores(self, teams: Sequence[str], ranked: Sequence[Sequence[Ranked]]) -> dict[str, int]:
        return _sum_scores(teams, ranked)


def _sum_scores(teams: Sequence[str], ranked: Sequence[Sequence[Ranked]]) -> dict[str, int]:
    scores = dict.fromkeys(teams, 0)
    for per_question in ranked:
        for r in per_question:
            if r.team in scores:
                scores[r.team] += r.score
    return scores


class AccuracyRule:
    """只計對錯（TRD M3）：判定正確者各得 1 × 倍率分；得主＝依 seq 最早的正確送出，供匯出寫回。"""

    name = "accuracy"

    def rank(self, submissions: Sequence[Submission], judgments: Mapping[str, bool] | None = None,
             attrs: QuestionAttrs | None = None) -> list[Ranked]:
        judged = judgments or {}
        m = (attrs or DEFAULT_ATTRS).multiplier
        out: list[Ranked] = []
        winner_found = False
        for i, s in enumerate(sorted(submissions, key=lambda s: s.seq), 1):
            correct = judged.get(s.team)
            is_winner = correct is True and not winner_found
            winner_found = winner_found or is_winner
            out.append(Ranked(s.team, s.answers, s.seq, i, is_winner, m if correct is True else 0, correct))
        return out

    def team_scores(self, teams: Sequence[str], ranked: Sequence[Sequence[Ranked]]) -> dict[str, int]:
        return _sum_scores(teams, ranked)
