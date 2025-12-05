"""
Exportador simple de informes a PDF/PNG en formato A4 horizontal.
Incluye: logo, título, período, gráfico y pie de página.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.patches as mpatches

from src.utils.export_helpers import DocumentExporter, create_document_base
from src.reports.exporters.pdf_exporter import PDFExporter
from src.reports.exporters.image_exporter import ImageExporter


class ReportExporter:
    """Exportador simple de informes con formato A4 horizontal."""
    
    # Paleta de colores corporativa
    _COLORS = {
        'primary': '#2C3E50',
        'secondary': '#3498DB',
        'accent': '#E74C3C',
        'success': '#27AE60',
        'warning': '#F39C12',
        'text': '#2C3E50',
        'light_bg': '#ECF0F1',
        'border': '#BDC3C7'
    }
    
    def __init__(self):
        """Inicializa el exportador de informes."""
        pass
    
    @staticmethod
    def export_report(
        title: str,
        data: Any,
        chart_type: str,
        chart_config: Dict,
        desde: Optional[str] = None,
        hasta: Optional[str] = None,
        path: str = "informe.pdf",
        format: str = "pdf"
    ):
        """
        Exporta un informe simple en formato A4 horizontal.
        
        Args:
            title: Título del informe
            data: Datos del informe (lista o diccionario según el tipo)
            chart_type: Tipo de gráfico ("bar", "pie", "line")
            chart_config: Configuración del gráfico (incluye data_extractor)
            desde: Fecha de inicio del período (opcional)
            hasta: Fecha de fin del período (opcional)
            path: Ruta donde guardar el archivo
            format: Formato de exportación ("pdf" o "png")
        """
        # Crear documento base A4 horizontal
        fig, ax = create_document_base()
        
        # Crear exporter helper
        exporter = DocumentExporter(fig, ax)
        
        # ============================================================
        # LOGO (esquina superior derecha)
        # ============================================================
        exporter.add_logo(position="top_right")
        
        # ============================================================
        # TÍTULO PRINCIPAL
        # ============================================================
        exporter.add_main_title("INFORME", title.upper())
        
        # ============================================================
        # PERÍODO
        # ============================================================
        periodo_text = "Período completo"
        if desde and hasta:
            periodo_text = f"Desde: {desde} | Hasta: {hasta}"
        elif desde:
            periodo_text = f"Desde: {desde}"
        elif hasta:
            periodo_text = f"Hasta: {hasta}"
        
        ax.text(0.50, 0.93, periodo_text, 
                ha="center", fontsize=11, style='italic', 
                color=ReportExporter._COLORS['text'],
                transform=ax.transAxes)
        
        # ============================================================
        # GRÁFICO
        # ============================================================
        if not data:
            # Sin datos
            ax.text(0.50, 0.50, "Sin datos disponibles para el período seleccionado",
                    ha="center", va="center", fontsize=14, 
                    style='italic', color=ReportExporter._COLORS['text'],
                    transform=ax.transAxes)
        else:
            # Extraer datos usando el extractor
            data_extractor = chart_config.get("data_extractor")
            if data_extractor:
                try:
                    labels, values = data_extractor(data)
                except Exception:
                    labels, values = [], []
            else:
                labels, values = [], []
            
            if not labels or not values:
                ax.text(0.50, 0.50, "No se pudieron extraer los datos del informe",
                        ha="center", va="center", fontsize=14, 
                        style='italic', color=ReportExporter._COLORS['text'],
                        transform=ax.transAxes)
            else:
                # Crear área para el gráfico (más grande en horizontal)
                # Ajustado para dejar espacio al logo en la esquina superior derecha
                # x: 0.10, y: 0.15, ancho: 0.75 (reducido de 0.80), alto: 0.60
                chart_ax = fig.add_axes([0.10, 0.15, 0.75, 0.60])
                
                if chart_type == "bar":
                    ReportExporter._create_bar_chart(chart_ax, labels, values, title, 
                                                     chart_config.get("ylabel", ""))
                elif chart_type == "pie":
                    ReportExporter._create_pie_chart(chart_ax, labels, values, title)
                elif chart_type == "line":
                    ReportExporter._create_line_chart(chart_ax, labels, values, title,
                                                     chart_config.get("xlabel", ""),
                                                     chart_config.get("ylabel", ""))
        
        # ============================================================
        # PIE DE PÁGINA
        # ============================================================
        fecha_generacion = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        ax.text(0.50, 0.02, 
                f"Generado por CRM Xtart - {fecha_generacion}",
                ha="center", fontsize=9, 
                color=ReportExporter._COLORS['border'],
                style='italic',
                transform=ax.transAxes)
        
        # ============================================================
        # EXPORTAR
        # ============================================================
        if format == "pdf":
            PDFExporter.export(fig, path)
        else:
            ImageExporter.export(fig, path)
        
        plt.close(fig)
    
    @staticmethod
    def _create_bar_chart(ax, labels: List[str], values: List[float], title: str, ylabel: str):
        """Crea gráfico de barras mejorado."""
        colors = [ReportExporter._COLORS['secondary']] * len(labels)
        
        bars = ax.bar(range(len(labels)), values, color=colors, 
                     edgecolor=ReportExporter._COLORS['primary'], linewidth=1.2)
        
        # Etiquetas de valor encima de cada barra
        for i, (bar, val) in enumerate(zip(bars, values)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'€{val:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'),
                   ha='center', va='bottom', fontsize=9, weight='bold')
        
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
        ax.set_ylabel(ylabel or "Valor (€)", fontsize=10, weight='bold')
        ax.set_title(title, fontsize=12, weight='bold', pad=10)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(ReportExporter._COLORS['border'])
        ax.spines['bottom'].set_color(ReportExporter._COLORS['border'])
    
    @staticmethod
    def _create_pie_chart(ax, labels: List[str], values: List[float], title: str):
        """Crea gráfico de donut mejorado."""
        colors = plt.cm.Set3(range(len(labels)))
        
        # Crear donut chart
        _, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%',
                                     colors=colors, startangle=90,
                                     pctdistance=0.85, labeldistance=1.05)
        
        # Hacer donut (círculo blanco en el centro)
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        ax.add_artist(centre_circle)
        
        # Mejorar etiquetas
        for autotext in autotexts:
            autotext.set_color(ReportExporter._COLORS['primary'])
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)
        
        for text in texts:
            text.set_fontsize(10)
            text.set_fontweight('bold')
        
        ax.set_title(title, fontsize=12, weight='bold', pad=10)
        ax.axis('equal')
    
    @staticmethod
    def _create_line_chart(ax, labels: List[str], values: List[float], title: str, 
                          xlabel: str, ylabel: str):
        """Crea gráfico de líneas mejorado."""
        ax.plot(range(len(labels)), values, marker='o', linewidth=2.5,
               color=ReportExporter._COLORS['secondary'], 
               markersize=8, markerfacecolor=ReportExporter._COLORS['accent'],
               markeredgecolor=ReportExporter._COLORS['primary'], markeredgewidth=1.5)
        
        # Área sombreada
        ax.fill_between(range(len(labels)), values, alpha=0.3, 
                       color=ReportExporter._COLORS['secondary'])
        
        # Etiquetas de valor en cada punto
        for i, (label, val) in enumerate(zip(labels, values)):
            ax.text(i, val, f'€{val:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'),
                   ha='center', va='bottom', fontsize=8, weight='bold')
        
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
        ax.set_ylabel(ylabel or "Valor (€)", fontsize=10, weight='bold')
        ax.set_xlabel(xlabel or "Período", fontsize=10, weight='bold')
        ax.set_title(title, fontsize=12, weight='bold', pad=10)
        ax.grid(alpha=0.3, linestyle='--')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(ReportExporter._COLORS['border'])
        ax.spines['bottom'].set_color(ReportExporter._COLORS['border'])
    

