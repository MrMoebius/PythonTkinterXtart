"""
Ventana de gestión de empleados
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional

from src.ui.entities.base_crud_window import BaseCRUDWindow
from src.widgets.validated_entry import ValidatedEntry


class EmpleadosWindow(BaseCRUDWindow):
    """Gestión de empleados (Solo ADMIN)."""

    def __init__(self, parent, api):

        # Crear lista vacía ANTES DE LLAMAR A super()
        self.roles = []

        # ---------------------------------------------------------
        # Columnas
        # ---------------------------------------------------------
        columns = [
            {"name": "id", "width": 60, "anchor": "center"},
            {"name": "nombre", "width": 150},
            {"name": "apellidos", "width": 150},
            {"name": "email", "width": 220},
            {"name": "telefono", "width": 130},
            {"name": "rol_nombre", "width": 150},
        ]

        # ---------------------------------------------------------
        # Filtros
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
        self.filter_panel.filter_widgets["rol_nombre"]["values"] = \
            ["(Sin filtro)"] + [r["nombre"] for r in self.roles]

        self.filter_panel.filter_widgets["rol_nombre"].set("(Sin filtro)")


        # Aplicar nombres de rol en la tabla
        self._apply_role_names()


    # =====================================================================
    # ROLES
    # =====================================================================
    def _load_roles(self):
        result = self.api.get_roles_empleado()
        if result.get("success"):
            self.roles = result.get("data", [])
        else:
            self.roles = []
        self.filter_panel.filter_widgets["rol_nombre"]["values"] = ["(Sin filtro)"] + [r["nombre"] for r in self.roles]
        self.filter_panel.filter_widgets["rol_nombre"].set("(Sin filtro)")


    def _apply_role_names(self):
        """Convierte rol_id → rol_nombre para mostrar en tabla."""
        for emp in self.data:
            rid = emp.get("rol_empleado")
            try:
                rid = int(rid)
            except:
                rid = None

            emp["rol_nombre"] = next(
                (r["nombre"] for r in self.roles if r["id"] == rid),
                "SIN ROL"
            )


        self.table.set_data(self.data)

    # =====================================================================
    # CAMPOS DEL FORMULARIO
    # =====================================================================
    def _get_form_fields(self):
        return [
            {"name": "nombre", "label": "Nombre", "type": "text", "required": True},
            {"name": "apellidos", "label": "Apellidos", "type": "text", "required": True},
            {"name": "email", "label": "Email", "type": "email", "required": True},
            {"name": "telefono", "label": "Teléfono", "type": "phone"},
            {"name": "rol_empleado", "label": "Rol", "type": "select", "required": True},
        ]

    # =====================================================================
    # FORMULARIO EMPLEADO
    # =====================================================================
    def _on_select(self, item):
        pass
    
    def _show_form(self, item: Optional[Dict]):
        print("ITEM =", item)

        form = tk.Toplevel(self)
        form.title("Nuevo Empleado" if item is None else "Editar Empleado")
        form.geometry("500x450")
        form.transient(self.winfo_toplevel())
        form.grab_set()

        form.update_idletasks()
        x = (form.winfo_screenwidth() // 2) - 250
        y = (form.winfo_screenheight() // 2) - 220
        form.geometry(f"500x450+{x}+{y}")

        # Frame principal
        main = ttk.Frame(form, padding=20)
        main.pack(fill=tk.BOTH, expand=True)

        fields = {}
        ffields = self._get_form_fields()

        for i, f in enumerate(ffields):

            ttk.Label(main, text=f["label"] + ":").grid(
                row=i, column=0, pady=6, padx=5, sticky="w"
            )

            # SELECT = roles
            if f["type"] == "select":

                options = [r["nombre"] for r in self.roles]
                combo = ttk.Combobox(main, values=options, state="readonly", width=37)
                combo.grid(row=i, column=1, pady=6, padx=5, sticky="ew")
                fields[f["name"]] = combo

                # Cargar valor
                if item:
                    rid = item.get("rol_empleado")
                    try:
                        rid = int(rid)
                    except:
                        rid = None

                    name = next((r["nombre"] for r in self.roles if r["id"] == rid), "")
                    combo.set(name)


            # EMAIL
            elif f["type"] == "email":
                entry = ValidatedEntry(main, validation_type="email",
                                       required=f.get("required", False),
                                       width=40)
                entry.grid(row=i, column=1, pady=6, padx=5, sticky="ew")
                fields[f["name"]] = entry

                if item:
                    entry.set_value(item.get(f["name"]))

            # PHONE
            elif f["type"] == "phone":
                entry = ValidatedEntry(main, validation_type="phone",
                                       required=False, width=40)
                entry.grid(row=i, column=1, pady=6, padx=5, sticky="ew")
                fields[f["name"]] = entry

                if item:
                    entry.set_value(item.get(f["name"]))

            # TEXTO
            else:
                entry = ValidatedEntry(main, validation_type="text",
                                       required=f.get("required", False),
                                       width=40)
                entry.grid(row=i, column=1, pady=6, padx=5, sticky="ew")
                fields[f["name"]] = entry

                if item:
                    entry.set_value(item.get(f["name"]))

        main.columnconfigure(1, weight=1)

        # ---------------------------------------------------------
        # BOTONES
        # ---------------------------------------------------------
        btns = ttk.Frame(main)
        btns.grid(row=len(ffields), column=0, columnspan=2, pady=20)

        def save():

            data = {}

            for name, widget in fields.items():

                # Combobox → obtener ID del rol
                if isinstance(widget, ttk.Combobox):
                    selected = widget.get()
                    rid = next((r["id"] for r in self.roles if r["nombre"] == selected), None)
                    if rid is None:
                        messagebox.showerror("Error", "Seleccione un rol válido")
                        return
                    data["rol_empleado"] = rid

                # ValidatedEntry
                elif isinstance(widget, ValidatedEntry):
                    if not widget.validate_input():
                        messagebox.showerror("Error", f"El campo '{name}' no es válido")
                        return
                    data[name] = widget.get_value()

            # Guardar
            if item:
                result = self.api.update("empleados", item["id"], data)
            else:
                result = self.api.create("empleados", data)

            if result.get("success"):
                messagebox.showinfo("Éxito", "Empleado guardado correctamente")
                form.destroy()
                self._load_data()
                self._apply_role_names()
            else:
                message = result.get("error", "Error desconocido")
                messagebox.showerror("Error", message)

        ttk.Button(btns, text="Guardar", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="Cancelar", command=form.destroy).pack(side=tk.LEFT, padx=5)
        
    def _load_data(self):
            super()._load_data()
            self._load_roles()
            self._apply_role_names()
            self._refresh_roles_in_table()
            
    def _refresh_roles_in_table(self):
        """Rellena rol_nombre según rol_empleado en self.data."""
        for emp in self.data:
            rid = emp.get("rol_empleado")
            emp["rol_nombre"] = next(
                (r["nombre"] for r in self.roles if r["id"] == rid),
                "SIN ROL"
            )

        if hasattr(self, "table"):
            self.table.set_data(self.data)



