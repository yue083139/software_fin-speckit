@echo off
rem Same as start.cmd, plus a Cloudflare quick tunnel so phones can scan the student QR code (needs cloudflared:
rem   winget install --id Cloudflare.cloudflared -e). Keep this file ASCII-only (see start.cmd).
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start.ps1" -Tunnel
pause
