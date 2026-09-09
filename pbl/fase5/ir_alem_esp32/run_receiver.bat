@echo off
chcp 65001 >nul
cd /d "%~dp0"

call setup_env.bat
if errorlevel 1 (
    echo Falha ao preparar o ambiente Python.
    pause
    exit /b 1
)

echo Iniciando servidor HTTP local em http://localhost:5000
".venv\Scripts\python.exe" receiver\server.py
