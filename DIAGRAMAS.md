# Diagramas del Sistema - CRM XTART Cliente de Escritorio

Este documento contiene diagramas UML, ER y de flujo que representan la arquitectura y funcionamiento del cliente de escritorio Python.

## Extensiones recomendadas

### **Markdown Preview Mermaid Support**
Permite que VS Code renderice diagramas Mermaid dentro de archivos Markdown.

### **Mermaid Markdown Syntax Highlighting**
Añade sintaxis coloreada y reconocimiento de bloques Mermaid.

---

## Cómo instalarlas

1. Abrir **VS Code**.  
2. Pulsar **Ctrl + Shift + X** para abrir el panel de extensiones.  
3. Buscar cada extensión por su nombre exacto.  
4. Pulsar **Install**.  

Tras instalarlas, VS Code será capaz de renderizar los diagramas Mermaid integrados en el proyecto.

---

## Visualizar Diagramas Mermaid en VS Code

### **Visualizar un archivo Markdown (.md)**

1. Abrir el archivo que contiene los diagramas.  
2. Pulsar:  
   **Ctrl + Shift + V** → *Abrir vista previa Markdown*.  
3. Los diagramas Mermaid se renderizan automáticamente en la vista previa.

---

## Visualizar Diagramas Mermaid desde archivos `.mmd`

Si los diagramas están separados en archivos Mermaid independientes:

1. Instalar también la extensión **“Mermaid Preview”** (opcional pero recomendada).  
2. Abrir cualquier archivo `.mmd`.  
3. Pulsar **Ctrl + Shift + P**.  
4. Escribir: **Mermaid: Preview Mermaid Diagram**.  
5. VS Code abrirá una vista previa interactiva del diagrama.


---

## 1. Diagrama de Arquitectura General

```mermaid
graph TB
    subgraph "Cliente Python"
        A[main.py] --> B[LoginWindow]
        B --> C[MainWindow]
        C --> D[Dashboard]
        C --> E[Entities Windows]
        C --> F[ReportsWindow]
        C --> G[HelpWindow]
        
        E --> E1[ClientesWindow]
        E --> E2[EmpleadosWindow]
        E --> E3[ProductosWindow]
        E --> E4[PresupuestosWindow]
        E --> E5[FacturasWindow]
        E --> E6[PagosWindow]
        
        E1 --> H[BaseCRUDWindow]
        E2 --> H
        E3 --> H
        E4 --> H
        E5 --> H
        E6 --> H
        
        H --> I[DataTable]
        H --> J[FilterPanel]
        
        F --> K[ReportLoader]
        F --> L[ChartFactory]
        F --> M[GraphicPanel]
        
        B --> N[RESTClient]
        C --> N
        E --> N
        F --> N
    end
    
    subgraph "Backend Java REST API"
        O[Servlets REST]
        P[Base de Datos]
        O --> P
    end
    
    N -->|HTTP Requests| O
    O -->|JSON Responses| N
    
    style A fill:#e1f5ff
    style N fill:#fff4e1
    style O fill:#ffe1f5
    style P fill:#e1ffe1
```

---

## 2. Diagrama de Clases UML - Componentes Principales

```mermaid
classDiagram
    class RESTClient {
        -session: Session
        -timeout: int
        -token: str
        -user_role: str
        -user_id: int
        +login(username, password) Dict
        +logout()
        +get_all(entity, params) Dict
        +get_by_id(entity, id) Dict
        +create(entity, payload) Dict
        +update(entity, id, payload) Dict
        +delete(entity, id) Dict
    }
    
    class MainWindow {
        -root: Window
        -api: RESTClient
        -user_info: Dict
        -is_admin: bool
        -is_empleado: bool
        -is_cliente: bool
        +show()
        +show_dashboard()
        +show_clientes()
        +show_facturas()
        +_logout()
    }
    
    class BaseCRUDWindow {
        -api: RESTClient
        -entity_name: str
        -columns: List
        -filters: List
        -data: List
        -table: DataTable
        +_load_data()
        +_on_new()
        +_on_edit()
        +_on_delete()
        +_on_filter()
    }
    
    class DataTable {
        -columns: List
        -data: List
        -current_page: int
        -items_per_page: int
        +set_data(data)
        +get_selected() Dict
        +_sort_by_column(column)
    }
    
    class ReportLoader {
        -api: RESTClient
        +ventas_por_empleado(desde, hasta) List
        +estados_presupuestos(desde, hasta) Dict
        +facturacion_mensual(desde, hasta) Dict
    }
    
    class ChartFactory {
        +bar_chart(labels, values, title, ylabel) Figure
        +pie_chart(labels, values, title) Figure
        +line_chart(labels, values, title, xlabel, ylabel) Figure
    }
    
    class ClientesWindow {
        +_load_data()
        +_show_form(record_id)
    }
    
    class FacturasWindow {
        +_load_data()
        +_show_form(record_id)
    }
    
    RESTClient --> MainWindow : uses
    MainWindow --> BaseCRUDWindow : creates
    BaseCRUDWindow --> DataTable : contains
    BaseCRUDWindow <|-- ClientesWindow : extends
    BaseCRUDWindow <|-- FacturasWindow : extends
    ReportLoader --> RESTClient : uses
    ChartFactory --> ReportLoader : processes data from
```

---

## 3. Diagrama de Secuencia - Flujo de Login

```mermaid
sequenceDiagram
    participant U as Usuario
    participant LW as LoginWindow
    participant RC as RESTClient
    participant API as Backend Java API
    participant MW as MainWindow
    
    U->>LW: Ingresa credenciales
    LW->>LW: Valida campos vacíos
    LW->>RC: login(email, password)
    RC->>API: POST /login {email, password}
    API-->>RC: {success: true, data: {user_info}}
    RC->>RC: Normaliza respuesta
    RC-->>LW: {success: true, data: user_info}
    LW->>LW: Cierra ventana
    LW->>MW: Crea MainWindow(user_info)
    MW->>MW: Determina rol (Admin/Empleado/Cliente)
    MW->>MW: Muestra Dashboard correspondiente
    MW-->>U: Interfaz principal visible
```

---

## 4. Diagrama de Secuencia - Operación CRUD (Crear/Editar)

```mermaid
sequenceDiagram
    participant U as Usuario
    participant BCW as BaseCRUDWindow
    participant DT as DataTable
    participant RC as RESTClient
    participant API as Backend Java API
    
    U->>BCW: Presiona "Nuevo" o "Editar"
    BCW->>BCW: Valida permisos
    BCW->>BCW: Muestra formulario
    U->>BCW: Completa campos
    BCW->>BCW: Valida en tiempo real (ValidatedEntry)
    U->>BCW: Presiona "Guardar"
    BCW->>BCW: Valida campos obligatorios
    BCW->>BCW: Construye payload JSON
    
    alt Crear
        BCW->>RC: create(entity, payload)
        RC->>API: POST /{entity} {payload}
    else Editar
        BCW->>RC: update(entity, id, payload)
        RC->>API: PUT /{entity}?id={id} {payload}
    end
    
    API-->>RC: {success: true, data: {...}}
    RC-->>BCW: {success: true, data: {...}}
    BCW->>BCW: Cierra formulario
    BCW->>BCW: _load_data()
    BCW->>RC: get_all(entity)
    RC->>API: GET /{entity}
    API-->>RC: {success: true, data: [...]}
    RC-->>BCW: {success: true, data: [...]}
    BCW->>DT: set_data(data)
    DT-->>U: Tabla actualizada
```

---

## 5. Diagrama de Secuencia - Generación de Informes

```mermaid
sequenceDiagram
    participant U as Usuario
    participant RW as ReportsWindow
    participant PS as PeriodSelector
    participant RL as ReportLoader
    participant RC as RESTClient
    participant API as Backend Java API
    participant CF as ChartFactory
    participant GP as GraphicPanel
    
    U->>RW: Selecciona tipo de informe
    U->>PS: Selecciona período (desde/hasta)
    U->>RW: Presiona "Generar"
    RW->>RL: ventas_por_empleado(desde, hasta)
    RL->>RC: get("/informes/ventas-empleado", params)
    RC->>API: GET /informes/ventas-empleado?desde=X&hasta=Y
    API-->>RC: {success: true, data: [...]}
    RC-->>RL: {success: true, data: [...]}
    RL-->>RW: data (lista)
    RW->>RW: Extrae labels y values (data_extractor)
    RW->>CF: bar_chart(labels, values, title, ylabel)
    CF-->>RW: Figure (matplotlib)
    RW->>GP: display(parent, figure)
    GP-->>U: Gráfico visible
    
    opt Exportar
        U->>RW: Presiona "Exportar PDF/PNG"
        RW->>RW: ReportExporter.export_report(...)
        RW-->>U: Archivo guardado
    end
```

---

## 6. Diagrama Entidad-Relación (Entidades del Sistema)

```mermaid
erDiagram
    CLIENTE ||--o{ PRESUPUESTO : "tiene"
    CLIENTE ||--o{ FACTURA : "recibe"
    EMPLEADO ||--o{ PRESUPUESTO : "crea"
    EMPLEADO ||--o{ FACTURA : "gestiona"
    EMPLEADO }o--|| ROL_EMPLEADO : "tiene"
    FACTURA ||--o{ FACTURA_PRODUCTO : "contiene"
    FACTURA ||--o{ PAGO : "tiene"
    PRODUCTO ||--o{ FACTURA_PRODUCTO : "está en"
    
    CLIENTE {
        int id_cliente PK
        string nombre
        string email
        string telefono
        string direccion
    }
    
    EMPLEADO {
        int id_empleado PK
        string nombre
        string email
        string telefono
        int id_rol FK
    }
    
    ROL_EMPLEADO {
        int id_rol PK
        string nombre_rol
    }
    
    PRODUCTO {
        int id_producto PK
        string nombre
        string descripcion
        decimal precio
        int stock
    }
    
    PRESUPUESTO {
        int id_Presupuesto PK
        int id_cliente FK
        int id_empleado FK
        date fecha
        decimal total
        string estado
    }
    
    FACTURA {
        int id_factura PK
        int id_cliente FK
        date fecha
        decimal total
        string estado
    }
    
    FACTURA_PRODUCTO {
        int id_factura_producto PK
        int id_factura FK
        int id_producto FK
        int cantidad
        decimal precio_unitario
    }
    
    PAGO {
        int id_pago PK
        int id_factura FK
        decimal monto
        date fecha
        string metodo_pago
    }
```

---

## 7. Diagrama de Flujo - Navegación y Permisos

```mermaid
flowchart TD
    Start([Usuario inicia aplicación]) --> Login[LoginWindow]
    Login --> |Ingresa credenciales| Auth{Autenticación exitosa?}
    Auth -->|No| Error[Mensaje de error]
    Error --> Login
    Auth -->|Sí| Main[MainWindow]
    Main --> DetectRol{Detectar Rol}
    
    DetectRol -->|Admin| AdminDash[Dashboard Admin]
    DetectRol -->|Empleado| EmpDash[Dashboard Empleado]
    DetectRol -->|Cliente| CliDash[Dashboard Cliente]
    
    AdminDash --> Menu[Menú de Navegación]
    EmpDash --> Menu
    CliDash --> Menu
    
    Menu --> Select{Usuario selecciona opción}
    
    Select -->|Clientes| CheckPerm1{¿Admin o Empleado?}
    CheckPerm1 -->|Sí| ClientesWin[ClientesWindow]
    CheckPerm1 -->|No| NoAccess[Acceso Denegado]
    
    Select -->|Empleados| CheckPerm2{¿Admin?}
    CheckPerm2 -->|Sí| EmpleadosWin[EmpleadosWindow]
    CheckPerm2 -->|No| NoAccess
    
    Select -->|Informes| CheckPerm3{¿Admin o Empleado?}
    CheckPerm3 -->|Sí| ReportsWin[ReportsWindow]
    CheckPerm3 -->|No| NoAccess
    
    Select -->|Mi Perfil| CheckPerm4{¿Cliente?}
    CheckPerm4 -->|Sí| ClientesWin
    CheckPerm4 -->|No| NoAccess
    
    ClientesWin --> CRUD[Operaciones CRUD]
    EmpleadosWin --> CRUD
    ReportsWin --> Reports[Generar Informes]
    
    NoAccess --> Menu
    CRUD --> Menu
    Reports --> Menu
    
    Select -->|Salir| Logout[Cerrar Sesión]
    Logout --> Login
    
    style Start fill:#e1f5ff
    style Login fill:#fff4e1
    style Main fill:#ffe1f5
    style NoAccess fill:#ffcccc
    style Logout fill:#ccffcc
```

---

## 8. Diagrama de Componentes - Arquitectura del Sistema

```mermaid
graph LR
    subgraph "Capa de Presentación"
        A[LoginWindow]
        B[MainWindow]
        C[Entity Windows]
        D[ReportsWindow]
        E[HelpWindow]
        F[Widgets Reutilizables]
    end
    
    subgraph "Capa de Lógica de Negocio"
        G[BaseCRUDWindow]
        H[ReportLoader]
        I[ChartFactory]
        J[Validators]
    end
    
    subgraph "Capa de Comunicación"
        K[RESTClient]
        L[RESTHelpers]
        M[Endpoints]
    end
    
    subgraph "Capa de Datos Externa"
        N[Backend Java REST API]
        O[Base de Datos]
    end
    
    A --> K
    B --> K
    C --> G
    G --> K
    D --> H
    H --> K
    E --> F
    
    G --> F
    C --> F
    
    H --> I
    D --> I
    
    K --> L
    K --> M
    M --> N
    N --> O
    
    J --> G
    J --> C
    
    style A fill:#e1f5ff
    style B fill:#e1f5ff
    style C fill:#e1f5ff
    style D fill:#e1f5ff
    style K fill:#fff4e1
    style N fill:#ffe1f5
    style O fill:#e1ffe1
```

---

## 9. Diagrama de Estados - Ciclo de Vida de una Entidad

```mermaid
stateDiagram-v2
    [*] --> Lista: Cargar ventana
    Lista --> Seleccionado: Usuario selecciona registro
    Seleccionado --> Editando: Presiona Editar / Doble clic
    Seleccionado --> Eliminando: Presiona Eliminar
    Lista --> Creando: Presiona Nuevo
    
    Creando --> Validando: Usuario completa formulario
    Editando --> Validando: Usuario modifica campos
    
    Validando --> Guardando: Validación exitosa
    Validando --> Creando: Error de validación
    Validando --> Editando: Error de validación
    
    Guardando --> Guardado: POST/PUT exitoso
    Guardando --> Creando: Error del servidor
    Guardando --> Editando: Error del servidor
    
    Guardado --> Lista: Recargar datos
    Eliminando --> Eliminado: DELETE exitoso
    Eliminado --> Lista: Recargar datos
    
    Lista --> [*]: Cerrar ventana
```

---

## 10. Diagrama de Flujo - Proceso de Filtrado

```mermaid
flowchart TD
    Start([Usuario en ventana CRUD]) --> ShowFilters[Mostrar FilterPanel]
    ShowFilters --> Input[Usuario ingresa criterios]
    Input --> Apply{Presiona Aplicar Filtros?}
    
    Apply -->|No| Clear{Presiona Limpiar?}
    Clear -->|Sí| ClearFields[Limpiar campos]
    ClearFields --> LoadAll[Cargar todos los datos]
    Clear -->|No| Input
    
    Apply -->|Sí| BuildParams[Construir parámetros de consulta]
    BuildParams --> Request[GET /{entidad}?param1=value1&param2=value2]
    Request --> Backend{Backend responde}
    
    Backend -->|Éxito| ProcessData[Procesar datos recibidos]
    Backend -->|Error| ShowError[Mostrar mensaje de error]
    ShowError --> Input
    
    ProcessData --> Normalize[Normalizar IDs y campos]
    Normalize --> FilterClient{¿Modo Cliente?}
    
    FilterClient -->|Sí| FilterByUser[Filtrar por user_id]
    FilterClient -->|No| UpdateTable
    
    FilterByUser --> UpdateTable[Actualizar DataTable]
    LoadAll --> UpdateTable
    UpdateTable --> Display[Mostrar resultados]
    Display --> Input
    
    style Start fill:#e1f5ff
    style Request fill:#fff4e1
    style Backend fill:#ffe1f5
    style Display fill:#e1ffe1
```

---

## 11. Diagrama de Paquetes - Estructura Modular

```mermaid
graph TB
    subgraph "tkinter/"
        subgraph "src/"
            subgraph "api/"
                A1[rest_client.py]
                A2[rest_helpers.py]
                A3[endpoints.py]
            end
            
            subgraph "ui/"
                B1[login_window.py]
                B2[main_window.py]
                B3[reports_window.py]
                B4[help_window.py]
                
                subgraph "dashboard/"
                    B5[dashboard_base.py]
                    B6[dashboard_admin.py]
                    B7[dashboard_employee.py]
                    B8[dashboard_client.py]
                end
                
                subgraph "entities/"
                    B9[base_crud_window.py]
                    B10[clientes_window.py]
                    B11[empleados_window.py]
                    B12[productos_window.py]
                    B13[presupuestos_window.py]
                    B14[facturas_window.py]
                    B15[pagos_window.py]
                end
                
                subgraph "widgets/"
                    B16[ctk_datepicker.py]
                    B17[ctk_scrollable_frame.py]
                    B18[period_selector.py]
                end
            end
            
            subgraph "widgets/"
                C1[data_table.py]
                C2[filter_panel.py]
                C3[validated_entry.py]
            end
            
            subgraph "reports/"
                D1[chart_factory.py]
                D2[graphic_panel.py]
                D3[report_loader.py]
                D4[zoom_manager.py]
                
                subgraph "exporters/"
                    D5[pdf_exporter.py]
                    D6[image_exporter.py]
                    D7[report_exporter.py]
                end
            end
            
            subgraph "utils/"
                E1[settings.py]
                E2[styles.py]
                E3[validators.py]
                E4[exceptions.py]
            end
        end
        
        F1[main.py]
        F2[requirements.txt]
    end
    
    F1 --> B1
    F1 --> A1
    B1 --> A1
    B2 --> A1
    B2 --> B5
    B2 --> B9
    B9 --> C1
    B9 --> C2
    B3 --> D3
    D3 --> A1
    D3 --> D1
    B10 --> B9
    B11 --> B9
    
    style A1 fill:#fff4e1
    style B2 fill:#e1f5ff
    style B9 fill:#ffe1f5
    style D1 fill:#e1ffe1
```

---

## Notas sobre los Diagramas

### Diagrama de Arquitectura General
Muestra la estructura general del sistema y cómo los componentes principales se relacionan entre sí y con el backend.

### Diagrama de Clases UML
Representa las clases principales del sistema, sus atributos y métodos clave, así como las relaciones de herencia y composición.

### Diagramas de Secuencia
Ilustran la interacción temporal entre objetos durante operaciones específicas como login, CRUD e informes.

### Diagrama ER
Muestra las entidades del dominio de negocio y sus relaciones, tal como las maneja el cliente (aunque la persistencia está en el backend).

### Diagramas de Flujo
Describen los procesos de negocio desde la perspectiva del usuario y el sistema.

### Diagrama de Estados
Muestra el ciclo de vida de una entidad durante las operaciones CRUD.

### Diagrama de Componentes
Representa la arquitectura en capas del sistema.

### Diagrama de Paquetes
Muestra la organización física del código en módulos y paquetes.

---

## Herramientas para Visualizar

Estos diagramas están escritos en **Mermaid**, que puede visualizarse en:
- GitHub (renderizado automático en archivos .md)
- GitLab
- VS Code (con extensión Mermaid)
- Documentación online (Mermaid Live Editor: https://mermaid.live)
- Herramientas de documentación como MkDocs, Docusaurus, etc.

Para exportar a otros formatos (PNG, SVG, PDF), puedes usar:
- Mermaid CLI: `npm install -g @mermaid-js/mermaid-cli`
- Herramientas online de conversión
- Extensiones de VS Code que permiten exportar

