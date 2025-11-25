"""
Panel de filtros avanzados
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Callable, Optional

class FilterPanel(ttk.LabelFrame):
    """Panel de filtros para búsqueda avanzada"""
    
    def __init__(self, parent, filters: List[Dict], on_filter: Callable, **kwargs):
        super().__init__(parent, text="Filtros de Búsqueda", **kwargs)
        
        self.filters = filters
        self.on_filter = on_filter
        self.filter_widgets = {}
        
        self._create_widgets()
    
    def _create_widgets(self):
        filters_frame = ttk.Frame(self)
        filters_frame.pack(fill=tk.X, padx=5, pady=5)

        row = 0
        col = 0
        max_cols = 3

        for filter_config in self.filters:
            ttk.Label(filters_frame, text=filter_config.get("label", filter_config["name"]) + ":")\
                .grid(row=row, column=col*2, sticky="w", padx=5, pady=2)

            filter_type = filter_config.get("type", "text")
            widget = None

            # TEXT
            if filter_type == "text":
                widget = ttk.Entry(filters_frame, width=25)

            # SELECT (CON OPCIÓN VACÍA REAL)
            elif filter_type == "select":
                options = ["(Sin filtro)"] + filter_config.get("options", [])
                widget = ttk.Combobox(filters_frame, state="readonly", width=23)
                widget["values"] = options
                widget.current(0)   # ESTA LÍNEA ES LA QUE FALTABA

            # DATE
            elif filter_type == "date":
                widget = ttk.Entry(filters_frame, width=25)
                widget.insert(0, "YYYY-MM-DD")

            # NUMBER
            elif filter_type == "number":
                widget = ttk.Entry(filters_frame, width=25)

            if widget:
                widget.grid(row=row, column=col*2+1, sticky="ew", padx=5, pady=2)
                self.filter_widgets[filter_config["name"]] = widget

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        for i in range(max_cols * 2):
            filters_frame.columnconfigure(i, weight=1)

        buttons_frame = ttk.Frame(self)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(buttons_frame, text="Aplicar Filtros",
                command=self._apply_filters).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Limpiar Filtros",
                command=self._clear_filters).pack(side=tk.LEFT, padx=5)
    
    # ==========================================================
    # APLICAR
    # ==========================================================
    def _apply_filters(self):
        filter_values = {}

        for name, widget in self.filter_widgets.items():

            # Entry normal
            if isinstance(widget, ttk.Entry):
                value = widget.get().strip()
                if value and value != "YYYY-MM-DD":
                    filter_values[name] = value

            # Combo
            elif isinstance(widget, ttk.Combobox):
                value = widget.get().strip()
                if value and value != "(Sin filtro)":   # ← IGNORAR
                    filter_values[name] = value
        
        self.on_filter(filter_values)
    
    # ==========================================================
    # LIMPIAR
    # ==========================================================
    def _clear_filters(self):
        for name, widget in self.filter_widgets.items():

            if isinstance(widget, ttk.Entry):
                widget.delete(0, tk.END)
                if name == "date":
                    widget.insert(0, "YYYY-MM-DD")

            elif isinstance(widget, ttk.Combobox):
                widget.current(0)

        self.on_filter({})

