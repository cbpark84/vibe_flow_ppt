@echo off
cd /d "%~1"
call venv\Scripts\activate.bat
set "PYTHONPATH=%~1"
echo [ARQ] PYTHONPATH=%PYTHONPATH%
echo [ARQ] Starting worker...
python -m arq engine.worker.settings.WorkerSettings
