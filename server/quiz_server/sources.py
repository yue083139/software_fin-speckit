"""Guided Notes 來源：上傳檔驗證與 Google 試算表連結解析。

出處：guided-notes-import D5、guided-notes-sheets-sync D4。

未登入的公開連結下載（Google 匯出網址）已移除：課程補充說明要求直接以 Sheets API 讀寫雲端試算表。
"""
import re
from urllib.parse import parse_qs, urlsplit

MAX_BYTES = 5 * 1024 * 1024
XLSX_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
SHEET_PATH = re.compile(r"^/spreadsheets/d/([A-Za-z0-9_-]{20,})(?:/|$)")


class SourceError(ValueError):
    """來源不可用；API 層轉成 400。"""


def check_upload(filename: str | None, data: bytes) -> None:
    if not filename or not filename.lower().endswith(".xlsx"):
        raise SourceError("只接受 .xlsx 檔（Google 試算表請登入後用「從 Google 試算表匯入」）")
    if len(data) > MAX_BYTES:
        raise SourceError("檔案超過 5 MB")


def parse_sheet_url(url: str) -> tuple[str, str | None]:
    """回傳 (試算表 id, gid 或 None)；不合規即拒絕，不發出任何請求。"""
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
    return m.group(1), gid
