@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  set "PYTHON_CMD=py -3"
) else (
  set "PYTHON_CMD=python"
)
if not exist ".venv\Scripts\python.exe" (
  %PYTHON_CMD% -m venv .venv
  if errorlevel 1 goto python_error
)
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto install_error
.venv\Scripts\python.exe iniciar.py
pause
exit /b
:python_error
echo Instala Python 3.12 o superior y vuelve a abrir este archivo.
pause
exit /b 1
:install_error
echo No se pudieron instalar las dependencias. Revisa tu conexion a Internet.
pause
exit /b 1
