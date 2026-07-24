@echo off

echo ==========================================
echo   vibe_flow_ppt Start (Windows)
echo ==========================================

cd /d "%~dp0.."

if not exist ".env" (
  echo [WARN] .env not found. Copying .env.example...
  copy .env.example .env
  echo [ERROR] Set your API key in .env and run again.
  pause
  exit /b 1
)

if not exist "venv\Scripts\activate.bat" (
  echo [1/5] Creating virtual environment...
  python -m venv venv
)
call venv\Scripts\activate.bat

python -c "import arq" >nul 2>&1
if %errorlevel% neq 0 (
  echo [1/5] Configuring pip for Nexus...
  pip config set global.index-url http://nexus.sdsdev.co.kr:8081/repository/pypi-public/simple/ >nul 2>&1
  pip config set global.trusted-host nexus.sdsdev.co.kr >nul 2>&1
  echo [1/5] Installing Python packages ^(prefer-binary^)...
  pip install -r requirements.txt --prefer-binary --trusted-host nexus.sdsdev.co.kr
  if %errorlevel% neq 0 (
    echo [ERROR] pip install failed.
    echo         Option: download wheels on internet PC then copy here:
    echo         pip download -r requirements.txt -d wheels --platform win_amd64 --python-version 311 --only-binary :all:
    echo         pip install -r requirements.txt --no-index --find-links wheels
    pause
    exit /b 1
  )
) else (
  echo [OK] Python packages installed
)

echo [2/5] Starting Redis...

sc query memurai >nul 2>&1
if %errorlevel% equ 0 (
  net start memurai >nul 2>&1
  echo [OK] Memurai Redis started
  goto redis_done
)

sc query redis >nul 2>&1
if %errorlevel% equ 0 (
  net start redis >nul 2>&1
  echo [OK] Redis service started
  goto redis_done
)

echo    Trying Docker Redis...
docker start vibe_redis 2>nul
if %errorlevel% neq 0 (
  docker run -d -p 6379:6379 --name vibe_redis redis:7-alpine 2>nul
)
if %errorlevel% equ 0 (
  echo [OK] Docker Redis started
  goto redis_done
)

echo [ERROR] Cannot start Redis.
echo.
echo   Install one of the following:
echo   A. Memurai   https://www.memurai.com/get-memurai
echo   B. Redis MSI https://github.com/tporadowski/redis/releases
echo   C. Docker    https://www.docker.com/products/docker-desktop
pause
exit /b 1

:redis_done

echo [3/5] Starting ARQ Worker...
start "vibe_flow_ppt - ARQ Worker" cmd /k "cd /d %CD% && venv\Scripts\activate.bat && python -m arq engine.worker.settings.WorkerSettings"

echo [4/5] Starting FastAPI server...
start "vibe_flow_ppt - FastAPI" cmd /k "cd /d %CD% && venv\Scripts\activate.bat && uvicorn api.main:app --host 0.0.0.0 --port 8000"

echo Waiting for server (5 sec)...
timeout /t 5 /nobreak > nul

echo [5/5] Starting Next.js web app...
start "vibe_flow_ppt - Next.js" cmd /k "cd /d %CD%\web && npm run dev"

timeout /t 5 /nobreak > nul
start http://localhost:3000

echo.
echo ==========================================
echo   All services started!
echo   Web:     http://localhost:3000
echo   API:     http://localhost:8000
echo   Swagger: http://localhost:8000/docs
echo ==========================================
echo To stop: scripts\stop-windows.bat
pause
