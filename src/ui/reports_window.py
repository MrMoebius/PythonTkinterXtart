"""
Ventana de informes y gráficos
"""

import tkinter as tk
from tkinter import ttk

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class ReportsWindow(ttk.Frame):
    """Ventana para mostrar informes y gráficos"""

    def __init__(self, parent, api):
        super().__init__(parent)
        self.api = api
        self._create_widgets()
        self._load_reports()

    # ================================================================
    # WIDGETS PRINCIPALES
    # ================================================================
    def _create_widgets(self):

        # Título
        title_frame = ttk.Frame(self)
        title_frame.pack(fill=tk.X, pady=10)

        ttk.Label(
            title_frame,
            text="Informes y Gráficos",
            font=("Arial", 18, "bold")
        ).pack(side=tk.LEFT)

        ttk.Button(
            title_frame,
            text="Actualizar",
            command=self._load_reports
        ).pack(side=tk.RIGHT, padx=5)

        # Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.ventas_frame = ttk.Frame(self.notebook)
        self.presupuestos_frame = ttk.Frame(self.notebook)
        self.facturacion_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.ventas_frame, text="Ventas por Empleado")
        self.notebook.add(self.presupuestos_frame, text="Estado Presupuestos")
        self.notebook.add(self.facturacion_frame, text="Facturación Mensual")

    # ================================================================
    # CARGA DE INFORMES
    # ================================================================
    def _load_reports(self):
        self._load_ventas_por_empleado()
        self._load_estado_presupuestos()
        self._load_facturacion_mensual()

    # ================================================================
    # INFORME 1 — VENTAS POR EMPLEADO
    # ================================================================
    def _load_ventas_por_empleado(self):

        for w in self.ventas_frame.winfo_children():
            w.destroy()

        fact = self.api.get_facturas()
        emp = self.api.get_empleados()

        if not (fact.get("success") and emp.get("success")):
            ttk.Label(self.ventas_frame, text="Error al cargar datos").pack(pady=20)
            return

        facturas = fact.get("data", [])
        empleados = emp.get("data", [])

        # Agrupar total por empleado
        ventas = {}
        for f in facturas:
            eid = f.get("empleado_id")
            if not eid:
                continue
            total = float(f.get("total") or 0)
            ventas[eid] = ventas.get(eid, 0) + total

        # Preparar datos
        nombres = []
        totales = []

        for e in empleados:
            eid = e.get("id")
            if eid in ventas:
                nombres.append(f"{e.get('nombre','')} {e.get('apellidos','')}")
                totales.append(ventas[eid])

        fig = Figure(figsize=(9, 5), dpi=100)
        ax = fig.add_subplot(111)

        if totales:
            ax.bar(nombres, totales)
            ax.set_title("Ventas por Empleado")
            ax.set_ylabel("Total (€)")
            ax.tick_params(axis="x", rotation=40)
        else:
            ax.text(0.5, 0.5, "Sin datos disponibles",
                    ha="center", va="center", transform=ax.transAxes)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.ventas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # ================================================================
    # INFORME 2 — ESTADO DE PRESUPUESTOS
    # ================================================================
    def _load_estado_presupuestos(self):

        for w in self.presupuestos_frame.winfo_children():
            w.destroy()

        res = self.api.get_presupuestos()

        if not res.get("success"):
            ttk.Label(self.presupuestos_frame, text="Error al cargar datos").pack(pady=20)
            return

        presupuestos = res.get("data", [])

        estados = {}
        for p in presupuestos:
            estado = p.get("estado", "DESCONOCIDO")
            estados[estado] = estados.get(estado, 0) + 1

        fig = Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111)

        if estados:
            labels = list(estados.keys())
            sizes = list(estados.values())
            ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
            ax.set_title("Estado de los Presupuestos")
        else:
            ax.text(0.5, 0.5, "Sin datos disponibles",
                    ha="center", va="center", transform=ax.transAxes)

        canvas = FigureCanvasTkAgg(fig, master=self.presupuestos_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # ================================================================
    # INFORME 3 — FACTURACIÓN MENSUAL
    # ================================================================
    def _load_facturacion_mensual(self):

        for w in self.facturacion_frame.winfo_children():
            w.destroy()

        res = self.api.get_facturas()

        if not res.get("success"):
            ttk.Label(self.facturacion_frame, text="Error al cargar datos").pack(pady=20)
            return

        facturas = res.get("data", [])

        fact_por_mes = {}

        for f in facturas:
            fecha = f.get("fecha", "")
            if not fecha or len(fecha) < 7:
                continue

            mes = fecha[:7]  # YYYY-MM
            total = float(f.get("total") or 0)
            fact_por_mes[mes] = fact_por_mes.get(mes, 0) + total

        fig = Figure(figsize=(10, 5), dpi=100)
        ax = fig.add_subplot(111)

        if fact_por_mes:
            meses = sorted(fact_por_mes.keys())
            totales = [fact_por_mes[m] for m in meses]

            ax.plot(meses, totales, marker="o")
            ax.set_title("Facturación Mensual")
            ax.set_xlabel("Mes")
            ax.set_ylabel("Total (€)")
            ax.tick_params(axis="x", rotation=40)
            ax.grid(alpha=0.3)
        else:
            ax.text(0.5, 0.5, "Sin datos disponibles",
                    ha="center", va="center", transform=ax.transAxes)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.facturacion_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
