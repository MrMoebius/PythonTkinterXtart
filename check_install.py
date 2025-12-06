#!/usr/bin/env python3
"""
Script de verificación de instalación - CRM XTART
Verifica que Python y todas las dependencias estén correctamente instaladas
"""

import sys
import importlib

def check_python_version():
    """Verifica que la versión de Python sea 3.8 o superior"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Error: Se requiere Python 3.8 o superior")
        print(f"   Versión actual: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} - OK")
    return True

def check_dependency(module_name, package_name=None, min_version=None):
    """
    Verifica que una dependencia esté instalada
    
    Args:
        module_name: Nombre del módulo a importar
        package_name: Nombre del paquete (si es diferente del módulo)
        min_version: Versión mínima requerida (opcional)
    """
    if package_name is None:
        package_name = module_name
    
    try:
        module = importlib.import_module(module_name)
        
        # Intentar obtener la versión
        version = None
        if hasattr(module, '__version__'):
            version = module.__version__
        elif hasattr(module, 'version'):
            version = module.version
        
        if version:
            print(f"✓ {package_name} {version} - OK")
        else:
            print(f"✓ {package_name} - OK (versión no disponible)")
        
        return True
    except ImportError:
        print(f"❌ {package_name} - NO INSTALADO")
        print(f"   Ejecuta: pip install {package_name}")
        return False
    except Exception as e:
        print(f"⚠ {package_name} - Error al verificar: {e}")
        return False

def main():
    """Función principal de verificación"""
    print("=" * 50)
    print("  CRM XTART - Verificación de Instalación")
    print("=" * 50)
    print()
    
    # Verificar Python
    print("[1/7] Verificando Python...")
    if not check_python_version():
        sys.exit(1)
    print()
    
    # Verificar dependencias
    dependencies = [
        ("requests", "requests", "2.31.0"),
        ("matplotlib", "matplotlib", "3.7.0"),
        ("PIL", "Pillow", "10.0.0"),
        ("customtkinter", "customtkinter", "5.2.0"),
        ("ttkbootstrap", "ttkbootstrap", "1.10.0"),
        ("tkinterweb", "tkinterweb", "3.21.0"),
    ]
    
    all_ok = True
    for i, (module, package, version) in enumerate(dependencies, start=2):
        print(f"[{i}/7] Verificando {package}...")
        if not check_dependency(module, package, version):
            all_ok = False
        print()
    
    # Resultado final
    print("=" * 50)
    if all_ok:
        print("✓ Todas las dependencias están instaladas correctamente")
        print()
        print("Para ejecutar la aplicación:")
        print("  python main.py")
        print()
        print("Nota: Asegúrate de que el backend Java esté ejecutándose")
        print("      en http://localhost:8080/crudxtart")
        sys.exit(0)
    else:
        print("❌ Faltan algunas dependencias")
        print()
        print("Para instalar todas las dependencias, ejecuta:")
        print("  pip install -r requirements.txt")
        print()
        print("O ejecuta el script de instalación:")
        print("  .\\install.ps1  (PowerShell)")
        print("  install.bat    (CMD)")
        sys.exit(1)

if __name__ == "__main__":
    main()

