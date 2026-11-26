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
    time_limit: int = 20  # 秒，5–120；只有時間計分模式使用（mode-timed-scoring D2）


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
    """經典搶答：依伺服器接收序第一個未被老師判錯者得該題，得 1 × 倍率分。

    `judgments` 只在結束後的檢查寫入（answer-review D1）；沒有任何判定時＝順位 1 得主（R-10）。
    判錯者往後遞補、判對即鎖定；全部判錯則無得主。
    """

    name = "classic"

    def rank(self, submissions: Sequence[Submission], judgments: Mapping[str, bool] | None = None,
             attrs: QuestionAttrs | None = None) -> list[Ranked]:
        judged = judgments or {}
        m = (attrs or DEFAULT_ATTRS).multiplier
        out: list[Ranked] = []
        winner_found = False
        for i, s in enumerate(sorted(submissions, key=lambda s: s.seq), 1):
            correct = judged.get(s.team)
            is_winner = correct is not False and not winner_found
            winner_found = winner_found or is_winner
            out.append(Ranked(s.team, s.answers, s.seq, i, is_winner, m if is_winner else 0, correct))
        return out

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


def timed_points(elapsed_ms: int, limit: int, multiplier: int) -> int:
    """Kahoot 式時間計分（mode-timed-scoring D4）。

    floor(1000 × (1 − t ÷ T ÷ 2) + 0.5) × 倍率，t ≤ 0.5 秒滿分。

    以整數運算 (2001T − ms) // (2T) 實作：與上式代數相等，浮點寫法在 T＝5–120 秒間有 5129 例少 1 分。
    """
    ms = min(max(elapsed_ms, 0), limit * 1000)
    base = 1000 if ms <= 500 else (2001 * limit - ms) // (2 * limit)
    return base * multiplier


class TimedRule:
    """時間計分（TRD M2）：判定正確者依伺服器量得的作答毫秒計分；得主＝依 seq 最早的正確送出。"""

    name = "timed"

    def rank(self, submissions: Sequence[Submission], judgments: Mapping[str, bool] | None = None,
             attrs: QuestionAttrs | None = None) -> list[Ranked]:
        judged = judgments or {}
        a = attrs or DEFAULT_ATTRS
        out: list[Ranked] = []
        winner_found = False
        for i, s in enumerate(sorted(submissions, key=lambda s: s.seq), 1):
            correct = judged.get(s.team)
            is_winner = correct is True and not winner_found
            winner_found = winner_found or is_winner
            score = timed_points(s.elapsed_ms, a.time_limit, a.multiplier) if correct is True else 0
            out.append(Ranked(s.team, s.answers, s.seq, i, is_winner, score, correct))
        return out

    def team_scores(self, teams: Sequence[str], ranked: Sequence[Sequence[Ranked]]) -> dict[str, int]:
        return _sum_scores(teams, ranked)
