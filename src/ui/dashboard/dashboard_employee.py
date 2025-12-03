import customtkinter as ctk
from .dashboard_base import DashboardBase

class EmployeeDashboardView(DashboardBase):
    @property
    def show_quick_access(self):
        return False  # Ya no se muestran botones, las tarjetas son clicables

    def _build_quick_access(self, parent):
        pass  # No se usa, las tarjetas de estadísticas son clicables

    def _navigate(self, method_name):
        """Navega a la ventana correspondiente"""
        if not self.navigation:
            return
        method = getattr(self.navigation, method_name, None)
        if method:
            method()

    # -------------------------------------------------------------
    # ESTADÍSTICAS — empleado (sin empleados)
    # -------------------------------------------------------------
    def _load_stats(self):
        for w in self.stats_container.winfo_children():
            w.destroy()

        result = self.api.get_dashboard_stats()
        if not result.get("success"):
            ctk.CTkLabel(
                self.stats_container,
                text="Error cargando estadísticas",
                text_color="#ff2a2a"
            ).pack()
            return

        data = result.get("data", {})

        items = [
            ("Clientes", data.get("clientes", 0), "#43B64A"),
            ("Productos", data.get("productos", 0), "#FF9800"),
            ("Presupuestos", data.get("presupuestos", 0), "#9933cc"),
            ("Facturas", data.get("facturas", 0), "#ff2a2a"),
            ("Pagos", data.get("pagos", 0), "#00BCD4"),
            ("Informes", "-", "#607D8B"),
        ]

        grid = ctk.CTkFrame(self.stats_container, fg_color="#252932")
        grid.pack(fill="both", expand=True, pady=8)

        # Mapeo de labels a métodos de navegación
        navigation_map = {
            "Clientes": "show_clientes",
            "Productos": "show_productos",
            "Presupuestos": "show_presupuestos",
            "Facturas": "show_facturas",
            "Pagos": "show_pagos",
            "Informes": "show_reports",
        }

        for i, (label, value, color) in enumerate(items):
            # Crear frame clicable
            frame = ctk.CTkFrame(grid, fg_color="#29304a", corner_radius=12)
            frame.grid(row=i // 3, column=i % 3, padx=18, pady=14, sticky="nsew")
            
            # Hacer el frame clicable si tiene navegación
            method_name = navigation_map.get(label)
            if method_name and self.navigation:
                # Colores para efecto hover
                original_color = "#29304a"
                hover_color = "#2d3542"
                
                # Funciones auxiliares para eventos
                def make_enter_handler(f):
                    return lambda e: f.configure(fg_color=hover_color)
                
                def make_leave_handler(f):
                    return lambda e: f.configure(fg_color=original_color)
                
                def make_click_handler(m):
                    return lambda e: self._navigate(m)
                
                # Bind eventos al frame
                frame.bind("<Enter>", make_enter_handler(frame))
                frame.bind("<Leave>", make_leave_handler(frame))
                frame.bind("<Button-1>", make_click_handler(method_name))

            value_label = ctk.CTkLabel(
                frame,
                text=str(value),
                font=("Arial", 24, "bold"),
                text_color=color
            )
            value_label.pack(pady=(12, 4))

            label_widget = ctk.CTkLabel(
                frame,
                text=label,
                font=("Arial", 13),
                text_color="white"
            )
            label_widget.pack(pady=(0, 12))
            
            # Hacer los labels también clicables
            if method_name and self.navigation:
                def make_enter_handler_label(f):
                    return lambda e: f.configure(fg_color=hover_color)
                
                def make_leave_handler_label(f):
                    return lambda e: f.configure(fg_color=original_color)
                
                def make_click_handler_label(m):
                    return lambda e: self._navigate(m)
                
                value_label.bind("<Button-1>", make_click_handler_label(method_name))
                value_label.bind("<Enter>", make_enter_handler_label(frame))
                value_label.bind("<Leave>", make_leave_handler_label(frame))
                
                label_widget.bind("<Button-1>", make_click_handler_label(method_name))
                label_widget.bind("<Enter>", make_enter_handler_label(frame))
                label_widget.bind("<Leave>", make_leave_handler_label(frame))

        for i in range(3):
            grid.grid_columnconfigure(i, weight=1)
            
    def show_dashboard(self):
        self.clear_content()
        view = EmployeeDashboardView(self.content, self.api, self)
        view.pack(fill="both", expand=True)