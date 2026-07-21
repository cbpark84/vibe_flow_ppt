# ============================================================
#  vibe_flow_ppt — Windows PowerShell 원클릭 실행 스크립트
#  사용법: .\scripts\start-windows.ps1
#  최초 실행 전: Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
# ============================================================

$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root

function Write-Step($n, $msg) { Write-Host "[$n/4] $msg" -ForegroundColor Yellow }
function Write-OK($msg)       { Write-Host "  v $msg" -ForegroundColor Green }

Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "  vibe_flow_ppt 시작 (Windows PowerShell)" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "[오류] .env에 API 키 입력 후 다시 실행하세요." -ForegroundColor Red
    exit 1
}

Write-Step 1 "Redis 시작 (Docker)..."
$running = docker ps --filter "name=vibe_redis" --format "{{.Names}}" 2>$null
if ($running -eq "vibe_redis") {
    Write-OK "Redis 이미 실행 중"
} else {
    try { docker start vibe_redis 2>$null } catch {}
    if ($LASTEXITCODE -ne 0) {
        docker run -d -p 6379:6379 --name vibe_redis redis:7-alpine
    }
    Write-OK "Redis 시작됨"
}

Write-Step 2 "ARQ 워커 시작..."
Start-Process pwsh -ArgumentList @(
    "-NoExit", "-Command",
    "Set-Location '$Root'; venv\Scripts\Activate.ps1; Write-Host 'ARQ Worker 시작' -ForegroundColor Cyan; arq engine.worker.settings.WorkerSettings"
) -WindowStyle Normal
Write-OK "ARQ 워커 창 열림"

Write-Step 3 "FastAPI 서버 시작..."
Start-Process pwsh -ArgumentList @(
    "-NoExit", "-Command",
    "Set-Location '$Root'; venv\Scripts\Activate.ps1; Write-Host 'FastAPI 시작' -ForegroundColor Cyan; uvicorn api.main:app --host 0.0.0.0 --port 8000"
) -WindowStyle Normal
Write-OK "FastAPI 창 열림"

Write-Host "  서버 준비 대기 (5초)..." -ForegroundColor Gray
Start-Sleep -Seconds 5

Write-Step 4 "Next.js 웹앱 시작..."
Start-Process pwsh -ArgumentList @(
    "-NoExit", "-Command",
    "Set-Location '$Root\web'; Write-Host 'Next.js 시작' -ForegroundColor Cyan; pnpm dev"
) -WindowStyle Normal
Write-OK "Next.js 창 열림"

Start-Sleep -Seconds 5
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "===========================================" -ForegroundColor Green
Write-Host "  실행 완료!" -ForegroundColor Green
Write-Host "  웹앱:     http://localhost:3000" -ForegroundColor Cyan
Write-Host "  API:      http://localhost:8000" -ForegroundColor Cyan
Write-Host "  Swagger:  http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Green
Write-Host "종료: scripts\stop-windows.bat" -ForegroundColor Gray
