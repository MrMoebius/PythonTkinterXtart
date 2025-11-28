import customtkinter as ctk
from .dashboard_base import DashboardBase

class ClientDashboardView(DashboardBase):
    @property
    def show_quick_access(self):
        return False  # NO muestra accesos rápidos

    def _build_quick_access(self, parent):
        pass  # no se usa para cliente

    # -------------------------------------------------------------
    # ESTADÍSTICAS — cliente
    # -------------------------------------------------------------
    def _load_stats(self):
        for w in self.stats_container.winfo_children():
            w.destroy()

        frame = ctk.CTkFrame(self.stats_container, fg_color="#29304a", corner_radius=12)
        frame.pack(fill="both", expand=True, padx=32, pady=14)

        try:
            facturas = self.api.get_my_facturas()
            pagos = self.api.get_my_pagos()

            # Manejar respuestas de manera segura
            facturas_data = facturas.get("data") if facturas.get("success") else []
            pagos_data = pagos.get("data") if pagos.get("success") else []
            
            # Asegurar que son listas
            if not isinstance(facturas_data, list):
                facturas_data = []
            if not isinstance(pagos_data, list):
                pagos_data = []

            num_facturas = len(facturas_data)
            num_pagos = len(pagos_data)

            ctk.CTkLabel(
                frame,
                text=f"Mis Facturas: {num_facturas}",
                font=("Arial", 16, "bold"),
                text_color="#ff2a2a",
            ).pack(pady=16)

            ctk.CTkLabel(
                frame,
                text=f"Mis Pagos: {num_pagos}",
                font=("Arial", 16, "bold"),
                text_color="#43B64A",
            ).pack(pady=16)
        except Exception as e:
            # Mostrar mensaje de error
            ctk.CTkLabel(
                frame,
                text=f"Error cargando estadísticas: {str(e)}",
                font=("Arial", 12),
                text_color="#ff2a2a",
            ).pack(pady=16)

