@echo off
set "ROOT=%~1"
cd /d "%ROOT%"
set "PYTHONPATH=%ROOT%"
set "PYTHON=%ROOT%\venv\Scripts\python.exe"

if not exist "%PYTHON%" (
  echo [ERROR] venv not found: %PYTHON%
  echo Run start-windows.bat first to create venv.
  pause
  exit /b 1
)

echo [ARQ] ROOT     = %ROOT%
echo [ARQ] PYTHON   = %PYTHON%
echo [ARQ] PYTHONPATH = %PYTHONPATH%
echo [ARQ] Starting ARQ Worker...
"%PYTHON%" -m arq engine.worker.settings.WorkerSettings
