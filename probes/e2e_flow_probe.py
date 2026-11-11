"""真棧探針：對已啟動的本機伺服器跑完整活動流程（匯入→加入→開始→作答→結束→匯出）。

用法：
  QUIZ_TEACHER_KEY=<金鑰> uv run --project server python -m quiz_server --port 8765   （另一個終端機）
  uv run --project server python probes/e2e_flow_probe.py http://127.0.0.1:8765 <金鑰> <xlsx>

只連本機；輸出每一步的狀態碼與關鍵欄位，供 verification.md 原樣引用。
"""
import asyncio
import io
import json
import sys

import httpx
import openpyxl
import websockets


async def main(base: str, key: str, xlsx: str) -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ws_base = base.replace("http", "ws")
    th = {"X-Teacher-Key": key}
    async with httpx.AsyncClient(base_url=base, timeout=10) as c:
        print("首頁", (await c.get("/")).status_code)
        with open(xlsx, "rb") as f:
            r = await c.post("/api/teacher/import", headers=th, files={"file": ("group.xlsx", f.read())})
        print("匯入", r.status_code, r.json())
        t1 = (await c.post("/api/student/join", json={"team": "第1組"})).json()["token"]
        t2 = (await c.post("/api/student/join", json={"team": "第2組"})).json()["token"]
        print("重複加入第1組", (await c.post("/api/student/join", json={"team": "第1組"})).status_code)
        async with websockets.connect(f"{ws_base}/ws?role=student&token={t2}") as w2, \
                websockets.connect(f"{ws_base}/ws?role=teacher&key={key}") as wt:
            print("第2組初始", json.loads(await w2.recv())["view"]["phase"])
            await wt.recv()
            print("開始", (await c.post("/api/teacher/start", headers=th)).status_code)
            print("第2組收到", json.loads(await w2.recv())["view"]["phase"])
            r = await c.post("/api/student/submit", headers={"X-Team-Token": t1},
                             json={"question": 3, "answers": ["甲組祕密答案"]})
            print("第1組送出第3題", r.status_code, r.json())
            try:
                extra = await asyncio.wait_for(w2.recv(), timeout=1.0)
                print("第2組在他組送出後收到訊息（不應發生）", "甲組祕密答案" in extra)
            except TimeoutError:
                print("第2組在他組送出後 1 秒內收到 0 則訊息")
            r = await c.post("/api/student/submit", headers={"X-Team-Token": t2},
                             json={"question": 1, "answers": ["CPU", "作業系統"]})
            print("第2組送出第1題（題組）", r.status_code)
            print("結束", (await c.post("/api/teacher/end", headers=th)).status_code)
            while True:
                view = json.loads(await w2.recv())["view"]
                if view["phase"] == "ended":
                    break
            winners = {q["number"]: q["winner"] for q in view["results"]}
            print("第2組看到結果", winners[1], winners[3], view["team_scores"])
        r = await c.get("/api/teacher/export", headers=th)
        print("匯出", r.status_code, r.headers.get("content-disposition"))
        ws = openpyxl.load_workbook(io.BytesIO(r.content)).worksheets[0]
        marks = ("CPU", "甲組", "作業系統")
        filled = sorted((c.coordinate, c.value) for row in ws.iter_rows() for c in row
                        if isinstance(c.value, str) and any(m in c.value for m in marks))
        print("匯出檔填入的格", filled)


if __name__ == "__main__":
    asyncio.run(main(*sys.argv[1:4]))
