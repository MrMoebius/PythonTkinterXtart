import customtkinter as ctk
from tkinter import filedialog, messagebox

from src.ui.widgets.ctk_datepicker import CTkDatePicker
from src.ui.widgets.ctk_scrollable_frame import CTkScrollableFrame

from src.reports.report_loader import ReportLoader
from src.reports.chart_factory import ChartFactory
from src.reports.graphic_panel import GraphicPanel
from src.reports.zoom_manager import ZoomManager

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

        # Zoom Manager
        self.zoom = ZoomManager()

        self._build_ui()

        # Cargar una pestaña inicial por defecto
        self._switch_tab("Ventas por empleado")

    # ================================================================
    # UI PRINCIPAL
    # ================================================================
    def _build_ui(self):

        # -------------------------
        # TITULO
        # -------------------------
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", pady=4)

        ctk.CTkLabel(
            title_frame,
            text="Informes y Gráficos",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            title_frame,
            text="Generar informe personalizado ▼",
            command=self._open_popover,
            corner_radius=6
        ).pack(side="left", padx=10)

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

        # ================================================================
        # SCROLLABLE GRAPH AREA
        # ================================================================
        self.scroll_area = CTkScrollableFrame(self)
        self.scroll_area.pack(fill="both", expand=True, padx=10, pady=10)

        # ================================================================
        # FOOTER FIJO (PDF, PNG, Refresh, Zoom)
        # ================================================================
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", side="bottom", pady=4)
        footer.pack_propagate(False)

        # IZQUIERDA
        ctk.CTkButton(
            footer,
            text="Exportar PDF",
            width=130,
            command=self._export_pdf
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            footer,
            text="Exportar PNG",
            width=130,
            command=self._export_png
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            footer,
            text="Actualizar",
            width=130,
            command=lambda: self._switch_tab(self.active_tab)
        ).pack(side="left", padx=5)

        # DERECHA
        ctk.CTkButton(
            footer, text="-", width=40,
            command=self._zoom_out
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            footer, text="+", width=40,
            command=self._zoom_in
        ).pack(side="right")

    # ================================================================
    # POPOVER PERSONALIZADO
    # ================================================================
    def _open_popover(self):
        if hasattr(self, "popover") and self.popover.winfo_exists():
            self.popover.destroy()

        self.popover = ctk.CTkToplevel(self)
        self.popover.overrideredirect(True)
        self.popover.configure(fg_color="#232323")

        options = [
            "Ventas por empleado",
            "Estado presupuestos",
            "Facturación mensual",
            "Ventas por producto",
            "Ratio conversión"
        ]

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
        if not desde: 
            desde = self.fecha_desde.get()
        if not hasta:
            hasta = self.fecha_hasta.get()
        # Llamar informe adecuado
        loader = self.loader
        # Selección del informe usando fechas
        if name == "Ventas por empleado":
            data = loader.ventas_por_empleado(desde, hasta)
        elif name == "Estado presupuestos":
            data = loader.estados_presupuestos(desde, hasta)
        elif name == "Facturación mensual":
            data = loader.facturacion_mensual(desde, hasta)
        elif name == "Ventas por producto":
            data = loader.ventas_por_producto(desde, hasta)
        elif name == "Ratio conversión":
            data = loader.ratio_conversion(desde, hasta)
        else:
            data = None
        # Renderizar gráfico
        self._render_report(data, name)

    # ================================================================
    # GENERAR POR PERIODO
    # ================================================================
    def _generate_from_period(self):
        desde = self.fecha_desde.get()
        hasta = self.fecha_hasta.get()
        self._switch_tab(self.active_tab, desde, hasta)


    # ================================================================
    # RENDERIZACIÓN DEL INFORME
    # ================================================================
    def _render_report(self, data, title):

        # El área scrolleable se limpia automáticamente por GraphicPanel
        desde = self.fecha_desde.get()
        hasta = self.fecha_hasta.get()

        if not data:
            fig = ChartFactory.empty("Sin datos disponibles")
        else:
            if title == "Ventas por empleado":
                labels = [x["nombre"] for x in data]
                values = [x["total"] for x in data]
                fig = ChartFactory.bar_chart(labels, values, title, "Total (€)")

            elif title == "Estado presupuestos":
                fig = ChartFactory.pie_chart(
                    labels=list(data.keys()),
                    values=list(data.values()),
                    title=title
                )

            elif title == "Facturación mensual":
                meses = sorted(data.keys())
                fig = ChartFactory.line_chart(
                    labels=meses,
                    values=[data[m] for m in meses],
                    title=title,
                    xlabel="Mes",
                    ylabel="€"
                )

            elif title == "Ventas por producto":
                labels = [x["producto"] for x in data]
                values = [x["total"] for x in data]
                fig = ChartFactory.bar_chart(labels, values, title, "Total (€)")

            elif title == "Ratio conversión":
                fig = ChartFactory.pie_chart(
                    labels=list(data.keys()),
                    values=list(data.values()),
                    title=title
                )

        # Texto del periodo dentro del gráfico
        fig.text(
            0.01, 0.01,
            f"Periodo: {desde} → {hasta}",
            fontsize=10
        )

        # Guardar figura actual
        fig.set_size_inches(8, 4)

        # Mostrar usando GraphicPanel avanzado
        self.canvas_widget = GraphicPanel.display(self.scroll_area, fig)

    # ================================================================
    # EXPORTAR
    # ================================================================
    def _export_pdf(self):
        if not self.current_figure:
            return messagebox.showwarning("Error", "No hay informe generado.")

        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")]
        )
        if path:
            PDFExporter.export(self.current_figure, path)

    def _export_png(self):
        if not self.current_figure:
            return messagebox.showwarning("Error", "No hay informe generado.")

        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png")]
        )
        if path:
            ImageExporter.export(self.current_figure, path)

    # ================================================================
    # ZOOM REAL
    # ================================================================
    def _zoom_in(self):
        if GraphicPanel.current_canvas:
            self.zoom.zoom_in()
            self.zoom.apply_zoom(GraphicPanel.current_canvas)
            return

        self.zoom.zoom_in()
        self.zoom.apply_zoom(self.current_figure)

        # Redibujar figura
        self._switch_tab(self.active_tab)

    def _zoom_out(self):
        if GraphicPanel.current_canvas:
            self.zoom.zoom_out()
            self.zoom.apply_zoom(GraphicPanel.current_canvas)
            return

        self.zoom.zoom_out()
        self.zoom.apply_zoom(self.current_figure)

        # Redibujar figura
        self._switch_tab(self.active_tab)
