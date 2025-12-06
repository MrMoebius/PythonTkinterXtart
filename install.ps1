# Script de instalación para CRM XTART - Cliente de Escritorio
# PowerShell Script para Windows

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CRM XTART - Instalador de Dependencias" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Función para verificar si un comando existe
function Test-Command {
    param($command)
    $null = Get-Command $command -ErrorAction SilentlyContinue
    return $?
}

# 1. Verificar Python
Write-Host "[1/3] Verificando Python..." -ForegroundColor Yellow

if (Test-Command python) {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Python encontrado: $pythonVersion" -ForegroundColor Green
    
    # Verificar versión mínima (3.8)
    $versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)"
    if ($versionMatch) {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
            Write-Host "  ✗ Error: Se requiere Python 3.8 o superior" -ForegroundColor Red
            Write-Host "    Versión actual: $pythonVersion" -ForegroundColor Red
            exit 1
        }
    }
} else {
    Write-Host "  ✗ Error: Python no está instalado o no está en el PATH" -ForegroundColor Red
    Write-Host "    Por favor, instala Python 3.8 o superior desde https://www.python.org/" -ForegroundColor Yellow
    Write-Host "    Asegúrate de marcar 'Add Python to PATH' durante la instalación" -ForegroundColor Yellow
    exit 1
}

# 2. Verificar pip
Write-Host ""
Write-Host "[2/3] Verificando pip..." -ForegroundColor Yellow

if (Test-Command pip) {
    $pipVersion = pip --version 2>&1
    Write-Host "  ✓ pip encontrado: $pipVersion" -ForegroundColor Green
} else {
    Write-Host "  ✗ Error: pip no está disponible" -ForegroundColor Red
    Write-Host "    Intentando instalar pip..." -ForegroundColor Yellow
    python -m ensurepip --upgrade
    if (-not $?) {
        Write-Host "    ✗ No se pudo instalar pip automáticamente" -ForegroundColor Red
        exit 1
    }
    Write-Host "    ✓ pip instalado correctamente" -ForegroundColor Green
}

# 3. Verificar requirements.txt
Write-Host ""
Write-Host "[3/3] Verificando requirements.txt..." -ForegroundColor Yellow

$requirementsPath = Join-Path $PSScriptRoot "requirements.txt"
if (Test-Path $requirementsPath) {
    Write-Host "  ✓ requirements.txt encontrado" -ForegroundColor Green
} else {
    Write-Host "  ✗ Error: No se encontró requirements.txt" -ForegroundColor Red
    Write-Host "    Ruta esperada: $requirementsPath" -ForegroundColor Yellow
    exit 1
}

# 4. Actualizar pip
Write-Host ""
Write-Host "[4/4] Actualizando pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
if ($?) {
    Write-Host "  ✓ pip actualizado" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Advertencia: No se pudo actualizar pip (continuando...)" -ForegroundColor Yellow
}

# 5. Instalar dependencias
Write-Host ""
Write-Host "Instalando dependencias desde requirements.txt..." -ForegroundColor Yellow
Write-Host ""

python -m pip install -r $requirementsPath

if ($?) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ✓ Instalación completada exitosamente" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Dependencias instaladas:" -ForegroundColor Cyan
    Write-Host "  - requests (cliente HTTP)" -ForegroundColor White
    Write-Host "  - matplotlib (gráficos)" -ForegroundColor White
    Write-Host "  - Pillow (procesamiento de imágenes)" -ForegroundColor White
    Write-Host "  - customtkinter (interfaz gráfica)" -ForegroundColor White
    Write-Host "  - ttkbootstrap (temas adicionales)" -ForegroundColor White
    Write-Host "  - tkinterweb (visor HTML)" -ForegroundColor White
    Write-Host ""
    Write-Host "Para ejecutar la aplicación:" -ForegroundColor Cyan
    Write-Host "  python main.py" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Nota: Asegúrate de que el backend Java esté ejecutándose" -ForegroundColor Yellow
    Write-Host "      en http://localhost:8080/crudxtart" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  ✗ Error durante la instalación" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor, revisa los mensajes de error anteriores." -ForegroundColor Yellow
    Write-Host "Intenta ejecutar manualmente:" -ForegroundColor Yellow
    Write-Host "  pip install -r requirements.txt" -ForegroundColor White
    Write-Host ""
    exit 1
}

