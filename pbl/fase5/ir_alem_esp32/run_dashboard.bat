@echo off
chcp 65001 >nul
cd /d "%~dp0"

call setup_env.bat
if errorlevel 1 (
    echo Falha ao preparar o ambiente Python.
    pause
    exit /b 1
)

echo Iniciando dashboard Streamlit em http://localhost:8502
".venv\Scripts\streamlit.exe" run dashboard\app.py --server.port 8502
