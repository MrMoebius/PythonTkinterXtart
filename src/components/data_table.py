"""
Componente de tabla para mostrar datos
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Optional, Callable

class DataTable(ttk.Frame):
    """Tabla con paginación y ordenación"""
    
    def __init__(self, parent, columns: List[Dict], 
                 on_select: Optional[Callable] = None,
                 on_double_click: Optional[Callable] = None,
                 **kwargs):
        """
        Args:
            parent: Widget padre
            columns: Lista de columnas con formato [{"name": "...", "width": ..., "anchor": "..."}, ...]
            on_select: Callback cuando se selecciona una fila
            on_double_click: Callback cuando se hace doble clic
        """
        super().__init__(parent, **kwargs)
        
        self.columns = columns
        self.data = []
        self.filtered_data = []
        self.on_select = on_select
        self.on_double_click = on_double_click
        self.current_page = 1
        self.items_per_page = 20
        self.sort_column = None
        self.sort_reverse = False
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea los widgets de la tabla"""
        # Frame para la tabla y scrollbar
        table_frame = ttk.Frame(self)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview
        column_names = [col["name"] for col in self.columns]
        self.tree = ttk.Treeview(table_frame, columns=column_names, show="headings", selectmode="browse")
        
        # Configurar columnas
        for col in self.columns:
            self.tree.heading(col["name"], text=col["name"], 
                            command=lambda c=col["name"]: self._sort_by_column(c))
            self.tree.column(col["name"], width=col.get("width", 100), 
                           anchor=col.get("anchor", "w"))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind eventos
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", self._on_double_click)
        
        # Frame para paginación
        pagination_frame = ttk.Frame(self)
        pagination_frame.pack(fill=tk.X, pady=5)
        
        self.page_label = ttk.Label(pagination_frame, text="Página 1 de 1")
        self.page_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(pagination_frame, text="◀ Anterior", 
                  command=self._prev_page).pack(side=tk.LEFT, padx=2)
        ttk.Button(pagination_frame, text="Siguiente ▶", 
                  command=self._next_page).pack(side=tk.LEFT, padx=2)
    
    def set_data(self, data: List[Dict]):
        """Establece los datos de la tabla"""
        self.data = data
        self.filtered_data = data.copy()
        self.current_page = 1
        self._refresh_table()
    
    def filter_data(self, filter_func: Callable):
        """Filtra los datos usando una función"""
        self.filtered_data = [row for row in self.data if filter_func(row)]
        self.current_page = 1
        self._refresh_table()
    
    def clear_filter(self):
        """Limpia el filtro"""
        self.filtered_data = self.data.copy()
        self.current_page = 1
        self._refresh_table()
    
    def _sort_by_column(self, column: str):
        """Ordena por columna"""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        
        # Ordenar datos
        try:
            self.filtered_data.sort(
                key=lambda x: str(x.get(column, "")).lower(),
                reverse=self.sort_reverse
            )
        except:
            pass
        
        self._refresh_table()
    
    def _refresh_table(self):
        """Actualiza la visualización de la tabla"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Calcular paginación
        total_pages = max(1, (len(self.filtered_data) + self.items_per_page - 1) // self.items_per_page)
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        page_data = self.filtered_data[start_idx:end_idx]
        
        # Insertar datos
        for row in page_data:
            values = [str(row.get(col["name"], "")) for col in self.columns]
            iid = str(row.get("id"))
            self.tree.insert("", tk.END, iid=iid, values=values)

        
        # Actualizar label de paginación
        self.page_label.config(text=f"Página {self.current_page} de {total_pages} (Total: {len(self.filtered_data)})")
    
    def _prev_page(self):
        """Página anterior"""
        total_pages = max(1, (len(self.filtered_data) + self.items_per_page - 1) // self.items_per_page)
        if self.current_page > 1:
            self.current_page -= 1
            self._refresh_table()
    
    def _next_page(self):
        """Página siguiente"""
        total_pages = max(1, (len(self.filtered_data) + self.items_per_page - 1) // self.items_per_page)
        if self.current_page < total_pages:
            self.current_page += 1
            self._refresh_table()
    
    def _on_select(self, event):
        """Maneja la selección de una fila"""
        selection = self.tree.selection()
        if selection and self.on_select:
            iid = selection[0]
            row = next((r for r in self.filtered_data if str(r.get("id")) == iid), None)
            if row and self.on_select:
                self.on_select(row)

    
    def _on_double_click(self, event):
        """Maneja el doble clic"""
        selection = self.tree.selection()
        if selection and self.on_double_click:
            item = self.tree.item(selection[0])
            tags = item.get("tags", [])
            if tags:
                self.on_double_click(tags[0])
    
    def get_selected(self) -> Optional[Dict]:
        """Obtiene el elemento seleccionado"""
        selection = self.tree.selection()
        if not selection:
            return None
        iid = selection[0]
        # Buscar el diccionario real en filtered_data
        for row in self.filtered_data:
            if str(row.get("id")) == iid:
                return row

        return None

    
    def clear_selection(self):
        """Limpia la selección"""
        self.tree.selection_remove(self.tree.selection())

