@echo off
setlocal

cd /d "%~dp0"

echo Iniciando ONCC Sistema...

set "PROJECT_DIR=%~dp0"
if not exist "%PROJECT_DIR%venv\Scripts\python.exe" set "PROJECT_DIR=%USERPROFILE%\Documents\Project ONCC\ONCC_Sistema\"

if not exist "%PROJECT_DIR%venv\Scripts\python.exe" (
    echo ERROR: No se encontro el entorno virtual en:
    echo %PROJECT_DIR%\venv\Scripts\python.exe
    echo.
    echo Revise la ruta del proyecto o cree el entorno con: python -m venv venv
    pause
    exit /b 1
)

start "ONCC Sistema" /D "%PROJECT_DIR%" "%PROJECT_DIR%venv\Scripts\python.exe" "%PROJECT_DIR%run.py"

echo Servidor iniciado. Abriendo el navegador...
timeout /t 3 /nobreak >nul
start "" "http://127.0.0.1:5000"

endlocal
exit /b 0
