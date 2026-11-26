"""HTTP 與 WebSocket 端點（app-skeleton D1、D4–D6）。介面契約見 contracts/api.md。"""
import asyncio
import logging
import os
import secrets
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
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
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import google_sheets, results
from .activity import Activity, AlreadySubmittedError, InviteCodeError, TeamTakenError
from .envfile import ENV_FILE, remove_keys, write_keys
from .google_auth import (
    COOKIE_NAME,
    STATE_TTL,
    GoogleApiError,
    GoogleAuthError,
    GoogleCallbackError,
    GoogleConfigError,
    GoogleConfigInvalid,
    GoogleSession,
    state_digest,
    validate_client,
)
from .guided_notes import GuidedNotesError, grids_to_xlsx, parse_grids, rename_sheets, write_answers
from .phases import Phase, PhaseError
from .sources import MAX_BYTES, SourceError, check_upload, parse_sheet_url
from .tunnel import Tunnel
from .views import view_for

log = logging.getLogger("quiz_server")
DEFAULT_STATIC = Path(__file__).resolve().parents[2] / "web" / "dist"
WS_UNAUTHORIZED = 4401
WS_NOT_LOCAL = 4403
# student-qr D2：老師身分只在本機。以 Host 主機名判斷，且不得帶 Cloudflare 邊緣加上的轉送標頭——
# 經通道的 Host 是公開網域、偽造 Host 會被邊緣 403；client.host 會被 uvicorn 依 X-Forwarded-For 改寫，不採用
#（探針 probes/results/2026-11-26-cloudflared.txt ②③④）
LOCAL_HOSTNAMES = frozenset({"127.0.0.1", "localhost", "[::1]"})
TUNNEL_HEADERS = ("cf-connecting-ip", "cf-ray")
NOT_LOCAL = "老師頁只能在本機開啟"
# easy-setup D2、D3
CONFIG_SIGNED_IN = "請先登出 Google 再變更設定"
TUNNEL_STARTING = "手機連線建立中"
TUNNEL_MISSING = "找不到 cloudflared，請先安裝：winget install --id Cloudflare.cloudflared -e"
TUNNEL_TIMEOUT = "建立手機連線逾時，請再試一次"
TUNNEL_IN_USE = "搶答進行中不能關閉手機連線"
TUNNEL_START_TIMEOUT = 30


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


class ReviewBody(BaseModel):
    question: int
    team: str
    correct: bool


class ReviewResetBody(BaseModel):
    question: int


class GoogleConfigBody(BaseModel):
    client_id: str
    client_secret: str


XLSX_MEDIA = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
COOKIE_PATH = "/api/google"
# 回呼頁只用固定文案，不回顯任何查詢參數（guided-notes-sheets-sync D1：避免反射型 XSS 偷老師金鑰）
CALLBACK_OK = ("<!doctype html><meta charset=utf-8><title>登入完成</title>"
               "<p>登入完成，可關閉此分頁，回到老師頁。</p>")
CALLBACK_NOT_LOCAL = ("<!doctype html><meta charset=utf-8><title>登入失敗</title>"
                      "<p>請在本機（127.0.0.1）開啟老師頁後重新登入。</p>")
CALLBACK_FAIL = ("<!doctype html><meta charset=utf-8><title>登入失敗</title>"
                 "<p>登入失敗，請回老師頁重新登入。</p>")


def export_filename(source: str | None) -> str:
    stem = (source or "guided-notes").rsplit(".", 1)[0]
    return f"{stem}_作答情況.xlsx"


def resolve_teacher_key(explicit: str | None = None) -> str:
    return explicit or os.environ.get("QUIZ_TEACHER_KEY") or secrets.token_urlsafe(16)


def create_app(activity: Activity | None = None, teacher_key: str | None = None,
               static_dir: Path | None = DEFAULT_STATIC,
               http_transport: httpx.AsyncBaseTransport | None = None,
               google: GoogleSession | None = None, student_url: str | None = None,
               tunnel: Tunnel | None = None, env_file: Path = ENV_FILE,
               tunnel_watch_interval: float = 2.0) -> FastAPI:
    act = activity or Activity()
    act.public_url = student_url
    act.tunnel_state = "on" if student_url else "off"
    # 手機連線（easy-setup D3）：鎖只包狀態轉換，不包約 4 秒的 tunnel.start
    tunnel_lock = asyncio.Lock()
    tunnel_flags = {"cancel": False}
    start_done = asyncio.Event()
    start_done.set()

    async def watch_tunnel() -> None:
        """子行程意外結束 ⇒ 轉 off（v1.1 藥方 6）；只記結果，不記網址。"""
        while True:
            await asyncio.sleep(tunnel_watch_interval)
            if tunnel is None or act.tunnel_state != "on" or tunnel.alive():
                continue
            async with tunnel_lock:
                if act.tunnel_state == "on" and not tunnel.alive():
                    await act.set_tunnel("off", None)
                    log.warning("手機連線的 cloudflared 已結束，改為只在本機")

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        watcher = asyncio.create_task(watch_tunnel())
        try:
            yield
        finally:
            watcher.cancel()
            if tunnel is not None:
                await asyncio.to_thread(tunnel.stop)

    app = FastAPI(title="課堂搶答系統", lifespan=lifespan)
    gs = google or GoogleSession(os.environ.get("GOOGLE_CLIENT_ID"), os.environ.get("GOOGLE_CLIENT_SECRET"),
                                 transport=http_transport)
    app.state.google = gs
    secret = resolve_teacher_key(teacher_key)
    app.state.activity = act

    def is_local(headers: Any) -> bool:
        host = headers.get("host", "").strip().lower()
        hostname = host.split("]")[0] + "]" if host.startswith("[") else host.rsplit(":", 1)[0]
        return hostname in LOCAL_HOSTNAMES and not any(h in headers for h in TUNNEL_HEADERS)

    def is_teacher(given: str | None) -> bool:
        return given is not None and secrets.compare_digest(given.encode(), secret.encode())

    def require_teacher(request: Request, x_teacher_key: Annotated[str | None, Header()] = None) -> None:
        if not is_local(request.headers):  # 先擋 Host，不讓公開網域探測金鑰對錯
            raise HTTPException(403, NOT_LOCAL)
        if not is_teacher(x_teacher_key):
            raise HTTPException(401, "需要老師金鑰")

    teacher = [Depends(require_teacher)]
    # 匯出與寫回序列化（answer-review D5 v1.1）：快照在鎖內取，兩次寫回不交錯，
    # 「上次寫過的題號」才與副本實際內容一致
    export_lock = asyncio.Lock()

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

    @app.exception_handler(GoogleConfigError)
    @app.exception_handler(google_sheets.SheetNotFoundError)
    async def _google_bad_request(_: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse({"detail": str(exc)}, status_code=400)

    @app.exception_handler(GoogleConfigInvalid)
    async def _google_config_invalid(_: Request, exc: GoogleConfigInvalid) -> JSONResponse:
        return JSONResponse({"detail": str(exc)}, status_code=422)

    @app.exception_handler(GoogleAuthError)
    async def _google_auth(_: Request, exc: GoogleAuthError) -> JSONResponse:
        return JSONResponse({"detail": str(exc)}, status_code=401)

    @app.exception_handler(GoogleApiError)
    async def _google_api(_: Request, exc: GoogleApiError) -> JSONResponse:
        return JSONResponse({"detail": str(exc)}, status_code=502)

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
        # 錯誤先後：409 階段 → 400 連結 → 401 Google 登入 → 502（D7）；登入檢查前不發對外請求
        act.require_preparing()
        sheet_id, gid = parse_sheet_url(body.url)
        title, copy_id, grids, notes = await google_sheets.import_copy(gs, sheet_id, gid, parse_grids)
        try:
            data, xlsx_sheets = grids_to_xlsx(grids)
            await act.load_questions(data, title, notes=notes, sheet_id=copy_id, xlsx_sheets=xlsx_sheets)
        except Exception:
            # 副本已建立但沒採用（例：等 Google 回應時老師已開始搶答 ⇒ 409）：刪掉，不留孤兒副本
            await google_sheets.delete_copy(gs, copy_id)
            raise
        log.info("匯入 Google 試算表副本：%d 題", len(act.questions))
        return {"source": act.source_name, "count": len(act.questions),
                "sheet_url": google_sheets.sheet_url(copy_id)}

    @app.post("/api/teacher/export-sheet", dependencies=teacher)
    async def export_sheet() -> dict[str, str]:
        async with export_lock:
            if act.phase is not Phase.ENDED:
                raise PhaseError("搶答結束後才能匯出")
            if act.notes is None:
                raise PhaseError("尚未匯入題目")
            if act.source_sheet_id is None:
                raise PhaseError("題目不是從 Google 試算表匯入，請改用下載 xlsx")
            sheet_id, notes, answers = act.source_sheet_id, act.notes, results.winning_answers(act)
            url = await google_sheets.write_answers(gs, sheet_id, notes, answers, restore=act.sheet_written)
            await act.mark_sheet_written(sheet_id, frozenset(answers))
        log.info("寫回 Google 試算表副本：活動 v%s", act.version)
        return {"url": url}

    @app.get("/api/teacher/google", dependencies=teacher)
    async def google_status() -> dict[str, Any]:
        return gs.status()

    @app.post("/api/teacher/google/login", dependencies=teacher)
    async def google_login() -> JSONResponse:
        url, state = gs.begin()
        resp = JSONResponse({"url": url})
        # cookie 綁定發起登入的瀏覽器：拿到授權網址的他人無法在自己的瀏覽器完成回呼（D1 v1.2）
        resp.set_cookie(COOKIE_NAME, state_digest(state), max_age=STATE_TTL, path=COOKIE_PATH,
                        httponly=True, samesite="lax")
        return resp

    @app.get("/api/google/callback")
    async def google_callback(request: Request) -> HTMLResponse:
        if not is_local(request.headers):
            return HTMLResponse(CALLBACK_NOT_LOCAL, status_code=403)
        q = request.query_params
        try:
            await gs.complete(q.get("state"), q.get("code"), request.cookies.get(COOKIE_NAME), q.get("error"))
        except (GoogleCallbackError, GoogleApiError):
            resp = HTMLResponse(CALLBACK_FAIL, status_code=400)
        else:
            log.info("老師已以 Google 帳號登入")
            resp = HTMLResponse(CALLBACK_OK)
        resp.delete_cookie(COOKIE_NAME, path=COOKIE_PATH)
        return resp

    # Google 設定精靈（easy-setup D2）：檢查已登入 → 寫 .env → 立即生效 → 設環境變數，整段在鎖內
    config_lock = asyncio.Lock()
    config_keys = ("GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET")

    @app.post("/api/teacher/google/config", dependencies=teacher)
    async def google_config(body: GoogleConfigBody) -> dict[str, Any]:
        validate_client(body.client_id, body.client_secret)  # 不 strip：寫入的就是驗證過的原值
        async with config_lock:
            if gs.signed_in:
                raise HTTPException(409, CONFIG_SIGNED_IN)
            values = dict(zip(config_keys, (body.client_id, body.client_secret), strict=True))
            await asyncio.to_thread(write_keys, values, env_file)
            gs.reconfigure(body.client_id, body.client_secret)
            os.environ.update(values)
        log.info("已更新 Google OAuth 用戶端設定")  # 不記 ID 與密鑰
        return gs.status()

    @app.delete("/api/teacher/google/config", dependencies=teacher)
    async def google_config_clear() -> dict[str, Any]:
        async with config_lock:
            if gs.signed_in:
                raise HTTPException(409, CONFIG_SIGNED_IN)
            await asyncio.to_thread(remove_keys, config_keys, env_file)
            gs.reconfigure(None, None)
            for k in config_keys:
                os.environ.pop(k, None)
        log.info("已清除 Google OAuth 用戶端設定")
        return gs.status()

    def tunnel_body() -> dict[str, Any]:
        return {"tunnel": act.tunnel_state, "student_url": act.public_url}

    @app.post("/api/teacher/tunnel", dependencies=teacher)
    async def tunnel_open() -> dict[str, Any]:
        async with tunnel_lock:
            if act.tunnel_state == "on":
                return tunnel_body()
            if act.tunnel_state == "starting":
                raise HTTPException(409, TUNNEL_STARTING)
            if tunnel is None or not tunnel.available():
                raise HTTPException(503, TUNNEL_MISSING)
            tunnel_flags["cancel"] = False
            start_done.clear()
            await act.set_tunnel("starting", None)
        url: str | None = None
        cancelled = False
        try:
            url = await asyncio.to_thread(tunnel.start, TUNNEL_START_TIMEOUT)
        finally:
            async with tunnel_lock:
                cancelled = tunnel_flags["cancel"]
                try:
                    if cancelled or url is None:
                        if url is not None:
                            await asyncio.to_thread(tunnel.stop)
                        await act.set_tunnel("off", None)
                    else:
                        await act.set_tunnel("on", url)
                finally:
                    start_done.set()
        if cancelled:
            return {"tunnel": "off", "student_url": None}
        if url is None:
            raise HTTPException(504, TUNNEL_TIMEOUT)
        log.info("手機連線已開啟")
        return tunnel_body()

    @app.delete("/api/teacher/tunnel", dependencies=teacher)
    async def tunnel_close() -> dict[str, Any]:
        if act.phase is not Phase.PREPARING:
            raise HTTPException(409, TUNNEL_IN_USE)  # 關掉會讓手機上的組別全部斷線（v1.1 藥方 3）
        wait = False
        async with tunnel_lock:
            if act.tunnel_state == "starting":
                tunnel_flags["cancel"] = True  # 建立完成後由開啟那端停掉子行程（v1.1 藥方 2）
                wait = True
            elif act.tunnel_state == "on":
                if tunnel is not None:
                    await asyncio.to_thread(tunnel.stop)
                await act.set_tunnel("off", None)
        if wait:
            await start_done.wait()
        log.info("手機連線已關閉")
        return tunnel_body()

    @app.post("/api/teacher/google/logout", dependencies=teacher)
    async def google_logout() -> dict[str, bool]:
        await gs.logout()
        return {"signed_in": False}

    @app.get("/api/teacher/export", dependencies=teacher)
    async def export() -> Response:
        async with export_lock:
            if act.phase is not Phase.ENDED:
                raise PhaseError("搶答結束後才能匯出")
            if act.notes is None or act.source_bytes is None:
                raise PhaseError("尚未匯入題目")
            notes = rename_sheets(act.notes, act.source_xlsx_sheets) if act.source_xlsx_sheets else act.notes
            data = write_answers(act.source_bytes, notes, results.winning_answers(act))
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

    @app.post("/api/teacher/review", dependencies=teacher)
    async def review(body: ReviewBody) -> dict[str, Any]:
        await act.review(body.question, body.team, body.correct)
        log.info("檢查：題 %s 組別 %s 結果 %s", body.question, body.team, body.correct)
        return {"question": body.question, "team": body.team, "correct": body.correct}

    @app.post("/api/teacher/review-reset", dependencies=teacher)
    async def review_reset(body: ReviewResetBody) -> dict[str, int]:
        await act.review_reset(body.question)
        log.info("重設檢查：題 %s", body.question)
        return {"question": body.question}

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
        if role == "teacher" and not is_local(socket.headers):
            # 先 accept 再關：交握前就關，瀏覽器只會收到 HTTP 403、關閉碼變 1006，前端無從分辨
            #（student-qr 實作偏離回稿）；accept 後不送任何 view 就關閉
            await socket.accept()
            await socket.close(code=WS_NOT_LOCAL)
            return
        if role == "teacher" and not is_teacher(key):
            # 同上：先 accept 再以 4401 關，前端才顯示得出「金鑰錯誤」（teacher-key-error）
            # 關閉前不送任何 view
            await socket.accept()
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
