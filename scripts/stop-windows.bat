@echo off
echo === vibe_flow_ppt 종료 ===
taskkill /f /fi "WINDOWTITLE eq vibe_flow_ppt*" 2>nul
docker stop vibe_redis 2>nul
echo 종료 완료
pause
