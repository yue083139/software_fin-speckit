# Research: 006 game-mode-framework

知識時點：2026-11-12。對標（`docs/research/competitors.md`）：Kahoot! Accuracy 模式只看答對與否；Kahoot!、Quizizz 題目都有標準答案、由系統自動判定。本系統的 Guided Notes 沒有標準答案欄（`probes/results/2026-11-11-guided-notes-structure.txt`：兩份範本表頭只有「題號／題目／作答」），故改為老師判定，參考答案只給建議（TRD §6 裁定）。

## R1 模式登記表

- **Decision**：`Mode(key, label, judged, rule)`、`MODES`、`DEFAULT_MODE="classic"`；`Activity.rule` 為 `mode.rule` 的唯讀屬性；`set_mode` 只在 `preparing`（409）、未知鍵 `ModeError`（422）；重置保留。
- **Rationale**：準備階段必然沒有送出（匯入與重置都清空），換模式不必清資料。
- **證偽欄｜可證偽**：`test_modes.py`；第一期測試不改即綠。

## R2 規則與得主

- **Decision**：`Ranked.correct: bool | None`；`AccuracyRule`：正確 1 分；得主＝依 `seq` 第一個 `correct is True`。
- **Rationale**：匯出只取 `is_winner` 的答案，得主定義放在規則裡，匯出不改。003 spec「順位 1 為搶答成功者」只對經典模式成立，判定模式以本條為準（v1.1，架構通道）。
- **證偽欄｜可證偽**：`test_scoring.py` 表格式：全對、全錯、先錯後對、部分未判定、無人作答。屬取捨：多組答對只寫回最早者。

## R3 判定階段與狀態機

- **Decision**：`end()` 加 `_require(ANSWERING)` 後依 `mode.judged` 轉 `judging`／`ended`；`judge`、`accept_suggestions` 只在 `judging`；`reveal()` 要求 `pending_judgments() == 0`。檢查與寫入之間放 `_checkpoint()`。
- **Rationale**：轉移表允許 `judging → ended`，若 `end()` 不擋，`POST /api/teacher/end` 可繞過揭曉的未判定檢查。
- **證偽欄｜可證偽**：`test_judging.py`（錯誤碼、未判定 409、判定中結束 409、改判、`test_concurrent_reveal_and_judge` 20 輪）；變異實錄：拿掉未判定檢查、拿掉 `_require(ANSWERING)`，必紅。

## R4 參考答案與建議

- **Decision**：`REFERENCE_ALIASES = ("參考答案", "正確答案", "標準答案", "解答", "answerkey")`，與題號、作答欄同列整格比對；`Slot.reference` 取作答格同列的值（合併只取錨點列、空白為 `None`）。`suggest`：缺參考 ⇒ `None`；NFKC＋去空白＋`casefold` 後全等 ⇒ `True`；否則 `False`。
- **Rationale**：別名不含「答案」（已是作答欄別名）；整格比對下「參考答案」不會被誤認為作答欄。
- **證偽欄｜可證偽**：夾具 `reference.xlsx`（`build_reference.py`，合成內容，含題組與一題無參考答案）；`test_guided_notes_parse.py`；`test_judging.py::test_suggest`。屬取捨：不做同義詞或模糊比對。

## R5 隔離與一致性

- **Decision**：學生 view 在 `judging` 與 `answering` 相同；`results.build(a, teacher=False)` 為共用欄位，`teacher=True` 另加 `suggestion` 與每題 `reference`；學生 view 增 `mode`、`score_label`。
- **證偽欄｜可證偽**：`test_isolation.py::test_judging_hides_judgments`、`test_reference_never_sent_to_students`；`test_results_view.py::test_teacher_and_student_agree` 改為「拿掉老師專屬欄位後相等」、兩模式各跑一次。
