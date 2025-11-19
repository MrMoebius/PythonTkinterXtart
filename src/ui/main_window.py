"""
Ventana principal de la aplicación
"""

import tkinter as tk
from tkinter import ttk, messagebox
from src.api.rest_client import RESTClient, UserRole
from src.ui.dashboard import DashboardWindow
from src.ui.entities.clientes_window import ClientesWindow
from src.ui.entities.empleados_window import EmpleadosWindow
from src.ui.entities.productos_window import ProductosWindow
from src.ui.entities.presupuestos_window import PresupuestosWindow
from src.ui.entities.facturas_window import FacturasWindow
from src.ui.entities.pagos_window import PagosWindow
from src.ui.reports_window import ReportsWindow
from src.ui.help_window import HelpWindow

class MainWindow:
    """Ventana principal con menú y navegación"""
    
    def __init__(self, root, api: RESTClient):
        self.root = root
        self.api = api
        self.window = None
        self.current_frame = None
    
    def show(self):
        """Muestra la ventana principal"""
        self.root.deiconify()
        self.root.title("CRM XTART - Sistema de Gestión")
        self.root.geometry("1200x800")
        
        # Centrar ventana
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"1200x800+{x}+{y}")
        
        self._create_menu()
        self._create_toolbar()
        self._create_statusbar()
        
        # Mostrar dashboard por defecto
        self.show_dashboard()
    
    def _create_menu(self):
        """Crea el menú principal"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Dashboard", command=self.show_dashboard, accelerator="Ctrl+D")
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self._logout, accelerator="Ctrl+Q")
        
        # Menú según rol
        if self.api.user_role == UserRole.EMPLEADO:
            # Menú Gestión
            gestion_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Gestión", menu=gestion_menu)
            gestion_menu.add_command(label="Clientes", command=self.show_clientes)
            gestion_menu.add_command(label="Empleados", command=self.show_empleados)
            gestion_menu.add_command(label="Productos", command=self.show_productos)
            gestion_menu.add_command(label="Presupuestos", command=self.show_presupuestos)
            gestion_menu.add_command(label="Facturas", command=self.show_facturas)
            gestion_menu.add_command(label="Pagos", command=self.show_pagos)
            
            # Menú Informes
            reports_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Informes", menu=reports_menu)
            reports_menu.add_command(label="Ver Informes", command=self.show_reports)
        
        else:  # CLIENTE
            # Menú Cliente
            cliente_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Mi Cuenta", menu=cliente_menu)
            cliente_menu.add_command(label="Mi Perfil", command=self.show_my_profile)
            cliente_menu.add_command(label="Mis Facturas", command=self.show_my_facturas)
            cliente_menu.add_command(label="Mis Pagos", command=self.show_my_pagos)
        
        # Menú Ayuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Ayuda", command=self.show_help, accelerator="F1")
        help_menu.add_command(label="Acerca de", command=self._show_about)
        
        # Atajos de teclado
        self.root.bind("<Control-d>", lambda e: self.show_dashboard())
        self.root.bind("<Control-q>", lambda e: self._logout())
        self.root.bind("<F1>", lambda e: self.show_help())
    
    def _create_toolbar(self):
        """Crea la barra de herramientas"""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Botón Dashboard
        ttk.Button(toolbar, text="Dashboard", command=self.show_dashboard).pack(side=tk.LEFT, padx=2)
        
        if self.api.user_role == UserRole.EMPLEADO:
            ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
            ttk.Button(toolbar, text="Clientes", command=self.show_clientes).pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="Empleados", command=self.show_empleados).pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="Productos", command=self.show_productos).pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="Presupuestos", command=self.show_presupuestos).pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="Facturas", command=self.show_facturas).pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="Pagos", command=self.show_pagos).pack(side=tk.LEFT, padx=2)
            ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
            ttk.Button(toolbar, text="Informes", command=self.show_reports).pack(side=tk.LEFT, padx=2)
        else:
            ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
            ttk.Button(toolbar, text="Mi Perfil", command=self.show_my_profile).pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="Mis Facturas", command=self.show_my_facturas).pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="Mis Pagos", command=self.show_my_pagos).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        ttk.Button(toolbar, text="Ayuda", command=self.show_help).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Salir", command=self._logout).pack(side=tk.LEFT, padx=2)
        
        # Info de usuario
        user_info = ttk.Label(toolbar, 
                            text=f"Usuario: {self.api.user_id} | Rol: {self.api.user_role.value if self.api.user_role else 'N/A'}",
                            font=("Arial", 9))
        user_info.pack(side=tk.RIGHT, padx=10)
    
    def _create_statusbar(self):
        """Crea la barra de estado"""
        self.statusbar = ttk.Label(self.root, text="Listo", relief=tk.SUNKEN, anchor=tk.W)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _set_status(self, message: str):
        """Actualiza el mensaje de la barra de estado"""
        self.statusbar.config(text=message)
    
    def _clear_frame(self):
        """Limpia el frame actual"""
        if self.current_frame:
            self.current_frame.destroy()
            self.current_frame = None
    
    def show_dashboard(self):
        """Muestra el dashboard"""
        self._clear_frame()
        self.current_frame = DashboardWindow(self.root, self.api, navigation_callback=self)
        self.current_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._set_status("Dashboard - Panel de resumen")
    
    def show_clientes(self):
        """Muestra la gestión de clientes"""
        if self.api.user_role != UserRole.EMPLEADO:
            messagebox.showwarning("Acceso Denegado", "No tiene permisos para acceder a esta sección")
            return
        self._clear_frame()
        self.current_frame = ClientesWindow(self.root, self.api)
        self.current_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._set_status("Gestión de Clientes")
    
    def show_empleados(self):
        """Muestra la gestión de empleados"""
        if self.api.user_role != UserRole.EMPLEADO:
            messagebox.showwarning("Acceso Denegado", "No tiene permisos para acceder a esta sección")
            return
        self._clear_frame()
        self.current_frame = EmpleadosWindow(self.root, self.api)
        self.current_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._set_status("Gestión de Empleados")
    
    def show_productos(self):
        """Muestra la gestión de productos"""
        if self.api.user_role != UserRole.EMPLEADO:
            messagebox.showwarning("Acceso Denegado", "No tiene permisos para acceder a esta sección")
            return
        self._clear_frame()
        self.current_frame = ProductosWindow(self.root, self.api)
        self.current_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._set_status("Gestión de Productos")
    
    def show_presupuestos(self):
        """Muestra la gestión de presupuestos"""
        if self.api.user_role != UserRole.EMPLEADO:
            messagebox.showwarning("Acceso Denegado", "No tiene permisos para acceder a esta sección")
            return
        self._clear_frame()
        self.current_frame = PresupuestosWindow(self.root, self.api)
        self.current_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._set_status("Gestión de Presupuestos")
    
    def show_facturas(self):
        """Muestra la gestión de facturas"""
        if self.api.user_role != UserRole.EMPLEADO:
            messagebox.showwarning("Acceso Denegado", "No tiene permisos para acceder a esta sección")
            return
        self._clear_frame()
        self.current_frame = FacturasWindow(self.root, self.api)
        self.current_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._set_status("Gestión de Facturas")
    
    def show_pagos(self):
        """Muestra la gestión de pagos"""
        if self.api.user_role != UserRole.EMPLEADO:
            messagebox.showwarning("Acceso Denegado", "No tiene permisos para acceder a esta sección")
            return
        self._clear_frame()
        self.current_frame = PagosWindow(self.root, self.api)
        self.current_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._set_status("Gestión de Pagos")
    
    def show_my_profile(self):
        """Muestra el perfil del cliente"""
        if self.api.user_role != UserRole.CLIENTE:
            messagebox.showwarning("Acceso Denegado", "Esta sección es solo para clientes")
            return
        self._clear_frame()
        # Reutilizar ClientesWindow pero en modo solo lectura/edición propia
        self.current_frame = ClientesWindow(self.root, self.api, client_mode=True)
        self.current_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._set_status("Mi Perfil")
    
    def show_my_facturas(self):
        """Muestra las facturas del cliente"""
        if self.api.user_role != UserRole.CLIENTE:
            messagebox.showwarning("Acceso Denegado", "Esta sección es solo para clientes")
            return
        self._clear_frame()
        self.current_frame = FacturasWindow(self.root, self.api, client_mode=True)
        self.current_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._set_status("Mis Facturas")
    
    def show_my_pagos(self):
        """Muestra los pagos del cliente"""
        if self.api.user_role != UserRole.CLIENTE:
            messagebox.showwarning("Acceso Denegado", "Esta sección es solo para clientes")
            return
        self._clear_frame()
        self.current_frame = PagosWindow(self.root, self.api, client_mode=True)
        self.current_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._set_status("Mis Pagos")
    
    def show_reports(self):
        """Muestra los informes"""
        if self.api.user_role != UserRole.EMPLEADO:
            messagebox.showwarning("Acceso Denegado", "No tiene permisos para acceder a esta sección")
            return
        self._clear_frame()
        self.current_frame = ReportsWindow(self.root, self.api)
        self.current_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._set_status("Informes y Gráficos")
    
    def show_help(self):
        """Muestra la ventana de ayuda"""
        help_window = HelpWindow(self.root)
        help_window.show()
    
    def _show_about(self):
        """Muestra información sobre la aplicación"""
        messagebox.showinfo("Acerca de CRM XTART", 
                          "CRM XTART - Sistema de Gestión\n\n"
                          "Versión 1.0\n"
                          "Cliente de Escritorio en Python/Tkinter\n\n"
                          "Desarrollado para gestión completa de entidades CRM")
    
    def _logout(self):
        """Cierra sesión y vuelve al login"""
        if messagebox.askyesno("Confirmar", "¿Desea cerrar sesión?"):
            self.api.logout()
            self._clear_frame()
            self.root.withdraw()
            
            # Volver a mostrar login
            from src.ui.login_window import LoginWindow
            login = LoginWindow(self.root)
            login.show()

