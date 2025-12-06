@echo off
REM Script de instalación para CRM XTART - Cliente de Escritorio
REM Script Batch para Windows

echo ========================================
echo   CRM XTART - Instalador de Dependencias
echo ========================================
echo.

REM 1. Verificar Python
echo [1/3] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   [ERROR] Python no esta instalado o no esta en el PATH
    echo   Por favor, instala Python 3.8 o superior desde https://www.python.org/
    echo   Asegurate de marcar 'Add Python to PATH' durante la instalacion
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo   [OK] Python encontrado: %PYTHON_VERSION%

REM 2. Verificar pip
echo.
echo [2/3] Verificando pip...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   [ADVERTENCIA] pip no esta disponible, intentando instalar...
    python -m ensurepip --upgrade
    if %errorlevel% neq 0 (
        echo   [ERROR] No se pudo instalar pip automaticamente
        pause
        exit /b 1
    )
    echo   [OK] pip instalado correctamente
) else (
    for /f "tokens=1,2" %%i in ('python -m pip --version 2^>^&1') do set PIP_VERSION=%%i %%j
    echo   [OK] pip encontrado: %PIP_VERSION%
)

REM 3. Verificar requirements.txt
echo.
echo [3/3] Verificando requirements.txt...
if not exist "requirements.txt" (
    echo   [ERROR] No se encontro requirements.txt
    echo   Asegurate de ejecutar este script desde la carpeta tkinter/
    pause
    exit /b 1
)
echo   [OK] requirements.txt encontrado

REM 4. Actualizar pip
echo.
echo [4/4] Actualizando pip...
python -m pip install --upgrade pip --quiet
if %errorlevel% equ 0 (
    echo   [OK] pip actualizado
) else (
    echo   [ADVERTENCIA] No se pudo actualizar pip (continuando...)
)

REM 5. Instalar dependencias
echo.
echo Instalando dependencias desde requirements.txt...
echo.

python -m pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   [OK] Instalacion completada exitosamente
    echo ========================================
    echo.
    echo Dependencias instaladas:
    echo   - requests (cliente HTTP)
    echo   - matplotlib (graficos)
    echo   - Pillow (procesamiento de imagenes)
    echo   - customtkinter (interfaz grafica)
    echo   - ttkbootstrap (temas adicionales)
    echo.
    echo Para ejecutar la aplicacion:
    echo   python main.py
    echo.
    echo Nota: Asegurate de que el backend Java este ejecutandose
    echo       en http://localhost:8080/crudxtart
    echo.
) else (
    echo.
    echo ========================================
    echo   [ERROR] Error durante la instalacion
    echo ========================================
    echo.
    echo Por favor, revisa los mensajes de error anteriores.
    echo Intenta ejecutar manualmente:
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

pause

