import customtkinter as ctk
from .dashboard_base import DashboardBase

class ClientDashboardView(DashboardBase):
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
    # ESTADÍSTICAS — cliente
    # -------------------------------------------------------------
    def _load_stats(self):
        for w in self.stats_container.winfo_children():
            w.destroy()

        try:
            # Obtener ID del cliente
            cliente_id = getattr(self.api, "user_id", None)
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Dashboard cliente - user_id: {cliente_id}")
            
            # Obtener datos del cliente
            facturas = self.api.get_my_facturas(cliente_id)
            pagos = self.api.get_my_pagos(cliente_id)
            
            # Obtener presupuestos del cliente (filtrar por cliente_pagador o cliente_beneficiario)
            presupuestos = self.api.get_all("presupuestos")
            
            # Manejar respuestas de manera segura
            facturas_data = facturas.get("data") if facturas.get("success") else []
            pagos_data = pagos.get("data") if pagos.get("success") else []
            presupuestos_data = presupuestos.get("data") if presupuestos.get("success") else []
            
            logger.info(f"Dashboard cliente - facturas: {len(facturas_data) if isinstance(facturas_data, list) else 0}, pagos: {len(pagos_data) if isinstance(pagos_data, list) else 0}")
            
            # Asegurar que son listas
            if not isinstance(facturas_data, list):
                facturas_data = []
            if not isinstance(pagos_data, list):
                pagos_data = []
            if not isinstance(presupuestos_data, list):
                presupuestos_data = []
            
            # Filtrar presupuestos del cliente actual
            cliente_id = getattr(self.api, "user_id", None)
            if cliente_id and presupuestos_data:
                try:
                    cliente_id_int = int(cliente_id)
                    presupuestos_cliente = []
                    for p in presupuestos_data:
                        if not isinstance(p, dict):
                            continue
                        # Intentar obtener IDs de diferentes formas
                        pagador_id = p.get("id_cliente_pagador")
                        beneficiario_id = p.get("id_cliente_beneficiario")
                        
                        # Comparar IDs (convertir a int para comparación segura)
                        try:
                            if pagador_id is not None and int(pagador_id) == cliente_id_int:
                                presupuestos_cliente.append(p)
                                continue
                            if beneficiario_id is not None and int(beneficiario_id) == cliente_id_int:
                                presupuestos_cliente.append(p)
                        except (ValueError, TypeError):
                            # Si no se puede convertir, comparar directamente
                            if pagador_id == cliente_id or beneficiario_id == cliente_id:
                                presupuestos_cliente.append(p)
                except (ValueError, TypeError):
                    logger.warning(f"No se pudo convertir cliente_id a int: {cliente_id}")
                    presupuestos_cliente = []
            else:
                presupuestos_cliente = []
                if not cliente_id:
                    logger.warning("cliente_id no disponible en dashboard cliente")

            num_facturas = len(facturas_data)
            num_pagos = len(pagos_data)
            num_presupuestos = len(presupuestos_cliente)

            items = [
                ("Perfil", "-", "#2491ed"),
                ("Presupuestos", num_presupuestos, "#9933cc"),
                ("Facturas", num_facturas, "#ff2a2a"),
                ("Pagos", num_pagos, "#00BCD4"),
            ]

            grid = ctk.CTkFrame(self.stats_container, fg_color="#252932")
            grid.pack(fill="both", expand=True, pady=8)

            # Mapeo de labels a métodos de navegación
            navigation_map = {
                "Perfil": "show_my_profile",
                "Presupuestos": "show_my_presupuestos",
                "Facturas": "show_my_facturas",
                "Pagos": "show_my_pagos",
            }

            for i, (label, value, color) in enumerate(items):
                # Crear frame clicable
                frame = ctk.CTkFrame(grid, fg_color="#29304a", corner_radius=12)
                frame.grid(row=i // 2, column=i % 2, padx=18, pady=14, sticky="nsew")
                
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
                
                # Hacer los labels clicables
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

            for i in range(2):
                grid.grid_columnconfigure(i, weight=1)

        except Exception as e:
            # Mostrar mensaje de error
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error cargando estadísticas del cliente: {e}", exc_info=True)
            ctk.CTkLabel(
                self.stats_container,
                text=f"Error cargando estadísticas: {str(e)[:50]}",
                font=("Arial", 12),
                text_color="#ff2a2a",
            ).pack(pady=16)

