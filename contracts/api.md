# 介面契約：課堂搶答系統（凍結件）

> 首建：卡 `app-skeleton`（2026-11-11）。之後各卡只**增加**端點與欄位，不改既有欄位語意；改語意須經規格變更與負責人批准（`CLAUDE.md`「契約即法律」）。
> 兩組（OpenSpec、SpecKit）實作同一份契約。

## 身分

| 身分 | 憑據 | REST | WebSocket |
|---|---|---|---|
| 老師 | 伺服器啟動時產生的老師金鑰 | 標頭 `X-Teacher-Key` | 查詢參數 `role=teacher&key=<金鑰>` |
| 學生 | `POST /api/student/join` 取得的組別憑證（一組一台裝置） | 標頭 `X-Team-Token` | 查詢參數 `role=student&token=<憑證>` |

伺服器一律由憑證反查組別，不採信客戶端自報的組別名稱。

## 列舉

`phase`：`preparing`（準備中）｜`answering`（搶答中）｜`judging`（判定中，經典模式不使用）｜`ended`（已結束）

## REST 端點

錯誤回應一律為 `{"detail": "<繁體中文訊息>"}`，訊息不含任何學生答案。

| 方法與路徑 | 身分 | 本體 | 成功回應 | 錯誤 |
|---|---|---|---|---|
| `GET /api/public/info` | 任何人 | — | `{phase, teams: [組名], joined: [已加入組名]}` | — |
| `POST /api/student/join` | 任何人 | `{team}` | `{team, token}` | 404 組別不存在；409 該組已有裝置 |
| `GET /api/teacher/state` | 老師 | — | 老師 view（同 WebSocket） | 401 |
| `POST /api/teacher/teams` | 老師 | `{count}`（2–12） | `{teams}`；撤銷所有組別憑證 | 401；409 非 preparing；422 超出範圍 |
| `POST /api/teacher/release` | 老師 | `{team}` | `{released}`；撤銷該組憑證 | 401；404 |
| `POST /api/teacher/start` | 老師 | — | `{phase}` | 401；409 階段不符 |
| `POST /api/teacher/end` | 老師 | — | `{phase}` | 401；409 階段不符 |
| `POST /api/teacher/reset` | 老師 | — | `{phase}`；清空作答 | 401；409 階段不符 |

## WebSocket `/ws`

- 老師金鑰錯誤 ⇒ 以代碼 `4401` 關閉；`role` 不是 `teacher`／`student` ⇒ `1008` 關閉。
- 連線後立即收到一則完整 view；之後**只在本連線自己的 view 內容改變時**才收到新訊息。
- 訊息：`{"type": "state", "seq": <本連線自己的遞增序號，從 1 起>, "view": <view>}`。不含全域版本號。
- 客戶端送來的文字一律忽略（僅供保持連線）。

### 老師 view

```json
{"role": "teacher", "phase": "preparing", "teams": ["第1組", "第2組"], "joined": ["第1組"]}
```

### 學生 view

```json
{"role": "student", "phase": "preparing", "team": "第1組", "team_valid": true}
```

憑證缺、錯或已撤銷：

```json
{"role": "student", "phase": "preparing", "team": null, "team_valid": false}
```
