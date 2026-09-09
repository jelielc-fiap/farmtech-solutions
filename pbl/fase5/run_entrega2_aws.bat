@echo off
setlocal
chcp 65001 >nul

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    call setup_env.bat
)

echo Gerando tabela e gráfico de custos AWS...
".venv\Scripts\python.exe" "entrega2_aws\scripts\gerar_comparativo_aws.py"

echo.
echo Entrega 2 concluída.
echo Documentação: entrega2_aws\README.md
pause
