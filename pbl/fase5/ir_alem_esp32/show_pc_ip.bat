@echo off
chcp 65001 >nul
cd /d "%~dp0"

call setup_env.bat
if errorlevel 1 (
    echo Falha ao preparar o ambiente Python.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" scripts\descobrir_ip_pc.py
pause
