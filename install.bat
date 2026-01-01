@echo off
REM SLAYER - Script de Instalacion para Windows
REM Este script instala todas las dependencias necesarias

echo ==========================================
echo   SLAYER - Instalacion Automatica
echo ==========================================
echo.

REM Verificar Python
echo [+] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [!] Python no encontrado. Por favor instala Python 3.8 o superior.
    echo.
    echo Descarga Python desde: https://www.python.org/downloads/
    echo.
    echo IMPORTANTE: Durante la instalacion, marca la opcion
    echo "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [+] Python %PYTHON_VERSION% encontrado
echo.

REM Verificar pip
echo [+] Verificando pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo [!] pip no encontrado. Instalando...
    python -m ensurepip --default-pip
    if errorlevel 1 (
        echo [!] No se pudo instalar pip. Por favor instala pip manualmente.
        pause
        exit /b 1
    )
)

echo [+] pip encontrado
echo.

REM Crear entorno virtual (opcional)
set /p CREATE_VENV="[?] Deseas crear un entorno virtual? (recomendado) [s/N]: "
if /i "%CREATE_VENV%"=="s" (
    echo [+] Creando entorno virtual...
    python -m venv venv
    
    echo [+] Activando entorno virtual...
    call venv\Scripts\activate.bat
    
    echo [+] Entorno virtual activado
    echo.
)

REM Actualizar pip
echo [+] Actualizando pip...
python -m pip install --upgrade pip

REM Instalar dependencias basicas
echo.
echo [+] Instalando dependencias basicas (slayer.py)...
pip install requests

echo [+] Dependencias basicas instaladas correctamente
echo.

REM Preguntar si instalar version enterprise
set /p INSTALL_ENTERPRISE="[?] Deseas instalar la version Enterprise completa? [s/N]: "
if /i "%INSTALL_ENTERPRISE%"=="s" (
    echo.
    echo [+] Instalando dependencias Enterprise...
    pip install -r requirements.txt
    echo [+] Dependencias Enterprise instaladas correctamente
)

echo.
echo ==========================================
echo   Instalacion Completada Exitosamente
echo ==========================================
echo.
echo Para usar la version basica (simple):
echo   python slayer.py
echo.

if /i "%INSTALL_ENTERPRISE%"=="s" (
    echo Para usar la version Enterprise (CLI):
    echo   python slayer_enterprise_cli.py request -u https://httpbin.org/get
    echo.
    echo Para pruebas de carga:
    echo   python slayer_enterprise_cli.py load-test -u https://httpbin.org/get -n 100
    echo.
)

echo Para ver la guia completa de uso:
echo   type GUIA_USO.md
echo.
echo Para ejecutar pruebas:
echo   pytest tests\ -v
echo.

if /i "%CREATE_VENV%"=="s" (
    echo NOTA: Has creado un entorno virtual.
    echo       Para usarlo en el futuro, ejecuta:
    echo       venv\Scripts\activate.bat
    echo.
)

echo Disfruta de SLAYER!
echo.
pause
