@echo off
cd /d "%~dp0"

set "PYTHON_CMD="

where py >nul 2>nul
if not errorlevel 1 (
    set "PYTHON_CMD=py"
)

if "%PYTHON_CMD%"=="" (
    where python >nul 2>nul
    if not errorlevel 1 (
        set "PYTHON_CMD=python"
    )
)

if "%PYTHON_CMD%"=="" (
    echo Python nao encontrado no PATH.
    echo Instale o Python 3 ou adicione o Python/py ao PATH do Windows.
    pause
    exit /b 1
)

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import sys" >nul 2>nul
    if errorlevel 1 (
        echo Ambiente virtual existente esta invalido. Recriando .venv...
        rmdir /s /q ".venv"
    )
)

if not exist ".venv\Scripts\streamlit.exe" (
    echo Ambiente virtual nao encontrado. Criando .venv...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 (
        echo Falha ao criar o ambiente virtual. Verifique se o Python esta instalado.
        pause
        exit /b 1
    )

    echo Instalando dependencias do projeto...
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Falha ao instalar as dependencias. Verifique sua conexao com a internet.
        pause
        exit /b 1
    )
)

".venv\Scripts\streamlit.exe" run app.py
