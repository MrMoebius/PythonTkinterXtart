import customtkinter as ctk
from tkinter import filedialog, messagebox

from src.ui.widgets.ctk_datepicker import CTkDatePicker
from src.ui.widgets.ctk_scrollable_frame import CTkScrollableFrame
from src.ui.widgets.period_selector import PeriodSelector

from src.reports.report_loader import ReportLoader
from src.reports.chart_factory import ChartFactory
from src.reports.graphic_panel import GraphicPanel
from src.reports.zoom_manager import ZoomManager
from src.ui.reports.report_definitions import (
    get_report_options, get_loader_method_name, get_chart_type, get_chart_config
)

from src.reports.exporters.pdf_exporter import PDFExporter
from src.reports.exporters.image_exporter import ImageExporter
from src.reports.exporters.report_exporter import ReportExporter


class ReportsWindow(ctk.CTkFrame):

    def __init__(self, parent, api):
        super().__init__(parent, fg_color="transparent")

        self.api = api
        self.loader = ReportLoader(api)

        self.current_figure = None
        self.active_tab = None
        self.canvas_widget = None
        self.last_data = None
        self.last_title = None

        # Zoom Manager
        self.zoom = ZoomManager()

        self._build_ui()

        # Establecer un informe por defecto pero sin cargar datos
        # Solo se cargarán datos cuando el usuario presione "Generar"
        self.active_tab = "Ventas por empleado"

    # ================================================================
    # UI PRINCIPAL
    # ================================================================
    def _build_ui(self):

        # -------------------------
        # TITULO + ACCIONES (arriba)
        # -------------------------
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", pady=4)

        # Izquierda: título y selector de informe
        left_title = ctk.CTkFrame(title_frame, fg_color="transparent")
        left_title.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            left_title,
            text="Informes y Gráficos",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#2491ed"  # Azul primario
        ).pack(side="left")

        ctk.CTkButton(
            left_title,
            text="Generar informe personalizado ▼",
            command=self._open_popover,
            corner_radius=6
        ).pack(side="left", padx=10)

        # Derecha: acciones (exportar / actualizar / zoom)
        actions_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        actions_frame.pack(side="right")

        ctk.CTkButton(
            actions_frame,
            text="Exportar PDF",
            width=120,
            command=self._export_pdf
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            actions_frame,
            text="Exportar PNG",
            width=120,
            command=self._export_png
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            actions_frame,
            text="Actualizar",
            width=120,
            command=self._generate_from_period
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            actions_frame, text="-", width=40,
            command=self._zoom_out
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            actions_frame, text="+", width=40,
            command=self._zoom_in
        ).pack(side="left", padx=2)

        # -------------------------
        # PERIODO DE TIEMPO
        # -------------------------
        period_frame = ctk.CTkFrame(self, fg_color="transparent")
        period_frame.pack(fill="x", pady=6)

        ctk.CTkLabel(
            period_frame,
            text="Periodo:",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#293553"
        ).pack(side="left", padx=5)

        # Nuevo selector de período con opciones rápidas
        self.period_selector = PeriodSelector(
            period_frame,
            on_period_change=self._on_period_changed
        )
        self.period_selector.pack(side="left", padx=5)

        ctk.CTkButton(
            period_frame,
            text="Generar",
            command=self._generate_from_period
        ).pack(side="left", padx=10)

        # Título del informe generado
        self.report_title_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=20, weight="bold"),  # Aumentado de 18 a 20
            text_color="#6f42c1"  # Color púrpura para destacar
        )
        self.report_title_label.pack(fill="x", pady=(0, 4))

        # ================================================================
        # SCROLLABLE GRAPH AREA
        # ================================================================
        self.scroll_area = CTkScrollableFrame(self)
        self.scroll_area.pack(fill="both", expand=True, padx=10, pady=10)

    # ================================================================
    # POPOVER PERSONALIZADO
    # ================================================================
    def _open_popover(self):
        if hasattr(self, "popover") and self.popover.winfo_exists():
            self.popover.destroy()

        self.popover = ctk.CTkToplevel(self)
        self.popover.overrideredirect(True)
        self.popover.configure(fg_color="#232323")

        options = get_report_options()

        for name in options:
            ctk.CTkButton(
                self.popover,
                text=name,
                fg_color="#353535",
                hover_color="#454545",
                command=lambda n=name: (self.popover.destroy(), self._switch_tab(n))
            ).pack(fill="x", padx=8, pady=4)

        x = self.winfo_rootx() + 200
        y = self.winfo_rooty() + 40
        self.popover.geometry(f"220x200+{x}+{y}")

    # ================================================================
    # CAMBIO DE TAB (solo cambia el informe activo, no hace consulta)
    # ================================================================
    def _switch_tab(self, name, desde=None, hasta=None):
        import logging
        logger = logging.getLogger(__name__)
        
        self.active_tab = name
        
        # Solo hacer consulta si se pasan fechas explícitamente (desde el botón "Generar")
        # Si no se pasan fechas, solo cambiar el informe activo sin consultar
        if desde is None and hasta is None:
            logger.info(f"[REPORTS_WINDOW] Cambiando a informe '{name}' sin generar datos")
            # Mostrar mensaje indicando que debe presionar "Generar"
            self._render_report(None, name)
            return
        
        # Si se pasan fechas, hacer la consulta
        logger.info(f"[REPORTS_WINDOW] Generando informe '{name}' con fechas: desde={desde}, hasta={hasta}")
        
        # Obtener método del loader desde las definiciones
        method_name = get_loader_method_name(name)
        if not method_name:
            logger.warning(f"[REPORTS_WINDOW] No se encontró método para '{name}'")
            data = None
        else:
            # Llamar método del loader dinámicamente
            loader_method = getattr(self.loader, method_name, None)
            if loader_method:
                data = loader_method(desde, hasta)
            else:
                logger.error(f"[REPORTS_WINDOW] Método '{method_name}' no existe en ReportLoader")
                data = None
        
        # Guardar última data y título para zoom/export
        self.last_data = data
        self.last_title = name
        # Renderizar gráfico
        self._render_report(data, name)

    # ================================================================
    # GENERAR POR PERIODO
    # ================================================================
    def _generate_from_period(self):
        if not hasattr(self, 'period_selector'):
            return
        
        # Validar que haya un informe seleccionado
        if not self.active_tab:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un informe primero.")
            return
        
        desde = self.period_selector.get_desde()
        hasta = self.period_selector.get_hasta()
        
        # Validar que se hayan seleccionado fechas
        if not desde or not hasta:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un período (desde y hasta).")
            return
        
        # Generar el informe con las fechas seleccionadas
        self._switch_tab(self.active_tab, desde, hasta)
    
    def _on_period_changed(self, desde, hasta):
        """Callback cuando cambia el período (opcional, para auto-generar)"""
        # Por ahora no hacemos nada automático, solo cuando se presiona "Generar"
        pass


    # ================================================================
    # RENDERIZACIÓN DEL INFORME
    # ================================================================
    def _render_report(self, data, title):
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[RENDER] Renderizando informe: {title}, data type: {type(data)}, data: {data}")

        # El área scrolleable se limpia automáticamente por GraphicPanel
        desde = None
        hasta = None
        if hasattr(self, 'period_selector'):
            desde = self.period_selector.get_desde()
            hasta = self.period_selector.get_hasta()

        # Si data es None (no se ha generado informe aún), mostrar mensaje
        if data is None:
            logger.info(f"[RENDER] No hay datos para {title}, mostrando mensaje inicial")
            fig = ChartFactory.empty("Seleccione un período y presione 'Generar' para ver el informe")
        # Verificar si data es lista vacía o diccionario vacío
        elif (isinstance(data, list) and len(data) == 0) or (isinstance(data, dict) and len(data) == 0):
            logger.warning(f"[RENDER] Datos vacíos para {title}, mostrando mensaje 'Sin datos disponibles'")
            fig = ChartFactory.empty("Sin datos disponibles para el período seleccionado")
        else:
            # Obtener configuración del informe desde las definiciones
            chart_type = get_chart_type(title)
            chart_config = get_chart_config(title)
            
            logger.info(f"[RENDER] chart_type: {chart_type}, chart_config: {chart_config is not None}")
            
            if not chart_type or not chart_config:
                logger.error(f"[RENDER] Configuración no encontrada para {title}")
                fig = ChartFactory.empty("Configuración de informe no encontrada")
            else:
                # Extraer datos usando la función extractor
                data_extractor = chart_config.get("data_extractor")
                if data_extractor:
                    try:
                        labels, values = data_extractor(data)
                        logger.info(f"[RENDER] Datos extraídos - labels: {len(labels) if labels else 0}, values: {len(values) if values else 0}")
                    except Exception as e:
                        logger.error(f"[RENDER] Error extrayendo datos: {e}", exc_info=True)
                        labels, values = [], []
                else:
                    logger.warning(f"[RENDER] No hay data_extractor en chart_config")
                    labels, values = [], []
                
                # Verificar si hay datos después de extraer
                if not labels or not values or len(labels) == 0 or len(values) == 0:
                    logger.warning(f"[RENDER] No hay datos después de extraer para {title}")
                    fig = ChartFactory.empty("Sin datos disponibles para el período seleccionado")
                else:
                    # Crear gráfico según el tipo
                    logger.info(f"[RENDER] Creando gráfico tipo {chart_type} con {len(labels)} elementos")
                    if chart_type == "bar":
                        xlabel = chart_config.get("xlabel", "")
                        ylabel = chart_config.get("ylabel", "")
                        fig = ChartFactory.bar_chart(labels, values, title, ylabel or xlabel)
                    
                    elif chart_type == "pie":
                        fig = ChartFactory.pie_chart(labels, values, title)
                    
                    elif chart_type == "line":
                        xlabel = chart_config.get("xlabel", "")
                        ylabel = chart_config.get("ylabel", "")
                        fig = ChartFactory.line_chart(labels, values, title, xlabel, ylabel)
                    
                    else:
                        logger.error(f"[RENDER] Tipo de gráfico '{chart_type}' no soportado")
                        fig = ChartFactory.empty("Tipo de gráfico no soportado: " + chart_type)

        # Texto del periodo dentro del gráfico y título descriptivo
        subtitle = title
        if desde and hasta:
            periodo_txt = f"{desde} → {hasta}"
            # Solo añadir texto del período si hay datos (no es None y no está vacío)
            # ChartFactory.empty ya tiene su propio texto, así que solo añadimos período a gráficos con datos
            if data is not None and not ((isinstance(data, list) and len(data) == 0) or (isinstance(data, dict) and len(data) == 0)):
                try:
                    if hasattr(fig, 'axes') and len(fig.axes) > 0:
                        ax = fig.axes[0]
                        if ax and ax.axis()[0]:  # Verificar si el eje está activo (axis()[0] != 0 significa que está activo)
                            ax.text(
                                0.01, 0.01,
                                f"Periodo: {periodo_txt}",
                                fontsize=10,
                                transform=ax.transAxes
                            )
                except Exception as e:
                    logger.warning(f"[RENDER] No se pudo añadir texto del período: {e}")
            subtitle = f"{title} ({periodo_txt})"

        # Actualizar etiqueta de título de informe en la ventana
        if hasattr(self, "report_title_label"):
            self.report_title_label.configure(text=subtitle)

        # Guardar figura actual con tamaño dependiente del zoom
        self.current_figure = fig
        scale = getattr(self.zoom, "scale", 1.0)
        fig.set_size_inches(8 * scale, 4 * scale)
        logger.info(f"[RENDER] Figura configurada con tamaño: {8 * scale} x {4 * scale}")

        # Mostrar usando GraphicPanel avanzado
        # CTkScrollableFrame tiene un inner_frame donde va el contenido
        parent_frame = self.scroll_area.inner_frame if hasattr(self.scroll_area, 'inner_frame') else self.scroll_area
        logger.info(f"[RENDER] Mostrando gráfico en parent_frame: {parent_frame}")
        try:
            self.canvas_widget = GraphicPanel.display(parent_frame, fig)
            logger.info(f"[RENDER] Gráfico mostrado correctamente")
        except Exception as e:
            logger.error(f"[RENDER] Error al mostrar gráfico: {e}", exc_info=True)
            raise

    # ================================================================
    # EXPORTAR
    # ================================================================
    def _export_pdf(self):
        if not self.last_data or not self.last_title:
            return messagebox.showwarning("Error", "No hay informe generado para exportar.")

        # Obtener configuración del informe
        chart_type = get_chart_type(self.last_title)
        chart_config = get_chart_config(self.last_title)
        
        if not chart_type or not chart_config:
            return messagebox.showerror("Error", "No se pudo obtener la configuración del informe.")

        # Obtener fechas
        desde = self.period_selector.get_desde() if hasattr(self, "period_selector") else None
        hasta = self.period_selector.get_hasta() if hasattr(self, "period_selector") else None

        # Nombre sugerido: Informe - <titulo> - <fecha>.pdf
        base_name = self.last_title or "Informe"
        if desde and hasta:
            base_name = f"{base_name} - {desde}_a_{hasta}"
        elif desde:
            base_name = f"{base_name} - desde_{desde}"
        elif hasta:
            base_name = f"{base_name} - hasta_{hasta}"
        initialfile = f"{base_name}.pdf"

        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            initialfile=initialfile
        )
        if path:
            try:
                ReportExporter.export_report(
                    title=self.last_title,
                    data=self.last_data,
                    chart_type=chart_type,
                    chart_config=chart_config,
                    desde=desde,
                    hasta=hasta,
                    path=path,
                    format="pdf"
                )
                messagebox.showinfo("Éxito", f"Informe exportado a PDF:\n{path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar PDF:\n{str(e)}")

    def _export_png(self):
        if not self.last_data or not self.last_title:
            return messagebox.showwarning("Error", "No hay informe generado para exportar.")

        # Obtener configuración del informe
        chart_type = get_chart_type(self.last_title)
        chart_config = get_chart_config(self.last_title)
        
        if not chart_type or not chart_config:
            return messagebox.showerror("Error", "No se pudo obtener la configuración del informe.")

        # Obtener fechas
        desde = self.period_selector.get_desde() if hasattr(self, "period_selector") else None
        hasta = self.period_selector.get_hasta() if hasattr(self, "period_selector") else None

        # Nombre sugerido: Informe - <titulo> - <fecha>.png
        base_name = self.last_title or "Informe"
        if desde and hasta:
            base_name = f"{base_name} - {desde}_a_{hasta}"
        elif desde:
            base_name = f"{base_name} - desde_{desde}"
        elif hasta:
            base_name = f"{base_name} - hasta_{hasta}"
        initialfile = f"{base_name}.png"

        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png")],
            initialfile=initialfile
        )
        if path:
            try:
                ReportExporter.export_report(
                    title=self.last_title,
                    data=self.last_data,
                    chart_type=chart_type,
                    chart_config=chart_config,
                    desde=desde,
                    hasta=hasta,
                    path=path,
                    format="png"
                )
                messagebox.showinfo("Éxito", f"Informe exportado a PNG:\n{path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar PNG:\n{str(e)}")

    # ================================================================
    # ZOOM REAL
    # ================================================================
    def _zoom_in(self):
        # Actualizar factor de zoom y volver a renderizar el informe actual
        self.zoom.zoom_in()
        if self.last_title is not None:
            self._render_report(self.last_data, self.last_title)

    def _zoom_out(self):
        self.zoom.zoom_out()
        if self.last_title is not None:
            self._render_report(self.last_data, self.last_title)
