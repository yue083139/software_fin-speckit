# Windows 啟動腳本，由 start.cmd 呼叫；只需 uv 與 Node.js（缺的話可代為以 winget 安裝）。開發者改用 make dev（步驟相同）
# 伺服器就緒後會自動開老師頁（easy-setup D1）；手機連線在老師頁按「開啟手機連線」（easy-setup D3）
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$env:PYTHONUTF8 = '1'
Set-Location $PSScriptRoot

function Fail([string]$msg) { Write-Host $msg -ForegroundColor Red; exit 1 }

# winget 安裝後同一行程的 PATH 不會自動更新：以 Machine＋User 登錄值刷新（探針 probes/results/2026-11-26-easy-setup.txt ③）
function Update-SessionPath {
    $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User')
}

# 缺工具時詢問代裝（easy-setup D5）：只認 Y／y，空值（直接按 Enter）、其他輸入或非互動一律視為 N
function Install-Tool([string]$command, [string]$name, [string]$wingetId) {
    if (Get-Command $command -ErrorAction SilentlyContinue) { return }
    $manual = "請在 PowerShell 執行 winget install --id $wingetId -e 裝好後，再雙擊一次 start.cmd。"
    Write-Host "找不到 $name。"
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        Fail "這台電腦沒有 winget：請到 Microsoft Store 安裝「應用程式安裝程式」，或到 $name 官網手動安裝後再雙擊一次 start.cmd。"
    }
    try { $answer = Read-Host '要幫你用 winget 安裝嗎？(Y/N)' } catch { $answer = '' }
    if ($answer -cne 'Y' -and $answer -cne 'y') { Fail $manual }
    Write-Host "正在安裝 $name（可能跳出「是否允許變更」視窗，請按「是」）…"
    winget install --id $wingetId -e --accept-source-agreements --accept-package-agreements
    Update-SessionPath
    if (-not (Get-Command $command -ErrorAction SilentlyContinue)) {
        Fail "已嘗試安裝 $name，但這個視窗還找不到它。請關閉視窗後再雙擊一次 start.cmd。"
    }
}

Install-Tool 'uv' 'uv' 'astral-sh.uv'
Install-Tool 'npm' 'Node.js' 'OpenJS.NodeJS.LTS'

# 與 make dev 同一條規則：npm 每次安裝都會改寫 node_modules/.package-lock.json，它不存在或比鎖檔舊才重裝
$stamp = 'web/node_modules/.package-lock.json'
if (-not (Test-Path $stamp) -or (Get-Item $stamp).LastWriteTime -lt (Get-Item 'web/package-lock.json').LastWriteTime) {
    Write-Host '安裝前端依賴，第一次約需一兩分鐘…'
    npm --prefix web ci --no-fund --no-audit
    if ($LASTEXITCODE -ne 0) { Fail '安裝前端依賴失敗。請把上面的錯誤訊息截圖給組員。' }
}
npm --prefix web run build
if ($LASTEXITCODE -ne 0) { Fail '建置前端失敗。請把上面的錯誤訊息截圖給組員。' }

Write-Host ''
Write-Host '伺服器啟動中，就緒後會自動開老師頁。關閉這個視窗就會停止活動，活動資料會清空，結束前請先匯出。'
uv run --project server python -m quiz_server
