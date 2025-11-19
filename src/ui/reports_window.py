"""
Ventana de informes y gráficos
"""

import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.api.rest_client import RESTClient

class ReportsWindow(ttk.Frame):
    """Ventana para mostrar informes y gráficos"""
    
    def __init__(self, parent, api: RESTClient):
        super().__init__(parent)
        self.api = api
        self._create_widgets()
        self._load_reports()
    
    def _create_widgets(self):
        """Crea los widgets de la ventana"""
        # Título
        title_frame = ttk.Frame(self)
        title_frame.pack(fill=tk.X, pady=10)
        
        title_label = ttk.Label(title_frame, text="Informes y Gráficos", 
                               font=("Arial", 18, "bold"))
        title_label.pack(side=tk.LEFT)
        
        ttk.Button(title_frame, text="Actualizar", 
                  command=self._load_reports).pack(side=tk.RIGHT, padx=5)
        
        # Notebook para diferentes informes
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame para gráfico de ventas por empleado
        self.ventas_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.ventas_frame, text="Ventas por Empleado")
        
        # Frame para estado de presupuestos
        self.presupuestos_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.presupuestos_frame, text="Estado de Presupuestos")
        
        # Frame para facturación mensual
        self.facturacion_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.facturacion_frame, text="Facturación Mensual")
    
    def _load_reports(self):
        """Carga y muestra los informes"""
        self._load_ventas_por_empleado()
        self._load_estado_presupuestos()
        self._load_facturacion_mensual()
    
    def _load_ventas_por_empleado(self):
        """Carga el gráfico de ventas por empleado"""
        # Limpiar frame
        for widget in self.ventas_frame.winfo_children():
            widget.destroy()
        
        # Obtener datos
        facturas_result = self.api.get_facturas()
        empleados_result = self.api.get_empleados()
        
        if not facturas_result.get("success") or not empleados_result.get("success"):
            ttk.Label(self.ventas_frame, text="Error al cargar datos").pack(pady=20)
            return
        
        facturas = facturas_result.get("data", [])
        empleados = empleados_result.get("data", [])
        
        # Calcular ventas por empleado
        ventas_por_empleado = {}
        for factura in facturas:
            empleado_id = factura.get("empleado_id")
            if empleado_id:
                total = float(factura.get("total", 0))
                ventas_por_empleado[empleado_id] = ventas_por_empleado.get(empleado_id, 0) + total
        
        # Crear gráfico
        fig = Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        nombres = []
        ventas = []
        for empleado in empleados:
            emp_id = empleado.get("id")
            if emp_id in ventas_por_empleado:
                nombres.append(f"{empleado.get('nombre', '')} {empleado.get('apellidos', '')}")
                ventas.append(ventas_por_empleado[emp_id])
        
        if nombres:
            ax.bar(nombres, ventas, color='#2196F3')
            ax.set_xlabel('Empleado')
            ax.set_ylabel('Total Ventas (€)')
            ax.set_title('Ventas por Empleado')
            ax.tick_params(axis='x', rotation=45)
            fig.tight_layout()
        else:
            ax.text(0.5, 0.5, 'No hay datos disponibles', 
                   ha='center', va='center', transform=ax.transAxes)
        
        canvas = FigureCanvasTkAgg(fig, self.ventas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _load_estado_presupuestos(self):
        """Carga el gráfico de estado de presupuestos"""
        # Limpiar frame
        for widget in self.presupuestos_frame.winfo_children():
            widget.destroy()
        
        # Obtener datos
        presupuestos_result = self.api.get_presupuestos()
        
        if not presupuestos_result.get("success"):
            ttk.Label(self.presupuestos_frame, text="Error al cargar datos").pack(pady=20)
            return
        
        presupuestos = presupuestos_result.get("data", [])
        
        # Contar por estado
        estados = {}
        for presupuesto in presupuestos:
            estado = presupuesto.get("estado", "DESCONOCIDO")
            estados[estado] = estados.get(estado, 0) + 1
        
        # Crear gráfico de pastel
        fig = Figure(figsize=(8, 8), dpi=100)
        ax = fig.add_subplot(111)
        
        if estados:
            labels = list(estados.keys())
            sizes = list(estados.values())
            colors = ['#4CAF50', '#FF9800', '#F44336', '#2196F3']
            
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', 
                  colors=colors[:len(labels)], startangle=90)
            ax.set_title('Estado de Presupuestos')
        else:
            ax.text(0.5, 0.5, 'No hay datos disponibles', 
                   ha='center', va='center', transform=ax.transAxes)
        
        canvas = FigureCanvasTkAgg(fig, self.presupuestos_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _load_facturacion_mensual(self):
        """Carga el gráfico de facturación mensual"""
        # Limpiar frame
        for widget in self.facturacion_frame.winfo_children():
            widget.destroy()
        
        # Obtener datos
        facturas_result = self.api.get_facturas()
        
        if not facturas_result.get("success"):
            ttk.Label(self.facturacion_frame, text="Error al cargar datos").pack(pady=20)
            return
        
        facturas = facturas_result.get("data", [])
        
        # Agrupar por mes
        facturacion_mensual = {}
        for factura in facturas:
            fecha = factura.get("fecha", "")
            if fecha and len(fecha) >= 7:
                mes = fecha[:7]  # YYYY-MM
                total = float(factura.get("total", 0))
                facturacion_mensual[mes] = facturacion_mensual.get(mes, 0) + total
        
        # Crear gráfico de líneas
        fig = Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        if facturacion_mensual:
            meses = sorted(facturacion_mensual.keys())
            totales = [facturacion_mensual[mes] for mes in meses]
            
            ax.plot(meses, totales, marker='o', color='#4CAF50', linewidth=2)
            ax.set_xlabel('Mes')
            ax.set_ylabel('Facturación (€)')
            ax.set_title('Facturación Mensual')
            ax.grid(True, alpha=0.3)
            ax.tick_params(axis='x', rotation=45)
            fig.tight_layout()
        else:
            ax.text(0.5, 0.5, 'No hay datos disponibles', 
                   ha='center', va='center', transform=ax.transAxes)
        
        canvas = FigureCanvasTkAgg(fig, self.facturacion_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

