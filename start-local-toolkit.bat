@echo off
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File "%~dp0run-local-tool.ps1"
pause
