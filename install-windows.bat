@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo.
echo === PaperQA2 GUI · instalacao Windows ===
echo Pasta: %CD%
echo.

echo %CD% | findstr /I /C:"8662-B449" >nul
if %ERRORLEVEL%==0 (
  echo ERRO: parece o pendrive exFAT.
  echo Copie a pasta para o SSD, ex.: C:\paperqa-gui-local
  echo e rode este .bat LA.
  exit /b 1
)

where py >nul 2>&1
if errorlevel 1 (
  echo ERRO: Python nao esta no PATH.
  echo Instale Python 3.12 e marque "Add python.exe to PATH".
  exit /b 1
)

py -3.12 --version
if errorlevel 1 (
  echo ERRO: precisa do Python 3.12 ^(py -3.12^).
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Criando .venv ...
  py -3.12 -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
echo Instalando PyTorch CPU ...
pip install torch --index-url https://download.pytorch.org/whl/cpu
echo Instalando PaperQA + Streamlit ...
pip install -c constraints-cpu.txt --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt

if not exist ".env" (
  copy /Y .env.example .env >nul
  echo Copiado .env.example -^> .env
)

echo.
echo Pronto. Agora:
echo   1. Instale o Ollama e rode:  ollama pull qwen3.5:4b
echo   2. No .env use OLLAMA_MODEL=qwen3.5:4b
echo   3. Rode:  .venv\Scripts\activate
echo             streamlit run app.py
echo.
endlocal
