@echo off
echo === vibe_flow_ppt Stop ===

taskkill /f /fi "WINDOWTITLE eq vibe_flow_ppt*" 2>nul

sc query memurai >nul 2>&1
if %errorlevel% equ 0 (
  net stop memurai >nul 2>&1
  echo [OK] Memurai stopped
  goto redis_stopped
)

sc query redis >nul 2>&1
if %errorlevel% equ 0 (
  net stop redis >nul 2>&1
  echo [OK] Redis service stopped
  goto redis_stopped
)

docker stop vibe_redis >nul 2>&1
echo [OK] Docker Redis stopped

:redis_stopped
echo Done.
pause
