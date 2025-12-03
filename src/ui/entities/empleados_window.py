"""
Ventana de gestión de empleados
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional
import logging

from src.ui.entities.base_crud_window import BaseCRUDWindow
from src.widgets.validated_entry import ValidatedEntry

logger = logging.getLogger(__name__)


class EmpleadosWindow(BaseCRUDWindow):
    """Gestión de empleados (Solo ADMIN)."""

    def __init__(self, parent, api):

        # Crear lista vacía ANTES DE LLAMAR A super()
        self.roles = []

        # ---------------------------------------------------------
        # Columnas (sin apellidos, el backend no lo tiene)
        # ---------------------------------------------------------
        columns = [
            {"name": "id", "width": 60, "anchor": "center"},
            {"name": "nombre", "width": 200},
            {"name": "email", "width": 220},
            {"name": "telefono", "width": 130},
            {"name": "rol_nombre", "width": 150},
        ]

        # ---------------------------------------------------------
        # Filtros (implementados en frontend, backend no los soporta)
        # ---------------------------------------------------------
        filters = [
            {"name": "nombre", "type": "text", "label": "Nombre"},
            {"name": "email", "type": "text", "label": "Email"},
            {"name": "rol_nombre", "type": "select", "label": "Rol", "options": ["(Sin filtro)"]},
        ]

        # Crear ventana base
        super().__init__(parent, api, "empleados", columns, filters, client_mode=False)

        # YA podemos cargar roles
        self._load_roles()

        # Actualizar las opciones del filtro de rol
        if hasattr(self, "filter_panel") and self.filter_panel:
            self.filter_panel.filter_widgets["rol_nombre"]["values"] = \
                ["(Sin filtro)"] + [r.get("nombre_rol", r.get("nombre", "")) for r in self.roles]
            self.filter_panel.filter_widgets["rol_nombre"].set("(Sin filtro)")

        # Aplicar nombres de rol en la tabla
        self._apply_role_names()

    # =====================================================================
    # ROLES
    # =====================================================================
    def _load_roles(self):
        """Carga los roles de empleado desde el backend"""
        result = self.api.get_roles_empleado()
        if result.get("success"):
            self.roles = result.get("data", [])
        else:
            self.roles = []
        
        # Actualizar filtro de rol si existe
        if hasattr(self, "filter_panel") and self.filter_panel:
            self.filter_panel.filter_widgets["rol_nombre"]["values"] = \
                ["(Sin filtro)"] + [r.get("nombre_rol", r.get("nombre", "")) for r in self.roles]
            self.filter_panel.filter_widgets["rol_nombre"].set("(Sin filtro)")

    def _apply_role_names(self):
        """Convierte id_rol → rol_nombre para mostrar en tabla."""
        for emp in self.data:
            # El backend devuelve id_rol como objeto: {"id_rol": {"id_rol": 1, "nombre_rol": "direccion"}}
            id_rol_obj = emp.get("id_rol")
            if isinstance(id_rol_obj, dict):
                # Extraer el ID del objeto id_rol
                rol_id = id_rol_obj.get("id_rol")
                # Extraer el nombre del rol del objeto
                rol_nombre = id_rol_obj.get("nombre_rol", "")
            else:
                # Si viene como número directo (por compatibilidad)
                rol_id = id_rol_obj if isinstance(id_rol_obj, int) else None
                rol_nombre = ""
            
            # Buscar el nombre del rol en la lista de roles cargados
            if rol_id and not rol_nombre:
                rol_nombre = next(
                    (r.get("nombre_rol", r.get("nombre", "")) for r in self.roles if r.get("id_rol") == rol_id),
                    "SIN ROL"
                )
            elif not rol_nombre:
                rol_nombre = "SIN ROL"
            
            emp["rol_nombre"] = rol_nombre

        if hasattr(self, "table"):
            self.table.set_data(self.data)

    # =====================================================================
    # CAMPOS DEL FORMULARIO
    # =====================================================================
    def _get_form_fields(self):
        """
        Definición de los campos del formulario de empleados.
        
        Campos que el backend Java acepta:
        - nombre (obligatorio)
        - email (obligatorio, único)
        - telefono (opcional)
        - id_rol (opcional, formato: {"id_rol": {"id_rol": 2}})
        """
        return [
            {"name": "nombre", "label": "Nombre", "type": "text", "required": True},
            {"name": "email", "label": "Email", "type": "email", "required": True},
            {"name": "telefono", "label": "Teléfono", "type": "phone", "required": False},
            {"name": "id_rol", "label": "Rol", "type": "select", "required": False},
        ]

    # =====================================================================
    # FORMULARIO EMPLEADO
    # =====================================================================
    def _on_select(self, item):
        pass
    
    def _show_form(self, item: Optional[Dict]):
        """Ventana de creación o edición de empleados."""

        # Validar que item es un diccionario si no es None
        if item is not None and not isinstance(item, dict):
            logger.error(f"Error: item debe ser un diccionario o None, pero recibió: {type(item)}")
            messagebox.showerror("Error", f"Error al cargar datos del formulario: tipo inesperado {type(item)}")
            return

        form = tk.Toplevel(self)
        form.title("Nuevo Empleado" if item is None else "Editar Empleado")
        form.geometry("600x300")
        form.transient(self.winfo_toplevel())
        form.grab_set()

        form.update_idletasks()
        x = (form.winfo_screenwidth() // 2) - 300
        y = (form.winfo_screenheight() // 2) - 160
        form.geometry(f"600x300+{x}+{y}")

        # Frame principal
        main = ttk.Frame(form, padding=15)
        main.pack(fill=tk.BOTH, expand=True)

        fields = {}
        form_fields = self._get_form_fields()

        # Asegurar que messagebox esté disponible en el closure
        from tkinter import messagebox as mb

        for i, field in enumerate(form_fields):

            ttk.Label(main, text=field["label"] + ":").grid(
                row=i, column=0, pady=4, padx=5, sticky="w"
            )

            field_type = field.get("type", "text")

            # SELECT = roles
            if field_type == "select":
                # Obtener nombres de roles
                options = [r.get("nombre_rol", r.get("nombre", "")) for r in self.roles]
                combo = ttk.Combobox(main, values=options, state="readonly", width=30)
                combo.grid(row=i, column=1, pady=6, padx=5, sticky="ew")
                fields[field["name"]] = combo

                # Cargar valor si se está editando
                if item and isinstance(item, dict):
                    id_rol_obj = item.get("id_rol")
                    if isinstance(id_rol_obj, dict):
                        rol_id = id_rol_obj.get("id_rol")
                        rol_nombre = id_rol_obj.get("nombre_rol", "")
                    else:
                        rol_id = id_rol_obj if isinstance(id_rol_obj, int) else None
                        rol_nombre = ""
                    
                    # Buscar el nombre del rol
                    if rol_id and not rol_nombre:
                        rol_nombre = next(
                            (r.get("nombre_rol", r.get("nombre", "")) for r in self.roles if r.get("id_rol") == rol_id),
                            ""
                        )
                    
                    if rol_nombre:
                        combo.set(rol_nombre)
                    elif options:
                        combo.current(0)

            # EMAIL
            elif field_type == "email":
                entry = ValidatedEntry(main, validation_type="email",
                                       required=field.get("required", False),
                                       width=30)
                entry.grid(row=i, column=1, pady=4, padx=5, sticky="ew")
                fields[field["name"]] = entry

                if item and isinstance(item, dict):
                    value = item.get(field["name"])
                    if value is not None:
                        entry.set_value(str(value))

            # PHONE
            elif field_type == "phone":
                entry = ValidatedEntry(main, validation_type="phone",
                                       required=False, width=40)
                entry.grid(row=i, column=1, pady=4, padx=5, sticky="ew")
                fields[field["name"]] = entry

                if item and isinstance(item, dict):
                    value = item.get(field["name"])
                    if value is not None:
                        entry.set_value(str(value))

            # TEXTO
            else:
                entry = ValidatedEntry(main, validation_type="text",
                                       required=field.get("required", False),
                                       width=30)
                entry.grid(row=i, column=1, pady=4, padx=5, sticky="ew")
                fields[field["name"]] = entry

                if item and isinstance(item, dict):
                    value = item.get(field["name"])
                    if value is not None:
                        entry.set_value(str(value))

        main.columnconfigure(1, weight=1)

        # ---------------------------------------------------------
        # BOTONES
        # ---------------------------------------------------------
        btns = ttk.Frame(main)
        btns.grid(row=len(form_fields), column=0, columnspan=2, pady=15)

        def save():
            data = {}

            # Validar y recoger datos
            for name, widget in fields.items():

                # Combobox → obtener ID del rol y formatear correctamente
                if isinstance(widget, ttk.Combobox):
                    selected = widget.get()
                    if selected and selected.strip():
                        # Buscar el rol por nombre
                        rol_obj = next(
                            (r for r in self.roles if r.get("nombre_rol", r.get("nombre", "")) == selected),
                            None
                        )
                        if rol_obj:
                            rol_id = rol_obj.get("id_rol")
                            # Formato correcto: {"id_rol": {"id_rol": 2}}
                            data["id_rol"] = {"id_rol": rol_id}
                        else:
                            mb.showerror("Error", "Seleccione un rol válido")
                            return
                    # Si no se selecciona rol, no se envía (opcional)

                # ValidatedEntry
                elif isinstance(widget, ValidatedEntry):
                    if not widget.validate_input():
                        mb.showerror("Error", f"El campo '{name}' no es válido")
                        return
                    value = widget.get_value()
                    if value and str(value).strip():
                        data[name] = str(value).strip()

            # Validar campos obligatorios
            if not data.get("nombre"):
                mb.showerror("Error", "El campo 'Nombre' es obligatorio")
                return
            
            if not data.get("email"):
                mb.showerror("Error", "El campo 'Email' es obligatorio")
                return

            # Guardar
            if item is None:
                # POST: Crear nuevo empleado
                # No enviar id_empleado, password, fecha_ingreso, estado (se generan automáticamente)
                logger.info(f"Datos a enviar al backend (POST): {data}")
                result = self.api.create("empleados", data)
            else:
                # PUT: Actualizar empleado existente
                # Obtener id_empleado del item
                empleado_id = item.get("id_empleado") or item.get("id")
                if not empleado_id:
                    mb.showerror("Error", "No se pudo obtener el ID del empleado")
                    return
                
                # Agregar id_empleado al payload (obligatorio para PUT)
                update_data = data.copy()
                update_data["id_empleado"] = empleado_id
                
                logger.info(f"Datos a enviar al backend (PUT): {update_data}")
                result = self.api.update("empleados", empleado_id, update_data)

            if result.get("success"):
                mb.showinfo("Éxito", "Empleado guardado correctamente")
                form.destroy()
                self._load_data()
            else:
                error_msg = result.get("error", "Error desconocido")
                # Si el error viene en data.error, extraerlo
                if isinstance(error_msg, dict):
                    error_msg = error_msg.get("error", str(error_msg))
                logger.error(f"Error al guardar empleado: {error_msg}")
                mb.showerror("Error", f"No se pudo guardar el empleado:\n{error_msg}")

        ttk.Button(btns, text="Guardar", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="Cancelar", command=form.destroy).pack(side=tk.LEFT, padx=5)
        
    def _load_data(self):
        """Carga los datos de empleados y aplica nombres de rol"""
        super()._load_data()
        self._load_roles()
        self._apply_role_names()

    def _on_filter(self, filter_values: Dict):
        """Aplica filtros a los empleados (implementado en frontend)"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Filtros recibidos: {filter_values}")
        
        # Cargar todos los empleados primero (backend no soporta filtros)
        result = self.api.get_all("empleados")
        
        if not result.get("success"):
            error_msg = result.get("error", "Error desconocido")
            logger.error(f"Error al cargar empleados: {error_msg}")
            messagebox.showerror("Error", f"Error al cargar empleados:\n{error_msg}")
            return

        data = result.get("data", [])
        if data is None:
            data = []
        elif not isinstance(data, list):
            data = [data] if data else []

        # Aplicar filtros en el frontend
        filtered_data = data.copy()
        
        # Filtro por nombre
        if "nombre" in filter_values and filter_values.get("nombre"):
            nombre_filter = filter_values["nombre"].lower()
            filtered_data = [
                emp for emp in filtered_data
                if nombre_filter in str(emp.get("nombre", "")).lower()
            ]
        
        # Filtro por email
        if "email" in filter_values and filter_values.get("email"):
            email_filter = filter_values["email"].lower()
            filtered_data = [
                emp for emp in filtered_data
                if email_filter in str(emp.get("email", "")).lower()
            ]
        
        # Filtro por rol
        if "rol_nombre" in filter_values and filter_values.get("rol_nombre"):
            rol_filter = filter_values["rol_nombre"]
            if rol_filter and rol_filter != "(Sin filtro)":
                # Buscar el ID del rol
                rol_obj = next(
                    (r for r in self.roles if r.get("nombre_rol", r.get("nombre", "")) == rol_filter),
                    None
                )
                if rol_obj:
                    rol_id = rol_obj.get("id_rol")
                    filtered_data = [
                        emp for emp in filtered_data
                        if self._get_empleado_rol_id(emp) == rol_id
                    ]

        # Normalizar IDs
        for row in filtered_data:
            if isinstance(row, dict):
                if "id_empleado" in row and "id" not in row:
                    row["id"] = row["id_empleado"]

        self.data = filtered_data
        logger.info(f"Datos filtrados: {len(self.data)} registros")

        # Aplicar nombres de rol
        self._apply_role_names()

    def _get_empleado_rol_id(self, emp: Dict) -> Optional[int]:
        """Extrae el ID del rol de un empleado"""
        id_rol_obj = emp.get("id_rol")
        if isinstance(id_rol_obj, dict):
            return id_rol_obj.get("id_rol")
        elif isinstance(id_rol_obj, int):
            return id_rol_obj
        return None
