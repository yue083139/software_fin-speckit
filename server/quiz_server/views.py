"""按身分裁切的畫面狀態（app-skeleton D4、作答隔離）。

送往學生的畫面狀態只能由 `student_view` 產生；不存在「同一份 payload 推給所有人」的路徑。
學生身分一律是由組別憑證反查出的組別（None＝無效憑證）。
"""
from typing import Any

from . import results
from .activity import Activity
from .phases import Phase


def question_outline(a: Activity) -> list[dict[str, Any]]:
    """題號與子題標籤；不含作答格座標與原檔內容（guided-notes-import D7）。"""
    return [{"number": q.number, "labels": [s.display for s in q.slots]} for q in a.questions]


def teacher_view(a: Activity) -> dict[str, Any]:
    return {
        "role": "teacher",
        "phase": a.phase.value,
        "teams": list(a.teams),
        "joined": a.joined_teams(),
        "source": a.source_name,
        "questions": question_outline(a),
    }


def student_view(a: Activity, team: str | None) -> dict[str, Any]:
    if team is None or team not in a.teams:
        # 無效憑證只回最少資訊，不得落到其他 view（作答隔離）
        return {"role": "student", "phase": a.phase.value, "team": None, "team_valid": False}
    view: dict[str, Any] = {
        "role": "student",
        "phase": a.phase.value,
        "team": team,
        "team_valid": True,
        "questions": question_outline(a),
        # 只含本組；不含順位、序號與他組是否送出（buzz-answering D3）
        "my_submissions": [
            {"question": s.question, "answers": list(s.answers)} for s in a.own_submissions(team)
        ],
    }
    # 只有 ended 才揭曉；其餘階段（含日後新增者）一律不帶他組資料
    if a.phase is Phase.ENDED:
        view["results"] = results.build(a)
    return view


def view_for(role: str, team: str | None, a: Activity) -> dict[str, Any]:
    if role == "teacher":
        return teacher_view(a)
    return student_view(a, team)
