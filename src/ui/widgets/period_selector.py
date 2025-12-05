"""
Selector de período con opciones rápidas y modo personalizado
"""

import customtkinter as ctk
from datetime import datetime, timedelta
from calendar import monthrange


class PeriodSelector(ctk.CTkFrame):
    """
    Selector de período con opciones rápidas (Esta semana, Este mes, Este año)
    y modo personalizado con selectores separados de día/mes/año
    """
    
    def __init__(self, master, on_period_change=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.on_period_change = on_period_change
        self.current_mode = "personalizado"  # "esta_semana", "este_mes", "este_año", "personalizado"
        self.fecha_desde = datetime.now()
        self.fecha_hasta = datetime.now()
        
        self._build_ui()
        self._set_default_period()
    
    def _build_ui(self):
        """Construye la interfaz del selector"""
        # Botón principal desplegable (hereda colores del tema por defecto)
        self.main_button = ctk.CTkButton(
            self,
            text="Seleccionar período ▼",
            command=self._toggle_dropdown,
            width=130,  # Ancho reducido
            anchor="w",
        )
        self.main_button.pack(side="left", padx=5)
        
        # Frame para el panel personalizado (inicialmente oculto)
        self.custom_panel = ctk.CTkFrame(self, fg_color="transparent")
        # No se empaqueta inicialmente, solo cuando se selecciona "Personalizado"
        
        # Popover para opciones rápidas
        self.popover = None
    
    def _toggle_dropdown(self):
        """Abre/cierra el menú desplegable"""
        if self.popover and self.popover.winfo_exists():
            self.popover.destroy()
            self.popover = None
            return
        
        # Crear popover
        self.popover = ctk.CTkToplevel(self)
        self.popover.overrideredirect(True)
        self.popover.configure(fg_color="#232323")
        
        # Opciones rápidas
        options = [
            ("Esta semana", "esta_semana"),
            ("Este mes", "este_mes"),
            ("Este año", "este_año"),
            ("Personalizado", "personalizado")
        ]
        
        frame = ctk.CTkFrame(self.popover, fg_color="#232323", corner_radius=8)
        frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        for text, mode in options:
            btn = ctk.CTkButton(
                frame,
                text=text,
                command=lambda m=mode: self._select_option(m),
                fg_color="#353535",
                hover_color="#454545",
                anchor="w",
                width=120,  # Ancho reducido para las opciones
                height=32  # Altura más pequeña para botones más compactos
            )
            btn.pack(fill="x", padx=4, pady=1)  # Padding vertical reducido
        
        # Posicionar popover (altura más compacta, ancho reducido)
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        self.popover.geometry(f"150x{len(options) * 34 + 8}+{x}+{y}")  # Ancho y altura reducidos
        self.popover.focus_force()
    
    def _select_option(self, mode):
        """Selecciona una opción rápida o activa modo personalizado"""
        if self.popover:
            self.popover.destroy()
            self.popover = None
        
        self.current_mode = mode
        
        if mode == "personalizado":
            self._show_custom_panel()
        else:
            self._hide_custom_panel()
            self._apply_quick_period(mode)
            self._update_button_text()
            if self.on_period_change:
                self.on_period_change(self.get_desde(), self.get_hasta())
    
    def _apply_quick_period(self, mode):
        """Aplica un período rápido"""
        hoy = datetime.now()
        
        if mode == "esta_semana":
            # Lunes de esta semana hasta domingo
            lunes = hoy - timedelta(days=hoy.weekday())
            domingo = lunes + timedelta(days=6)
            self.fecha_desde = lunes.replace(hour=0, minute=0, second=0, microsecond=0)
            self.fecha_hasta = domingo.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        elif mode == "este_mes":
            # Primer día del mes hasta último día del mes
            self.fecha_desde = datetime(hoy.year, hoy.month, 1)
            ultimo_dia = monthrange(hoy.year, hoy.month)[1]
            self.fecha_hasta = datetime(hoy.year, hoy.month, ultimo_dia, 23, 59, 59, 999999)
        
        elif mode == "este_año":
            # 1 de enero hasta 31 de diciembre
            self.fecha_desde = datetime(hoy.year, 1, 1)
            self.fecha_hasta = datetime(hoy.year, 12, 31, 23, 59, 59, 999999)
    
    def _show_custom_panel(self):
        """Muestra el panel de selección personalizada"""
        if self.custom_panel.winfo_ismapped():
            return
        
        # Limpiar panel si ya existe
        for widget in self.custom_panel.winfo_children():
            widget.destroy()
        
        # Frame "Desde"
        desde_frame = ctk.CTkFrame(self.custom_panel, fg_color="transparent")
        desde_frame.pack(side="left", padx=10)
        
        ctk.CTkLabel(
            desde_frame,
            text="Desde:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#293553"
        ).pack(side="left", padx=5)
        
        # Selectores Desde
        self.desde_dia = self._create_day_selector(desde_frame, "desde")
        self.desde_mes = self._create_month_selector(desde_frame, "desde")
        self.desde_año = self._create_year_selector(desde_frame, "desde")
        
        # Frame "Hasta"
        hasta_frame = ctk.CTkFrame(self.custom_panel, fg_color="transparent")
        hasta_frame.pack(side="left", padx=10)
        
        ctk.CTkLabel(
            hasta_frame,
            text="Hasta:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#293553"
        ).pack(side="left", padx=5)
        
        # Selectores Hasta
        self.hasta_dia = self._create_day_selector(hasta_frame, "hasta")
        self.hasta_mes = self._create_month_selector(hasta_frame, "hasta")
        self.hasta_año = self._create_year_selector(hasta_frame, "hasta")
        
        # Inicializar valores
        self._update_custom_selectors()
        
        # Empaquetar panel
        self.custom_panel.pack(side="left", padx=5)
        
        # Actualizar texto del botón
        self.main_button.configure(text="Personalizado ▼")
    
    def _hide_custom_panel(self):
        """Oculta el panel de selección personalizada"""
        if self.custom_panel.winfo_ismapped():
            self.custom_panel.pack_forget()
    
    def _create_day_selector(self, parent, tipo):
        """Crea un selector de día (1-31)"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(side="left", padx=2)
        
        # Valores iniciales
        hoy = datetime.now()
        if tipo == "desde":
            mes_actual = self.fecha_desde.month
            año_actual = self.fecha_desde.year
        else:
            mes_actual = self.fecha_hasta.month
            año_actual = self.fecha_hasta.year
        
        max_days = monthrange(año_actual, mes_actual)[1]
        valores_dias = [str(i) for i in range(1, max_days + 1)]
        
        combo = ctk.CTkComboBox(
            frame,
            values=valores_dias,
            width=60,
            command=lambda v, t=tipo: self._on_date_change(t),
            fg_color=("#3B3B3B", "#2B2B2B"),  # Colores por defecto de CustomTkinter
            button_color=("#3B3B3B", "#2B2B2B"),
            button_hover_color=("#4A4A4A", "#3A3A3A")
        )
        combo.pack()
        
        # Guardar referencia para actualización posterior
        if tipo == "desde":
            self._desde_dia_combo = combo
        else:
            self._hasta_dia_combo = combo
        
        return combo
    
    def _create_month_selector(self, parent, tipo):
        """Crea un selector de mes (1-12)"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(side="left", padx=2)
        
        meses = [str(i) for i in range(1, 13)]
        combo = ctk.CTkComboBox(
            frame,
            values=meses,
            width=60,
            command=lambda v, t=tipo: self._update_days_for_month(t),
            fg_color=("#3B3B3B", "#2B2B2B"),  # Colores por defecto de CustomTkinter
            button_color=("#3B3B3B", "#2B2B2B"),
            button_hover_color=("#4A4A4A", "#3A3A3A")
        )
        combo.pack()
        
        # Guardar referencia
        if tipo == "desde":
            self._desde_mes_combo = combo
        else:
            self._hasta_mes_combo = combo
        
        return combo
    
    def _create_year_selector(self, parent, tipo):
        """Crea un selector de año"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(side="left", padx=2)
        
        año_actual = datetime.now().year
        años = [str(i) for i in range(año_actual - 5, año_actual + 6)]
        combo = ctk.CTkComboBox(
            frame,
            values=años,
            width=70,
            command=lambda v, t=tipo: self._update_days_for_month(t),
            fg_color=("#3B3B3B", "#2B2B2B"),  # Colores por defecto de CustomTkinter
            button_color=("#3B3B3B", "#2B2B2B"),
            button_hover_color=("#4A4A4A", "#3A3A3A")
        )
        combo.pack()
        
        # Guardar referencia
        if tipo == "desde":
            self._desde_año_combo = combo
        else:
            self._hasta_año_combo = combo
        
        return combo
    
    def _update_custom_selectors(self):
        """Actualiza los valores de los selectores personalizados"""
        # Desde
        if hasattr(self, 'desde_dia'):
            self.desde_dia.set(str(self.fecha_desde.day))
            self.desde_mes.set(str(self.fecha_desde.month))
            self.desde_año.set(str(self.fecha_desde.year))
        
        # Hasta
        if hasattr(self, 'hasta_dia'):
            self.hasta_dia.set(str(self.fecha_hasta.day))
            self.hasta_mes.set(str(self.fecha_hasta.month))
            self.hasta_año.set(str(self.fecha_hasta.year))
    
    def _update_days_for_month(self, tipo):
        """Actualiza los días disponibles cuando cambia mes o año"""
        if not self.custom_panel.winfo_ismapped():
            return
        
        try:
            if tipo == "desde":
                mes = int(self.desde_mes.get())
                año = int(self.desde_año.get())
                max_days = monthrange(año, mes)[1]
                nuevos_dias = [str(i) for i in range(1, max_days + 1)]
                self.desde_dia.configure(values=nuevos_dias)
                # Ajustar día si es mayor al máximo
                dia_actual = int(self.desde_dia.get()) if self.desde_dia.get() else 1
                if dia_actual > max_days:
                    self.desde_dia.set(str(max_days))
            else:
                mes = int(self.hasta_mes.get())
                año = int(self.hasta_año.get())
                max_days = monthrange(año, mes)[1]
                nuevos_dias = [str(i) for i in range(1, max_days + 1)]
                self.hasta_dia.configure(values=nuevos_dias)
                # Ajustar día si es mayor al máximo
                dia_actual = int(self.hasta_dia.get()) if self.hasta_dia.get() else 1
                if dia_actual > max_days:
                    self.hasta_dia.set(str(max_days))
            
            # Actualizar fecha y validar
            self._on_date_change(tipo)
        except (ValueError, AttributeError):
            pass
    
    def _on_date_change(self, tipo):
        """Se llama cuando cambia cualquier selector de fecha"""
        if not hasattr(self, 'desde_dia') or not self.custom_panel.winfo_ismapped():
            return
        
        try:
            if tipo == "desde":
                dia = int(self.desde_dia.get())
                mes = int(self.desde_mes.get())
                año = int(self.desde_año.get())
                self.fecha_desde = datetime(año, mes, dia)
            else:
                dia = int(self.hasta_dia.get())
                mes = int(self.hasta_mes.get())
                año = int(self.hasta_año.get())
                self.fecha_hasta = datetime(año, mes, dia)
            
            # Validar que desde <= hasta
            if self.fecha_desde > self.fecha_hasta:
                # Ajustar automáticamente
                if tipo == "desde":
                    self.fecha_hasta = self.fecha_desde
                    self._update_custom_selectors()
                else:
                    self.fecha_desde = self.fecha_hasta
                    self._update_custom_selectors()
            
            # Actualizar texto del botón
            self._update_button_text()
            
            # Notificar cambio
            if self.on_period_change:
                self.on_period_change(self.get_desde(), self.get_hasta())
        
        except (ValueError, AttributeError):
            pass
    
    def _update_button_text(self):
        """Actualiza el texto del botón principal según el modo"""
        if self.current_mode == "esta_semana":
            self.main_button.configure(text="Esta semana ▼")
        elif self.current_mode == "este_mes":
            self.main_button.configure(text="Este mes ▼")
        elif self.current_mode == "este_año":
            self.main_button.configure(text="Este año ▼")
        else:
            desde_str = self.fecha_desde.strftime("%d/%m/%Y")
            hasta_str = self.fecha_hasta.strftime("%d/%m/%Y")
            self.main_button.configure(text=f"{desde_str} - {hasta_str} ▼")
    
    def _set_default_period(self):
        """Establece el período por defecto (este mes)"""
        self._apply_quick_period("este_mes")
        self.current_mode = "este_mes"
        self._update_button_text()
    
    def get_desde(self):
        """Retorna la fecha desde en formato YYYY-MM-DD"""
        return self.fecha_desde.strftime("%Y-%m-%d")
    
    def get_hasta(self):
        """Retorna la fecha hasta en formato YYYY-MM-DD"""
        return self.fecha_hasta.strftime("%Y-%m-%d")
    
    def set_period(self, desde, hasta):
        """Establece un período específico"""
        try:
            self.fecha_desde = datetime.strptime(desde, "%Y-%m-%d")
            self.fecha_hasta = datetime.strptime(hasta, "%Y-%m-%d")
            if self.current_mode == "personalizado" and hasattr(self, 'desde_dia'):
                self._update_custom_selectors()
            self._update_button_text()
        except ValueError:
            pass

