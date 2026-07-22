@echo off
echo === vibe_flow_ppt 종료 ===
taskkill /f /fi "WINDOWTITLE eq vibe_flow_ppt*" 2>nul

REM Redis 종료 (설치된 방식에 맞게 자동 감지)
sc query memurai >nul 2>&1
if %errorlevel% equ 0 (
  net stop memurai >nul 2>&1
) else (
  sc query redis >nul 2>&1
  if %errorlevel% equ 0 (
    net stop redis >nul 2>&1
  ) else (
    docker stop vibe_redis >nul 2>&1
  )
)

echo 종료 완료
pause
