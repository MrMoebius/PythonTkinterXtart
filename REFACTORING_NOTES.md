# Notas de Refactorización - CRM XTART

## ✅ Completado

### 1. Estructura de Carpetas
- ✅ Creada carpeta `src/models/` con modelos de datos (dataclasses)
- ✅ Creada carpeta `src/services/` con servicios de negocio
- ✅ Creada carpeta `src/widgets/` con widgets reutilizables
- ✅ Creada carpeta `src/ui/views/` para nuevas vistas

### 2. Modelos de Datos
- ✅ `Cliente` - Modelo con from_dict/to_dict
- ✅ `Empleado` - Modelo con from_dict/to_dict
- ✅ `Producto` - Modelo con from_dict/to_dict
- ✅ `Factura` - Modelo con from_dict/to_dict
- ✅ `FacturaDetalle` - Modelo con from_dict/to_dict

### 3. API REST
- ✅ `rest_client.py` - Cliente REST profesional con:
  - Manejo de errores robusto
  - Timeouts configurables
  - Logging
  - Autenticación con tokens
- ✅ `endpoints.py` - Mapeo centralizado de endpoints del backend Java

### 4. Servicios
- ✅ `AuthService` - Autenticación
- ✅ `ClienteService` - CRUD de clientes
- ✅ `EmpleadoService` - CRUD de empleados
- ✅ `ProductoService` - CRUD de productos
- ✅ `FacturaService` - CRUD de facturas, presupuestos, pagos

### 5. Widgets
- ✅ Movidos a `src/widgets/`:
  - `data_table.py`
  - `filter_panel.py`
  - `validated_entry.py` (actualizado para usar validators de utils)

### 6. Utilidades
- ✅ `settings.py` - Configuración centralizada
- ✅ `exceptions.py` - Excepciones personalizadas
- ✅ `validators.py` - Validadores reutilizables

### 7. Eliminación de Demo
- ✅ Eliminado `demo_client.py`
- ✅ Eliminada carpeta `demo_data/`
- ✅ Actualizado `main.py` para eliminar modo demo
- ✅ Actualizadas referencias en código

### 8. Actualizaciones de Imports
- ✅ Actualizados imports en `base_crud_window.py`
- ✅ Actualizados imports en todas las ventanas de entidades

## 🔄 Pendiente / Mejoras Futuras

### 1. Migración Completa a Servicios
Las ventanas de entidades (`src/ui/entities/*`) aún usan el API directamente. 
Para una migración completa:

**Opción A: Refactorizar BaseCRUDWindow**
- Modificar `BaseCRUDWindow` para aceptar servicios en lugar de API
- Actualizar todas las ventanas de entidades para usar servicios

**Opción B: Crear Nuevas Vistas**
- Completar las vistas en `src/ui/views/` (ya se creó `ClientesView` como ejemplo)
- Migrar gradualmente desde `entities/` a `views/`

### 2. Vistas Completas
- ⚠️ Solo `ClientesView` está creada como ejemplo
- Pendientes: `EmpleadosView`, `ProductosView`, `FacturasView`, `PagosView`, `PresupuestosView`

### 3. MainWindow y Dashboard
- ⚠️ `main_window.py` aún usa API directamente
- ⚠️ `dashboard.py` aún usa API directamente
- **Recomendación**: Inicializar servicios en `MainWindow` y pasarlos a las vistas

### 4. Login Window
- ⚠️ `login_window.py` usa API directamente (funcional, pero idealmente usaría `AuthService`)

## 📁 Nueva Estructura

```
src/
├── api/
│   ├── rest_client.py      ✅ Cliente REST profesional
│   └── endpoints.py        ✅ Mapeo de endpoints
├── models/                 ✅ Modelos de datos (dataclasses)
│   ├── cliente.py
│   ├── empleado.py
│   ├── producto.py
│   ├── factura.py
│   └── factura_detalle.py
├── services/               ✅ Lógica de negocio
│   ├── auth_service.py
│   ├── cliente_service.py
│   ├── empleado_service.py
│   ├── producto_service.py
│   └── factura_service.py
├── widgets/                ✅ Widgets reutilizables
│   ├── data_table.py
│   ├── filter_panel.py
│   └── validated_entry.py
├── ui/
│   ├── views/              ⚠️ Nuevas vistas (parcial)
│   │   ├── clientes_view.py
│   │   └── ...
│   ├── entities/           ⚠️ Ventanas actuales (a migrar)
│   │   ├── base_crud_window.py
│   │   ├── clientes_window.py
│   │   └── ...
│   ├── login_window.py
│   ├── main_window.py
│   └── dashboard.py
└── utils/
    ├── settings.py         ✅ Configuración
    ├── exceptions.py       ✅ Excepciones
    ├── validators.py       ✅ Validadores
    └── styles.py
```

## 🚀 Cómo Usar la Nueva Estructura

### Inicializar Servicios

```python
from src.api.rest_client import RESTClient
from src.services import (
    AuthService,
    ClienteService,
    EmpleadoService,
    ProductoService,
    FacturaService
)

# Crear cliente REST
rest_client = RESTClient(base_url="http://localhost:8080/democrudapi")

# Crear servicios
auth_service = AuthService(rest_client)
cliente_service = ClienteService(rest_client)
empleado_service = EmpleadoService(rest_client)
producto_service = ProductoService(rest_client)
factura_service = FacturaService(rest_client)
```

### Usar Modelos

```python
from src.models.cliente import Cliente

# Desde JSON del backend
cliente = Cliente.from_dict({"id": 1, "nombre": "Juan", ...})

# A JSON para enviar al backend
data = cliente.to_dict()
```

### Usar Servicios

```python
# Obtener todos los clientes
result = cliente_service.get_all()
if result["success"]:
    clientes = result["data"]  # Lista de objetos Cliente

# Crear un cliente
nuevo_cliente = Cliente(nombre="Juan", apellidos="Pérez", email="juan@example.com")
result = cliente_service.create(nuevo_cliente)
```

## 📝 Notas Importantes

1. **Backward Compatibility**: Las ventanas actuales en `entities/` siguen funcionando porque aún usan el API directamente. Esto permite una migración gradual.

2. **Configuración**: La URL del backend se configura en `src/utils/settings.py` o mediante variable de entorno `API_BASE_URL`.

3. **Validación**: Los validadores están centralizados en `src/utils/validators.py` y son usados por `ValidatedEntry`.

4. **Logging**: El cliente REST incluye logging automático para debugging.

## 🔧 Próximos Pasos Recomendados

1. **Completar Vistas**: Crear todas las vistas en `src/ui/views/` siguiendo el patrón de `ClientesView`
2. **Actualizar MainWindow**: Inicializar servicios y pasarlos a las vistas
3. **Migrar Dashboard**: Usar servicios en lugar de API directa
4. **Testing**: Probar la integración con el backend Java real
5. **Documentación**: Actualizar README con la nueva estructura

