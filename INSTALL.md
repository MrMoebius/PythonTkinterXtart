# Guía de Instalación - CRM XTART

Esta guía te ayudará a instalar todas las dependencias necesarias para ejecutar el cliente de escritorio CRM XTART.

## 📋 Requisitos Previos

- **Python 3.8 o superior** - [Descargar Python](https://www.python.org/downloads/)
- **Sistema Operativo**: Windows 10/11
- **Backend Java** ejecutándose en `http://localhost:8080/crudxtart`

## 🚀 Instalación Automática

### Opción 1: Script PowerShell (Recomendado)

1. Abre PowerShell como administrador (opcional, pero recomendado)
2. Navega a la carpeta del proyecto:
   ```powershell
   cd ruta\a\tu\proyecto\tkinter
   ```
3. Ejecuta el script de instalación:
   ```powershell
   .\install.ps1
   ```

Si obtienes un error de política de ejecución, ejecuta primero:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Opción 2: Script Batch

1. Abre el Explorador de Archivos
2. Navega a la carpeta `tkinter`
3. Haz doble clic en `install.bat`
4. Sigue las instrucciones en pantalla

## 🔧 Instalación Manual

Si prefieres instalar manualmente:

1. **Verificar Python**:
   ```bash
   python --version
   ```
   Debe mostrar Python 3.8 o superior.

2. **Actualizar pip**:
   ```bash
   python -m pip install --upgrade pip
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

## ✅ Verificación

Para verificar que todo está instalado correctamente:

```bash
python -c "import customtkinter; import ttkbootstrap; import requests; import matplotlib; import PIL; print('✓ Todas las dependencias están instaladas')"
```

## 📦 Dependencias Instaladas

El script instalará automáticamente:

- **requests** (>=2.31.0) - Cliente HTTP para comunicación con la API REST
- **matplotlib** (>=3.7.0) - Generación de gráficos e informes
- **Pillow** (>=10.0.0) - Procesamiento de imágenes
- **customtkinter** (>=5.2.0) - Interfaz gráfica moderna
- **ttkbootstrap** (>=1.10.0) - Temas y estilos adicionales

## 🎯 Ejecutar la Aplicación

Una vez completada la instalación:

```bash
python main.py
```

## ⚠️ Solución de Problemas

### Error: "Python no está en el PATH"

1. Reinstala Python desde [python.org](https://www.python.org/)
2. Durante la instalación, marca la opción **"Add Python to PATH"**
3. Reinicia la terminal/PowerShell después de la instalación

### Error: "pip no está disponible"

Ejecuta:
```bash
python -m ensurepip --upgrade
```

### Error: "No se puede instalar customtkinter"

Asegúrate de tener Python 3.8 o superior:
```bash
python --version
```

Si el problema persiste, intenta:
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Error de permisos en Windows

Ejecuta PowerShell o CMD como administrador, o usa:
```bash
pip install --user -r requirements.txt
```

## 📝 Notas Adicionales

- El script verifica automáticamente la versión de Python
- Si alguna dependencia falla, el script mostrará un mensaje de error específico
- Todas las dependencias se instalan en el entorno de Python actual
- Si usas un entorno virtual, actívalo antes de ejecutar el script

## 🆘 Soporte

Si encuentras problemas durante la instalación:

1. Verifica que Python 3.8+ está instalado correctamente
2. Asegúrate de estar en la carpeta correcta (`tkinter/`)
3. Revisa los mensajes de error específicos
4. Intenta la instalación manual como alternativa

