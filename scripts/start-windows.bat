@echo off
chcp 65001 > nul
echo ==========================================
echo   vibe_flow_ppt 시작 (Windows)
echo ==========================================

cd /d "%~dp0.."

if not exist ".env" (
  echo [경고] .env 파일 없음. .env.example 복사 중...
  copy .env.example .env
  echo [오류] .env 파일에 API 키를 설정한 후 다시 실행하세요.
  pause
  exit /b 1
)

if not exist "venv\Scripts\activate.bat" (
  echo [1/5] 가상환경 생성 중...
  python -m venv venv
  call venv\Scripts\activate.bat
  pip install -r requirements.txt -q
) else (
  echo [OK] 가상환경 확인됨
)

echo [2/5] Redis 시작...

REM 우선순위: Memurai -> tporadowski Redis 서비스 -> Docker
sc query memurai >nul 2>&1
if %errorlevel% equ 0 (
  net start memurai >nul 2>&1
  echo [OK] Memurai Redis 시작됨
  goto redis_done
)

sc query redis >nul 2>&1
if %errorlevel% equ 0 (
  net start redis >nul 2>&1
  echo [OK] Redis 서비스 시작됨
  goto redis_done
)

echo    Docker로 Redis 시도 중...
docker start vibe_redis 2>nul
if %errorlevel% neq 0 (
  docker run -d -p 6379:6379 --name vibe_redis redis:7-alpine 2>nul
)
if %errorlevel% equ 0 (
  echo [OK] Docker Redis 시작됨
  goto redis_done
)

echo [오류] Redis를 시작할 수 없습니다.
echo.
echo  Redis 설치 옵션 (하나만 선택):
echo  A. Memurai   https://www.memurai.com/get-memurai
echo  B. Redis MSI https://github.com/tporadowski/redis/releases
echo  C. Docker    https://www.docker.com/products/docker-desktop
pause
exit /b 1

:redis_done

echo [3/5] ARQ 워커 시작...
start "vibe_flow_ppt - ARQ Worker" cmd /k "cd /d %CD% && venv\Scripts\activate.bat && arq engine.worker.settings.WorkerSettings"

echo [4/5] FastAPI 서버 시작...
start "vibe_flow_ppt - FastAPI" cmd /k "cd /d %CD% && venv\Scripts\activate.bat && uvicorn api.main:app --host 0.0.0.0 --port 8000"

echo 서버 준비 대기 중 (5초)...
timeout /t 5 /nobreak > nul

echo [5/5] Next.js 웹앱 시작...
start "vibe_flow_ppt - Next.js" cmd /k "cd /d %CD%\web && npm run dev"

timeout /t 5 /nobreak > nul
start http://localhost:3000

echo.
echo ==========================================
echo   실행 완료!
echo   웹앱:     http://localhost:3000
echo   API:      http://localhost:8000
echo   Swagger:  http://localhost:8000/docs
echo ==========================================
echo 종료: scripts\stop-windows.bat
pause
