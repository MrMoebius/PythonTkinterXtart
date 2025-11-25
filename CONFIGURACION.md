# Configuración del Cliente CRM XTART

## Modos de Operación

El cliente soporta dos modos de operación:

### Modo Real (Backend Java)

El cliente está configurado para conectarse al backend Java en:
```
http://localhost:8080/democrudapi
```

Para cambiar la URL del backend, edite el archivo `src/api/rest_client.py`:

```python
BASE_URL = "http://localhost:8080/democrudapi"
```

Cambie esta URL por la dirección de su servidor.

**Ejecución**:
```bash
python main.py
```

### Modo Demo (Datos Locales)

El modo demo permite usar la aplicación sin backend, leyendo datos desde archivos JSON locales en `demo_data/`.

**Ejecución**:
```bash
python main.py --demo
```

**Configuración de datos demo**:
- Los datos se encuentran en `demo_data/*.json`
- El archivo `demo_data/login.json` contiene los usuarios disponibles
- Los cambios no se guardan en modo demo (solo lectura)

## Estructura de Respuesta del Backend

El cliente espera que el backend devuelva respuestas en formato JSON con la siguiente estructura:

### Login
```json
{
  "token": "jwt_token_here",
  "id": 1,
  "rol": "EMPLEADO" | "CLIENTE",
  "username": "usuario"
}
```

### Lista de Entidades
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
  "id": 1,
  "campo1": "valor1",
  "campo2": "valor2"
}
```

### Errores
El cliente maneja códigos de estado HTTP:
- `200, 201`: Éxito
- `204`: Sin contenido (éxito en DELETE)
- Otros: Error

## Autenticación

### Modo Real

El cliente soporta autenticación basada en tokens JWT. El token se envía en el header:
```
Authorization: Bearer {token}
```

Si su backend usa otro método de autenticación, modifique el método `login()` en `src/api/rest_client.py`.

### Modo Demo

En modo demo, la autenticación es simplificada:
- No requiere contraseña real
- Los usuarios se definen en `demo_data/login.json`
- El formato es: `{"username": {"id": 1, "rol": "EMPLEADO", "token": "demo_token"}}`

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

Modifique `src/components/validated_entry.py` para añadir nuevos tipos de validación. Los tipos actuales incluyen:
- `email`: Validación de formato de email
- `phone`: Validación de teléfono
- `date`: Validación de fecha (YYYY-MM-DD)
- `number`: Validación numérica

### Modificar Columnas de Tablas

Edite las ventanas de entidades en `src/ui/entities/` para cambiar las columnas mostradas. Cada ventana define sus columnas en el método `__init__()`.

### Configurar Informes

Los informes se configuran en `src/ui/reports_window.py`:
- Añadir nuevos gráficos en `_load_reports()`
- Los tipos de gráficos disponibles están en `src/reports/chart_factory.py`
- Exportadores disponibles: PDF, PNG, Email

### Configurar Exportadores de Email

Para usar el exportador de email, configure los parámetros SMTP en `src/reports/exporters/email_exporter.py` o pase los parámetros al método `send_email()`:

```python
EmailExporter.send_email(
    sender_email="tu@email.com",
    sender_password="tu_password",
    receiver_email="destino@email.com",
    subject="Informe CRM",
    body="Adjunto encontrarás el informe.",
    attachment_path="ruta/al/archivo.pdf"
)
```

## Dependencias

Asegúrese de tener instaladas todas las dependencias:

```bash
pip install -r requirements.txt
```

**Nota**: `requirements.txt` puede no incluir todas las dependencias. Instale manualmente si es necesario:
- `customtkinter`
- `ttkbootstrap`

Para instalar todas las dependencias:
```bash
pip install customtkinter ttkbootstrap requests matplotlib Pillow
```

