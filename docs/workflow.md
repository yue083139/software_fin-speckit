# 開發工作流：有紀律的 vibe coding（SpecKit 組）

> 移植自 hybrid_agent 專案的工作流（2026-11-11）。判據以根目錄 [`CLAUDE.md`](../CLAUDE.md) 為準，本文是導讀；新成員先讀本文與 [`docs/requirements.md`](requirements.md)。

## 1. 一句話

**用自然語言和 AI 一起寫程式（vibe coding），但每一步都有「寫死的規格、會擋人的門禁、看不到彼此結論的評審」把關。**

需求 P-01 要求以 AI 代理開發、不自己寫程式碼；P-05 要求檢查 AI 產出並人工驗證。所以我們讓 AI 負責大部分的寫，讓**機械可驗證的東西**負責判對錯，讓**人**負責決定與最後驗收。

## 2. 角色分工

| 誰 | 做什麼 | 不做什麼 |
|---|---|---|
| **負責人（人）** | 定需求取捨、裁「未決事項」、批准契約、按合併、親手 `git push`、人工驗證 | 不逐行寫程式 |
| **組員（人）** | 各自一卡一會話推進、與 OpenSpec 組對齊 `docs/parity.md`、人工驗證、錄 Demo | 不直接推 `main`／`dev` |
| **主會話 AI（Claude Code／Codex）** | 寫提案、跑探針、寫測試與實作、派評審、改稿、開 PR、報「都綠否」 | 不推送、不合併、不替負責人裁定 |
| **評審子代理** | 唯讀找洞：紅隊找作答洩漏與判定不公，架構找決策互斥與 parity 漏登記 | 不改檔、不知道其他評審結論、不知道第幾輪 |
| **門禁（程式）** | `make gate-pr`、CI：lint、測試、繁體、金鑰形狀、憲章、圖表（PNG 配對＋語法）、Codex 規範同步 | 不會被說服 |

## 3. 一張卡從想法到合入

```
想法 ──► ① 定檔（S／B／C），對照 docs/parity.md §4 取卡名，登記 parity
          │
          ▼
        ② 探針：依賴 openpyxl、Google Sheets、WebSocket 行為的決策先跑 probes/
          │
          ▼
        ③ /speckit-specify：spec.md ＋ diagrams/ 三種 PlantUML 圖 ──► make diagrams 轉 PNG
          │
          ▼
        ④ /speckit-clarify ──► /speckit-plan（以圖為藍圖，Summary 首屏決策摘要，research 證偽欄）
           ──► /speckit-tasks ──► /speckit-analyze（跨文件一致性）
          │
          ▼
        ⑤ 提案輪評審（review-dispatch 骨架派單）──► 返修 ──► 負責人裁未決
          │
          ▼
        ⑥ /speckit-implement：先寫失敗的驗收測試，再寫實作（TDD）
          │
          ▼
        ⑦ 圖碼一致核對表 ＋ 人工驗證 寫進 specs/NNN-<卡名>/verification.md
          │
          ▼
        ⑧ 實作輪評審（對抗通道，只看 diff）──► 報「都綠否」──► 負責人合併
```

### 檔位速查

| 檔 | 什麼樣的改動 | 評審 |
|---|---|---|
| **S** | 搶答判定與順位、作答隔離、階段狀態機與同步、Guided Notes 解析與寫回、`contracts/` | 紅隊＋架構雙通道，提案 1 輪＋實作 1 輪 |
| **B** | 其他使用者看得到的行為：介面流程、CSV 匯出 | 提案架構 1 輪＋實作對抗 1 輪 |
| **C** | 文件、測試、門禁腳本、重構 | 實作對抗 1 輪 |

拿不準就取高一檔。**輪次上限是硬的**。

## 4. 本專案最容易出錯的三件事（評審重點）

1. **作答洩漏**：WebSocket 一廣播就是整份狀態、REST 回應帶了全部組別。驗收要斷言**傳輸內容**，不是畫面。
2. **「最快」不唯一**：兩組同一毫秒送出時要恰一組成功；不能用客戶端時間。
3. **寫死座標**：用官方範本測都綠、換助教的檔就錯位。至少三份版面不同的夾具。

## 5. 兩組協作（parity）

- 每張改行為的卡開卡前，在兩個 repo 的 `docs/parity.md` 同批登記（各開一個 PR，互相連結）。
- 一邊規格先定稿，另一邊照同一行為寫自己工具格式的規格——不互抄檔案，評分各看自己工具的產物。
- 合併前在本機跑 `make gate-parity`（預設比對 `../software_fin-openspec`）。

## 6. 推送與合併

| 防線 | 擋什麼 | 擋不住什麼 |
|---|---|---|
| pre-push 鉤子（`make hooks`） | 推 `main`／`dev` | 沒跑 `make hooks` 的 clone、`--no-verify` |
| `.claude/settings.json` deny、`.codex/rules/` | AI 直接寫出的 `git push` | 換寫法包裝 |
| GitHub PR | 約定的唯一合入路徑（評分加分項：branch／PR 協作） | 私人 repo 免費方案無分支保護；改公開後可加 |

日常：**`/speckit-specify` 會建立 `NNN-<卡名>` 分支 → AI 提交 → 你用 `!git push -u origin <分支>` 推 → AI 開 PR、看 CI、報都綠否 → 你按合併**。

## 7. 日常怎麼跟 AI 說話

| 情境 | 建議說法 |
|---|---|
| 新功能 | 「`/speckit-specify` 卡 `guided-notes-import`（檔位 S）：〈需求 R-02、X-01 的行為描述〉，依憲章原則 VII 產出三種圖」 |
| 規格有模糊處 | 「`/speckit-clarify`」 |
| 規劃 | 「`/speckit-plan` 以 diagrams/ 為藍圖，技術選型照 docs/parity.md §2」 |
| 開始實作 | 「`/speckit-implement`，先寫失敗的測試；完成後做圖碼一致核對」 |
| 送審 | 「派評審」 |
| 合併前 | 「報都綠否」 |
| AI 說了不確定的事實 | 「附原樣輸出」 |
| 卡結束 | `/export` 存到 `docs/ai-logs/`，然後 `/clear` |

**一卡一會話**；AI 用量先用中階模型（需求 P-01），評審與卡關再升級。
