# Verification: 014 student-qr（v1.1）

## 評審紀錄

S 檔壓縮版一輪（提案輪架構全卡掃＋實作輪對抗 diff，雙通道，與 OpenSpec 組同批）：架構 **CLEARED（0B/3M/1m）**、對抗 **CLEARED（0B/0M/1m）**。藥方落點同 OpenSpec 組 `openspec/changes/student-qr/verification.md`（程式逐字相同）；前端 4403 提示與學生連結 QR 已於 rebase 到 `web-workbench` 後落地（research R2、R5）。

## 真實 WebSocket 用戶端（4403 關閉碼）

```
帶 cf-connecting-ip 的老師 WS 關閉碼： 4403
本機老師 WS 第一則： {"type":"state","seq":1,"view"
```

## followup（不阻塞）

- 老師金鑰錯誤（4401）仍在交握前關閉，瀏覽器實際收到 1006 而非 4401，「老師金鑰錯誤」提示顯示不出來（現行行為，本卡不改）。實測：`websockets.connect(".../ws?role=teacher&key=wrong")` → 「錯誤金鑰老師 WS：交握被拒 HTTP 403」。主人：@yue083139。

- 以 `--host 0.0.0.0` 啟動時，同區網的人偽造 `Host: 127.0.0.1` 且不帶 Cloudflare 標頭會被判為本機——仍須老師金鑰，與改版前同強度；預設只綁 127.0.0.1，不另處理。主人：@yue083139。

## 圖表與程式一致性（原則 VII）

| 圖 | 元素 | 程式 |
|---|---|---|
| component | `tunnel.Tunnel`、`app.is_local`、老師端點與學生端點分流、`views.teacher_view.student_url`、`Activity.public_url` | `server/quiz_server/{tunnel,app,views,activity}.py` 同名 |
| class | `Tunnel.start/stop`、`find_cloudflared`、`parse_url`、`wait_for_url`、`LOCAL_HOSTNAMES`、`TUNNEL_HEADERS`、`WS_NOT_LOCAL`、`NOT_LOCAL`、`CALLBACK_NOT_LOCAL` | 同名存在（`git grep -n` 逐一核對） |
| sequence | 啟動取網址、本機看 student_url、手機經通道 join、公開網址開老師頁 403 先於金鑰 | `__main__.main`；`test_api_host.py` 四類情境 |

兩組程式碼逐字相同；變異實錄與真棧在 OpenSpec 組跑（`openspec/changes/student-qr/verification.md`）。

## 變異實錄

```
變異1 拿掉 Cloudflare 標頭檢查（is_local 只看 Host）：test_api_host.py → 1 failed, 10 passed
變異2 is_local 一律回 True：test_api_host.py → 5 failed, 6 passed
```

## 真棧

見 `probes/results/2026-11-26-student-qr-real-stack.txt`。

## 門禁實錄

`make gate`（2026-11-26，014-student-qr）：

```
ruff：All checks passed!（server、ops probes）
server pytest：294 passed, 1 warning
ops pytest：58 passed
web vitest：Test Files 8 passed (8)；Tests 41 passed (41)
gate-zh-hant: 0 處簡體字
gate-secrets: 0 findings
gate-speckit: 憲章 v1.0.0，0 處問題
gate-diagrams: 37 個圖檔，0 處問題
gate-agents: 0 處漂移
gate-diagrams-syntax: 37 個圖檔語法通過
make gate-parity SIBLING=../wt-os-qr → gate-parity: 0 處不一致
```

`make gate` 內建的 `gate-parity`（SIBLING 預設 `../software_fin-openspec`，該工作樹未在本分支）報 2 處不一致（`docs/parity.md`、`contracts/api.md`），對 OpenSpec 組同批分支 `wt-os-qr` 為 0。

## 人工驗證（需求 P-05）

狀態：**待執行**（負責人，`docs/manual-verification.md` 場次 F）。
