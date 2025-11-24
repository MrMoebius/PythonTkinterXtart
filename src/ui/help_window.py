"""
Ventana de ayuda y documentación
"""

import tkinter as tk
from tkinter import ttk

class HelpWindow:
    """Ventana de ayuda contextual"""
    
    def __init__(self, parent):
        self.parent = parent
        self.window = None
    
    def show(self):
        """Muestra la ventana de ayuda"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Ayuda - CRM XTART")
        self.window.geometry("800x600")
        self.window.transient(self.parent)
        
        # Centrar ventana
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.window.winfo_screenheight() // 2) - (600 // 2)
        self.window.geometry(f"800x600+{x}+{y}")
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea los widgets de la ventana"""
        # Frame principal con scrollbar
        main_frame = ttk.Frame(self.window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas para scroll
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Contenido de ayuda
        content_frame = ttk.Frame(scrollable_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title = ttk.Label(content_frame, text="Ayuda - CRM XTART", 
                         font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # Secciones de ayuda
        sections = [
            {
                "title": "Inicio de Sesión",
                "content": """
Para acceder al sistema, ingrese su nombre de usuario y contraseña en la pantalla de login.
El sistema detectará automáticamente su rol (Empleado o Cliente) y mostrará las opciones correspondientes.
                """
            },
            {
                "title": "Dashboard",
                "content": """
El dashboard muestra un resumen de estadísticas y accesos rápidos a las diferentes secciones del sistema.
Desde aquí puede navegar rápidamente a cualquier módulo disponible según su rol.
                """
            },
            {
                "title": "Gestión de Entidades (Empleados)",
                "content": """
Los empleados tienen acceso completo a todas las entidades del sistema:
- Clientes: Gestión completa de clientes
- Empleados: Gestión de empleados y sus roles
- Productos: Catálogo de productos
- Presupuestos: Creación y seguimiento de presupuestos
- Facturas: Gestión de facturas
- Pagos: Registro y seguimiento de pagos

En cada pantalla puede:
- Crear nuevos registros (botón "Nuevo")
- Editar registros existentes (seleccionar y "Editar" o doble clic)
- Eliminar registros (seleccionar y "Eliminar")
- Filtrar y buscar registros
- Ordenar por columnas
- Navegar entre páginas si hay muchos registros
                """
            },
            {
                "title": "Funcionalidades para Clientes",
                "content": """
Los clientes pueden:
- Ver y editar su propio perfil
- Consultar sus facturas
- Ver su historial de pagos
- Modificar preferencias de pago

Los clientes NO pueden:
- Crear o eliminar otros clientes
- Gestionar empleados o productos
- Crear facturas o presupuestos
                """
            },
            {
                "title": "Filtros y Búsqueda",
                "content": """
En las pantallas de listado encontrará paneles de filtros que permiten:
- Buscar por diferentes campos (nombre, email, estado, etc.)
- Aplicar múltiples filtros simultáneamente
- Limpiar filtros para ver todos los registros

Los filtros se aplican en tiempo real y puede combinarlos según sus necesidades.
                """
            },
            {
                "title": "Validación de Datos",
                "content": """
El sistema valida automáticamente los datos ingresados:
- Campos obligatorios están marcados
- Emails deben tener formato válido
- Teléfonos deben tener formato correcto
- Fechas deben estar en formato YYYY-MM-DD
- Números deben ser valores numéricos válidos

Los campos inválidos se resaltan visualmente.
                """
            },
            {
                "title": "Informes y Gráficos",
                "content": """
Los empleados pueden acceder a informes visuales:
- Ventas por Empleado: Gráfico de barras mostrando el total de ventas por cada empleado
- Estado de Presupuestos: Gráfico circular mostrando la distribución de estados
- Facturación Mensual: Gráfico de líneas mostrando la evolución de la facturación

Los informes se actualizan automáticamente con los datos del sistema.
                """
            },
            {
                "title": "Atajos de Teclado",
                "content": """
- Ctrl+D: Ir al Dashboard
- Ctrl+Q: Cerrar sesión
- F1: Mostrar ayuda
- Enter: En formularios, puede presionar Enter para confirmar acciones
- Doble clic: En tablas, doble clic en una fila para editarla
                """
            },
            {
                "title": "Navegación",
                "content": """
Puede navegar por el sistema usando:
- Menú superior: Acceso a todas las secciones
- Barra de herramientas: Accesos rápidos
- Botones en el dashboard: Acceso directo a módulos

La barra de estado en la parte inferior muestra información sobre la sección actual.
                """
            },
            {
                "title": "Soporte",
                "content": """
Para más información o soporte técnico, consulte la documentación del sistema
o contacte con el administrador del sistema.
                """
            }
        ]
        
        # Mostrar secciones
        for section in sections:
            section_frame = ttk.LabelFrame(content_frame, text=section["title"], padding=10)
            section_frame.pack(fill=tk.X, pady=5)
            
            content_label = ttk.Label(section_frame, text=section["content"].strip(), 
                                     wraplength=750, justify=tk.LEFT)
            content_label.pack(anchor="w")
        
        # Pack canvas y scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botón cerrar
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Cerrar", 
                  command=self.window.destroy).pack()

