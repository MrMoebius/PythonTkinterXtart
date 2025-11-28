import customtkinter as ctk

class DashboardWindow(ctk.CTkFrame):
    """Panel de resumen y acceso rápido"""

    def __init__(self, parent, api, navigation_callback=None):
        super().__init__(parent, fg_color="#23243a", corner_radius=20)
        self.api = api
        self.navigation = navigation_callback
        self.role = str(getattr(api, "user_role", "CLIENTE")).upper()
        self._create_widgets()
        self._load_stats()

    # =====================================================================
    # WIDGETS
    # =====================================================================
    def _create_widgets(self):
        # Título
        title = ctk.CTkLabel(
            self, text="Dashboard", font=("Arial", 26, "bold"), text_color="white"
        )
        title.pack(pady=14)

        # Contenedor estadísticas
        stats_frame = ctk.CTkFrame(self, fg_color="#252932", corner_radius=16)
        stats_frame.pack(fill="x", padx=24, pady=12)

        self.stats_container = ctk.CTkFrame(stats_frame, fg_color="#252932", corner_radius=0)
        self.stats_container.pack(fill="both", expand=True, pady=6)

        # Accesos rápidos (ADMIN + EMPLEADO)
        if self.role in ("ADMIN", "EMPLEADO") and self.navigation:
            quick_frame = ctk.CTkFrame(self, fg_color="#252932", corner_radius=16)
            quick_frame.pack(fill="x", padx=24, pady=10)
            self._build_quick_access(quick_frame)

    # =====================================================================
    # ACCESOS RÁPIDOS
    # =====================================================================
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
        if self.role != "ADMIN":
            buttons = [b for b in buttons if b[1] != "show_empleados"]

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

    # =====================================================================
    # ESTADÍSTICAS
    # =====================================================================
    def _load_stats(self):
        for widget in self.stats_container.winfo_children():
            widget.destroy()

        if self.role in ("ADMIN", "EMPLEADO"):
            self._load_stats_admin()
        else:
            self._load_stats_cliente()

    # =====================================================================
    # STATS ADMIN / EMPLEADO
    # =====================================================================
    def _load_stats_admin(self):
        result = self.api.get_dashboard_stats()
        if not result.get("success"):
            ctk.CTkLabel(self.stats_container, text="Error cargando estadísticas", text_color="#ff2a2a").pack()
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
        if self.role != "ADMIN":
            items = [i for i in items if i[0] != "Empleados"]

        grid = ctk.CTkFrame(self.stats_container, fg_color="#252932")
        grid.pack(fill="both", expand=True, pady=8)

        for i, (label, value, color) in enumerate(items):
            frame = ctk.CTkFrame(
                grid, fg_color="#29304a", corner_radius=12
            )
            frame.grid(row=i // 3, column=i % 3, padx=18, pady=14, sticky="nsew")
            ctk.CTkLabel(
                frame,
                text=str(value),
                font=("Arial", 24, "bold"),
                text_color=color,
                fg_color=None,
            ).pack(pady=(12, 4))
            ctk.CTkLabel(
                frame, text=label, font=("Arial", 13), text_color="white"
            ).pack(pady=(0, 12))

        for i in range(3):
            grid.grid_columnconfigure(i, weight=1)

    # =====================================================================
    # STATS CLIENTE
    # =====================================================================
    def _load_stats_cliente(self):
        frame = ctk.CTkFrame(self.stats_container, fg_color="#29304a", corner_radius=12)
        frame.pack(fill="both", expand=True, padx=32, pady=14)

        facturas = self.api.get_my_facturas()
        pagos = self.api.get_my_pagos()

        num_facturas = len(facturas.get("data", [])) if facturas.get("success") else 0
        num_pagos = len(pagos.get("data", [])) if pagos.get("success") else 0

        ctk.CTkLabel(
            frame,
            text=f"Mis Facturas: {num_facturas}",
            font=("Arial", 16, "bold"),
            text_color="#ff2a2a").pack(pady=16)
        ctk.CTkLabel(
            frame,
            text=f"Mis Pagos: {num_pagos}",
            font=("Arial", 16, "bold"),
            text_color="#43B64A").pack(pady=16)
