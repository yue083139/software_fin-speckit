# Windows 啟動腳本，由 start.cmd 呼叫；只需 uv 與 Node.js。開發者改用 make dev（步驟相同）
# -Tunnel（start-tunnel.cmd）：另以 Cloudflare 快速通道取得公開網址，讓手機掃 QR code 進學生頁（student-qr）
param([switch]$Tunnel)
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$env:PYTHONUTF8 = '1'
Set-Location $PSScriptRoot

function Fail([string]$msg) { Write-Host $msg -ForegroundColor Red; exit 1 }

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Fail '找不到 uv。請在 PowerShell 執行 winget install --id astral-sh.uv -e 裝好後，再雙擊一次 start.cmd。'
}
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Fail '找不到 Node.js。請在 PowerShell 執行 winget install --id OpenJS.NodeJS.LTS -e 裝好後，再雙擊一次 start.cmd。'
}

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
Write-Host '伺服器啟動中。關閉這個視窗就會停止活動，活動資料會清空，結束前請先匯出。'
if ($Tunnel) {
    uv run --project server python -m quiz_server --tunnel
} else {
    uv run --project server python -m quiz_server
}
