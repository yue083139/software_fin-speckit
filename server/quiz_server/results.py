"""搶答結果（results-view D1）：老師與學生共用同一個函式，結果一律經 `Activity.rule` 產生。

`teacher=True` 只**多加**老師專屬欄位（判定建議、參考答案；game-mode-framework D5、D6），共用欄位兩邊相同。
"""
from typing import Any

from .activity import Activity
from .scoring import Ranked


def _ranked(a: Activity, number: int) -> list[Ranked]:
    return a.rule.rank(a.submissions.get(number, []), a.judgments.get(number, {}), a.attrs_of(number))


def build(a: Activity, teacher: bool = False) -> list[dict[str, Any]]:
    out = []
    for q in a.questions:
        ranked = _ranked(a, q.number)
        winner = next((r for r in ranked if r.is_winner), None)
        ranking = []
        for r in ranked:
            item: dict[str, Any] = {"team": r.team, "answers": list(r.answers), "rank": r.rank,
                                    "is_winner": r.is_winner, "score": r.score, "correct": r.correct}
            if teacher:
                item["suggestion"] = a.suggestion(q.number, r.team)
            ranking.append(item)
        entry: dict[str, Any] = {
            "number": q.number,
            "labels": [s.display for s in q.slots],
            "multiplier": a.attrs_of(q.number).multiplier,
            "ranking": ranking,
            "winner": None if winner is None else {"team": winner.team, "answers": list(winner.answers)},
        }
        if teacher:
            entry["reference"] = [s.reference for s in q.slots]
        out.append(entry)
    return out


def team_scores(a: Activity) -> dict[str, int]:
    """各組得分，由目前規則產生（經典規則＝各組得題數）。"""
    return a.rule.team_scores(a.teams, [_ranked(a, q.number) for q in a.questions])


def winning_answers(a: Activity) -> dict[int, tuple[str, ...]]:
    """每題得主的答案（經規則產生）；無得主的題目不列入。"""
    out: dict[int, tuple[str, ...]] = {}
    for q in a.questions:
        winner = next((r for r in _ranked(a, q.number) if r.is_winner), None)
        if winner is not None:
            out[q.number] = winner.answers
    return out


# ---- 時間計分：每題揭曉後的本組結果與名次（mode-timed-scoring D5） ----
def revealed_numbers(a: Activity) -> list[int]:
    return [q.number for q in a.questions if (r := a.rounds.get(q.number)) is not None and r.revealed]


def revealed_scores(a: Activity) -> dict[str, int]:
    """各組在**已揭曉題**的累積分數；關閉但未揭曉的題目不計入。"""
    return a.rule.team_scores(a.teams, [_ranked(a, n) for n in revealed_numbers(a)])


def leaderboard(a: Activity, with_scores: bool) -> list[dict[str, Any]]:
    """名次：同分同名次、下一名跳號（1、1、3），依名次再依組別順序。

    學生版不帶分數（with_scores=False）：分數是作答秒數的單調函數，公開他組分數即可反推秒數（v1.1）。
    """
    scores = revealed_scores(a)
    rows = []
    for team in sorted(a.teams, key=lambda t: (-scores[t], a.teams.index(t))):
        row: dict[str, Any] = {"team": team, "rank": 1 + sum(1 for s in scores.values() if s > scores[team])}
        if with_scores:
            row["score"] = scores[team]
        rows.append(row)
    return rows


def own_revealed(a: Activity, team: str) -> list[dict[str, Any]]:
    """只有本組：每個已揭曉題的是否送出、對錯與得分。"""
    out = []
    for n in revealed_numbers(a):
        mine = next((r for r in _ranked(a, n) if r.team == team), None)
        if mine is None:
            out.append({"question": n, "submitted": False, "correct": None, "score": 0})
        else:
            out.append({"question": n, "submitted": True, "correct": mine.correct, "score": mine.score})
    return out
