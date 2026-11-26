# Feature Specification: 啟動即進老師頁，Google 設定與手機連線都在老師頁引導完成

**Feature Branch**: `017-easy-setup`
**Created**: 2026-11-26
**Status**: Implemented（v1.1；提案輪評審藥方已併入，負責人指示審完直接實作；與 OpenSpec 組 `openspec/changes/easy-setup/` 同批）
**Input**: 負責人 2026-11-26：「現在的啟動過程有點複雜，需要 .env，有辦法簡化或是在後台頁面裡面引導式操作嗎」⇒ 裁四項全做（Google 設定精靈、啟動後自動開老師頁、老師頁一鍵開手機連線、啟動腳本自動補裝工具）；補充「希望 make dev 之類的啟動後就能直接進後台做」。
**需求編號**：R-01、X-04｜**parity**：`docs/parity.md` §4 `easy-setup`｜**檔位**：S（憑證 Google API、`contracts/`、跨元件架構取捨：執行期起停外部子行程與開瀏覽器）
**圖表**：`diagrams/017-easy-setup-{component,class,sequence}.puml`
**合入順序**：在 `015-teacher-key-hidden`、`016-teacher-key-error` 之後（三者都改 `web/src/pages/Teacher.tsx`）

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 啟動後直接進老師頁 (Priority: P1)

老師雙擊 `start.cmd`（或 `make dev`），伺服器就緒後預設瀏覽器自動開老師頁；之後所有設定都在老師頁完成，不必看終端機。

**Why this priority**: 負責人補充的核心訴求：啟動後就能直接進後台。

**Independent Test**: 以替身開瀏覽器函式計次：預設 1 次、`--no-browser`／`QUIZ_NO_BROWSER=1`／`CI=1` 各 0 次。

**Acceptance Scenarios**:

1. **Given** 正常啟動，**When** 伺服器就緒，**Then** 預設瀏覽器開 `http://127.0.0.1:8000/#/teacher?key=…` 恰一次，終端機仍印網址。
2. **Given** 帶 `--no-browser` 或 `QUIZ_NO_BROWSER=1`，**When** 啟動，**Then** 不開瀏覽器。

---

### User Story 2 - Google 設定精靈 (Priority: P1)

Google 未設定時，老師頁「Google 帳號」區展開六步引導（Cloud Console 直達連結、一鍵複製重新導向 URI），老師貼上用戶端 ID 與密鑰按「儲存設定」，不重啟即可登入。

**Why this priority**: 免手動編 `.env` 與重啟；助教自建 OAuth 用戶端也靠它。

**Independent Test**: 以暫存目錄的 `.env` 驗證只改兩鍵、其他行保留、回應與日誌不含密鑰。

**Acceptance Scenarios**:

1. **Given** 未設定，**When** 貼上格式正確的 ID 與密鑰並儲存，**Then** 狀態 `configured: true`（只回遮罩 ID），登入取得含新 ID 的授權網址。
2. **Given** 密鑰不以 `GOCSPX-` 開頭、含換行（含尾端換行）或 `=`、超過 128 字，**When** 儲存，**Then** 422 且 `.env` 不變、不回顯輸入。
3. **Given** 經通道公開網址，**When** 呼叫設定端點，**Then** 403「老師頁只能在本機開啟」。
4. **Given** 已登入 Google，**When** 變更或清除設定，**Then** 409「請先登出 Google 再變更設定」。
5. **Given** 未登入，**When** 清除設定，**Then** `.env` 移除兩鍵、其他行保留，`configured: false`。
6. **Given** `.env` 有「`GOOGLE_CLIENT_ID = 舊值`」與重複鍵，**When** 儲存，**Then** 只留一行新值、其他行不變。
7. **Given** 以舊設定發起登入尚未完成，**When** 又儲存新設定後舊回呼抵達，**Then** 不以舊授權登入（世代號）。

---

### User Story 3 - 一鍵開關手機連線 (Priority: P1)

老師在「學生連結」區按「開啟手機連線」，伺服器即時起 cloudflared，QR code 自動更新；可按「關閉手機連線」。

**Why this priority**: 免在啟動前選 `start-tunnel.cmd`。

**Independent Test**: 假 Tunnel（可控延遲、可回 None、可模擬找不到）驗狀態序列與錯誤碼。

**Acceptance Scenarios**:

1. **Given** 已安裝 cloudflared，**When** 按開啟，**Then** 老師 view `tunnel` 依序 `starting`、`on`，`student_url` 為公開網址。
2. **Given** 未安裝，**When** 按開啟，**Then** 503 含安裝指令，前端顯示指令與複製鈕。
3. **Given** 兩個老師分頁幾乎同時按開啟，**Then** 只起一個 cloudflared，第二個回 409「手機連線建立中」。
4. **Given** 已開啟，**When** 按關閉，**Then** 子行程結束、`tunnel: off`、`student_url: null`。
5. 學生 view 永不含 `tunnel`、`student_url`。
6. **Given** 建立中，**When** 按關閉，**Then** 建立完成後子行程被停止，兩個請求都回 off。
7. **Given** 活動不在準備階段，**When** 按關閉，**Then** 409「搶答進行中不能關閉手機連線」，通道維持開啟。
8. **Given** cloudflared 意外結束，**Then** `tunnel` 轉 off、`student_url` 為 null。
9. **Given** 以 `--tunnel` 啟動，**Then** 該通道與老師頁開關是同一個 `Tunnel` 實例（以伺服器埠建立），按關閉停得掉。

---

### User Story 4 - 開始前的設定清單 (Priority: P2)

準備階段老師頁頂部顯示 Google、手機連線、題目三項狀態，點了捲到對應分區；其他階段不顯示。

**Acceptance Scenarios**:

1. **Given** 未設定 Google、未開手機連線、未匯入，**When** 開老師頁，**Then** 三項分別「未設定」「關閉」「尚未匯入」，Google 分區展開精靈。

---

### User Story 5 - 啟動腳本代裝工具 (Priority: P2)

缺 uv 或 Node.js 時 `start.ps1` 詢問「要幫你用 winget 安裝嗎？(Y/N)」，Y 則安裝、刷新 PATH 後繼續啟動。

**Acceptance Scenarios**:

1. **Given** 缺 uv，**When** 雙擊 `start.cmd` 並輸入 Y，**Then** 安裝 uv、刷新 PATH 並繼續，不需重開視窗。
2. **Given** 缺 uv，**When** 直接按 Enter 或輸入其他字，**Then** 視為 N，印手動安裝指令後結束（只認 Y／y）。

### Edge Cases

- 瀏覽器開不了 ⇒ 印提示，伺服器照常。
- 系統環境變數另設 `GOOGLE_CLIENT_ID` ⇒ 重啟後以系統值為準（`load_env` 不覆蓋），README 註明。
- 通道 DNS 約 1 分鐘生效 ⇒ 前端提示。

## Requirements *(mandatory)*

- **FR-001**: 啟動就緒後 MUST 自動開本機老師頁恰一次；`--no-browser`、`QUIZ_NO_BROWSER=1`、`CI` 非空 MUST NOT 開（R1）。
- **FR-002**: Google 設定端點 MUST 限本機＋金鑰、白名單驗證、只改 `.env` 兩鍵、原子寫入、立即生效；密鑰 MUST NOT 出現在回應、view、日誌；已登入 MUST 409（R2）。
- **FR-003**: 手機連線端點 MUST 限本機＋金鑰、以鎖序列化、執行期起停注入的 `Tunnel` 實例；建立中關閉 MUST 取消、非準備階段關閉 MUST 409、子行程意外結束 MUST 轉 off；老師 view MUST 含 `tunnel`；學生 view MUST NOT 含 `tunnel`、`student_url`；找不到 503、逾時 504（R3）。
- **FR-004**: 準備階段 MUST 顯示開始前的設定清單（R4）。
- **FR-005**: `start.ps1` 缺工具 MUST 詢問代裝並刷新 PATH（R5）。
- **FR-006**: `contracts/api.md`、README、`.env.example`、手冊同批更新；移除 `start-tunnel.cmd`（R3、R6）。

## Success Criteria *(mandatory)*

- **SC-001**: 雙擊 `start.cmd` 到完成 Google 登入與手機連線，全程不看終端機、不編輯 `.env`。
- **SC-002**: `test_google_config.py`、`test_tunnel_api.py`、`test_launch.py` 全綠，矩陣 M-025、M-026、M-027 covered。
