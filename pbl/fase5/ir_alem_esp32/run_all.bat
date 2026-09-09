@echo off
chcp 65001 >nul
cd /d "%~dp0"

call setup_env.bat
if errorlevel 1 (
    echo Falha ao preparar o ambiente Python.
    pause
    exit /b 1
)

start "FarmTech ESP32 Receiver" cmd /k ""%CD%\.venv\Scripts\python.exe" "%CD%\receiver\server.py""
timeout /t 3 >nul
start "FarmTech ESP32 Dashboard" cmd /k ""%CD%\.venv\Scripts\streamlit.exe" run "%CD%\dashboard\app.py" --server.port 8502"

echo Servidor HTTP: http://localhost:5000
echo Dashboard Streamlit: http://localhost:8502
echo.
".venv\Scripts\python.exe" scripts\descobrir_ip_pc.py
echo.
echo Configure o SERVER_URL do sketch com a URL exibida acima.
pause
