"""搶答結果（results-view D1）：老師與學生共用同一個函式，結果一律經 `Activity.rule` 產生。"""
from typing import Any

from .activity import Activity


def build(a: Activity) -> list[dict[str, Any]]:
    out = []
    for q in a.questions:
        ranked = a.rule.rank(a.submissions.get(q.number, []))
        winner = next((r for r in ranked if r.is_winner), None)
        out.append({
            "number": q.number,
            "labels": [s.display for s in q.slots],
            "ranking": [
                {"team": r.team, "answers": list(r.answers), "rank": r.rank,
                 "is_winner": r.is_winner, "score": r.score}
                for r in ranked
            ],
            "winner": None if winner is None else {"team": winner.team, "answers": list(winner.answers)},
        })
    return out


def team_scores(a: Activity) -> dict[str, int]:
    """各組得分，由目前規則產生（經典規則＝各組得題數）。"""
    ranked = [a.rule.rank(a.submissions.get(q.number, [])) for q in a.questions]
    return a.rule.team_scores(a.teams, ranked)
