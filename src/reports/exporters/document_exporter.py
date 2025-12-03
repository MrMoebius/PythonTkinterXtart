"""
Exportador reutilizable para documentos (PDF/PNG)
Puede ser usado por Presupuestos, Facturas, Pagos, etc.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Dict, List, Optional, Callable
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from src.reports.exporters.pdf_exporter import PDFExporter
from src.reports.exporters.image_exporter import ImageExporter


class DocumentExporter:
    """Exportador genérico para documentos"""
    
    @staticmethod
    def export_selected(
        table,
        entity_name: str,
        get_full_data: Callable,
        generate_document: Callable,
        api
    ):
        """
        Exporta el elemento seleccionado en la tabla a PDF o PNG.
        
        Args:
            table: Tabla de datos (DataTable)
            entity_name: Nombre de la entidad (para el nombre del archivo)
            get_full_data: Función que obtiene los datos completos del backend
            generate_document: Función que genera el documento matplotlib
            api: Cliente API para obtener datos relacionados
        """
        selected = table.get_selected()
        if not selected:
            messagebox.showwarning("Advertencia", f"Seleccione un {entity_name} para exportar")
            return None
        
        # Preguntar formato
        format_choice = messagebox.askyesno(
            "Formato de exportación",
            "¿Exportar como PDF?\n\nSí = PDF\nNo = PNG"
        )
        
        format_ext = "pdf" if format_choice else "png"
        format_name = "PDF" if format_choice else "PNG"
        
        # Solicitar ruta
        path = filedialog.asksaveasfilename(
            defaultextension=f".{format_ext}",
            filetypes=[(format_name.upper(), f"*.{format_ext}")],
            initialfile=f"{entity_name}_{selected.get('id', 'N')}.{format_ext}"
        )
        
        if not path:
            return None
        
        try:
            # Obtener datos completos
            full_data = get_full_data(selected, api)
            if not full_data:
                raise ValueError("No se pudieron obtener los datos completos")
            
            # Generar documento
            generate_document(full_data, path, format_ext, api)
            
            messagebox.showinfo("Éxito", f"{entity_name.capitalize()} exportado a {format_name}:\n{path}")
            return path
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar {format_name}:\n{str(e)}")
            return None
    
    @staticmethod
    def create_document_figure(title: str, data_sections: List[Dict]) -> Figure:
        """
        Crea una figura matplotlib con secciones de datos.
        
        Args:
            title: Título del documento
            data_sections: Lista de secciones, cada una con:
                - "title": Título de la sección
                - "items": Lista de tuplas (label, value)
        
        Returns:
            Figura matplotlib lista para exportar
        """
        fig = Figure(figsize=(8.5, 11), dpi=100)  # Tamaño A4
        ax = fig.add_subplot(111)
        ax.axis('off')
        
        y_position = 0.95
        line_height = 0.05
        
        def add_text(text, fontsize=12, weight='normal', y_pos=None):
            nonlocal y_position
            if y_pos is None:
                y_pos = y_position
            ax.text(0.1, y_pos, text, fontsize=fontsize, weight=weight, transform=ax.transAxes)
            y_position = y_pos - line_height
        
        # Título principal
        add_text(title.upper(), fontsize=20, weight='bold', y_pos=0.95)
        y_position = 0.90
        
        # Secciones
        for section in data_sections:
            section_title = section.get("title", "")
            items = section.get("items", [])
            
            if section_title:
                add_text(section_title.upper(), fontsize=14, weight='bold')
            
            for label, value in items:
                if value is None:
                    value = "N/A"
                elif isinstance(value, float):
                    value = f"€{value:.2f}"
                elif isinstance(value, (int, float)) and value == int(value):
                    value = f"€{int(value)}"
                else:
                    value = str(value)
                
                add_text(f"{label}: {value}")
            
            y_position -= line_height  # Espacio entre secciones
        
        return fig

