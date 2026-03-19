$ErrorActionPreference = "Stop"
$RootDir = $PSScriptRoot

if (-not (Test-Path "$RootDir\.venv")) {
    Write-Host "[1/3] 가상환경 생성 중..." -ForegroundColor Cyan
    python -m venv "$RootDir\.venv"
}

Write-Host "[2/3] 패키지 설치 중..." -ForegroundColor Cyan
& "$RootDir\.venv\Scripts\pip.exe" install -r "$RootDir\requirements.txt" --quiet

$PlaywrightMark = "$RootDir\.venv\playwright_installed"
if (-not (Test-Path $PlaywrightMark)) {
    Write-Host "[2/3] Playwright 브라우저 설치 중 (최초 1회)..." -ForegroundColor Cyan
    & "$RootDir\.venv\Scripts\playwright.exe" install chromium
    New-Item -ItemType File -Path $PlaywrightMark | Out-Null
}

Write-Host "[3/3] 서버 시작 중... http://localhost:8000" -ForegroundColor Green
Start-Sleep -Seconds 1
Start-Process "http://localhost:8000"
& "$RootDir\.venv\Scripts\uvicorn.exe" app.main:app --host 127.0.0.1 --port 8000 --reload
