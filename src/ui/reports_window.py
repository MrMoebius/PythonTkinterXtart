import customtkinter as ctk
from tkinter import filedialog, messagebox

from src.ui.widgets.ctk_datepicker import CTkDatePicker
from src.ui.widgets.ctk_scrollable_frame import CTkScrollableFrame

from src.reports.report_loader import ReportLoader
from src.reports.chart_factory import ChartFactory
from src.reports.graphic_panel import GraphicPanel
from src.reports.zoom_manager import ZoomManager
from src.ui.reports.report_definitions import (
    get_report_options, get_loader_method_name, get_chart_type, get_chart_config
)

from src.reports.exporters.pdf_exporter import PDFExporter
from src.reports.exporters.image_exporter import ImageExporter


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

        # Cargar una pestaña inicial por defecto (después de que los widgets estén creados)
        self.after(100, lambda: self._switch_tab("Ventas por empleado"))

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
            font=ctk.CTkFont(size=22, weight="bold")
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
            command=lambda: self._switch_tab(self.active_tab)
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
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=5)

        self.fecha_desde = CTkDatePicker(period_frame)
        self.fecha_desde.pack(side="left", padx=5)

        self.fecha_hasta = CTkDatePicker(period_frame)
        self.fecha_hasta.pack(side="left", padx=5)

        ctk.CTkButton(
            period_frame,
            text="Generar",
            command=self._generate_from_period
        ).pack(side="left", padx=10)

        # Título del informe generado
        self.report_title_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=18, weight="bold")
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
    # CAMBIO DE TAB
    # ================================================================
    def _switch_tab(self, name, desde=None, hasta=None):
        self.active_tab = name
        # Si no se pasan fechas, usar las del datepicker
        if not desde and hasattr(self, 'fecha_desde'):
            desde = self.fecha_desde.get()
        if not hasta and hasattr(self, 'fecha_hasta'):
            hasta = self.fecha_hasta.get()
        
        # Obtener método del loader desde las definiciones
        method_name = get_loader_method_name(name)
        if not method_name:
            data = None
        else:
            # Llamar método del loader dinámicamente
            loader_method = getattr(self.loader, method_name, None)
            if loader_method:
                data = loader_method(desde, hasta)
            else:
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
        if not hasattr(self, 'fecha_desde') or not hasattr(self, 'fecha_hasta'):
            return
        desde = self.fecha_desde.get()
        hasta = self.fecha_hasta.get()
        if self.active_tab:
            self._switch_tab(self.active_tab, desde, hasta)


    # ================================================================
    # RENDERIZACIÓN DEL INFORME
    # ================================================================
    def _render_report(self, data, title):

        # El área scrolleable se limpia automáticamente por GraphicPanel
        desde = None
        hasta = None
        if hasattr(self, 'fecha_desde') and hasattr(self, 'fecha_hasta'):
            desde = self.fecha_desde.get()
            hasta = self.fecha_hasta.get()

        if not data:
            fig = ChartFactory.empty("Sin datos disponibles")
        else:
            # Obtener configuración del informe desde las definiciones
            chart_type = get_chart_type(title)
            chart_config = get_chart_config(title)
            
            if not chart_type or not chart_config:
                fig = ChartFactory.empty("Configuración de informe no encontrada")
            else:
                # Extraer datos usando la función extractor
                data_extractor = chart_config.get("data_extractor")
                if data_extractor:
                    labels, values = data_extractor(data)
                else:
                    labels, values = [], []
                
                # Crear gráfico según el tipo
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
                    fig = ChartFactory.empty(f"Tipo de gráfico '{chart_type}' no soportado")

        # Texto del periodo dentro del gráfico y título descriptivo
        subtitle = title
        if desde and hasta:
            periodo_txt = f"{desde} → {hasta}"
            fig.text(
                0.01, 0.01,
                f"Periodo: {periodo_txt}",
                fontsize=10
            )
            subtitle = f"{title} ({periodo_txt})"

        # Actualizar etiqueta de título de informe en la ventana
        if hasattr(self, "report_title_label"):
            self.report_title_label.configure(text=subtitle)

        # Guardar figura actual con tamaño dependiente del zoom
        self.current_figure = fig
        scale = getattr(self.zoom, "scale", 1.0)
        fig.set_size_inches(8 * scale, 4 * scale)

        # Mostrar usando GraphicPanel avanzado
        # CTkScrollableFrame tiene un inner_frame donde va el contenido
        parent_frame = self.scroll_area.inner_frame if hasattr(self.scroll_area, 'inner_frame') else self.scroll_area
        self.canvas_widget = GraphicPanel.display(parent_frame, fig)

    # ================================================================
    # EXPORTAR
    # ================================================================
    def _export_pdf(self):
        if not self.current_figure:
            return messagebox.showwarning("Error", "No hay informe generado.")

        # Nombre sugerido: Informe - <titulo> - <fecha>.pdf
        base_name = self.last_title or "Informe"
        desde = self.fecha_desde.get() if hasattr(self, "fecha_desde") else ""
        hasta = self.fecha_hasta.get() if hasattr(self, "fecha_hasta") else ""
        if desde and hasta:
            base_name = f"{base_name} - {desde}_a_{hasta}"
        initialfile = f"{base_name}.pdf"

        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            initialfile=initialfile
        )
        if path:
            PDFExporter.export(self.current_figure, path)

    def _export_png(self):
        if not self.current_figure:
            return messagebox.showwarning("Error", "No hay informe generado.")

        base_name = self.last_title or "Informe"
        desde = self.fecha_desde.get() if hasattr(self, "fecha_desde") else ""
        hasta = self.fecha_hasta.get() if hasattr(self, "fecha_hasta") else ""
        if desde and hasta:
            base_name = f"{base_name} - {desde}_a_{hasta}"
        initialfile = f"{base_name}.png"

        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png")],
            initialfile=initialfile
        )
        if path:
            ImageExporter.export(self.current_figure, path)

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
