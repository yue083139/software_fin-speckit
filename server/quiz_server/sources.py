"""Guided Notes 來源：上傳檔驗證與 Google Sheets 連結下載（guided-notes-import D5）。"""
import re
from urllib.parse import parse_qs, urljoin, urlsplit

import httpx

MAX_BYTES = 5 * 1024 * 1024
MAX_REDIRECTS = 5
TIMEOUT_SECONDS = 15
XLSX_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
SHEET_PATH = re.compile(r"^/spreadsheets/d/([A-Za-z0-9_-]{20,})(?:/|$)")
DOWNLOAD_HINT = "無法下載，請確認試算表共用設定為「知道連結者可檢視」，或改用上傳 xlsx"


class SourceError(ValueError):
    """來源不可用；API 層轉成 400。"""


def check_upload(filename: str | None, data: bytes) -> None:
    if not filename or not filename.lower().endswith(".xlsx"):
        raise SourceError("只接受 .xlsx 檔（Google 試算表請用「檔案 → 下載 → Microsoft Excel」）")
    if len(data) > MAX_BYTES:
        raise SourceError("檔案超過 5 MB")


def export_url(url: str) -> str:
    """把使用者貼的 Google Sheets 連結改寫成 xlsx 匯出網址；不合規即拒絕，不發出任何請求。"""
    parts = urlsplit(url.strip())
    if parts.scheme != "https" or parts.hostname != "docs.google.com" or parts.port not in (None, 443):
        raise SourceError("只接受 https://docs.google.com/spreadsheets/ 開頭的連結")
    m = SHEET_PATH.match(parts.path)
    if not m:
        raise SourceError("連結不是 Google 試算表（應為 /spreadsheets/d/<id>/…）")
    gid = None
    for source in (parts.query, parts.fragment):
        values = parse_qs(source).get("gid")
        if values and values[0].isdigit():
            gid = values[0]
    out = f"https://docs.google.com/spreadsheets/d/{m.group(1)}/export?format=xlsx"
    return f"{out}&gid={gid}" if gid else out


def _allowed_hop(url: str) -> bool:
    parts = urlsplit(url)
    host = parts.hostname or ""
    return (parts.scheme == "https" and parts.port in (None, 443)
            and (host == "docs.google.com" or host.endswith(".googleusercontent.com")))


async def download_sheet(url: str, transport: httpx.AsyncBaseTransport | None = None) -> bytes:
    """逐跳跟隨轉址，每一跳都限 Google 網域；串流讀取，超過上限即中止。"""
    target = export_url(url)
    async with httpx.AsyncClient(transport=transport, follow_redirects=False,
                                 timeout=TIMEOUT_SECONDS) as client:
        for _ in range(MAX_REDIRECTS + 1):
            if not _allowed_hop(target):
                raise SourceError("下載被轉址到非 Google 網域，已中止")
            try:
                async with client.stream("GET", target) as resp:
                    if resp.is_redirect:
                        target = urljoin(target, resp.headers.get("location", ""))
                        continue
                    ctype = resp.headers.get("content-type", "")
                    if resp.status_code != 200 or not ctype.startswith(XLSX_TYPE):
                        raise SourceError(DOWNLOAD_HINT)
                    chunks, size = [], 0
                    async for chunk in resp.aiter_bytes():
                        size += len(chunk)
                        if size > MAX_BYTES:
                            raise SourceError("檔案超過 5 MB")
                        chunks.append(chunk)
                    return b"".join(chunks)
            except httpx.HTTPError as exc:
                raise SourceError(DOWNLOAD_HINT) from exc
    raise SourceError("轉址次數過多，已中止")
