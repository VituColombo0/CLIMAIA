@echo off
echo ===================================================
echo   Construindo CLIMAIA para Windows (PyInstaller)
echo ===================================================
echo.

if not exist venv_win (
    echo 1. Criando ambiente virtual isolado para Windows...
    python -m venv venv_win
)

echo 2. Instalando dependencias no ambiente virtual...
call venv_win\Scripts\activate.bat
pip install -r requirements.txt
pip install pyinstaller

echo.
echo 3. Gerando executavel (pode demorar alguns minutos)...
pyinstaller --clean CLIMAIA.spec

echo.
echo ===================================================
echo   Construcao concluida!
echo   O arquivo CLIMAIA.exe estara na pasta "dist".
echo ===================================================
pause
