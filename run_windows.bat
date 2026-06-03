@echo off
echo ===================================================
echo   Iniciando CLIMAIA (Modo de Desenvolvimento Windows)
echo ===================================================
echo.

echo Verificando ambiente virtual...
if not exist venv_win (
    echo Criando novo ambiente virtual "venv_win"...
    python -m venv venv_win
    if errorlevel 1 (
        echo.
        echo ERRO: Nao foi possivel criar o ambiente virtual.
        echo Verifique se o Python esta instalado e no PATH.
        pause
        exit /b 1
    )
)

echo Ativando ambiente virtual...
call venv_win\Scripts\activate.bat

echo Instalando/Atualizando dependencias principais...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo.
    echo ERRO: Falha ao instalar dependencias principais.
    pause
    exit /b 1
)

echo Tentando instalar TensorFlow (opcional)...
pip install tensorflow>=2.15.0 --quiet 2>nul
if errorlevel 1 (
    echo.
    echo ===================================================
    echo   AVISO: TensorFlow nao foi instalado.
    echo   Sua versao do Python pode nao ser compativel.
    echo   (TensorFlow suporta Python 3.9 a 3.12)
    echo.
    echo   O CLIMAIA funcionara normalmente usando XGBoost.
    echo   Apenas o modelo LSTM estara indisponivel.
    echo ===================================================
    echo.
)

echo.
echo Iniciando o CLIMAIA...
python main.py

pause
