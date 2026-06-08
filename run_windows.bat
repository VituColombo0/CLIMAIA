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
    echo   AVISO: TensorFlow nao foi instalado.
    echo   Funcionalidade LSTM indisponivel.
    echo   (TensorFlow suporta Python 3.9 a 3.12)
    echo.
) else (
    echo Verificando se TensorFlow funciona...
    python -c "import tensorflow" 2>nul
    if errorlevel 1 (
        echo   AVISO: TensorFlow instalado mas NAO funciona.
        echo   Removendo para evitar erros...
        pip uninstall tensorflow keras -y --quiet 2>nul
        echo   Funcionalidade LSTM indisponivel.
    ) else (
        echo   TensorFlow OK!
    )
)

echo.
echo Iniciando o CLIMAIA...
python main.py

pause
