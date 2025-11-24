"""
Ventana de gestión de clientes
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional

from src.ui.entities.base_crud_window import BaseCRUDWindow
from src.components.validated_entry import ValidatedEntry


class ClientesWindow(BaseCRUDWindow):
    """Ventana para gestionar clientes (Empleado/Admin) o perfil (Cliente)."""

    def __init__(self, parent, api, client_mode: bool = False):

        # ---------------------------------------------------------
        # Columnas visibles en la tabla
        # ---------------------------------------------------------
        columns = [
            {"name": "id", "width": 60, "anchor": "center"},
            {"name": "nombre", "width": 150},
            {"name": "apellidos", "width": 150},
            {"name": "email", "width": 200},
            {"name": "telefono", "width": 130},
            {"name": "direccion", "width": 220},
        ]

        # ---------------------------------------------------------
        # Filtros → solo empleados/admin (controlado por BaseCRUD)
        # ---------------------------------------------------------
        filters = [
            {"name": "nombre", "type": "text", "label": "Nombre"},
            {"name": "email", "type": "text", "label": "Email"},
            {"name": "telefono", "type": "text", "label": "Teléfono"},
        ]

        super().__init__(parent, api, "clientes", columns, filters, client_mode)

    # =====================================================================
    # CAMPOS DEL FORMULARIO
    # =====================================================================
    def _get_form_fields(self) -> list:
        """Definición de los campos del formulario de clientes."""
        return [
            {"name": "nombre", "label": "Nombre", "type": "text", "required": True},
            {"name": "apellidos", "label": "Apellidos", "type": "text", "required": True},
            {"name": "email", "label": "Email", "type": "email", "required": True},
            {"name": "telefono", "label": "Teléfono", "type": "phone"},
            {"name": "direccion", "label": "Dirección", "type": "text"},
        ]

    # =====================================================================
    # FORMULARIO: CREAR / EDITAR
    # =====================================================================
    def _on_select(self, item):
        pass    
    
    def _show_form(self, item: Optional[Dict]):
        """Ventana de creación o edición de clientes."""

        form_window = tk.Toplevel(self)
        form_window.title("Nuevo Cliente" if item is None else "Editar Cliente")
        form_window.geometry("500x420")
        form_window.transient(self.winfo_toplevel())
        form_window.grab_set()

        # Centrar
        form_window.update_idletasks()
        x = (form_window.winfo_screenwidth() // 2) - 250
        y = (form_window.winfo_screenheight() // 2) - 210
        form_window.geometry(f"500x420+{x}+{y}")

        # Frame principal
        main = ttk.Frame(form_window, padding=20)
        main.pack(fill=tk.BOTH, expand=True)

        fields = {}
        form_fields = self._get_form_fields()

        # ---------------------------------------------------------
        # Crear campos
        # ---------------------------------------------------------
        for i, field in enumerate(form_fields):
            ttk.Label(main, text=field["label"] + ":").grid(
                row=i, column=0, sticky="w", pady=6, padx=5
            )

            entry = ValidatedEntry(
                main,
                validation_type=field["type"],
                required=field.get("required", False),
                width=40,
            )
            entry.grid(row=i, column=1, padx=5, pady=6, sticky="ew")

            # Rellenar si se está editando
            if item and field["name"] in item:
                entry.set_value(item[field["name"]])

            fields[field["name"]] = entry

        main.columnconfigure(1, weight=1)

        # ---------------------------------------------------------
        # BOTONES
        # ---------------------------------------------------------
        btns = ttk.Frame(main)
        btns.grid(row=len(form_fields), column=0, columnspan=2, pady=20)

        def save():
            data = {}

            # Validar y recoger datos
            for key, entry in fields.items():
                if not entry.validate_input():
                    messagebox.showerror("Error", f"El campo '{key}' no es válido.")
                    return

                value = entry.get_value()
                if value is not None:
                    data[key] = value

            # Crear o actualizar
            if item is None:
                result = self.api.create("clientes", data)
            else:
                result = self.api.update("clientes", item["id"], data)

            if result.get("success"):
                messagebox.showinfo("Éxito", "Cliente guardado correctamente.")
                form_window.destroy()
                self._load_data()
            else:
                error_msg = result.get("error", "Error desconocido")
                messagebox.showerror("Error", f"No se pudo guardar:\n{error_msg}")

        ttk.Button(btns, text="Guardar", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="Cancelar", command=form_window.destroy).pack(side=tk.LEFT, padx=5)
