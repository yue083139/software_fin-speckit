# 015 teacher-key-hidden — verification（v1.1）

## 門禁實錄

2026-11-26，web 兩組逐字相同：
- OpenSpec `make gate-pr` 連跑兩次 exit=0：server 313 passed、ops 48 passed、web `Tests 61 passed (61)`、gate-zh-hant 0、gate-secrets 0、openspec 12 passed、gate-agents 0。
- SpecKit `make gate SIBLING=../wt-os-key` 連跑兩次 exit=0：server 313、ops 58、web 61 passed；gate-speckit 0、gate-diagrams 46 個 0 問題、gate-diagrams-syntax 46 個通過、gate-agents 0、gate-parity 0 處不一致。
- 先紅後綠：v1.0 新測試在實作前 `Tests 7 failed (7)`。
- v1.1（評審藥方後）兩組各連跑兩次皆 exit=0：OpenSpec `make gate-pr` server 313、ops 48、web `Tests 66 passed (66)`、openspec 12 passed、zh-hant 0、secrets 0、agents 0；SpecKit `make gate SIBLING=../wt-os-key` server 313、ops 58、web 66 passed、speckit 0、diagrams 46 個 0 問題、diagrams-syntax 46 通過、agents 0、parity 0 處不一致。

## 評審紀錄

- 架構通道（全卡掃，v1.0）：NOT CLEARED(1B/2M/2m)。阻斷——取金鑰在 render 的 `useMemo`，同分頁重貼同一網址不重繪、key 留在網址列（評審探針 PROBE2b `hash= #/teacher?key=good`）；重要——錯誤狀態不清、先錯後對卡在錯誤頁（PROBE1 `stillError=true`）；重要——合流統一整頁 `BadKeyNotice`；次要——tasks 3.1、design D3 註明。藥方已落（v1.1）。
- 對抗通道（diff，v1.0）：NOT CLEARED(1B/0M/1m)。阻斷——所有 REST 401 當金鑰錯，Google 未登入時老師被踢出、金鑰被刪（探針 `KEY_AFTER= null BADKEY_SHOWN= true GOOGLE_MSG= false`）⇒ 只認 detail「需要老師金鑰」；次要——兩個清除點無測試 ⇒ 補。藥方已落（v1.1）。

### v1.1 先紅後綠與變異實錄

- `app.test.tsx` 兩例（重貼同一網址、先錯後對）在 v1.0 的 `App.tsx` 上 `× ×`（2 failed），v1.1 上 passed。
- 變異（`teacherkey.test.tsx`，各自還原）：拿掉 `setError` 的 `clearTeacherKey()` ⇒ `1 failed | 3 passed`；拿掉 4401 的 `clearTeacherKey()` ⇒ `1 failed | 3 passed`；`isBadTeacherKey` 不比對 detail（所有 401 都算）⇒ `1 failed | 3 passed`。

## followup（不改，主人 @yue083139）

- `Teacher.tsx` Google 登入以 `window.open("", "_blank")` 開新分頁、無 `noopener`：新分頁會複製本分頁 sessionStorage（Google 登入分頁也帶金鑰，不外送，未外洩）。
- `Home.tsx` 「進入老師頁」按鈕 `href` 含金鑰，滑鼠停留時瀏覽器狀態列可見。
- 瀏覽器「記錄」頁與網址列自動完成仍可能保留最初貼上的完整網址（手冊場次 G 註明）。

## 人工驗證（需求 P-05）

狀態：**待執行**（負責人，`docs/manual-verification.md` 場次 G）。
