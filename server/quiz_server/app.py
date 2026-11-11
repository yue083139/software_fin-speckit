"""HTTP 與 WebSocket 端點（app-skeleton D1、D4–D6）。介面契約見 contracts/api.md。"""
import asyncio
import logging
import os
import secrets
from pathlib import Path
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Header, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .activity import Activity, TeamTakenError
from .phases import PhaseError
from .views import view_for

log = logging.getLogger("quiz_server")
DEFAULT_STATIC = Path(__file__).resolve().parents[2] / "web" / "dist"
WS_UNAUTHORIZED = 4401


class TeamsBody(BaseModel):
    count: int


class TeamBody(BaseModel):
    team: str


def resolve_teacher_key(explicit: str | None = None) -> str:
    return explicit or os.environ.get("QUIZ_TEACHER_KEY") or secrets.token_urlsafe(16)


def create_app(activity: Activity | None = None, teacher_key: str | None = None,
               static_dir: Path | None = DEFAULT_STATIC) -> FastAPI:
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
    async def _team_taken(_: Request, exc: TeamTakenError) -> JSONResponse:
        return JSONResponse({"detail": str(exc)}, status_code=409)

    @app.exception_handler(ValueError)
    async def _value_error(_: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse({"detail": str(exc)}, status_code=422)

    @app.exception_handler(KeyError)
    async def _key_error(_: Request, exc: KeyError) -> JSONResponse:
        return JSONResponse({"detail": "找不到指定的組別或題目"}, status_code=404)

    @app.get("/api/public/info")
    async def public_info() -> dict[str, Any]:
        return {"phase": act.phase.value, "teams": list(act.teams), "joined": act.joined_teams()}

    @app.post("/api/student/join")
    async def join(body: TeamBody) -> dict[str, str]:
        token = await act.join(body.team)
        log.info("組別 %s 加入", body.team)
        return {"team": body.team, "token": token}

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
