@echo off
echo ===================================================
echo   Construindo CLIMAIA para Windows (PyInstaller)
echo ===================================================
echo.

echo 1. Instalando dependencias...
pip install -r requirements.txt
pip install pyinstaller

echo.
echo 2. Gerando executavel...
pyinstaller --clean CLIMAIA.spec

echo.
echo ===================================================
echo   Construcao concluida!
echo   O arquivo CLIMAIA.exe estara na pasta "dist".
echo ===================================================
pause
