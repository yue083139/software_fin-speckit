# Quickstart Validation: 010 team-limit-50

本指南只描述可執行的驗證流程；實作任務由後續 `tasks.md` 定義。所有資料使用合成組名、假憑證與測試答案。

## 前置

```bash
make web-install
make diagrams
```

確認位於 `010-team-limit-50` 分支，且 `specs/010-team-limit-50/contracts/api-change.md` 的契約變更已獲負責人批准後才進入實作驗證。

## 1. 邊界與生命週期

```bash
uv run --project server pytest -q server/tests/test_phases.py server/tests/test_api_skeleton.py
```

預期：2、12、13、50 成功；1、51 與格式錯誤回 422；非準備階段回 409；所有失敗操作不改狀態；合法改組數撤銷舊 token、邀請碼與草稿。

## 2. 300 台容量與狀態更新觀測

```bash
uv run --project server python probes/team_limit_50_capacity_probe.py
```

預期輸出包含：

```text
連線：300（50 組 × 6 台）
最終狀態一致：是（300/300）
```

另記錄環境、95% 更新時間與最慢時間；2 秒為觀測目標，不作阻塞門檻。300/300 一致與無例外才是阻塞條件。

## 3. 隔離與公平

```bash
uv run --project server pytest -q server/tests/test_isolation.py server/tests/test_submit.py server/tests/test_team_mode.py
```

預期：搶答結束前每組 payload 不含其他 49 組答案；50 組同題並發 20 次，每次順位無重號且恰一組得主；每組最多 6 台，第 301 台加入已滿組別被拒。

## 4. 50 組 UI

```bash
npm --prefix web test -- team-limit.test.tsx
npm --prefix web run build
make dev
```

人工以一般桌面寬度與 768 px 寬視窗驗證：

1. 老師在準備階段設定 50 組。
2. 學生在 30 秒內捲動找到並加入第 50 組。
3. 老師找到並釋放第 50 組，再確認舊 token 失效。
4. 匯入合成學習單並完成一輪作答後，在結果表捲動定位第 50 組的答案、順位與得分。
5. 記錄操作者、日期、環境、步驟與實際結果到 `specs/010-team-limit-50/verification.md`。

## 5. 圖表與全量門禁

```bash
make gate-diagrams
make gate
```

`make gate` 只在姊妹 repo 已同步 `docs/parity.md`、`contracts/api.md` 等共用檔後可認綠。實作完成後另在 `verification.md` 逐項核對 010 三張圖的組件、類別與訊息序對應程式落點。
