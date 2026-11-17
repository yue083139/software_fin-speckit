"""直接讀寫雲端 Google 試算表（guided-notes-sheets-sync D2、D3）。

匯入時先以 Drive 複製一份「<原標題>-搶答結果」，解析與寫回都對這份副本；原試算表只在匯入時讀標題、複製各一次。
所有 httpx 例外在本模組攔下轉成 GoogleApiError（訊息不含網址），以免權杖或網址進 traceback。
"""
from urllib.parse import quote

import httpx

from .google_auth import GoogleApiError, GoogleSession, google_error
from .guided_notes import GuidedNotesError, ParsedNotes, Range, fill

SHEETS = "https://sheets.googleapis.com/v4/spreadsheets"
DRIVE = "https://www.googleapis.com/drive/v3/files"
GRID_FIELDS = ("sheets(properties(title,sheetId),merges,"
               "data.rowData.values(formattedValue,effectiveValue))")
COPY_SUFFIX = "-搶答結果"


class SheetNotFoundError(ValueError):
    """連結指定的分頁不存在；API 層轉 400。"""


def sheet_url(sheet_id: str) -> str:
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"


def _value(cell: dict) -> object:
    ev = cell.get("effectiveValue") or {}
    if "numberValue" in ev:
        n = ev["numberValue"]
        return int(n) if isinstance(n, float) and n.is_integer() else n
    if "stringValue" in ev:
        return ev["stringValue"]
    if "boolValue" in ev:
        return ev["boolValue"]
    return cell.get("formattedValue")


class SheetsGrid:
    """Sheets API 一個分頁的格狀資料 → guided_notes.Grid（D2：effectiveValue 優先，與 xlsx 型別一致）。"""

    def __init__(self, sheet: dict) -> None:
        self.title: str = sheet["properties"]["title"]
        self._cells: dict[tuple[int, int], object] = {}
        data = sheet.get("data") or [{}]
        for r, row in enumerate(data[0].get("rowData") or [], 1):
            for c, cell in enumerate(row.get("values") or [], 1):
                value = _value(cell)
                if value is not None and value != "":
                    self._cells[(r, c)] = value
        self.merges = [Range(m.get("startRowIndex", 0) + 1, m.get("startColumnIndex", 0) + 1,
                             m["endRowIndex"], m["endColumnIndex"]) for m in sheet.get("merges") or []]
        rows = [r for r, _ in self._cells] + [m.max_row for m in self.merges]
        cols = [c for _, c in self._cells] + [m.max_col for m in self.merges]
        self.max_row = max(rows, default=0)
        self.max_column = max(cols, default=0)

    def cell(self, row: int, col: int) -> object:
        return self._cells.get((row, col))


async def _call(client: httpx.AsyncClient, method: str, url: str, **kw) -> httpx.Response:
    try:
        resp = await client.request(method, url, **kw)
    except httpx.HTTPError:
        raise GoogleApiError("Google 服務錯誤") from None
    if resp.status_code >= 400:
        raise google_error(resp)
    return resp


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def import_copy(session: GoogleSession, sheet_id: str, gid: str | None,
                      parse) -> tuple[str, str, list[SheetsGrid], ParsedNotes]:
    """標題 → 複製 → 讀副本 → 解析；解析失敗盡力刪副本後拋原錯誤。

    回傳 (原標題, 副本 id, 格狀資料, 解析結果)。
    """
    token = await session.token()
    async with session.client() as c:
        meta = await _call(c, "GET", f"{SHEETS}/{sheet_id}", headers=_auth(token),
                           params={"fields": "properties.title,sheets.properties.sheetId"})
        body = meta.json()
        title = body["properties"]["title"]
        sheet_ids = [s["properties"]["sheetId"] for s in body.get("sheets", [])]
        if gid is not None and int(gid) not in sheet_ids:
            raise SheetNotFoundError("找不到連結指定的分頁")
        copied = await _call(c, "POST", f"{DRIVE}/{sheet_id}/copy", headers=_auth(token),
                             params={"fields": "id"}, json={"name": f"{title}{COPY_SUFFIX}"})
        copy_id = copied.json()["id"]
        try:
            grid = await _call(c, "GET", f"{SHEETS}/{copy_id}", headers=_auth(token),
                               params={"includeGridData": "true", "fields": GRID_FIELDS})
            # files.copy 保留分頁 sheetId，連結的 gid 在副本中同樣有效
            sheets = [s for s in grid.json().get("sheets", [])
                      if gid is None or s["properties"]["sheetId"] == int(gid)]
            grids = [SheetsGrid(s) for s in sheets]
            notes = parse(grids)
        except (GuidedNotesError, GoogleApiError):
            try:
                await c.request("DELETE", f"{DRIVE}/{copy_id}", headers=_auth(token))
            except httpx.HTTPError:
                pass
            raise
    return title, copy_id, grids, notes


def _a1(sheet: str, cell: str) -> str:
    return "'" + sheet.replace("'", "''") + "'!" + cell


async def write_answers(session: GoogleSession, copy_id: str, notes: ParsedNotes,
                        answers: dict[int, tuple[str, ...]]) -> str:
    """只寫副本；RAW 讓「=」開頭的答案存成文字（D3）。回傳副本網址。"""
    data = []
    for q in notes.questions:
        values = answers.get(q.number)
        if values is None:
            continue
        for slot, answer in zip(q.slots, values, strict=True):
            data.append({"range": _a1(slot.sheet, slot.cell), "values": [[fill(slot, answer)]]})
    token = await session.token()
    if data:
        async with session.client() as c:
            await _call(c, "POST", f"{SHEETS}/{quote(copy_id)}/values:batchUpdate", headers=_auth(token),
                        json={"valueInputOption": "RAW", "data": data})
    return sheet_url(copy_id)
