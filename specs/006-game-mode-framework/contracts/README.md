# 006 game-mode-framework 介面契約

於 [`/contracts/api.md`](../../../contracts/api.md) 新增 `POST /api/teacher/mode`（`{mode}`；401／409 非 preparing／422 未知模式）、`POST /api/teacher/judge`（`{question, team, correct}`；401／404 無此送出／409 非 judging）、`POST /api/teacher/accept-suggestions`（`{applied}`；401／409）、`POST /api/teacher/reveal`（`{phase}`；401／409 非 judging 或尚有未判定）；`POST /api/teacher/end` 在判定模式回 `{phase: "judging"}`、非 answering 回 409。view 增欄位見 [data-model.md](../data-model.md)。
