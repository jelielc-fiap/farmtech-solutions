@echo off
setlocal
chcp 65001 >nul

cd /d "%~dp0"

set "PY_CMD="
where py >nul 2>nul
if %errorlevel%==0 set "PY_CMD=py -3"

if "%PY_CMD%"=="" (
    where python >nul 2>nul
    if %errorlevel%==0 set "PY_CMD=python"
)

if "%PY_CMD%"=="" (
    echo Python não encontrado no PATH.
    echo Instale o Python 3 ou habilite o launcher "py" no Windows.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Criando ambiente virtual da Fase 5...
    %PY_CMD% -m venv .venv
)

echo Atualizando pip...
".venv\Scripts\python.exe" -m pip install --upgrade pip

echo Instalando dependências da Fase 5...
".venv\Scripts\python.exe" -m pip install -r requirements.txt

echo.
echo Ambiente pronto.
pause
