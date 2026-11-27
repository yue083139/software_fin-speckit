"""010 team-limit-50：300 條真 WebSocket 連線的狀態更新觀測探針。"""

import asyncio
import math
import platform
import time
from contextlib import suppress
from urllib.parse import quote

import uvicorn
import websockets
from quiz_server.activity import Activity, team_names
from quiz_server.app import create_app

HOST = "127.0.0.1"
PORT = 18770
TEACHER_KEY = "probe-teacher-key-" + "0" * 16


async def main() -> None:
    activity = Activity()
    # 直接建立 50 組以隔離量測廣播容量；join、token 反查、view 裁切、changed 通知與
    # 真 WebSocket 路徑皆走產品碼，組數範圍另由 API 與 Activity 邊界測試驗證。
    activity.teams = team_names(50)
    await activity.set_team_play(True)

    tokens: list[str] = []
    for team in activity.teams:
        tokens.append(await activity.join(team))
        code = activity.invite_code(team)
        tokens.extend([await activity.join(team, code) for _ in range(5)])

    server = uvicorn.Server(
        uvicorn.Config(
            create_app(activity=activity, teacher_key=TEACHER_KEY, static_dir=None),
            host=HOST,
            port=PORT,
            log_level="warning",
            access_log=False,
        )
    )
    server_task = asyncio.create_task(server.serve())
    while not server.started:
        await asyncio.sleep(0.01)

    sockets = []
    try:
        for token in tokens:
            socket = await websockets.connect(f"ws://{HOST}:{PORT}/ws?role=student&token={quote(token)}")
            await socket.recv()
            sockets.append(socket)

        started = time.perf_counter()
        await activity.set_team_play(False)

        async def receive(socket) -> tuple[float, bool]:
            payload = await asyncio.wait_for(socket.recv(), timeout=30)
            elapsed_ms = (time.perf_counter() - started) * 1000
            return elapsed_ms, '"team_valid":false' in payload and '"team":null' in payload

        observed = await asyncio.gather(*(receive(socket) for socket in sockets))
        latencies = sorted(item[0] for item in observed)
        p95 = latencies[math.ceil(len(latencies) * 0.95) - 1]
        consistent = all(item[1] for item in observed)

        print(f"環境：{platform.platform()}；Python {platform.python_version()}")
        print(f"連線：{len(sockets)}（50 組 × 6 台）")
        print(f"95% 收到更新：{p95:.1f} ms")
        print(f"最慢收到更新：{latencies[-1]:.1f} ms")
        consistent_count = sum(item[1] for item in observed)
        print(
            f"最終狀態一致：{'是' if consistent else '否'}"
            f"（{consistent_count}/{len(observed)}）"
        )
    finally:
        await asyncio.gather(*(socket.close() for socket in sockets), return_exceptions=True)
        server.should_exit = True
        with suppress(asyncio.CancelledError):
            await server_task


if __name__ == "__main__":
    asyncio.run(main())
