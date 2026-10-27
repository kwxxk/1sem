@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" server.py --open
) else (
  where py >nul 2>nul
  if errorlevel 1 (
    python server.py --open
  ) else (
    py -3 server.py --open
  )
)
pause
