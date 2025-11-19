# Configuración del Cliente CRM XTART

## Configuración del Backend

El cliente está configurado para conectarse al backend Java en:
```
http://localhost:8080/democrudapi
```

Para cambiar la URL del backend, edite el archivo `src/api/rest_client.py`:

```python
BASE_URL = "http://localhost:8080/democrudapi"
```

Cambie esta URL por la dirección de su servidor.

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

El cliente soporta autenticación basada en tokens. El token se envía en el header:
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

## Personalización

### Cambiar Tema
Edite `src/utils/styles.py` para personalizar colores y estilos.

### Añadir Validaciones
Modifique `src/components/validated_entry.py` para añadir nuevos tipos de validación.

### Modificar Columnas de Tablas
Edite las ventanas de entidades en `src/ui/entities/` para cambiar las columnas mostradas.

