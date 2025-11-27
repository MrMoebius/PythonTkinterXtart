"""
Ventana base para CRUD de entidades
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Optional

from src.widgets.data_table import DataTable
from src.widgets.filter_panel import FilterPanel


class BaseCRUDWindow(ttk.Frame):
    """Ventana base para operaciones CRUD con control de permisos."""

    def __init__(self, parent, api, entity_name: str,
                 columns: List[Dict], filters: List[Dict] = None,
                 client_mode: bool = False):
        """
        parent       → Tk o Frame padre
        api          → RESTClient
        entity_name  → 'clientes', 'facturas', etc.
        columns      → definiciones de columnas para DataTable
        filters      → lista de campos filtrables
        client_mode  → True si es cliente final (solo su registro)
        """
        super().__init__(parent)

        # API
        self.api = api
        self.entity_name = entity_name

        # Config
        self.columns = columns
        self.filters = filters or []
        self.client_mode = client_mode

        # Data
        self.data = []

        self._create_widgets()
        # self._load_data()

    # =====================================================================
    # UI
    # =====================================================================
    def _create_widgets(self):
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, pady=5)

        # -------------------------------------------------------------
        # PERMISOS (CLIENTE vs EMPLEADO/ADMIN)
        # -------------------------------------------------------------
        if self.client_mode:
            # Cliente solo edita su propio registro
            self.btn_edit = ttk.Button(toolbar, text="Editar", command=self._on_edit)
            self.btn_edit.pack(side=tk.LEFT, padx=2)

        else:
            # Empleado/Admin → CRUD completo
            self.btn_new = ttk.Button(toolbar, text="Nuevo", command=self._on_new)
            self.btn_new.pack(side=tk.LEFT, padx=2)

            self.btn_edit = ttk.Button(toolbar, text="Editar", command=self._on_edit)
            self.btn_edit.pack(side=tk.LEFT, padx=2)

            self.btn_delete = ttk.Button(toolbar, text="Eliminar", command=self._on_delete)
            self.btn_delete.pack(side=tk.LEFT, padx=2)

        ttk.Button(toolbar, text="Actualizar", command=self._load_data).pack(side=tk.LEFT, padx=2)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # -------------------------------------------------------------
        # FILTROS (solo empleados/admin)
        # -------------------------------------------------------------
        if self.filters and not self.client_mode:
            self.filter_panel = FilterPanel(self, self.filters, self._on_filter)
            self.filter_panel.pack(fill=tk.X, pady=5)

        # -------------------------------------------------------------
        # TABLA
        # -------------------------------------------------------------
        self.table = DataTable(
            self,
            self.columns,
            on_select=self._on_select,
            on_double_click=self._on_edit
        )
        self.table.pack(fill=tk.BOTH, expand=True, pady=5)

    # =====================================================================
    # CARGA DE DATOS
    # =====================================================================
    def _load_data(self):
        result = self.api.get_all(self.entity_name)

        if not result.get("success"):
            messagebox.showerror("Error", f"Error al cargar datos: {result.get('error')}")
            return

        data = result.get("data", [])

        # -------------------------------------------------------------
        # CLIENTE → Solo ve su propio registro (id == user_id)
        # -------------------------------------------------------------
        if self.client_mode:
            uid = getattr(self.api, "user_id", None)
            data = [row for row in data if row.get("id") == uid]

        self.data = data

        # Si es ventana de empleados, aplicar roles
        if hasattr(self, "_apply_role_names"):
            self._apply_role_names()
        else:
            self.table.set_data(self.data)


    # =====================================================================
    # FILTRADO (solo empleados/admin)
    # =====================================================================
    def _on_filter(self, filter_values: Dict):

        nombre = filter_values.get("nombre")
        email = filter_values.get("email")
        rol_text = filter_values.get("rol_nombre")  # valor exacto del combo

        params = {}

        if nombre:
            params["nombre"] = nombre

        if email:
            params["email"] = email

        # Filtro por rol solo si NO es "(Sin filtro)"
        if rol_text and rol_text != "(Sin filtro)":
            rid = next((r["id"] for r in self.roles if r["nombre"] == rol_text), None)
            if rid:
                params["rol_empleado"] = rid

        # Si no hay filtros, recargar todo
        if not params:
            self._load_data()
            return

        # Pedir al backend DEMO
        result = self.api.get_all("empleados", params=params)

        if not result.get("success"):
            messagebox.showerror("Error", "No se pudo aplicar filtros.")
            return

        self.data = result.get("data", [])

        # Aplicar conversion rol_id → rol_nombre
        self._apply_role_names()

        # Mostrar en tabla
        self.table.set_data(self.data)



    # =====================================================================
    # CRUD
    # =====================================================================
    def _on_new(self):
        if self.client_mode:
            messagebox.showwarning("Acceso denegado", "No puede crear registros.")
            return

        self._show_form(None)

    def _on_edit(self):
        selected = self.table.get_selected()

        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un registro.")
            return

        # Cliente solo edita su propio registro
        if self.client_mode:
            if selected.get("id") != getattr(self.api, "user_id", None):
                messagebox.showwarning("Acceso denegado", "Solo puede editar su propio perfil.")
                return

        self._show_form(selected)

    def _on_delete(self):
        if self.client_mode:
            messagebox.showwarning("Acceso denegado", "No puede eliminar registros.")
            return

        selected = self.table.get_selected()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un registro.")
            return

        if not messagebox.askyesno("Confirmar", "¿Eliminar este registro?"):
            return

        entity_id = selected.get("id")
        result = self.api.delete(self.entity_name, entity_id)

        if result.get("success"):
            messagebox.showinfo("Éxito", "Registro eliminado.")
            self._load_data()
        else:
            messagebox.showerror("Error", f"No se pudo eliminar: {result.get('error')}")

    # =====================================================================
    # Métodos a implementar por las clases hijas
    # =====================================================================
    def _show_form(self, item: Optional[Dict]):
        raise NotImplementedError("Debe implementarse en la clase hija")

    def _get_form_fields(self) -> List[Dict]:
        raise NotImplementedError("Debe implementarse en la clase hija")

    def get_all_filtered(self, entity_name, filters):
        return self.get(entity_name, params=filters)
