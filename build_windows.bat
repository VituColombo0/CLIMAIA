@echo off
echo ===================================================
echo   Construindo CLIMAIA para Windows (PyInstaller)
echo ===================================================
echo.

if not exist venv_win (
    echo 1. Criando ambiente virtual isolado para Windows...
    python -m venv venv_win
    if errorlevel 1 (
        echo ERRO: Nao foi possivel criar o ambiente virtual.
        echo Verifique se o Python esta instalado e no PATH.
        pause
        exit /b 1
    )
)

call venv_win\Scripts\activate.bat

echo 2. Instalando dependencias principais no ambiente virtual...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERRO: Falha ao instalar dependencias principais.
    pause
    exit /b 1
)

echo.
echo Tentando instalar TensorFlow (opcional)...
pip install tensorflow>=2.15.0 2>nul
if errorlevel 1 (
    echo.
    echo ===================================================
    echo   AVISO: TensorFlow nao foi instalado.
    echo   Sua versao do Python pode nao ser compativel.
    echo   (TensorFlow suporta Python 3.9 a 3.12)
    echo.
    echo   O executavel funcionara com XGBoost.
    echo   Apenas o modelo LSTM estara indisponivel.
    echo ===================================================
    echo.
) else (
    echo Verificando se TensorFlow funciona corretamente...
    python -c "import tensorflow" 2>nul
    if errorlevel 1 (
        echo.
        echo ===================================================
        echo   AVISO: TensorFlow foi instalado mas NAO funciona.
        echo   Possivel causa: CPU nao suporta AVX/AVX2 ou
        echo   Visual C++ Redistributable esta ausente/desatualizado.
        echo.
        echo   Removendo TensorFlow para evitar erros no build...
        echo ===================================================
        echo.
        pip uninstall tensorflow -y 2>nul
        pip uninstall keras -y 2>nul
        echo   O executavel funcionara com XGBoost.
        echo   Apenas o modelo LSTM estara indisponivel.
    ) else (
        echo   TensorFlow funcionando corretamente!
    )
)

echo Instalando PyInstaller...
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
