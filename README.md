# CRM XTART - Cliente de Escritorio

Cliente de escritorio en Python con Tkinter para gestionar el sistema CRM XTART. Esta aplicación proporciona una interfaz gráfica completa para interactuar con el backend Java REST API.

## 📋 Tabla de Contenidos

- [Características](#características)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Uso](#uso)
- [Roles y Permisos](#roles-y-permisos)
- [Endpoints Consumidos](#endpoints-consumidos)
- [Flujos de Usuario](#flujos-de-usuario)
- [Ampliación del Sistema](#ampliación-del-sistema)
- [Manual de Usuario](#manual-de-usuario)

## ✨ Características

- **Interfaz Moderna**: Tema claro y fácilmente extensible a temas oscuros
- **CRUD Completo**: Gestión completa de todas las entidades del sistema
- **Sistema de Roles**: Diferentes interfaces según el tipo de usuario (Empleado/Cliente)
- **Validación en Tiempo Real**: Validación visual de campos (email, teléfono, fecha, etc.)
- **Filtros Avanzados**: Búsqueda y filtrado de registros
- **Paginación**: Navegación eficiente en grandes volúmenes de datos
- **Informes Gráficos**: Visualización de datos con gráficos interactivos
- **Ayuda Contextual**: Sistema de ayuda integrado
- **Navegación por Teclado**: Atajos de teclado para operaciones rápidas

## 🔧 Requisitos

- Python 3.8 o superior
- Backend Java REST API ejecutándose en `http://localhost:8080/democrudapi`
- Dependencias Python (ver `requirements.txt`)

## 📦 Instalación

1. **Clonar o descargar el proyecto**

2. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

3. **Asegurarse de que el backend Java está ejecutándose**:
   - El backend debe estar disponible en `http://localhost:8080/democrudapi`
   - Verificar que los endpoints REST están accesibles

4. **Ejecutar la aplicación**:
```bash
python main.py
```

## 📁 Estructura del Proyecto

```
tkinter/
├── main.py                          # Punto de entrada principal
├── requirements.txt                 # Dependencias del proyecto
├── README.md                        # Este archivo
│
├── src/
│   ├── __init__.py
│   │
│   ├── api/                         # Módulo de comunicación REST
│   │   ├── __init__.py
│   │   └── rest_client.py          # Cliente REST para backend
│   │
│   ├── ui/                          # Interfaces de usuario
│   │   ├── __init__.py
│   │   ├── login_window.py         # Ventana de login
│   │   ├── main_window.py          # Ventana principal con menú
│   │   ├── dashboard.py            # Panel de resumen
│   │   ├── reports_window.py       # Informes y gráficos
│   │   ├── help_window.py          # Ventana de ayuda
│   │   │
│   │   └── entities/                # Gestión de entidades
│   │       ├── __init__.py
│   │       ├── base_crud_window.py  # Ventana base CRUD
│   │       ├── clientes_window.py   # Gestión de clientes
│   │       ├── empleados_window.py  # Gestión de empleados
│   │       ├── productos_window.py  # Gestión de productos
│   │       ├── presupuestos_window.py # Gestión de presupuestos
│   │       ├── facturas_window.py   # Gestión de facturas
│   │       └── pagos_window.py      # Gestión de pagos
│   │
│   ├── components/                  # Componentes reutilizables
│   │   ├── __init__.py
│   │   ├── validated_entry.py     # Campo de entrada con validación
│   │   ├── data_table.py           # Tabla con paginación
│   │   └── filter_panel.py         # Panel de filtros
│   │
│   └── utils/                       # Utilidades
│       ├── __init__.py
│       └── styles.py               # Configuración de estilos
│
└── assets/                          # Recursos (iconos, imágenes)
    └── (opcional)
```

## 🚀 Uso

### Inicio de Sesión

1. Al ejecutar la aplicación, se mostrará la ventana de login
2. Ingrese su nombre de usuario y contraseña
3. El sistema detectará automáticamente su rol (Empleado o Cliente)
4. Presione "Iniciar Sesión" o Enter

### Navegación

- **Menú Superior**: Acceso a todas las secciones disponibles según su rol
- **Barra de Herramientas**: Accesos rápidos a funciones comunes
- **Dashboard**: Panel de resumen con estadísticas y accesos rápidos
- **Atajos de Teclado**:
  - `Ctrl+D`: Ir al Dashboard
  - `Ctrl+Q`: Cerrar sesión
  - `F1`: Mostrar ayuda
  - `Enter`: Confirmar en formularios
  - `Doble clic`: Editar registro en tablas

## 👥 Roles y Permisos

### Empleado

Los empleados tienen acceso completo al sistema:

- ✅ **Clientes**: Crear, editar, eliminar y consultar todos los clientes
- ✅ **Empleados**: Gestión completa de empleados y roles
- ✅ **Productos**: Gestión del catálogo de productos
- ✅ **Presupuestos**: Crear, editar y gestionar presupuestos
- ✅ **Facturas**: Gestión completa de facturas
- ✅ **Pagos**: Registro y seguimiento de pagos
- ✅ **Informes**: Acceso a informes y gráficos

### Cliente

Los clientes tienen acceso limitado a su propia información:

- ✅ **Mi Perfil**: Ver y editar su propio perfil
- ✅ **Mis Facturas**: Consultar sus facturas (solo lectura)
- ✅ **Mis Pagos**: Ver su historial de pagos
- ❌ **No puede**: Crear otros clientes, gestionar empleados, productos, presupuestos o facturas

## 🔌 Endpoints Consumidos

La aplicación consume los siguientes endpoints del backend REST:

### Autenticación
- `POST /auth/login` - Iniciar sesión

### Entidades CRUD
Todas las entidades siguen el mismo patrón:

- `GET /{entidad}` - Obtener todos los registros
- `GET /{entidad}/{id}` - Obtener un registro por ID
- `POST /{entidad}` - Crear un nuevo registro
- `PUT /{entidad}/{id}` - Actualizar un registro
- `DELETE /{entidad}/{id}` - Eliminar un registro

### Entidades Disponibles

1. **roles_empleado** - Roles de empleados
2. **empleados** - Empleados del sistema
3. **clientes** - Clientes
4. **productos** - Catálogo de productos
5. **presupuestos** - Presupuestos
6. **facturas** - Facturas
7. **factura_productos** - Productos asociados a facturas
8. **pagos** - Pagos realizados

### Endpoints Específicos

- `GET /facturas?cliente_id={id}` - Facturas de un cliente específico
- `GET /pagos?cliente_id={id}` - Pagos de un cliente específico
- `GET /factura_productos?factura_id={id}` - Productos de una factura

## 📖 Flujos de Usuario

### Flujo: Empleado

1. **Login** → Ingresa credenciales de empleado
2. **Dashboard** → Ve estadísticas generales
3. **Gestión de Clientes**:
   - Ver lista de clientes
   - Crear nuevo cliente
   - Editar cliente existente
   - Eliminar cliente
   - Filtrar por nombre, email, teléfono
4. **Gestión de Productos**:
   - Ver catálogo
   - Añadir producto
   - Actualizar precios y stock
5. **Crear Presupuesto**:
   - Seleccionar cliente y empleado
   - Establecer fecha y total
   - Definir estado
6. **Gestionar Facturas**:
   - Crear factura asociada a cliente
   - Ver todas las facturas
   - Actualizar estados
7. **Registrar Pagos**:
   - Asociar pago a factura
   - Registrar método de pago
8. **Ver Informes**:
   - Ventas por empleado
   - Estado de presupuestos
   - Facturación mensual

### Flujo: Cliente

1. **Login** → Ingresa credenciales de cliente
2. **Dashboard** → Ve resumen de sus facturas y pagos
3. **Mi Perfil**:
   - Ver información personal
   - Editar datos (nombre, email, teléfono, dirección)
4. **Mis Facturas**:
   - Ver lista de sus facturas
   - Consultar detalles (solo lectura)
   - Filtrar por estado
5. **Mis Pagos**:
   - Ver historial de pagos
   - Consultar métodos de pago utilizados

## 🔧 Ampliación del Sistema

### Añadir Nueva Entidad

1. **Crear ventana de gestión** en `src/ui/entities/`:
```python
from src.ui.entities.base_crud_window import BaseCRUDWindow

class NuevaEntidadWindow(BaseCRUDWindow):
    def __init__(self, parent, api: RESTClient):
        columns = [
            {"name": "id", "width": 50},
            {"name": "campo1", "width": 150},
            # ... más columnas
        ]
        super().__init__(parent, api, "nueva_entidad", columns)
    
    def _get_form_fields(self):
        return [
            {"name": "campo1", "label": "Campo 1", "type": "text", "required": True},
            # ... más campos
        ]
    
    def _show_form(self, item):
        # Implementar formulario
        pass
```

2. **Añadir método en RESTClient** (`src/api/rest_client.py`):
```python
def get_nueva_entidad(self):
    return self.get_all("nueva_entidad")
```

3. **Añadir navegación** en `src/ui/main_window.py`:
```python
def show_nueva_entidad(self):
    self._clear_frame()
    self.current_frame = NuevaEntidadWindow(self.root, self.api)
    self.current_frame.pack(fill=tk.BOTH, expand=True)
```

4. **Añadir al menú y toolbar** en `_create_menu()` y `_create_toolbar()`

### Añadir Nuevo Tipo de Validación

En `src/components/validated_entry.py`, añadir nuevo tipo en `_validate_*`:

```python
def _validate_custom(self, value: str) -> bool:
    # Lógica de validación
    return True
```

Y añadir el caso en `validate_input()`.

### Añadir Nuevo Gráfico

En `src/ui/reports_window.py`:

1. Crear nuevo frame en el notebook
2. Implementar método `_load_nuevo_grafico()`
3. Llamar desde `_load_reports()`

### Cambiar Tema

Modificar `src/utils/styles.py` para añadir tema oscuro:

```python
def configure_dark_theme():
    style = ttk.Style()
    style.theme_use('dark')
    # Configurar colores oscuros
```

## 📚 Manual de Usuario

### Operaciones Básicas

#### Crear Registro

1. Navegar a la sección deseada (ej: Clientes)
2. Hacer clic en "Nuevo"
3. Completar el formulario
4. Los campos obligatorios están marcados
5. Hacer clic en "Guardar"

#### Editar Registro

1. Seleccionar un registro en la tabla
2. Hacer clic en "Editar" o hacer doble clic
3. Modificar los campos necesarios
4. Hacer clic en "Guardar"

#### Eliminar Registro

1. Seleccionar un registro en la tabla
2. Hacer clic en "Eliminar"
3. Confirmar la eliminación

#### Filtrar Datos

1. En el panel de filtros, ingresar criterios
2. Hacer clic en "Aplicar Filtros"
3. Para limpiar, hacer clic en "Limpiar Filtros"

#### Ordenar Tabla

- Hacer clic en el encabezado de una columna para ordenar
- Hacer clic nuevamente para invertir el orden

#### Navegar Páginas

- Usar botones "Anterior" y "Siguiente" en la parte inferior de la tabla
- El contador muestra la página actual y el total

### Validaciones

El sistema valida automáticamente:

- **Email**: Formato válido (ejemplo@dominio.com)
- **Teléfono**: Formato numérico válido
- **Fecha**: Formato YYYY-MM-DD
- **Números**: Valores numéricos válidos
- **Campos Obligatorios**: Deben estar completos

Los campos inválidos se resaltan en rojo.

### Informes

Los informes se actualizan automáticamente con los datos del sistema:

- **Ventas por Empleado**: Gráfico de barras
- **Estado de Presupuestos**: Gráfico circular
- **Facturación Mensual**: Gráfico de líneas

Hacer clic en "Actualizar" para refrescar los datos.

### Ayuda

- Acceder desde el menú "Ayuda" → "Ayuda" o presionar `F1`
- La ventana de ayuda contiene información detallada sobre todas las funcionalidades

## 🐛 Solución de Problemas

### Error: "No se pudo conectar con el servidor"

- Verificar que el backend Java está ejecutándose
- Verificar que la URL en `src/api/rest_client.py` es correcta
- Verificar la conexión de red

### Error: "Error de Autenticación"

- Verificar credenciales
- Verificar que el backend tiene usuarios creados
- Verificar que el endpoint de login está funcionando

### La interfaz no se muestra correctamente

- Verificar que todas las dependencias están instaladas
- Ejecutar `pip install -r requirements.txt` nuevamente

## 📝 Notas

- El sistema está diseñado para trabajar con el backend Java REST API
- Todos los datos se almacenan en el backend, no localmente
- La sesión se mantiene mientras la aplicación esté abierta
- Los cambios se guardan inmediatamente en el backend

## 🔄 Actualizaciones Futuras

Posibles mejoras:

- [ ] Tema oscuro
- [ ] Exportación de datos (PDF, Excel)
- [ ] Búsqueda avanzada con múltiples criterios
- [ ] Notificaciones en tiempo real
- [ ] Historial de cambios
- [ ] Autenticación con tokens JWT
- [ ] Caché local para mejor rendimiento
- [ ] Soporte para múltiples idiomas

## 📄 Licencia

Este proyecto es parte del sistema CRM XTART.

---

**Desarrollado con Python y Tkinter para gestión completa de entidades CRM**

