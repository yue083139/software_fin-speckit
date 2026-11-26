"""按身分裁切的畫面狀態（app-skeleton D4、作答隔離）。

送往學生的畫面狀態只能由 `student_view` 產生；不存在「同一份 payload 推給所有人」的路徑。
學生身分一律是由組別憑證反查出的組別（None＝無效憑證）。
"""
from typing import Any

from . import results
from .activity import Activity
from .modes import MODES
from .phases import Phase


def _prompt_visible(a: Activity, number: int, teacher: bool) -> bool:
    """question-text D2：學生只在搶答開始後看得到敘述，逐題模式只看得到已開放過的題。

    預設不給（fail-closed）：日後新增的階段不在下列條件中就不帶。
    """
    if teacher or a.phase is Phase.ENDED:
        return True
    if a.phase not in (Phase.ANSWERING, Phase.JUDGING):
        return False
    return not a.mode.sequential or number in a.rounds


def question_outline(a: Activity, teacher: bool) -> list[dict[str, Any]]:
    """題號、子題標籤與依階段開放的題目敘述；不含作答格座標與原檔其他內容（guided-notes-import D7）。"""
    outline = []
    for q in a.questions:
        # 倍率不是他組資訊，學生也看得到（question-settings D3）
        item: dict[str, Any] = {"number": q.number, "labels": [s.display for s in q.slots],
                                "multiplier": a.attrs_of(q.number).multiplier,
                                "time_limit": a.attrs_of(q.number).time_limit}
        if _prompt_visible(a, q.number, teacher):
            item["prompts"] = [s.prompt for s in q.slots]
        outline.append(item)
    return outline


def round_view(a: Activity) -> dict[str, Any] | None:
    """目前回合的公開狀態：同一時間對所有人相同，不含任何組別資訊（mode-timed-scoring D5）。"""
    rnd = a.current
    if rnd is None:
        return None
    return {"question": rnd.number, "state": "closed" if rnd.closed else "open",
            "deadline_epoch_ms": rnd.deadline_epoch_ms}


def mode_info(a: Activity, teacher: bool) -> dict[str, Any]:
    info: dict[str, Any] = {"key": a.mode.key, "label": a.mode.label, "sequential": a.mode.sequential}
    if teacher:
        info["judged"] = a.mode.judged
    return info


def score_label(a: Activity) -> str:
    plain = a.mode.key == "classic" and all(a.attrs_of(q.number).multiplier == 1 for q in a.questions)
    return "得題數" if plain else "得分"


def teacher_view(a: Activity) -> dict[str, Any]:
    view: dict[str, Any] = {
        "role": "teacher",
        "phase": a.phase.value,
        "teams": list(a.teams),
        "joined": a.joined_teams(),
        "team_play": a.team_play,
        "devices": {t: a.devices(t) for t in a.teams},
        "invite_codes": {t: c for t in a.teams if (c := a.invite_code(t))},  # 老師看得到邀請碼，看不到草稿
        "source": a.source_name,
        "student_url": a.public_url,  # 只在老師 view（student-qr D3）：給 QR code 用
        "tunnel": a.tunnel_state,  # 手機連線狀態，只在老師 view（easy-setup D3）
        "questions": question_outline(a, teacher=True),
        "mode": mode_info(a, teacher=True),
        "round": round_view(a),
        "modes": [{"key": m.key, "label": m.label} for m in MODES.values()],
        "score_label": score_label(a),
        "pending_judgments": a.pending_judgments(),
        # 老師任何階段都看得到即時作答狀況與結果（results-view D2）；判定建議與參考答案只在這裡
        "board": results.build(a, teacher=True),
        "team_scores": results.team_scores(a),
    }
    if a.mode.sequential:
        view["leaderboard"] = results.leaderboard(a, with_scores=True)
    return view


def student_view(a: Activity, team: str | None) -> dict[str, Any]:
    if team is None or team not in a.teams:
        # 無效憑證只回最少資訊，不得落到其他 view（作答隔離）
        return {"role": "student", "phase": a.phase.value, "team": None, "team_valid": False}
    view: dict[str, Any] = {
        "role": "student",
        "phase": a.phase.value,
        "team": team,
        "team_valid": True,
        "questions": question_outline(a, teacher=False),
        "mode": mode_info(a, teacher=False),
        "round": round_view(a),
        "score_label": score_label(a),
        "team_play": a.team_play,
        # 只含本組；不含順位、序號與他組是否送出（buzz-answering D3）
        "my_submissions": [
            {"question": s.question, "answers": list(s.answers)} for s in a.own_submissions(team)
        ],
    }
    if a.team_play:
        # 邀請碼只在準備階段給學生；搶答中只有老師畫面有（team-mode v1.1 D5）
        if a.phase is Phase.PREPARING:
            view["invite_code"] = a.invite_code(team)
        # 組內草稿只在搶答中、只含本組（team-mode D5）；其餘階段不帶，fail-closed
        if a.phase is Phase.ANSWERING:
            view["drafts"] = [{"question": n, "answers": list(ans)}
                              for n, ans in sorted(a.drafts.get(team, {}).items())]
    # 時間計分的例外（負責人 2026-11-12 裁定）：已揭曉題只給本組結果與各組名次，不給他組答案與分數
    if a.mode.sequential and a.phase is not Phase.ENDED:
        mine = results.own_revealed(a, team)
        view["revealed"] = mine
        view["my_total"] = sum(r["score"] for r in mine)
        view["leaderboard"] = results.leaderboard(a, with_scores=False)
    # 只有 ended 才揭曉完整結果；其餘階段（含 judging 與日後新增者）一律不帶他組資料與判定結果
    if a.phase is Phase.ENDED:
        view["results"] = results.build(a)
        view["team_scores"] = results.team_scores(a)
    return view


def view_for(role: str, team: str | None, a: Activity) -> dict[str, Any]:
    if role == "teacher":
        return teacher_view(a)
    return student_view(a, team)
