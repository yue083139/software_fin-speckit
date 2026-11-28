"""Google Sheets 讀寫（guided-notes-sheets-sync D2、D3）：格狀資料與 xlsx 解析等價、匯入時複製、只寫副本。"""
import asyncio
import json

import pytest
from google_fake import CLIENT_ID, CLIENT_SECRET, COPY_ID, ORIGINAL_ID, FakeGoogle, sheet_json

from quiz_server import google_sheets
from quiz_server.google_auth import GoogleApiError, GoogleSession
from quiz_server.google_sheets import SheetsGrid
from quiz_server.guided_notes import GuidedNotesError, parse_grids, parse_workbook

FIXTURES = ["single.xlsx", "group.xlsx", "variant.xlsx", "reference.xlsx"]


def _summary(notes):
    return [(q.number, [(s.sheet, s.cell, s.label, s.placeholder, s.display, s.reference) for s in q.slots])
            for q in notes.questions]


@pytest.mark.parametrize("name", FIXTURES)
def test_sheets_grid_parses_same_as_xlsx(fixture_bytes, name):
    data = fixture_bytes(name)
    from_api = parse_grids([SheetsGrid(s) for s in sheet_json(data)])
    assert _summary(from_api) == _summary(parse_workbook(data))


def test_number_column_uses_effective_value():
    """題號欄套了數字格式（顯示「1.00」）：effectiveValue 讀成 1，與 xlsx 型別一致（D2，紅隊 v1.2）。"""
    def cell(text, number=None):
        c = {"formattedValue": text}
        c["effectiveValue"] = {"numberValue": number} if number is not None else {"stringValue": text}
        return c
    sheet = {"properties": {"title": "表", "sheetId": 0}, "merges": [], "data": [{"rowData": [
        {"values": [cell("題號"), cell("作答")]},
        {"values": [cell("1.00", 1.0), {}]},
        {"values": [cell("2.00", 2.0), {}]},
    ]}]}
    notes = parse_grids([SheetsGrid(sheet)])
    assert [q.number for q in notes.questions] == [1, 2]


def _session(fake: FakeGoogle) -> GoogleSession:
    s = GoogleSession(CLIENT_ID, CLIENT_SECRET, transport=fake.transport())
    s._store({"access_token": "ya29." + "0" * 40, "expires_in": 3599})
    return s


def test_import_copies_first_then_reads_the_copy(fixture_bytes):
    fake = FakeGoogle(fixture_bytes("group.xlsx"))
    title, copy_id, grids, notes = asyncio.run(
        google_sheets.import_copy(_session(fake), ORIGINAL_ID, None, parse_grids))
    assert (title, copy_id) == ("題組＋單題範本", COPY_ID)
    steps = [(r.method, r.url.host, r.url.path.rsplit("/", 1)[-1], r.url.params.get("includeGridData"))
             for r in fake.calls]
    assert steps == [
        ("GET", "sheets.googleapis.com", ORIGINAL_ID, None),           # 原檔標題
        ("POST", "www.googleapis.com", "copy", None),                  # 複製
        ("GET", "sheets.googleapis.com", COPY_ID, "true"),             # 讀副本
    ]
    assert json.loads(fake.calls[1].content) == {"name": "題組＋單題範本_作答情況"}
    assert [len(q.slots) for q in notes.questions] == [2, 2, 1, 1]


def test_parse_failure_deletes_copy(fixture_bytes):
    fake = FakeGoogle(fixture_bytes("group.xlsx"))
    fake.sheets[0]["data"][0]["rowData"] = [{"values": [{"formattedValue": "無表頭"}]}]
    with pytest.raises(GuidedNotesError):
        asyncio.run(google_sheets.import_copy(_session(fake), ORIGINAL_ID, None, parse_grids))
    assert fake.deleted == [COPY_ID]


def test_gid_not_found_is_rejected_before_copy(fixture_bytes):
    fake = FakeGoogle(fixture_bytes("group.xlsx"))
    with pytest.raises(google_sheets.SheetNotFoundError):
        asyncio.run(google_sheets.import_copy(_session(fake), ORIGINAL_ID, "999", parse_grids))
    assert not any(r.url.path.endswith("/copy") for r in fake.calls)


def test_google_error_is_sanitized(fixture_bytes):
    fake = FakeGoogle(fixture_bytes("group.xlsx"))
    fake.fail["copy"] = 403
    with pytest.raises(GoogleApiError) as e:
        asyncio.run(google_sheets.import_copy(_session(fake), ORIGINAL_ID, None, parse_grids))
    assert str(e.value) == "Google 服務錯誤：PERMISSION_DENIED"
    assert "http" not in str(e.value) and "ya29" not in str(e.value)


def test_write_targets_only_the_copy_with_raw(fixture_bytes):
    fake = FakeGoogle(fixture_bytes("group.xlsx"))
    session = _session(fake)
    _, copy_id, _, notes = asyncio.run(google_sheets.import_copy(session, ORIGINAL_ID, None, parse_grids))
    before = len(fake.requests_to(ORIGINAL_ID))
    answers = {1: ("CPU", "=1+1"), 3: ("位址",)}
    url = asyncio.run(google_sheets.write_answers(session, copy_id, notes, answers))
    assert url == f"https://docs.google.com/spreadsheets/d/{COPY_ID}/edit"
    assert len(fake.requests_to(ORIGINAL_ID)) == before  # 匯入後原檔 0 次請求
    assert fake.writes == [{"valueInputOption": "RAW", "data": [
        {"range": "'學習單'!H5", "values": [["CPU"]]},
        {"range": "'學習單'!H6", "values": [["=1+1"]]},
        {"range": "'學習單'!G11", "values": [["位址"]]},
    ]}]


def test_sheet_name_quote_is_escaped(fixture_bytes):
    fake = FakeGoogle(fixture_bytes("single.xlsx"))
    fake.sheets[0]["properties"]["title"] = "O'Brien"
    session = _session(fake)
    _, copy_id, _, notes = asyncio.run(google_sheets.import_copy(session, ORIGINAL_ID, None, parse_grids))
    asyncio.run(google_sheets.write_answers(session, copy_id, notes, {1: ("甲",)}))
    assert fake.writes[0]["data"][0]["range"] == "'O''Brien'!G5"
