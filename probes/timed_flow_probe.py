"""真棧探針：時間計分一個完整回合（mode-timed-scoring D8）。

對已啟動的本機伺服器：選時間計分、第 3 題時限 5 秒、開始、逐題推進到第 3 題、兩組送出、
**不手動關閉**、等伺服器計時器自動關閉並推播、判定、揭曉、讀名次。驗的是 TestClient 測不到的真事件迴圈計時器。

用法：
  QUIZ_TEACHER_KEY=<金鑰> uv run --project server python -m quiz_server --port 8765   （另一個終端機）
  uv run --project server python probes/timed_flow_probe.py http://127.0.0.1:8765 <金鑰> <group.xlsx>

只連本機；斷言失敗即非零退出。
"""
import asyncio
import json
import sys
import time

import httpx
import websockets

MARK = "甲組祕密答案"


async def submit(c: httpx.AsyncClient, token: str, answers: list[str]) -> httpx.Response:
    return await c.post("/api/student/submit", headers={"X-Team-Token": token},
                        json={"question": 3, "answers": answers})


async def main(base: str, key: str, xlsx: str) -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ws_base = base.replace("http", "ws")
    th = {"X-Teacher-Key": key}
    async with httpx.AsyncClient(base_url=base, timeout=10) as c:
        with open(xlsx, "rb") as f:
            r = await c.post("/api/teacher/import", headers=th, files={"file": ("group.xlsx", f.read())})
        print("匯入", r.status_code)
        print("模式", (await c.post("/api/teacher/mode", headers=th, json={"mode": "timed"})).json())
        r = await c.post("/api/teacher/question-settings", headers=th, json={"question": 3, "time_limit": 5})
        print("第3題時限", r.json())
        t1 = (await c.post("/api/student/join", json={"team": "第1組"})).json()["token"]
        t2 = (await c.post("/api/student/join", json={"team": "第2組"})).json()["token"]
        print("開始", (await c.post("/api/teacher/start", headers=th)).json())
        for _ in range(2):  # 第 1、2 題直接關閉並揭曉
            await c.post("/api/teacher/open-next", headers=th)
            await c.post("/api/teacher/close-question", headers=th)
            await c.post("/api/teacher/reveal-question", headers=th)
        async with websockets.connect(f"{ws_base}/ws?role=student&token={t2}") as w2:
            json.loads(await w2.recv())
            opened = time.monotonic()
            print("開放", (await c.post("/api/teacher/open-next", headers=th)).json())
            view = json.loads(await w2.recv())["view"]
            print("第2組收到回合", view["round"]["question"], view["round"]["state"])
            await asyncio.sleep(1.0)
            r = await submit(c, t1, [MARK])
            print("第1組送出", r.status_code)
            try:
                extra = await asyncio.wait_for(w2.recv(), timeout=0.5)
                print("第2組在他組送出後收到訊息（不應發生）", MARK in extra)
                raise SystemExit(1)
            except TimeoutError:
                print("第2組在他組送出後 0.5 秒內收到 0 則訊息")
            r = await submit(c, t2, ["地址"])
            print("第2組送出", r.status_code)
            while True:  # 不手動關閉：等伺服器計時器
                view = json.loads(await asyncio.wait_for(w2.recv(), timeout=10))["view"]
                if view["round"] and view["round"]["state"] == "closed":
                    break
            waited = time.monotonic() - opened
            print(f"伺服器自動關閉並推播：開題後 {waited:.2f} 秒（時限 5 秒）")
            assert 4.9 <= waited <= 6.5, waited
            r = await submit(c, t2, ["太晚"])
            print("關閉後送出", r.status_code, r.json()["detail"])
            for team, ok in (("第1組", True), ("第2組", False)):
                body = {"question": 3, "team": team, "correct": ok}
                await c.post("/api/teacher/judge", headers=th, json=body)
            print("揭曉", (await c.post("/api/teacher/reveal-question", headers=th)).json())
            while "revealed" not in view or not view["revealed"] or view["revealed"][-1]["question"] != 3:
                view = json.loads(await asyncio.wait_for(w2.recv(), timeout=5))["view"]
            raw = json.dumps(view, ensure_ascii=False)
            print("第2組本組結果", view["revealed"][-1], "累積", view["my_total"])
            print("第2組看到名次", view["leaderboard"][:2])
            has_scores = any("score" in r for r in view["leaderboard"])
            print("第2組 payload 含第1組答案", MARK in raw, "；名次含分數", has_scores)
            assert MARK not in raw and not has_scores
        teacher = (await c.get("/api/teacher/state", headers=th)).json()
        q3 = next(b for b in teacher["board"] if b["number"] == 3)
        print("老師看到第3題", [(r["team"], r["correct"], r["score"]) for r in q3["ranking"]])
        print("老師名次", teacher["leaderboard"][:2])


if __name__ == "__main__":
    asyncio.run(main(*sys.argv[1:4]))
