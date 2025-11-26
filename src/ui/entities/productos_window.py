"""
Ventana de gestión de productos
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional

from src.ui.entities.base_crud_window import BaseCRUDWindow
from src.widgets.validated_entry import ValidatedEntry


class ProductosWindow(BaseCRUDWindow):
    """Gestión de productos."""

    def __init__(self, parent, api):
        columns = [
            {"name": "id", "width": 60, "anchor": "center"},
            {"name": "nombre", "width": 200},
            {"name": "descripcion", "width": 300},
            {"name": "precio", "width": 100, "anchor": "e"},
            {"name": "stock", "width": 80, "anchor": "center"},
        ]

        filters = [
            {"name": "nombre", "type": "text", "label": "Nombre"},
            {"name": "precio", "type": "number", "label": "Precio"},
        ]

        super().__init__(parent, api, "productos", columns, filters, client_mode=False)

    # =====================================================================
    # CAMPOS DEL FORMULARIO
    # =====================================================================
    def _get_form_fields(self):
        return [
            {"name": "nombre", "label": "Nombre", "type": "text", "required": True},
            {"name": "descripcion", "label": "Descripción", "type": "text"},
            {"name": "precio", "label": "Precio", "type": "number", "required": True},
            {"name": "stock", "label": "Stock", "type": "number", "required": True},
        ]

    # =====================================================================
    # FORMULARIO
    # =====================================================================
    def _on_select(self, item):
        pass
    
    def _show_form(self, item: Optional[Dict]):
        form = tk.Toplevel(self)
        form.title("Nuevo Producto" if item is None else "Editar Producto")
        form.geometry("500x400")
        form.transient(self.winfo_toplevel())
        form.grab_set()

        # Centrar ventana
        form.update_idletasks()
        x = (form.winfo_screenwidth() // 2) - 250
        y = (form.winfo_screenheight() // 2) - 200
        form.geometry(f"500x400+{x}+{y}")

        # Frame principal
        main = ttk.Frame(form, padding=20)
        main.pack(fill=tk.BOTH, expand=True)

        fields = {}
        specs = self._get_form_fields()

        # Crear campos
        for i, f in enumerate(specs):
            ttk.Label(main, text=f["label"] + ":").grid(
                row=i, column=0, sticky="w", pady=5, padx=5
            )

            if f["type"] == "number":
                entry = ValidatedEntry(main, validation_type="number",
                                       required=f.get("required", False),
                                       width=40)
            else:
                entry = ValidatedEntry(main, validation_type="text",
                                       required=f.get("required", False),
                                       width=40)

            entry.grid(row=i, column=1, pady=5, padx=5, sticky="ew")

            if item and f["name"] in item:
                entry.set_value(str(item[f["name"]]))

            fields[f["name"]] = entry

        main.columnconfigure(1, weight=1)

        # =====================================================================
        # BOTONES
        # =====================================================================
        btns = ttk.Frame(main)
        btns.grid(row=len(specs), column=0, columnspan=2, pady=20)

        def save():
            data = {}

            for name, entry in fields.items():
                if not entry.validate_input():
                    messagebox.showerror("Error", f"El campo '{name}' no es válido")
                    return

                value = entry.get_value()

                if value == "":
                    continue

                # Convertir valores numéricos
                if name == "precio":
                    try:
                        data[name] = float(value)
                    except ValueError:
                        messagebox.showerror("Error", "Precio debe ser un número válido")
                        return

                elif name == "stock":
                    try:
                        data[name] = int(value)
                    except ValueError:
                        messagebox.showerror("Error", "Stock debe ser un entero")
                        return

                else:
                    data[name] = value

            # Guardar en API
            if item:
                result = self.api.update("productos", item["id"], data)
            else:
                result = self.api.create("productos", data)

            if result.get("success"):
                messagebox.showinfo("Éxito", "Producto guardado correctamente")
                form.destroy()
                self._load_data()
            else:
                messagebox.showerror("Error", result.get("error", "Error desconocido"))

        ttk.Button(btns, text="Guardar", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="Cancelar", command=form.destroy).pack(side=tk.LEFT, padx=5)
