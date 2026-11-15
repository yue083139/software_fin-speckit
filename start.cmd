@echo off
rem Windows double-click launcher: runs start.ps1 (needs only uv and Node.js). Developers use: make dev
rem Keep this file ASCII-only: cmd mis-tracks its read position in UTF-8 batch files after a long-running command.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start.ps1"
pause
