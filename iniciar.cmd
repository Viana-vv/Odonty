@echo off
setlocal
rem Configuracao publica somente para este processo, sem credenciais.
if not defined XANO_API_BASE_URL set "XANO_API_BASE_URL=https://x8ki-letl-twmt.n7.xano.io/api:sorriso-acesso:v1"
if not defined XANO_HTTP_TIMEOUT_SECONDS set "XANO_HTTP_TIMEOUT_SECONDS=10"

set "pythonLocal=%~dp0.venv-win\Scripts\python.exe"
if exist "%pythonLocal%" (
    "%pythonLocal%" -m streamlit --version >nul 2>&1
    if not errorlevel 1 goto executar
)
set "pythonLocal=%~dp0.venv\Scripts\python.exe"
if exist "%pythonLocal%" (
    "%pythonLocal%" -m streamlit --version >nul 2>&1
    if not errorlevel 1 goto executar
)
echo Crie um ambiente virtual e instale requirements.txt conforme o README.
exit /b 1

:executar
pushd "%~dp0"
"%pythonLocal%" -m streamlit run app.py
set "codigoSaida=%errorlevel%"
popd
exit /b %codigoSaida%
