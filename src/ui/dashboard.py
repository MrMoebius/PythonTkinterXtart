"""
Ventana del Dashboard
"""

import tkinter as tk
from tkinter import ttk
from src.api.rest_client import RESTClient, UserRole

class DashboardWindow(ttk.Frame):
    """Panel de resumen y acceso rápido"""
    
    def __init__(self, parent, api: RESTClient, navigation_callback=None):
        super().__init__(parent)
        self.api = api
        self.navigation_callback = navigation_callback
        self._create_widgets()
        self._load_stats()
    
    def _create_widgets(self):
        """Crea los widgets del dashboard"""
        # Título
        title_frame = ttk.Frame(self)
        title_frame.pack(fill=tk.X, pady=10)
        
        title_label = ttk.Label(title_frame, text="Dashboard", 
                               font=("Arial", 18, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Frame de estadísticas
        stats_frame = ttk.LabelFrame(self, text="Estadísticas Generales", padding=10)
        stats_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.stats_container = ttk.Frame(stats_frame)
        self.stats_container.pack(fill=tk.BOTH, expand=True)
        
        # Frame de accesos rápidos
        if self.api.user_role == UserRole.EMPLEADO:
            quick_access_frame = ttk.LabelFrame(self, text="Accesos Rápidos", padding=10)
            quick_access_frame.pack(fill=tk.X, pady=10)
            
            buttons_frame = ttk.Frame(quick_access_frame)
            buttons_frame.pack()
            
            quick_actions = [
                ("Clientes", "show_clientes"),
                ("Empleados", "show_empleados"),
                ("Productos", "show_productos"),
                ("Presupuestos", "show_presupuestos"),
                ("Facturas", "show_facturas"),
                ("Pagos", "show_pagos"),
                ("Informes", "show_reports"),
            ]
            
            for i, (text, method_name) in enumerate(quick_actions):
                def make_command(method=method_name):
                    return lambda: self._navigate(method)
                btn = ttk.Button(buttons_frame, text=text, command=make_command(), width=15)
                btn.grid(row=i//4, column=i%4, padx=5, pady=5)
    
    def _navigate(self, method_name):
        """Navega a una sección usando el callback"""
        if self.navigation_callback:
            method = getattr(self.navigation_callback, method_name, None)
            if method:
                method()
            
            for i, (text, command) in enumerate(quick_actions):
                btn = ttk.Button(buttons_frame, text=text, command=command, width=15)
                btn.grid(row=i//4, column=i%4, padx=5, pady=5)
    
    def _load_stats(self):
        """Carga las estadísticas"""
        # Limpiar estadísticas anteriores
        for widget in self.stats_container.winfo_children():
            widget.destroy()
        
        if self.api.user_role == UserRole.EMPLEADO:
            # Estadísticas para empleado
            stats = self.api.get_dashboard_stats()
            
            if stats.get("success"):
                data = stats.get("data", {})
                
                stats_grid = ttk.Frame(self.stats_container)
                stats_grid.pack(fill=tk.BOTH, expand=True)
                
                stat_items = [
                    ("Clientes", data.get("clientes", 0), "#4CAF50"),
                    ("Empleados", data.get("empleados", 0), "#2196F3"),
                    ("Productos", data.get("productos", 0), "#FF9800"),
                    ("Presupuestos", data.get("presupuestos", 0), "#9C27B0"),
                    ("Facturas", data.get("facturas", 0), "#F44336"),
                    ("Pagos", data.get("pagos", 0), "#00BCD4"),
                ]
                
                for i, (label, value, color) in enumerate(stat_items):
                    stat_frame = ttk.Frame(stats_grid)
                    stat_frame.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="nsew")
                    
                    value_label = ttk.Label(stat_frame, text=str(value), 
                                           font=("Arial", 24, "bold"),
                                           foreground=color)
                    value_label.pack()
                    
                    label_label = ttk.Label(stat_frame, text=label, 
                                           font=("Arial", 12))
                    label_label.pack()
                
                # Configurar pesos
                for i in range(3):
                    stats_grid.columnconfigure(i, weight=1)
            
        else:
            # Estadísticas para cliente
            cliente_frame = ttk.Frame(self.stats_container)
            cliente_frame.pack(fill=tk.BOTH, expand=True)
            
            # Obtener facturas del cliente
            facturas_result = self.api.get_my_facturas()
            num_facturas = 0
            if facturas_result.get("success"):
                num_facturas = len(facturas_result.get("data", []))
            
            # Obtener pagos del cliente
            pagos_result = self.api.get_my_pagos()
            num_pagos = 0
            if pagos_result.get("success"):
                num_pagos = len(pagos_result.get("data", []))
            
            ttk.Label(cliente_frame, text=f"Mis Facturas: {num_facturas}", 
                     font=("Arial", 14)).pack(pady=10)
            ttk.Label(cliente_frame, text=f"Mis Pagos: {num_pagos}", 
                     font=("Arial", 14)).pack(pady=10)

