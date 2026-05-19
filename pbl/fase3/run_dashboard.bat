@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\streamlit.exe" (
    echo Ambiente virtual nao encontrado. Rode o setup antes.
    pause
    exit /b 1
)
".venv\Scripts\streamlit.exe" run app.py
