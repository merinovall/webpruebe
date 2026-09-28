@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Ejecuta primero INICIAR_WINDOWS.bat para preparar Python.
  pause
  exit /b 1
)
.venv\Scripts\python.exe app.py create-admin
pause
