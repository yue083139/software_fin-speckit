# 015 teacher-key-hidden — data model

| 名稱 | 位置 | 形狀 | 生命週期 |
|---|---|---|---|
| `qz_teacher_key` | 瀏覽器 sessionStorage（本分頁） | 字串 | 首次自網址帶入時寫入；網址帶新 key 時覆寫；401／4401 清除；關分頁即失效 |

伺服器端資料模型不變。
