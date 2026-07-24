@echo off
set "ROOT=%~1"
cd /d "%ROOT%"
set "PYTHONPATH=%ROOT%"
set "PYTHON=%ROOT%\venv\Scripts\python.exe"

if not exist "%PYTHON%" (
  echo [ERROR] venv not found: %PYTHON%
  pause
  exit /b 1
)

echo [API] ROOT   = %ROOT%
echo [API] PYTHON = %PYTHON%
echo [API] Starting FastAPI...
"%PYTHON%" -m uvicorn api.main:app --host 0.0.0.0 --port 8000
