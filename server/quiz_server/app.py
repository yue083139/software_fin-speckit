"""HTTP 與 WebSocket 端點（app-skeleton D1、D4–D6）。介面契約見 contracts/api.md。"""
import asyncio
import logging
import os
import secrets
from pathlib import Path
from typing import Annotated, Any
from urllib.parse import quote

import httpx
from fastapi import (
    Depends,
    FastAPI,
    File,
    Header,
    HTTPException,
    Request,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import results
from .activity import Activity, AlreadySubmittedError, InviteCodeError, TeamTakenError
from .guided_notes import GuidedNotesError, write_answers
from .phases import Phase, PhaseError
from .sources import MAX_BYTES, SourceError, check_upload, download_sheet
from .views import view_for

log = logging.getLogger("quiz_server")
DEFAULT_STATIC = Path(__file__).resolve().parents[2] / "web" / "dist"
WS_UNAUTHORIZED = 4401


class TeamsBody(BaseModel):
    count: int


class TeamBody(BaseModel):
    team: str


class JoinBody(BaseModel):
    team: str
    code: str | None = None  # 組隊時加入已有裝置的組別須帶邀請碼（team-mode D2）


class TeamPlayBody(BaseModel):
    enabled: bool


class DraftBody(BaseModel):
    question: int
    answers: list[str]


class UrlBody(BaseModel):
    url: str


class SubmitBody(BaseModel):
    question: int
    answers: list[str]


class QuestionSettingsBody(BaseModel):
    question: int
    multiplier: int | None = None
    time_limit: int | None = None  # mode-timed-scoring：兩欄皆可選、至少一欄


class ModeBody(BaseModel):
    mode: str


class JudgeBody(BaseModel):
    question: int
    team: str
    correct: bool


XLSX_MEDIA = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def export_filename(source: str | None) -> str:
    stem = (source or "guided-notes").rsplit(".", 1)[0]
    return f"{stem}-搶答結果.xlsx"


def resolve_teacher_key(explicit: str | None = None) -> str:
    return explicit or os.environ.get("QUIZ_TEACHER_KEY") or secrets.token_urlsafe(16)


def create_app(activity: Activity | None = None, teacher_key: str | None = None,
               static_dir: Path | None = DEFAULT_STATIC,
               http_transport: httpx.AsyncBaseTransport | None = None) -> FastAPI:
    app = FastAPI(title="課堂搶答系統")
    act = activity or Activity()
    secret = resolve_teacher_key(teacher_key)
    app.state.activity = act

    def is_teacher(given: str | None) -> bool:
        return given is not None and secrets.compare_digest(given.encode(), secret.encode())

    def require_teacher(x_teacher_key: Annotated[str | None, Header()] = None) -> None:
        if not is_teacher(x_teacher_key):
            raise HTTPException(401, "需要老師金鑰")

    teacher = [Depends(require_teacher)]

    @app.exception_handler(PhaseError)
    async def _phase_error(_: Request, exc: PhaseError) -> JSONResponse:
        return JSONResponse({"detail": str(exc)}, status_code=409)

    @app.exception_handler(TeamTakenError)
    @app.exception_handler(AlreadySubmittedError)
    async def _conflict(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse({"detail": str(exc)}, status_code=409)

    @app.exception_handler(InviteCodeError)
    async def _bad_code(_: Request, exc: InviteCodeError) -> JSONResponse:
        return JSONResponse({"detail": str(exc)}, status_code=403)

    @app.exception_handler(RequestValidationError)
    async def _invalid_body(_: Request, exc: RequestValidationError) -> JSONResponse:
        # FastAPI 預設會把請求本體原樣放進錯誤回應；本體可能含答案，一律不回顯（作答隔離）
        return JSONResponse({"detail": "請求格式不正確"}, status_code=422)

    @app.exception_handler(GuidedNotesError)
    @app.exception_handler(SourceError)
    async def _bad_source(_: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse({"detail": str(exc)}, status_code=400)

    @app.exception_handler(ValueError)
    async def _value_error(_: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse({"detail": str(exc)}, status_code=422)

    @app.exception_handler(KeyError)
    async def _key_error(_: Request, exc: KeyError) -> JSONResponse:
        return JSONResponse({"detail": "找不到指定的組別或題目"}, status_code=404)

    @app.get("/api/public/info")
    async def public_info() -> dict[str, Any]:
        # 只多組隊開關；台數與邀請碼不公開（team-mode D5）
        return {"phase": act.phase.value, "teams": list(act.teams), "joined": act.joined_teams(),
                "team_play": act.team_play}

    @app.post("/api/student/join")
    async def join(body: JoinBody) -> dict[str, str]:
        token = await act.join(body.team, body.code)
        log.info("組別 %s 加入", body.team)
        return {"team": body.team, "token": token}

    @app.post("/api/student/submit")
    async def submit(body: SubmitBody,
                     x_team_token: Annotated[str | None, Header()] = None) -> dict[str, Any]:
        team = act.team_of(x_team_token)  # 只認憑證，不採信請求內的任何組別名稱
        if team is None:
            raise HTTPException(403, "組別憑證無效，請回首頁重新加入")
        sub = await act.submit(team, body.question, body.answers)
        log.info("送出：組別 %s 題 %s 序號 %s", team, sub.question, sub.seq)
        # 成功回應只回本組這筆的題號與答案，不含序號與順位（buzz-answering D3）
        return {"question": sub.question, "answers": list(sub.answers)}

    @app.post("/api/student/draft")
    async def draft(body: DraftBody,
                    x_team_token: Annotated[str | None, Header()] = None) -> dict[str, int]:
        team = act.team_of(x_team_token)
        if team is None:
            raise HTTPException(403, "組別憑證無效，請回首頁重新加入")
        await act.set_draft(team, body.question, body.answers)
        # 不回顯草稿內容，也不記日誌（team-mode D4）
        return {"question": body.question}

    @app.post("/api/teacher/team-play", dependencies=teacher)
    async def team_play(body: TeamPlayBody) -> dict[str, bool]:
        await act.set_team_play(body.enabled)
        return {"team_play": act.team_play}

    @app.get("/api/teacher/state", dependencies=teacher)
    async def teacher_state() -> dict[str, Any]:
        return view_for("teacher", None, act)

    @app.post("/api/teacher/teams", dependencies=teacher)
    async def set_teams(body: TeamsBody) -> dict[str, Any]:
        await act.configure_teams(body.count)
        return {"teams": list(act.teams)}

    @app.post("/api/teacher/release", dependencies=teacher)
    async def release(body: TeamBody) -> dict[str, str]:
        await act.release(body.team)
        return {"released": body.team}

    @app.post("/api/teacher/import", dependencies=teacher)
    async def import_file(file: Annotated[UploadFile, File()]) -> dict[str, Any]:
        data = await file.read(MAX_BYTES + 1)
        check_upload(file.filename, data)
        await act.load_questions(data, file.filename or "guided-notes.xlsx")
        log.info("匯入上傳檔：%d 題", len(act.questions))
        return {"source": act.source_name, "count": len(act.questions)}

    @app.post("/api/teacher/import-url", dependencies=teacher)
    async def import_url(body: UrlBody) -> dict[str, Any]:
        act.require_preparing()  # 先擋階段，避免搶答中還對外發請求
        data = await download_sheet(body.url, transport=http_transport)
        await act.load_questions(data, "Google 試算表.xlsx")
        log.info("匯入 Google 試算表：%d 題", len(act.questions))
        return {"source": act.source_name, "count": len(act.questions)}

    @app.get("/api/teacher/export", dependencies=teacher)
    async def export() -> Response:
        if act.phase is not Phase.ENDED:
            raise PhaseError("搶答結束後才能匯出")
        if act.notes is None or act.source_bytes is None:
            raise PhaseError("尚未匯入題目")
        data = write_answers(act.source_bytes, act.notes, results.winning_answers(act))
        name = export_filename(act.source_name)
        disposition = f"attachment; filename=\"guided-notes-result.xlsx\"; filename*=UTF-8''{quote(name)}"
        return Response(data, media_type=XLSX_MEDIA, headers={"Content-Disposition": disposition})

    @app.post("/api/teacher/start", dependencies=teacher)
    async def start() -> dict[str, str]:
        await act.start()
        log.info("活動 v%s 開始搶答", act.version)
        return {"phase": act.phase.value}

    @app.post("/api/teacher/end", dependencies=teacher)
    async def end() -> dict[str, str]:
        await act.end()
        log.info("活動 v%s 結束搶答", act.version)
        return {"phase": act.phase.value}

    @app.post("/api/teacher/question-settings", dependencies=teacher)
    async def question_settings(body: QuestionSettingsBody) -> dict[str, int]:
        attrs = await act.set_question(body.question, body.multiplier, body.time_limit)
        return {"question": body.question, "multiplier": attrs.multiplier, "time_limit": attrs.time_limit}

    @app.post("/api/teacher/open-next", dependencies=teacher)
    async def open_next() -> dict[str, int]:
        number = await act.open_next()
        log.info("開放第 %s 題", number)
        return {"question": number}

    @app.post("/api/teacher/close-question", dependencies=teacher)
    async def close_question() -> dict[str, int]:
        return {"question": await act.close_question()}

    @app.post("/api/teacher/reveal-question", dependencies=teacher)
    async def reveal_question() -> dict[str, int]:
        number = await act.reveal_question()
        log.info("揭曉第 %s 題", number)
        return {"question": number}

    @app.post("/api/teacher/mode", dependencies=teacher)
    async def set_mode(body: ModeBody) -> dict[str, str]:
        await act.set_mode(body.mode)
        return {"mode": act.mode.key}

    @app.post("/api/teacher/judge", dependencies=teacher)
    async def judge(body: JudgeBody) -> dict[str, Any]:
        await act.judge(body.question, body.team, body.correct)
        log.info("判定：題 %s 組別 %s 結果 %s", body.question, body.team, body.correct)
        return {"question": body.question, "team": body.team, "correct": body.correct}

    @app.post("/api/teacher/accept-suggestions", dependencies=teacher)
    async def accept_suggestions() -> dict[str, int]:
        return {"applied": await act.accept_suggestions()}

    @app.post("/api/teacher/reveal", dependencies=teacher)
    async def reveal() -> dict[str, str]:
        await act.reveal()
        log.info("活動 v%s 揭曉結果", act.version)
        return {"phase": act.phase.value}

    @app.post("/api/teacher/reset", dependencies=teacher)
    async def reset() -> dict[str, str]:
        await act.reset()
        return {"phase": act.phase.value}

    @app.websocket("/ws")
    async def ws(socket: WebSocket, role: str = "student", key: str | None = None,
                 token: str | None = None) -> None:
        if role not in ("teacher", "student"):
            await socket.close(code=1008)
            return
        if role == "teacher" and not is_teacher(key):
            await socket.close(code=WS_UNAUTHORIZED)
            return
        await socket.accept()

        def current_view() -> dict[str, Any]:
            # 每次都由憑證重新反查組別：老師釋放後立即失效；客戶端自報的組別名稱一律不用
            team = None if role == "teacher" else act.team_of(token)
            return view_for(role, team, act)

        async def first_then_loop() -> None:
            seen_version = act.version
            view = current_view()
            await socket.send_json({"type": "state", "seq": 1, "view": view})
            last_view, seq = view, 1
            while True:
                async with act.changed:
                    await act.changed.wait_for(lambda v=seen_version: act.version != v)
                seen_version = act.version
                view = current_view()
                # 只在本連線自己的 view 改變時才送，seq 為本連線自己的序號：
                # 推播時機與全域版本號都不得透露他組活動（app-skeleton v1.1 D4）
                if view == last_view:
                    continue
                last_view, seq = view, seq + 1
                await socket.send_json({"type": "state", "seq": seq, "view": view})

        sender = asyncio.create_task(first_then_loop())
        try:
            while True:
                # 客戶端送來的任何訊框（文字或二進位）一律忽略，只等斷線
                # （實作輪紅隊：receive_text 遇二進位訊框會拋 KeyError）
                message = await socket.receive()
                if message["type"] == "websocket.disconnect":
                    break
        except WebSocketDisconnect:
            pass
        finally:
            sender.cancel()

    if static_dir is not None and static_dir.is_dir():
        app.mount("/", StaticFiles(directory=static_dir, html=True), name="web")
    return app
