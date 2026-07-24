# ============================================================
#  vibe_flow_ppt — Windows PowerShell 원클릭 실행 스크립트
#  사용법: .\scripts\start-windows.ps1
#  최초 실행 전: Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
# ============================================================

$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root

# PowerShell 7(pwsh) 우선, 없으면 기본 PowerShell 5(powershell) 사용
$PS = if (Get-Command pwsh -ErrorAction SilentlyContinue) { "pwsh" } else { "powershell" }

function Write-Step($n, $msg) { Write-Host "[$n] $msg" -ForegroundColor Yellow }
function Write-OK($msg)       { Write-Host "  v $msg" -ForegroundColor Green }

Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "  vibe_flow_ppt 시작 (Windows PowerShell)" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "[오류] .env에 API 키 입력 후 다시 실행하세요." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Step "1/5" "Creating virtual environment..."
    python -m venv venv
}
& "venv\Scripts\Activate.ps1"

$arqCheck = python -c "import arq" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Configuring pip for Nexus..." -ForegroundColor Gray
    pip config set global.index-url http://nexus.sdsdev.co.kr:8081/repository/pypi-public/simple/ | Out-Null
    pip config set global.trusted-host nexus.sdsdev.co.kr | Out-Null
    Write-Host "  Tip: if packages are missing, ask IT for pypi-group URL" -ForegroundColor Gray
    Write-Host "  e.g. http://nexus.sdsdev.co.kr:8081/repository/pypi-all/simple/" -ForegroundColor Gray
    Write-Step "1/5" "Installing Python packages..."
    pip install -r requirements.txt --prefer-binary --find-links wheels --trusted-host nexus.sdsdev.co.kr
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] pip install failed." -ForegroundColor Red
        exit 1
    }
} else {
    Write-OK "Python packages installed"
}

Write-Step "2/5" "Redis 시작..."
$redisDone = $false

# Memurai 서비스 확인
if (Get-Service -Name "memurai" -ErrorAction SilentlyContinue) {
    Start-Service -Name "memurai" -ErrorAction SilentlyContinue
    Write-OK "Memurai Redis 시작됨"
    $redisDone = $true
}
# tporadowski Redis 서비스 확인
elseif (Get-Service -Name "redis" -ErrorAction SilentlyContinue) {
    Start-Service -Name "redis" -ErrorAction SilentlyContinue
    Write-OK "Redis 서비스 시작됨"
    $redisDone = $true
}
# Docker 시도
else {
    $running = docker ps --filter "name=vibe_redis" --format "{{.Names}}" 2>$null
    if ($running -eq "vibe_redis") {
        Write-OK "Docker Redis 이미 실행 중"
        $redisDone = $true
    } else {
        $started = $false
        try { docker start vibe_redis 2>$null; if ($LASTEXITCODE -eq 0) { $started = $true } } catch {}
        if (-not $started) {
            try { docker run -d -p 6379:6379 --name vibe_redis redis:7-alpine 2>$null; if ($LASTEXITCODE -eq 0) { $started = $true } } catch {}
        }
        if ($started) {
            Write-OK "Docker Redis 시작됨"
            $redisDone = $true
        }
    }
}

if (-not $redisDone) {
    Write-Host "[오류] Redis를 시작할 수 없습니다." -ForegroundColor Red
    Write-Host ""
    Write-Host "  Redis 설치 옵션 (하나만 선택):" -ForegroundColor Yellow
    Write-Host "  A. Memurai   https://www.memurai.com/get-memurai" -ForegroundColor Cyan
    Write-Host "  B. Redis MSI https://github.com/tporadowski/redis/releases" -ForegroundColor Cyan
    Write-Host "  C. Docker    https://www.docker.com/products/docker-desktop" -ForegroundColor Cyan
    exit 1
}

Write-Step "3/5" "ARQ 워커 시작..."
Start-Process $PS -ArgumentList @(
    "-NoExit", "-Command",
    "Set-Location '$Root'; venv\Scripts\Activate.ps1; Write-Host 'ARQ Worker 시작' -ForegroundColor Cyan; python -m arq engine.worker.settings.WorkerSettings"
) -WindowStyle Normal
Write-OK "ARQ 워커 창 열림"

Write-Step "4/5" "FastAPI 서버 시작..."
Start-Process $PS -ArgumentList @(
    "-NoExit", "-Command",
    "Set-Location '$Root'; venv\Scripts\Activate.ps1; Write-Host 'FastAPI 시작' -ForegroundColor Cyan; uvicorn api.main:app --host 0.0.0.0 --port 8000"
) -WindowStyle Normal
Write-OK "FastAPI 창 열림"

Write-Host "  서버 준비 대기 (5초)..." -ForegroundColor Gray
Start-Sleep -Seconds 5

Write-Step "5/5" "Next.js 웹앱 시작..."
Start-Process $PS -ArgumentList @(
    "-NoExit", "-Command",
    "Set-Location '$Root\web'; Write-Host 'Next.js 시작' -ForegroundColor Cyan; npm run dev"
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
