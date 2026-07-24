@echo off
cd /d "%~1"
call venv\Scripts\activate.bat
set "PYTHONPATH=%~1"
echo [API] PYTHONPATH=%PYTHONPATH%
echo [API] Starting FastAPI...
uvicorn api.main:app --host 0.0.0.0 --port 8000
