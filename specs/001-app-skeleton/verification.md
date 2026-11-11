# Verification: 001 app-skeleton

## 門禁（2026-11-11，本機 Windows）

```
$ make gate-pr
All checks passed!
All checks passed!
47 passed, 1 warning in 0.99s
51 passed in 5.53s
 Test Files  1 passed (1)
      Tests  4 passed (4)
gate-zh-hant: 0 處簡體字
gate-secrets: 0 findings
gate-speckit: 憲章 v1.0.0，0 處問題
gate-diagrams: 4 個圖檔，0 處問題
gate-agents: 0 處漂移
```

## 變異實錄（research R1）

```
$ （activity.py 的 async with self._lock 換成 contextlib.nullcontext()）uv run --project server pytest -q server/tests/test_phases.py -k concurrent
FAILED server\tests\test_phases.py::test_concurrent_transitions_serialized - ...
FAILED server\tests\test_phases.py::test_concurrent_join_same_team_once - ass...
2 failed, 21 deselected in 0.09s
```

## 圖碼一致核對（憲章原則 VII 實作階段）

> 本表行號以本功能實作提交 `59a6bfa` 當下的程式為準（後續功能會移動行號）；交付版（最終分支）的行號見 `specs/005-guided-notes-export/verification.md`「交付版圖碼核對」。

| 圖 | 元素 | 程式落點 | 一致／偏離 |
|---|---|---|---|
| class | `Phase`（含預留 JUDGING） | `server/quiz_server/phases.py:8` | 一致 |
| class | `PhaseError`、轉移檢查 | `phases.py:23`、`phases.py:27` | 一致 |
| class | `TeamTakenError` | `server/quiz_server/activity.py:15` | 一致 |
| class | `Activity._checkpoint`、`_bump` | `activity.py:33`、`activity.py:36` | 一致 |
| class | `Activity.team_of`／`joined_teams`／`join`／`release` | `activity.py:47`、`:56`、`:59`、`:71` | 一致 |
| class | `Activity.configure_teams`／`start`／`end`／`reset` | `activity.py:78`、`:94`、`:99`、`:104` | 一致 |
| class | `views.teacher_view`／`student_view`／`view_for` | `server/quiz_server/views.py:11`、`:20`、`:27` | 一致 |
| class | `app.create_app`、`resolve_teacher_key` | `server/quiz_server/app.py:35`、`:31` | 一致 |
| component | Home／Teacher／Student／useLiveView／api.ts | `web/src/pages/Home.tsx`、`Teacher.tsx`、`Student.tsx`、`web/src/live.ts`、`web/src/api.ts` | 一致 |
| component | `__main__` 印老師頁網址、`log_level=warning` | `server/quiz_server/__main__.py:23` | 一致 |
| sequence | `POST /api/student/join` → `join` → 409 | `app.py:71` | 一致 |
| sequence | WS 以 token 反查（`team_of`）後 `student_view` | `app.py:109` 起 `current_view` | 一致 |
| sequence | par：每連線送出迴圈、view 相同不送 | `app.py:124`、`app.py:136` | 一致 |
| system-component | scoring／results／guided_notes／sources | 尚未實作（002～005） | 預告元素，非偏離 |

偏離：無。實作階段新增的「忽略客戶端二進位訊框」（OpenSpec 組實作輪紅隊發現）屬 `app.py` ws 內部細節，不影響圖上的元件與訊息序。

## 人工驗證（需求 P-05）

狀態：**待負責人執行**。步驟同 OpenSpec 組 `openspec/changes/app-skeleton/verification.md`：

1. `make web-install` 後 `make dev`，記下終端機印出的老師頁網址。
2. 三個分頁：老師頁、首頁選第1組、首頁選第2組；第四個分頁再選第1組應顯示「此組已有裝置加入」。
3. 老師頁看到已加入的組；按「釋放」第2組，第2組分頁顯示需重新加入。
4. 老師按開始／結束，學生分頁階段同步。

結果：＿＿＿（執行人／日期／看到什麼）
