@echo off
set "ROOT=%~1"
cd /d "%ROOT%"
echo [WEB] Starting Next.js in %ROOT%...
npm run dev
