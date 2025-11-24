"""
Panel de filtros avanzados
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Callable, Optional

class FilterPanel(ttk.LabelFrame):
    """Panel de filtros para búsqueda avanzada"""
    
    def __init__(self, parent, filters: List[Dict], on_filter: Callable, **kwargs):
        """
        Args:
            parent: Widget padre
            filters: Lista de filtros con formato [{"name": "...", "type": "...", "label": "..."}, ...]
                     type puede ser: "text", "select", "date", "number"
            on_filter: Callback cuando se aplica el filtro
        """
        super().__init__(parent, text="Filtros de Búsqueda", **kwargs)
        
        self.filters = filters
        self.on_filter = on_filter
        self.filter_widgets = {}
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea los widgets de filtro"""
        # Frame para los filtros
        filters_frame = ttk.Frame(self)
        filters_frame.pack(fill=tk.X, padx=5, pady=5)
        
        row = 0
        col = 0
        max_cols = 3
        
        for filter_config in self.filters:
            # Label
            label = ttk.Label(filters_frame, text=filter_config.get("label", filter_config["name"]) + ":")
            label.grid(row=row, column=col*2, sticky="w", padx=5, pady=2)
            
            # Widget de filtro
            filter_type = filter_config.get("type", "text")
            widget = None
            
            if filter_type == "text":
                widget = ttk.Entry(filters_frame, width=20)
            elif filter_type == "select":
                options = filter_config.get("options", [])
                widget = ttk.Combobox(filters_frame, width=18, values=options, state="readonly")
            elif filter_type == "date":
                widget = ttk.Entry(filters_frame, width=20)
                widget.insert(0, "YYYY-MM-DD")
            elif filter_type == "number":
                widget = ttk.Entry(filters_frame, width=20)
            
            if widget:
                widget.grid(row=row, column=col*2+1, sticky="ew", padx=5, pady=2)
                self.filter_widgets[filter_config["name"]] = widget
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Configurar pesos de columnas
        for i in range(max_cols * 2):
            filters_frame.columnconfigure(i, weight=1)
        
        # Botones
        buttons_frame = ttk.Frame(self)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(buttons_frame, text="Aplicar Filtros", 
                  command=self._apply_filters).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Limpiar Filtros", 
                  command=self._clear_filters).pack(side=tk.LEFT, padx=5)
    
    def _apply_filters(self):
        """Aplica los filtros"""
        filter_values = {}
        for name, widget in self.filter_widgets.items():
            if isinstance(widget, ttk.Entry):
                value = widget.get().strip()
                if value and value != "YYYY-MM-DD":
                    filter_values[name] = value
            elif isinstance(widget, ttk.Combobox):
                value = widget.get()
                if value:
                    filter_values[name] = value
        
        self.on_filter(filter_values)
    
    def _clear_filters(self):
        """Limpia todos los filtros"""
        for name, widget in self.filter_widgets.items():
            if isinstance(widget, ttk.Entry):
                widget.delete(0, tk.END)
                if name == "date":
                    widget.insert(0, "YYYY-MM-DD")
            elif isinstance(widget, ttk.Combobox):
                widget.set("")
        
        self.on_filter({})
    
    def get_filter_values(self) -> Dict:
        """Obtiene los valores actuales de los filtros"""
        filter_values = {}
        for name, widget in self.filter_widgets.items():
            if isinstance(widget, ttk.Entry):
                value = widget.get().strip()
                if value and value != "YYYY-MM-DD":
                    filter_values[name] = value
            elif isinstance(widget, ttk.Combobox):
                value = widget.get()
                if value:
                    filter_values[name] = value
        return filter_values

