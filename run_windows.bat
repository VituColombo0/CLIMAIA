@echo off
echo ===================================================
echo   Iniciando CLIMAIA (Modo de Desenvolvimento Windows)
echo ===================================================
echo.

echo Verificando ambiente virtual...
if not exist venv_win (
    echo Criando novo ambiente virtual "venv_win"...
    python -m venv venv_win
)

echo Ativando ambiente virtual...
call venv_win\Scripts\activate.bat

echo Instalando/Atualizando dependencias (isso pode demorar na primeira vez)...
pip install -r requirements.txt --quiet

echo.
echo Iniciando o CLIMAIA...
python main.py

pause
