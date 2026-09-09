@echo off
setlocal
chcp 65001 >nul

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    call setup_env.bat
)

echo Analisando o CSV importado e executando o notebook...
".venv\Scripts\python.exe" "entrega1_ml\scripts\gerar_notebook.py"
if errorlevel 1 (
    echo Falha na analise. Confira a mensagem acima e a importacao da base oficial.
    pause
    exit /b 1
)

echo.
echo Entrega 1 concluída.
echo Notebook: entrega1_ml\notebooks\JelielCardoso_RM572665_pbl_fase4.ipynb
pause
