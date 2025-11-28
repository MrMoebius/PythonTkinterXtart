import customtkinter as ctk
from .dashboard_base import DashboardBase

class AdminDashboardView(DashboardBase):
    @property
    def show_quick_access(self):
        return True

    # -------------------------------------------------------------
    # ACCESOS RÁPIDOS — Admin ve todo
    # -------------------------------------------------------------
    def _build_quick_access(self, parent):
        buttons = [
            ("Clientes", "show_clientes"),
            ("Empleados", "show_empleados"),
            ("Productos", "show_productos"),
            ("Presupuestos", "show_presupuestos"),
            ("Facturas", "show_facturas"),
            ("Pagos", "show_pagos"),
            ("Informes", "show_reports"),
        ]

        frame = ctk.CTkFrame(parent, fg_color="#252932")
        frame.pack()

        for i, (text, method_name) in enumerate(buttons):
            btn = ctk.CTkButton(
                frame,
                text=text,
                width=130,
                height=34,
                corner_radius=12,
                font=("Arial", 12, "bold"),
                fg_color="#2491ed",
                hover_color="#137bd6",
                text_color="white",
                command=lambda m=method_name: self._navigate(m),
            )
            btn.grid(row=i // 4, column=i % 4, padx=8, pady=7)

    def _navigate(self, method_name):
        if not self.navigation:
            return
        method = getattr(self.navigation, method_name, None)
        if method:
            method()

    # -------------------------------------------------------------
    # ESTADÍSTICAS — admin ve todo
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
            ("Empleados", data.get("empleados", 0), "#2491ed"),
            ("Productos", data.get("productos", 0), "#FF9800"),
            ("Presupuestos", data.get("presupuestos", 0), "#9933cc"),
            ("Facturas", data.get("facturas", 0), "#ff2a2a"),
            ("Pagos", data.get("pagos", 0), "#00BCD4"),
        ]

        grid = ctk.CTkFrame(self.stats_container, fg_color="#252932")
        grid.pack(fill="both", expand=True, pady=8)

        for i, (label, value, color) in enumerate(items):
            frame = ctk.CTkFrame(grid, fg_color="#29304a", corner_radius=12)
            frame.grid(row=i // 3, column=i % 3, padx=18, pady=14, sticky="nsew")

            ctk.CTkLabel(
                frame, text=str(value),
                font=("Arial", 24, "bold"),
                text_color=color
            ).pack(pady=(12, 4))

            ctk.CTkLabel(
                frame, text=label,
                font=("Arial", 13),
                text_color="white"
            ).pack(pady=(0, 12))

        for i in range(3):
            grid.grid_columnconfigure(i, weight=1)

    def show_dashboard(self):
        self.clear_content()
        view = AdminDashboardView(self.content, self.api, self)
        view.pack(fill="both", expand=True)
