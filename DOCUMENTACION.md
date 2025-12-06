# Documentación Técnica - CRM XTART Cliente de Escritorio

## 1. Arquitectura General del Proyecto

### 1.1 Estructura de Carpetas

El proyecto está organizado siguiendo una arquitectura modular que separa claramente las responsabilidades:

```
tkinter/
├── main.py                    # Punto de entrada principal
├── requirements.txt           # Dependencias del proyecto
│
├── src/
│   ├── api/                   # Capa de comunicación REST
│   │   ├── rest_client.py     # Cliente HTTP principal
│   │   ├── rest_helpers.py    # Métodos auxiliares específicos
│   │   └── endpoints.py       # Definición de endpoints
│   │
│   ├── ui/                    # Interfaz gráfica
│   │   ├── login_window.py    # Ventana de autenticación
│   │   ├── main_window.py     # Ventana principal con navegación
│   │   ├── help_window.py     # Sistema de ayuda HTML
│   │   ├── reports_window.py  # Ventana de informes y gráficos
│   │   │
│   │   ├── dashboard/         # Dashboards por rol
│   │   │   ├── dashboard_base.py
│   │   │   ├── dashboard_admin.py
│   │   │   ├── dashboard_employee.py
│   │   │   └── dashboard_client.py
│   │   │
│   │   ├── entities/          # Ventanas CRUD de entidades
│   │   │   ├── base_crud_window.py  # Clase base para CRUD
│   │   │   ├── clientes_window.py
│   │   │   ├── empleados_window.py
│   │   │   ├── productos_window.py
│   │   │   ├── presupuestos_window.py
│   │   │   ├── facturas_window.py
│   │   │   └── pagos_window.py
│   │   │
│   │   ├── widgets/           # Widgets personalizados
│   │   │   ├── ctk_datepicker.py
│   │   │   ├── ctk_scrollable_frame.py
│   │   │   └── period_selector.py
│   │   │
│   │   └── reports/            # Configuración de informes
│   │       └── report_definitions.py
│   │
│   ├── models/                 # Modelos de datos (DTOs)
│   │   ├── cliente.py
│   │   ├── empleado.py
│   │   ├── producto.py
│   │   ├── factura.py
│   │   └── factura_detalle.py
│   │
│   ├── widgets/                # Componentes reutilizables
│   │   ├── data_table.py      # Tabla con paginación
│   │   ├── filter_panel.py    # Panel de filtros
│   │   └── validated_entry.py # Campos con validación
│   │
│   ├── reports/                # Sistema de informes
│   │   ├── chart_factory.py   # Generación de gráficos
│   │   ├── graphic_panel.py   # Visualización de gráficos
│   │   ├── report_loader.py   # Carga de datos
│   │   ├── zoom_manager.py    # Gestión de zoom
│   │   └── exporters/          # Exportadores
│   │       ├── pdf_exporter.py
│   │       ├── image_exporter.py
│   │       └── report_exporter.py
│   │
│   └── utils/                  # Utilidades
│       ├── settings.py        # Configuración
│       ├── styles.py          # Estilos de UI
│       ├── validators.py      # Validadores de datos
│       └── exceptions.py      # Excepciones personalizadas
│
└── docs/                       # Documentación HTML
    ├── ayuda.html
    └── Style.css
```

### 1.2 Organización Interna

El proyecto sigue el patrón **Modelo-Vista-Controlador (MVC)** adaptado:

- **Modelo**: Los módulos en `src/models/` representan las entidades de negocio
- **Vista**: Las ventanas en `src/ui/` y componentes en `src/widgets/` conforman la interfaz
- **Controlador**: La lógica de negocio está distribuida entre las ventanas y el cliente REST

La comunicación se realiza mediante una **capa de abstracción REST** (`src/api/`) que encapsula todas las interacciones con el backend Java, proporcionando una interfaz uniforme independientemente de los detalles de implementación del servidor.

---

## 2. Tecnologías y Librerías Utilizadas

### 2.1 Framework de Interfaz Gráfica

**CustomTkinter (>=5.2.0)**
- Framework principal para la construcción de la interfaz de usuario
- Proporciona widgets modernos con tema oscuro por defecto
- Utilizado para ventanas principales, botones, campos de entrada y contenedores
- Permite una apariencia visual moderna y consistente en toda la aplicación

**ttkbootstrap (>=1.10.0)**
- Biblioteca complementaria que extiende las capacidades de ttk (Tkinter temático)
- Utilizada principalmente para la ventana raíz y estilos adicionales
- Proporciona temas predefinidos y componentes estilizados

**Tkinter (nativo)**
- Base sobre la cual se construyen CustomTkinter y ttkbootstrap
- Utilizado para componentes básicos y estructura de ventanas

### 2.2 Comunicación con Backend

**requests (>=2.31.0)**
- Biblioteca HTTP para realizar peticiones REST al backend Java
- Gestiona sesiones HTTP, cookies (JSESSIONID), timeouts y manejo de errores
- Implementa el cliente REST que encapsula toda la comunicación con la API

### 2.3 Visualización de Datos

**matplotlib (>=3.7.0)**
- Generación de gráficos para los informes del sistema
- Soporta gráficos de barras, líneas y circulares (pie charts)
- Permite exportación a PDF y PNG con alta calidad

**tkinterweb (>=3.21.0)**
- Renderizado de contenido HTML en la ventana de ayuda
- Permite mostrar documentación formateada con estilos CSS
- Utilizado exclusivamente para el sistema de ayuda contextual

### 2.4 Procesamiento de Imágenes

**Pillow (>=10.0.0)**
- Procesamiento y manipulación de imágenes
- Utilizado para cargar y redimensionar el logo de la aplicación
- Soporte para exportación de gráficos a formatos de imagen

### 2.5 Funciones Específicas

Cada librería cumple un rol específico:
- **CustomTkinter**: Interfaz de usuario moderna y responsive
- **requests**: Abstracción de la comunicación HTTP con el backend
- **matplotlib**: Visualización de datos estadísticos e informes
- **tkinterweb**: Documentación HTML integrada
- **Pillow**: Manejo de recursos gráficos

---

## 3. Comunicación con el Backend Java

### 3.1 Cliente REST

El sistema utiliza un **cliente REST centralizado** (`RESTClient`) que encapsula toda la comunicación con el backend Java. Este cliente:

- **Gestiona sesiones HTTP**: Mantiene cookies de sesión (JSESSIONID) automáticamente mediante `requests.Session()`
- **Normaliza respuestas**: Convierte las respuestas del backend a un formato uniforme `{"success": bool, "data": any, "error": str}`
- **Maneja errores**: Captura excepciones de red, timeouts y errores HTTP, devolviendo mensajes descriptivos
- **Soporta múltiples formatos**: El backend puede devolver `{"success": true, "data": {...}}` o `{"success": true, "dataObj": {...}}`, y el cliente normaliza ambos formatos

### 3.2 Endpoints Utilizados

El sistema consume los siguientes endpoints del backend:

**Autenticación:**
- `POST /login` - Autenticación de usuarios (email y password)
- `POST /logout` - Cierre de sesión

**Entidades CRUD (patrón uniforme):**
- `GET /{entidad}?id={id}` - Obtener registro por ID
- `GET /{entidad}` - Obtener todos los registros (con filtros opcionales)
- `POST /{entidad}` - Crear nuevo registro
- `PUT /{entidad}?id={id}` - Actualizar registro existente
- `DELETE /{entidad}?id={id}` - Eliminar registro

**Entidades disponibles:**
- `/clientes` - Gestión de clientes
- `/empleados` - Gestión de empleados
- `/productos` - Catálogo de productos
- `/presupuestos` - Presupuestos
- `/facturas` - Facturas
- `/pagos` - Pagos
- `/factura_productos` - Detalles de productos en facturas
- `/roles_empleado` - Roles de empleados

**Endpoints específicos:**
- `GET /clientes?nombre={nombre}` - Filtrar clientes por nombre
- `GET /clientes?email={email}` - Filtrar clientes por email
- `GET /clientes?telefono={telefono}` - Filtrar clientes por teléfono
- `GET /factura_productos?factura_id={id}` - Productos de una factura
- `GET /dashboard/stats` - Estadísticas del dashboard

**Endpoints de informes (opcionales):**
- `GET /informes/ventas-empleado?desde={fecha}&hasta={fecha}`
- `GET /informes/presupuestos-estado?desde={fecha}&hasta={fecha}`
- `GET /informes/facturacion-mensual?desde={fecha}&hasta={fecha}`
- `GET /informes/ventas-producto?desde={fecha}&hasta={fecha}`
- `GET /informes/ratio-conversion?desde={fecha}&hasta={fecha}`

### 3.3 Formato de Datos

**Peticiones:**
- Las peticiones POST y PUT envían datos en formato JSON (`Content-Type: application/json`)
- Los parámetros de consulta se envían como query params en las URLs

**Respuestas:**
- El backend devuelve JSON con estructura `{"success": bool, "data": any}` o `{"success": bool, "dataObj": any}`
- El cliente REST normaliza ambos formatos a `{"success": bool, "data": any}`
- Los errores se devuelven como `{"success": false, "error": "mensaje"}`

### 3.4 Manejo de Respuestas

El cliente REST implementa un sistema robusto de manejo de respuestas:

1. **Normalización automática**: Convierte `dataObj` a `data` para compatibilidad
2. **Manejo de nulls**: Convierte `null` en listas vacías `[]` cuando corresponde
3. **Validación de tipos**: Verifica que las respuestas sean del tipo esperado
4. **Logging**: Registra todas las peticiones y respuestas para depuración
5. **Manejo de errores HTTP**: Distingue entre errores 404 (endpoint no encontrado), 401 (no autorizado), y otros errores

### 3.5 Autenticación y Sesiones

El sistema utiliza **sesiones HTTP** (no tokens JWT):
- El backend Java mantiene la sesión mediante cookies `JSESSIONID`
- El cliente REST mantiene una sesión persistente durante toda la ejecución
- Al hacer login, el backend establece la cookie automáticamente
- Todas las peticiones subsecuentes incluyen la cookie automáticamente

---

## 4. Interfaz Gráfica

### 4.1 Ventanas Principales

**LoginWindow (`src/ui/login_window.py`)**
- Primera ventana que se muestra al ejecutar la aplicación
- Solicita credenciales (email y contraseña)
- Valida campos antes de enviar petición al backend
- Muestra mensajes de error descriptivos
- Al autenticarse exitosamente, cierra la ventana y muestra `MainWindow`

**MainWindow (`src/ui/main_window.py`)**
- Ventana principal de la aplicación
- Contiene la barra superior (topbar) con información del usuario y menú
- Área de contenido central que cambia según la sección seleccionada
- Barra de estado inferior para mensajes informativos
- Gestiona la navegación entre diferentes secciones según el rol del usuario

**HelpWindow (`src/ui/help_window.py`)**
- Ventana modal que muestra documentación HTML
- Utiliza `tkinterweb` para renderizar contenido HTML con estilos CSS
- Carga el archivo `docs/ayuda.html` con la documentación completa
- Permite cerrar y volver a la ventana principal

**ReportsWindow (`src/ui/reports_window.py`)**
- Ventana especializada para visualización de informes y gráficos
- Permite seleccionar tipo de informe, período de tiempo y generar gráficos
- Incluye controles de zoom y exportación a PDF/PNG
- Área scrolleable para gráficos grandes

### 4.2 Navegación

El sistema implementa una **navegación basada en roles**:

**Menú contextual:**
- Se accede mediante un botón con el logo en la esquina superior derecha
- Muestra opciones diferentes según el rol del usuario (Admin, Empleado, Cliente)
- Las opciones se generan dinámicamente según los permisos

**Atajos de teclado:**
- `Ctrl+D` / `Ctrl+d`: Ir al Dashboard
- `Ctrl+Q` / `Ctrl+q`: Cerrar sesión
- `F1`: Mostrar ayuda
- `Enter`: Confirmar en formularios
- `Doble clic`: Editar registro en tablas

**Navegación programática:**
- Cada ventana puede navegar a otras mediante callbacks
- El sistema mantiene el estado de la ventana actual
- Al cambiar de sección, se destruye el contenido anterior y se carga el nuevo

### 4.3 Componentes Reutilizables

**BaseCRUDWindow (`src/ui/entities/base_crud_window.py`)**
- Clase base abstracta para todas las ventanas de gestión de entidades
- Proporciona funcionalidad común: tabla de datos, filtros, botones CRUD, paginación
- Las ventanas específicas (ClientesWindow, FacturasWindow, etc.) heredan de esta clase
- Implementa el patrón Template Method para operaciones CRUD

**DataTable (`src/widgets/data_table.py`)**
- Componente de tabla con funcionalidades avanzadas:
  - Paginación automática (20 registros por página)
  - Ordenación por columnas (clic en encabezado)
  - Selección de filas
  - Soporte para doble clic
  - Scroll automático
- Utiliza `ttk.Treeview` como base pero con funcionalidades extendidas

**FilterPanel (`src/widgets/filter_panel.py`)**
- Panel de filtros dinámico que se genera según la configuración
- Soporta diferentes tipos de filtros: texto, número, fecha
- Botones para aplicar y limpiar filtros
- Los filtros se envían como parámetros de consulta al backend

**ValidatedEntry (`src/widgets/validated_entry.py`)**
- Campo de entrada con validación en tiempo real
- Soporta validación de email, teléfono, fecha, números
- Muestra indicadores visuales (rojo/verde) según la validez
- Previene la entrada de datos inválidos

**CTkDatePicker (`src/ui/widgets/ctk_datepicker.py`)**
- Selector de fechas personalizado para CustomTkinter
- Interfaz intuitiva para seleccionar fechas
- Formato de salida: YYYY-MM-DD

**PeriodSelector (`src/ui/widgets/period_selector.py`)**
- Selector de períodos de tiempo con opciones rápidas (último mes, último año, etc.)
- Permite selección personalizada de fechas desde/hasta
- Utilizado en la ventana de informes

### 4.4 Lógica General de la Interfaz

**Flujo de inicialización:**
1. `main.py` crea la ventana raíz y el cliente REST
2. Se muestra `LoginWindow`
3. Tras autenticación exitosa, se crea `MainWindow` con información del usuario
4. `MainWindow` determina el rol y muestra el dashboard correspondiente

**Gestión de estado:**
- El estado del usuario (rol, ID, nombre) se almacena en `MainWindow` y `RESTClient`
- Cada ventana CRUD mantiene su propio estado local (datos cargados, filtros aplicados)
- No hay estado global compartido; la comunicación se realiza mediante callbacks

**Actualización de datos:**
- Las tablas se actualizan mediante llamadas al backend
- Los datos se cargan bajo demanda (lazy loading)
- Botón "Actualizar" disponible en todas las ventanas CRUD para refrescar datos

---

## 5. Gestión de Informes y Gráficos

### 5.1 Arquitectura del Sistema de Informes

El sistema de informes está compuesto por varios módulos que trabajan en conjunto:

**ReportLoader (`src/reports/report_loader.py`)**
- Carga datos desde el backend para cada tipo de informe
- Cada método corresponde a un informe específico (ventas por empleado, facturación mensual, etc.)
- Maneja parámetros de fecha (desde/hasta) para filtrar datos temporales
- Si el endpoint no está disponible (404), devuelve datos vacíos sin error

**ChartFactory (`src/reports/chart_factory.py`)**
- Factory pattern para crear diferentes tipos de gráficos
- Métodos estáticos: `bar_chart()`, `pie_chart()`, `line_chart()`, `empty()`
- Aplica estilos consistentes a todos los gráficos
- Utiliza una paleta de colores predefinida para mantener coherencia visual

**ReportDefinitions (`src/ui/reports/report_definitions.py`)**
- Configuración centralizada de todos los informes disponibles
- Define el tipo de gráfico, método de carga, y función extractora de datos
- Permite agregar nuevos informes sin modificar código de la interfaz

**GraphicPanel (`src/reports/graphic_panel.py`)**
- Componente que muestra gráficos de matplotlib en la interfaz
- Convierte figuras de matplotlib a widgets de Tkinter
- Gestiona el renderizado y actualización de gráficos

### 5.2 Tipos de Informes

El sistema soporta cinco tipos de informes:

1. **Ventas por empleado**: Gráfico de barras mostrando total de ventas por cada empleado
2. **Estado presupuestos**: Gráfico circular (pie) con distribución de estados de presupuestos
3. **Facturación mensual**: Gráfico de líneas mostrando evolución mensual de facturación
4. **Ventas por producto**: Gráfico de barras con ventas totales por producto
5. **Ratio conversión**: Gráfico circular con métricas de conversión de presupuestos a facturas

### 5.3 Flujo de Generación de Informes

1. **Selección de informe**: El usuario selecciona un tipo de informe del menú desplegable
2. **Selección de período**: El usuario selecciona fechas "desde" y "hasta" usando el `PeriodSelector`
3. **Generación**: Al presionar "Generar", se llama al método correspondiente de `ReportLoader`
4. **Carga de datos**: `ReportLoader` realiza petición GET al endpoint correspondiente con parámetros de fecha
5. **Extracción**: Se aplica la función `data_extractor` definida en `report_definitions.py` para extraer labels y valores
6. **Creación del gráfico**: `ChartFactory` crea el gráfico según el tipo configurado
7. **Renderizado**: `GraphicPanel` muestra el gráfico en la interfaz

### 5.4 Exportadores

**ReportExporter (`src/reports/exporters/report_exporter.py`)**
- Exportador unificado que delega a exportadores específicos
- Soporta exportación a PDF y PNG

**PDFExporter (`src/reports/exporters/pdf_exporter.py`)**
- Exporta gráficos a formato PDF
- Incluye título, período, y el gráfico completo
- Utiliza matplotlib para generar el PDF

**ImageExporter (`src/reports/exporters/image_exporter.py`)**
- Exporta gráficos a formato PNG
- Alta resolución para impresión
- Permite guardar con nombre personalizado

### 5.5 Gestión de Zoom

**ZoomManager (`src/reports/zoom_manager.py`)**
- Gestiona el nivel de zoom de los gráficos
- Permite zoom in (+) y zoom out (-)
- Al cambiar el zoom, se vuelve a renderizar el gráfico con el nuevo tamaño
- El zoom afecta al tamaño de la figura de matplotlib antes de renderizar

### 5.6 Características Adicionales

- **Manejo de datos vacíos**: Si no hay datos para el período seleccionado, se muestra un mensaje informativo
- **Endpoints opcionales**: Si un endpoint de informes no está disponible en el backend, se muestra un mensaje sin generar error
- **Actualización manual**: Botón "Actualizar" para regenerar el informe con los mismos parámetros
- **Título dinámico**: El título del informe incluye el período seleccionado

---

## 6. Modo Demo

**El proyecto NO implementa un modo Demo activo.**

En el código de `login_window.py` existe código comentado que sugiere que en algún momento se consideró implementar un "modo visual" cuando el backend no está disponible, pero esta funcionalidad está deshabilitada.

El sistema actual **requiere conexión al backend Java** para funcionar. Si el backend no está disponible:
- El login fallará con un mensaje de error
- No se puede acceder a ninguna funcionalidad
- No hay datos demo ni modo offline

El sistema está diseñado exclusivamente para trabajar en **modo REST** con el backend Java ejecutándose en `http://localhost:8080/crudxtart` (configurable mediante variable de entorno `API_BASE_URL`).

---

## 7. Entidades Manejadas

El sistema gestiona las siguientes entidades desde la perspectiva del cliente de escritorio:

### 7.1 Clientes

**Ventana**: `ClientesWindow`
- **Operaciones**: Crear, leer, actualizar, eliminar (solo Admin/Empleado)
- **Filtros**: Por nombre, email, teléfono
- **Campos principales**: ID, nombre, email, teléfono, dirección
- **Modo cliente**: Los clientes solo pueden ver y editar su propio perfil

### 7.2 Empleados

**Ventana**: `EmpleadosWindow`
- **Operaciones**: Crear, leer, actualizar, eliminar (solo Admin)
- **Filtros**: No implementados (se pueden agregar)
- **Campos principales**: ID, nombre, email, teléfono, rol
- **Relaciones**: Cada empleado tiene un rol asociado (obtenido de `/roles_empleado`)

### 7.3 Productos

**Ventana**: `ProductosWindow`
- **Operaciones**: Crear, leer, actualizar, eliminar (solo Admin/Empleado)
- **Filtros**: No implementados
- **Campos principales**: ID, nombre, descripción, precio, stock
- **Uso**: Catálogo de productos disponibles para presupuestos y facturas

### 7.4 Presupuestos

**Ventana**: `PresupuestosWindow`
- **Operaciones**: Crear, leer, actualizar, eliminar (solo Admin/Empleado)
- **Filtros**: Por cliente, empleado, estado, fecha
- **Campos principales**: ID, cliente, empleado, fecha, total, estado
- **Funcionalidades especiales**:
  - Exportación a PDF/PNG
  - Conversión a factura
  - Filtros avanzados por período

### 7.5 Facturas

**Ventana**: `FacturasWindow`
- **Operaciones**: Crear, leer, actualizar, eliminar (solo Admin/Empleado)
- **Filtros**: Por cliente, estado, fecha
- **Campos principales**: ID, cliente pagador, fecha, total, estado
- **Funcionalidades especiales**:
  - Gestión de productos asociados (detalles de factura)
  - Exportación a PDF/PNG
  - Visualización de pagos asociados
- **Modo cliente**: Los clientes solo pueden ver sus propias facturas (solo lectura)

### 7.6 Pagos

**Ventana**: `PagosWindow`
- **Operaciones**: Crear, leer, actualizar, eliminar (solo Admin/Empleado)
- **Filtros**: Por factura, método de pago, fecha
- **Campos principales**: ID, factura asociada, monto, fecha, método de pago
- **Funcionalidades especiales**:
  - Exportación a PDF/PNG
  - Filtros por período
- **Modo cliente**: Los clientes solo pueden ver sus propios pagos

### 7.7 Relaciones entre Entidades

- **Presupuestos** → Cliente, Empleado
- **Facturas** → Cliente (pagador)
- **Factura Productos** → Factura, Producto
- **Pagos** → Factura
- **Empleados** → Rol (de roles_empleado)

---

## 8. Flujos Clave del Programa

### 8.1 Flujo de Login

1. **Inicio**: `main.py` crea la ventana raíz y el cliente REST
2. **Mostrar login**: Se crea y muestra `LoginWindow`
3. **Ingreso de credenciales**: Usuario ingresa email y contraseña
4. **Validación local**: Se verifica que los campos no estén vacíos
5. **Petición al backend**: `RESTClient.login()` envía POST a `/login` con credenciales
6. **Procesamiento de respuesta**:
   - Si falla: Se muestra mensaje de error y se mantiene en login
   - Si éxito: Se extrae información del usuario (ID, nombre, rol, tipo)
7. **Normalización de datos**: El cliente REST normaliza la respuesta del backend (maneja diferentes formatos)
8. **Cierre de login**: Se destruye `LoginWindow`
9. **Apertura de MainWindow**: Se crea `MainWindow` con la información del usuario
10. **Determinación de permisos**: `MainWindow` determina si el usuario es Admin, Empleado o Cliente
11. **Mostrar dashboard**: Se muestra el dashboard correspondiente al rol

### 8.2 Flujo de Carga de Módulos

1. **Selección de sección**: Usuario selecciona una opción del menú (ej: "Clientes")
2. **Verificación de permisos**: `MainWindow` verifica si el usuario tiene acceso
3. **Limpieza de contenido**: Se destruye el frame actual si existe
4. **Creación de ventana**: Se instancia la ventana correspondiente (ej: `ClientesWindow`)
5. **Inicialización**: La ventana crea sus widgets (toolbar, filtros, tabla)
6. **Carga de datos**: Se llama a `_load_data()` que realiza GET al backend
7. **Procesamiento**: Los datos se normalizan (IDs, campos relacionados)
8. **Filtrado (si aplica)**: En modo cliente, se filtran solo los registros del usuario
9. **Mostrar en tabla**: Los datos se pasan a `DataTable` para visualización
10. **Actualización de título**: Se actualiza el título en el header de `MainWindow`

### 8.3 Flujo de Interacción con Listas

1. **Visualización**: `DataTable` muestra los datos paginados (20 por página)
2. **Selección**: Usuario hace clic en una fila → se selecciona
3. **Doble clic**: Si el usuario hace doble clic → se abre formulario de edición
4. **Ordenación**: Usuario hace clic en encabezado de columna → se ordena ascendente/descendente
5. **Paginación**: Usuario navega con botones "Anterior"/"Siguiente"
6. **Filtrado**: Usuario ingresa criterios en `FilterPanel` y presiona "Aplicar Filtros"
7. **Aplicación de filtros**: Se construyen parámetros de consulta y se realiza GET con filtros
8. **Actualización**: La tabla se actualiza con los resultados filtrados

### 8.4 Flujo de Filtros

1. **Configuración**: Cada ventana CRUD define qué campos son filtrables en `filters`
2. **Renderizado**: `FilterPanel` crea campos de entrada dinámicamente según la configuración
3. **Ingreso de valores**: Usuario ingresa valores en los campos de filtro
4. **Aplicar**: Al presionar "Aplicar Filtros", se recopilan los valores
5. **Construcción de parámetros**: Se construye diccionario de parámetros para la petición GET
6. **Petición al backend**: Se realiza GET a `/{entidad}` con parámetros de consulta
7. **Filtrado en backend**: El backend Java aplica los filtros y devuelve resultados
8. **Actualización de tabla**: Los resultados se muestran en la tabla
9. **Limpiar**: Al presionar "Limpiar Filtros", se vacían los campos y se recarga sin filtros

### 8.5 Flujo de Edición

1. **Selección**: Usuario selecciona un registro en la tabla
2. **Apertura de formulario**: Se presiona "Editar" o se hace doble clic
3. **Validación de permisos**: 
   - En modo cliente: Se verifica que el registro pertenezca al usuario
   - En modo empleado/admin: Se permite editar cualquier registro
4. **Carga de datos completos**: Se realiza GET por ID para obtener todos los campos
5. **Mostrar formulario**: Se crea ventana modal o frame con campos del formulario
6. **Validación en tiempo real**: `ValidatedEntry` valida campos mientras el usuario escribe
7. **Guardar**: Al presionar "Guardar":
   - Se validan todos los campos obligatorios
   - Se construye el payload JSON
   - Se realiza PUT a `/{entidad}?id={id}` con el payload
8. **Procesamiento de respuesta**:
   - Si éxito: Se cierra el formulario y se recarga la tabla
   - Si error: Se muestra mensaje de error y se mantiene el formulario abierto
9. **Actualización**: La tabla se actualiza mostrando los cambios

### 8.6 Flujo de Creación

1. **Inicio**: Usuario presiona "Nuevo" en la toolbar
2. **Validación de permisos**: Se verifica que el usuario tenga permisos de creación
3. **Formulario vacío**: Se muestra formulario con campos vacíos
4. **Validación**: Misma validación en tiempo real que en edición
5. **Guardar**: Al presionar "Guardar":
   - Se validan campos obligatorios
   - Se construye payload JSON (sin ID)
   - Se realiza POST a `/{entidad}`
6. **Procesamiento**: Similar a edición, pero el backend asigna el ID
7. **Actualización**: La tabla se recarga mostrando el nuevo registro

### 8.7 Flujo de Eliminación

1. **Selección**: Usuario selecciona un registro
2. **Confirmación**: Se muestra diálogo de confirmación
3. **Eliminación**: Si se confirma:
   - Se realiza DELETE a `/{entidad}?id={id}`
4. **Procesamiento**:
   - Si éxito: Se recarga la tabla
   - Si error: Se muestra mensaje de error
5. **Actualización**: La tabla se actualiza sin el registro eliminado

### 8.8 Flujo de Informes

1. **Acceso**: Usuario (Admin/Empleado) selecciona "Informes" del menú
2. **Selección de informe**: Usuario selecciona tipo de informe del menú desplegable
3. **Selección de período**: Usuario selecciona fechas "desde" y "hasta"
4. **Generación**: Usuario presiona "Generar"
5. **Carga de datos**: `ReportLoader` realiza GET al endpoint correspondiente con parámetros de fecha
6. **Procesamiento**:
   - Si el endpoint no existe (404): Se muestra mensaje informativo
   - Si hay datos: Se extraen labels y valores usando `data_extractor`
   - Si no hay datos: Se muestra gráfico vacío con mensaje
7. **Creación del gráfico**: `ChartFactory` crea el gráfico según el tipo
8. **Renderizado**: `GraphicPanel` muestra el gráfico en la interfaz
9. **Interacción**:
   - Zoom: Usuario puede hacer zoom in/out
   - Exportar: Usuario puede exportar a PDF o PNG
   - Actualizar: Usuario puede regenerar con nuevos parámetros

---

## Conclusión

El cliente de escritorio CRM XTART es una aplicación Python moderna que proporciona una interfaz gráfica completa para gestionar todas las entidades del sistema CRM. Utiliza tecnologías modernas (CustomTkinter, requests, matplotlib) para ofrecer una experiencia de usuario fluida y profesional.

La arquitectura modular permite fácil extensión y mantenimiento, mientras que la capa de abstracción REST garantiza que los cambios en el backend no afecten significativamente al cliente.

El sistema está diseñado para trabajar exclusivamente con el backend Java REST API, requiriendo conexión activa para todas las operaciones. No implementa modo offline ni datos demo.
