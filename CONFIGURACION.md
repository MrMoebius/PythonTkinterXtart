# Configuración del Cliente CRM XTART

## Configuración del Backend

El cliente está configurado para conectarse al backend Java en:
```
http://localhost:8080/crudxtart
```

### Cambiar la URL del Backend

Para cambiar la URL del backend, puede hacerlo de dos formas:

**Opción 1: Variable de entorno (recomendado)**
```bash
export API_BASE_URL="http://localhost:8080/crudxtart"
python main.py
```

**Opción 2: Editar el archivo de configuración**

Edite el archivo `src/utils/settings.py`:

```python
API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8080/crudxtart")
```

Cambie el valor por defecto por la dirección de su servidor.

**Ejecución**:
```bash
python main.py
```

## Estructura de Respuesta del Backend

El cliente espera que el backend devuelva respuestas en formato JSON con la siguiente estructura:

### Login
El backend devuelve una respuesta con el siguiente formato:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "rol": "ADMIN" | "EMPLEADO" | "CLIENTE",
    "tipo": "empleado" | "cliente",
    "nombre": "Nombre del usuario",
    "email": "usuario@email.com",
    "token": "jwt_token_here"  // Opcional
  }
}
```

**Nota**: El cliente también soporta el formato antiguo `{"success": true, "dataObj": {...}}` para compatibilidad.

### Lista de Entidades
El backend puede devolver listas en dos formatos:

**Formato estándar (recomendado)**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "campo1": "valor1",
      "campo2": "valor2"
    },
    ...
  ]
}
```

**Formato directo (también soportado)**:
```json
[
  {
    "id": 1,
    "campo1": "valor1",
    "campo2": "valor2"
  },
  ...
]
```

### Entidad Individual
```json
{
  "success": true,
  "data": {
    "id": 1,
    "campo1": "valor1",
    "campo2": "valor2"
  }
}
```

**Nota**: El cliente también soporta el formato antiguo `{"success": true, "dataObj": {...}}` para compatibilidad. Si `data` es `null`, se convierte automáticamente a lista vacía `[]`.

### Errores
El cliente maneja códigos de estado HTTP:
- `200, 201`: Éxito
- `204`: Sin contenido (éxito en DELETE)
- Otros: Error

## Autenticación

El cliente soporta autenticación mediante sesiones HTTP. El backend Java utiliza cookies (JSESSIONID) para mantener la sesión.

El login se realiza mediante:
- Endpoint: `POST /auth/login`
- Payload: `{"email": "usuario", "password": "contraseña"}`
- Respuesta: `{"success": true, "data": {"id": 1, "rol": "ADMIN", "tipo": "empleado", ...}}`

Si el backend devuelve un token JWT, este se almacena y se envía en el header:
```
Authorization: Bearer {token}
```

Si su backend usa otro método de autenticación, modifique el método `login()` en `src/api/rest_client.py`.

## Campos de Entidades

Asegúrese de que los campos de las entidades coincidan con los esperados por el cliente:

### Clientes
- id, nombre, apellidos, email, telefono, direccion

### Empleados
- id, nombre, apellidos, email, telefono, rol_empleado

### Productos
- id, nombre, descripcion, precio, stock

### Presupuestos
- id, cliente_id, empleado_id, fecha, total, estado

### Facturas
- id, cliente_id, empleado_id, fecha, total, estado

### Pagos
- id, factura_id, cliente_id, fecha, importe, metodo_pago, estado

## Configuración de la Interfaz

### CustomTkinter

La aplicación usa CustomTkinter para la interfaz. La configuración se encuentra en `src/ui/main_window.py`:

```python
ctk.set_appearance_mode("dark")  # "dark" o "light"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"
```

### ttkbootstrap

El tema de la ventana principal se configura en `main.py`:

```python
root = tb.Window(themename="cosmo")  # Cambiar por otro tema disponible
```

Temas disponibles: `cosmo`, `flatly`, `journal`, `litera`, `lumen`, `minty`, `pulse`, `sandstone`, `united`, `yeti`, etc.

### Personalización de Estilos

Edite `src/utils/styles.py` para personalizar colores y estilos adicionales.

## Personalización de Funcionalidades

### Añadir Validaciones

Modifique `src/utils/validators.py` para añadir nuevas funciones de validación. Los tipos actuales incluyen:
- `validate_email()`: Validación de formato de email
- `validate_phone()`: Validación de teléfono
- `validate_date()`: Validación de fecha (YYYY-MM-DD)
- `validate_number()`: Validación numérica
- `validate_required()`: Validación de campos obligatorios

Y use en `src/widgets/validated_entry.py` añadiendo el caso en `validate_input()`.

### Modificar Columnas de Tablas

Edite las ventanas de entidades en `src/ui/entities/` para cambiar las columnas mostradas. Cada ventana define sus columnas en el método `__init__()`.

### Configurar Informes

Los informes se configuran en `src/ui/reports/report_definitions.py`:
- Añadir nuevas definiciones de informes en `REPORT_CONFIGS`
- Los tipos de gráficos disponibles están en `src/reports/chart_factory.py`
- Los métodos de carga de datos están en `src/reports/report_loader.py`
- Exportadores disponibles: PDF, PNG

### Configurar Exportadores

Los exportadores disponibles son:

**PDF**: Exporta informes y documentos a formato PDF usando matplotlib
**PNG**: Exporta informes y documentos a formato PNG usando matplotlib

Los exportadores se encuentran en:
- `src/reports/exporters/pdf_exporter.py` - Exportación a PDF
- `src/reports/exporters/image_exporter.py` - Exportación a PNG
- `src/reports/exporters/report_exporter.py` - Exportador unificado para informes
- `src/utils/export_helpers.py` - Helpers para exportación de documentos (presupuestos, facturas, pagos)

## Dependencias

Asegúrese de tener instaladas todas las dependencias:

```bash
pip install -r requirements.txt
```

**Dependencias principales**:
- `customtkinter>=5.2.0` - Interfaz gráfica moderna
- `ttkbootstrap>=1.10.0` - Temas y estilos adicionales
- `requests>=2.31.0` - Cliente HTTP para API REST
- `matplotlib>=3.7.0` - Generación de gráficos
- `Pillow>=10.0.0` - Procesamiento de imágenes

Para instalar todas las dependencias:
```bash
pip install -r requirements.txt
```

