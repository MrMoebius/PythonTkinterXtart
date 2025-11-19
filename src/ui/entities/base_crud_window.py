"""
Ventana base para CRUD de entidades
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Optional, Callable
from src.api.rest_client import RESTClient
from src.components.data_table import DataTable
from src.components.filter_panel import FilterPanel

class BaseCRUDWindow(ttk.Frame):
    """Ventana base para operaciones CRUD"""
    
    def __init__(self, parent, api: RESTClient, entity_name: str, 
                 columns: List[Dict], filters: List[Dict] = None,
                 client_mode: bool = False):
        """
        Args:
            parent: Widget padre
            api: Cliente REST
            entity_name: Nombre de la entidad (ej: "clientes")
            columns: Columnas de la tabla
            filters: Filtros disponibles
            client_mode: Si está en modo cliente (solo lectura/edición propia)
        """
        super().__init__(parent)
        self.api = api
        self.entity_name = entity_name
        self.columns = columns
        self.filters = filters or []
        self.client_mode = client_mode
        self.data = []
        
        self._create_widgets()
        self._load_data()
    
    def _create_widgets(self):
        """Crea los widgets de la ventana"""
        # Frame superior con botones
        toolbar_frame = ttk.Frame(self)
        toolbar_frame.pack(fill=tk.X, pady=5)
        
        if not self.client_mode:
            ttk.Button(toolbar_frame, text="Nuevo", 
                      command=self._on_new).pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar_frame, text="Editar", 
                      command=self._on_edit).pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar_frame, text="Eliminar", 
                      command=self._on_delete).pack(side=tk.LEFT, padx=2)
        else:
            ttk.Button(toolbar_frame, text="Editar", 
                      command=self._on_edit).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(toolbar_frame, text="Actualizar", 
                  command=self._load_data).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Filtros
        if self.filters:
            filter_panel = FilterPanel(self, self.filters, self._on_filter)
            filter_panel.pack(fill=tk.X, pady=5)
        
        # Tabla
        self.table = DataTable(self, self.columns, 
                              on_select=self._on_select,
                              on_double_click=self._on_edit)
        self.table.pack(fill=tk.BOTH, expand=True, pady=5)
    
    def _load_data(self):
        """Carga los datos desde la API"""
        result = self.api.get_all(self.entity_name)
        
        if result.get("success"):
            self.data = result.get("data", [])
            self.table.set_data(self.data)
        else:
            messagebox.showerror("Error", f"Error al cargar datos: {result.get('error')}")
    
    def _on_filter(self, filter_values: Dict):
        """Aplica filtros a los datos"""
        if not filter_values:
            self.table.clear_filter()
            return
        
        def filter_func(row):
            for key, value in filter_values.items():
                if key in row:
                    row_value = str(row[key]).lower()
                    if value.lower() not in row_value:
                        return False
            return True
        
        self.table.filter_data(filter_func)
    
    def _on_select(self, item: Dict):
        """Maneja la selección de un item"""
        pass
    
    def _on_new(self):
        """Crea un nuevo registro"""
        self._show_form(None)
    
    def _on_edit(self):
        """Edita el registro seleccionado"""
        selected = self.table.get_selected()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un registro")
            return
        self._show_form(selected)
    
    def _on_delete(self):
        """Elimina el registro seleccionado"""
        selected = self.table.get_selected()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un registro")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este registro?"):
            entity_id = selected.get("id")
            result = self.api.delete(self.entity_name, entity_id)
            
            if result.get("success"):
                messagebox.showinfo("Éxito", "Registro eliminado correctamente")
                self._load_data()
            else:
                messagebox.showerror("Error", f"Error al eliminar: {result.get('error')}")
    
    def _show_form(self, item: Optional[Dict]):
        """Muestra el formulario de edición/creación"""
        # Este método debe ser sobrescrito en las clases hijas
        raise NotImplementedError("Las clases hijas deben implementar _show_form")
    
    def _get_form_fields(self) -> List[Dict]:
        """Retorna la lista de campos del formulario"""
        # Este método debe ser sobrescrito en las clases hijas
        raise NotImplementedError("Las clases hijas deben implementar _get_form_fields")

