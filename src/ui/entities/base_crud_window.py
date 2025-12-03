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
            # Cliente NO puede editar datos (solo visualización)
            # No se muestra botón de edición
            pass
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
        # En modo cliente, no permitir edición con doble click
        double_click_handler = None if self.client_mode else self._on_edit
        self.table = DataTable(
            self,
            self.columns,
            on_select=self._on_select,
            on_double_click=double_click_handler
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
        
        # Normalizar IDs: el backend Java usa id_cliente, id_empleado, etc.
        # pero la tabla espera "id" genérico
        if isinstance(data, list):
            for row in data:
                if isinstance(row, dict):
                    # Mapear id_cliente, id_empleado, etc. a "id" para la tabla
                    if "id_cliente" in row and "id" not in row:
                        row["id"] = row["id_cliente"]
                    elif "id_empleado" in row and "id" not in row:
                        row["id"] = row["id_empleado"]
                    elif "id_producto" in row and "id" not in row:
                        row["id"] = row["id_producto"]
                    elif "id_factura" in row and "id" not in row:
                        row["id"] = row["id_factura"]
                    elif "id_Presupuesto" in row and "id" not in row:
                        row["id"] = row["id_Presupuesto"]
                    elif "id_pago" in row and "id" not in row:
                        row["id"] = row["id_pago"]
                    
                    # Normalizar campos relacionados para presupuestos/facturas
                    # Si la tabla muestra cliente_id pero el backend devuelve id_cliente
                    if "id_cliente" in row and "cliente_id" not in row:
                        row["cliente_id"] = row["id_cliente"]
                    if "id_empleado" in row and "empleado_id" not in row:
                        row["empleado_id"] = row["id_empleado"]
                    
                    # Para presupuestos: normalizar presupuesto (el backend devuelve presupuesto, no total)
                    # Ya está correcto, solo asegurar que id_Presupuesto se normalice a id

        # -------------------------------------------------------------
        # CLIENTE → Solo ve su propio registro (id == user_id)
        # -------------------------------------------------------------
        if self.client_mode:
            uid = getattr(self.api, "user_id", None)
            data = [row for row in data if row.get("id") == uid or row.get("id_cliente") == uid]

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
        """Aplica filtros a la entidad actual"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Filtros recibidos: {filter_values}")
        
        # Construir parámetros de filtro según los valores recibidos
        params = {}
        
        # Filtros comunes (nombre, email, telefono)
        if "nombre" in filter_values and filter_values.get("nombre"):
            params["nombre"] = filter_values["nombre"]
        
        if "email" in filter_values and filter_values.get("email"):
            params["email"] = filter_values["email"]
        
        if "telefono" in filter_values and filter_values.get("telefono"):
            params["telefono"] = filter_values["telefono"]
        
        # Filtro por cliente_id (para facturas, pagos, etc.)
        if "cliente_id" in filter_values and filter_values.get("cliente_id"):
            cliente_id_val = filter_values.get("cliente_id")
            # Intentar convertir a entero si es posible
            try:
                if isinstance(cliente_id_val, str) and cliente_id_val.strip():
                    # Si es un string numérico, convertirlo
                    params["cliente_id"] = int(cliente_id_val.strip())
                elif isinstance(cliente_id_val, (int, float)):
                    params["cliente_id"] = int(cliente_id_val)
            except (ValueError, TypeError):
                # Si no es un número válido, intentar buscar por nombre
                # Esto se manejará en el método específico de la entidad
                pass
        
        # Filtro por rol (solo para empleados, si existe el atributo roles)
        if "rol_nombre" in filter_values and hasattr(self, "roles"):
            rol_text = filter_values.get("rol_nombre")
            if rol_text and rol_text != "(Sin filtro)":
                rid = next((r["id"] for r in self.roles if r["nombre"] == rol_text), None)
                if rid:
                    params["rol_empleado"] = rid

        logger.info(f"Parámetros construidos: {params}")

        # Si no hay filtros, recargar todo
        if not params:
            logger.info("No hay filtros, recargando todos los datos")
            self._load_data()
            return

        # Usar el método específico según la entidad
        if self.entity_name == "clientes":
            # Usar el método específico de clientes con filtros
            logger.info(f"Llamando a get_clientes con: nombre={params.get('nombre')}, email={params.get('email')}, telefono={params.get('telefono')}")
            result = self.api.get_clientes(
                nombre=params.get("nombre"),
                email=params.get("email"),
                telefono=params.get("telefono")
            )
        elif self.entity_name == "empleados":
            # Para empleados, el backend NO soporta filtros, se manejan en el frontend
            # La ventana EmpleadosWindow tiene su propio método _on_filter
            # Por ahora, cargar todos los empleados
            logger.info(f"Empleados: backend no soporta filtros, se manejan en frontend")
            result = self.api.get_all(self.entity_name)
        else:
            # Para otras entidades, usar el método genérico
            logger.info(f"Llamando a get_all('{self.entity_name}') con params: {params}")
            result = self.api.get_all(self.entity_name, params=params)

        logger.info(f"Resultado del backend: success={result.get('success')}, data type={type(result.get('data'))}, data length={len(result.get('data', [])) if isinstance(result.get('data'), list) else 'N/A'}")

        if not result.get("success"):
            error_msg = result.get("error", "Error desconocido")
            logger.error(f"Error al aplicar filtros: {error_msg}")
            messagebox.showerror("Error", f"No se pudo aplicar filtros.\n{error_msg}")
            return

        self.data = result.get("data", [])
        
        # Asegurar que data es una lista
        if self.data is None:
            logger.warning("Data es None, convirtiendo a lista vacía")
            self.data = []
        elif not isinstance(self.data, list):
            logger.warning(f"Data no es una lista (es {type(self.data)}), convirtiendo a lista")
            self.data = [self.data] if self.data else []

        # Normalizar IDs igual que en _load_data para que la tabla siempre tenga columna 'id'
        if isinstance(self.data, list):
            for row in self.data:
                if isinstance(row, dict):
                    # Mapear id_cliente, id_empleado, etc. a "id" genérico
                    if "id_cliente" in row and "id" not in row:
                        row["id"] = row["id_cliente"]
                    elif "id_empleado" in row and "id" not in row:
                        row["id"] = row["id_empleado"]
                    elif "id_producto" in row and "id" not in row:
                        row["id"] = row["id_producto"]
                    elif "id_factura" in row and "id" not in row:
                        row["id"] = row["id_factura"]
                    elif "id_Presupuesto" in row and "id" not in row:
                        row["id"] = row["id_Presupuesto"]
                    elif "id_pago" in row and "id" not in row:
                        row["id"] = row["id_pago"]

        logger.info(f"Datos procesados: {len(self.data)} registros")

        # Aplicar conversion rol_id → rol_nombre (solo si el método existe)
        if hasattr(self, "_apply_role_names"):
            self._apply_role_names()

        # Mostrar en tabla
        self.table.set_data(self.data)
        logger.info("Datos establecidos en la tabla")



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

        # Validar que selected es un diccionario
        if not isinstance(selected, dict):
            messagebox.showerror("Error", f"Error al obtener datos del registro seleccionado: tipo inesperado {type(selected)}")
            return

        # Cliente solo edita su propio registro
        if self.client_mode:
            if selected.get("id") != getattr(self.api, "user_id", None):
                messagebox.showwarning("Acceso denegado", "Solo puede editar su propio perfil.")
                return

        # Obtener el ID del registro (puede ser "id", "id_cliente", "id_empleado", etc.)
        entity_id = selected.get("id") or selected.get("id_cliente") or selected.get("id_empleado") or selected.get("id_factura") or selected.get("id_producto")
        
        if not entity_id:
            messagebox.showerror("Error", "No se pudo obtener el ID del registro seleccionado.")
            return

        # Obtener el registro completo del backend para asegurar que tenemos todos los campos
        # Para clientes, usar el método específico get_clientes que maneja mejor el caso de ID individual
        if self.entity_name == "clientes":
            result = self.api.get_clientes(cliente_id=entity_id)
        else:
            result = self.api.get_by_id(self.entity_name, entity_id)
        
        if not result.get("success"):
            error_msg = result.get("error", "Error desconocido")
            messagebox.showerror("Error", f"No se pudo cargar el registro para editar:\n{error_msg}")
            return

        # El backend puede devolver un objeto o una lista
        item_data = result.get("data")
        
        # Si es None, el registro no existe
        if item_data is None:
            messagebox.showerror("Error", "El registro no se encontró en el servidor.")
            return
        
        # Si es una lista, tomar el primer elemento
        if isinstance(item_data, list):
            if item_data:
                item_data = item_data[0]
            else:
                messagebox.showerror("Error", "El registro no se encontró en el servidor.")
                return
        
        # Validar que es un diccionario
        if not isinstance(item_data, dict):
            # Si no es un diccionario, usar los datos de la tabla como fallback
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"El backend devolvió un tipo inesperado: {type(item_data)}, usando datos de la tabla")
            item_data = selected
        else:
            # Normalizar ID para la tabla
            if "id_cliente" in item_data and "id" not in item_data:
                item_data["id"] = item_data["id_cliente"]
            elif "id_empleado" in item_data and "id" not in item_data:
                item_data["id"] = item_data["id_empleado"]
            elif "id_producto" in item_data and "id" not in item_data:
                item_data["id"] = item_data["id_producto"]
            elif "id_factura" in item_data and "id" not in item_data:
                item_data["id"] = item_data["id_factura"]
            elif "id_Presupuesto" in item_data and "id" not in item_data:
                item_data["id"] = item_data["id_Presupuesto"]
            elif "id_pago" in item_data and "id" not in item_data:
                item_data["id"] = item_data["id_pago"]

        self._show_form(item_data)

    def _on_delete(self):
        if self.client_mode:
            messagebox.showwarning("Acceso denegado", "No puede eliminar registros.")
            return

        selected = self.table.get_selected()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un registro.")
            return

        # Validar que selected es un diccionario
        if not isinstance(selected, dict):
            messagebox.showerror("Error", f"Error al obtener datos del registro seleccionado: tipo inesperado {type(selected)}")
            return

        if not messagebox.askyesno("Confirmar", "¿Eliminar este registro?"):
            return

        # Obtener el ID del registro (puede ser "id", "id_cliente", "id_empleado", etc.)
        entity_id = selected.get("id") or selected.get("id_cliente") or selected.get("id_empleado") or selected.get("id_factura") or selected.get("id_producto")
        
        if not entity_id:
            messagebox.showerror("Error", "No se pudo obtener el ID del registro seleccionado.")
            return

        result = self.api.delete(self.entity_name, entity_id)

        if result.get("success"):
            messagebox.showinfo("Éxito", "Registro eliminado.")
            self._load_data()
        else:
            error_msg = result.get("error", "Error desconocido")
            messagebox.showerror("Error", f"No se pudo eliminar:\n{error_msg}")

    # =====================================================================
    # Métodos a implementar por las clases hijas
    # =====================================================================
    def _show_form(self, item: Optional[Dict]):
        raise NotImplementedError("Debe implementarse en la clase hija")

    def _get_form_fields(self) -> List[Dict]:
        raise NotImplementedError("Debe implementarse en la clase hija")

