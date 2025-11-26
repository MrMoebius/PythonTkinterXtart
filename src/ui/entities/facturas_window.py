"""
Ventana de gestión de facturas
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional

from src.ui.entities.base_crud_window import BaseCRUDWindow
from src.widgets.validated_entry import ValidatedEntry


class FacturasWindow(BaseCRUDWindow):
    """Ventana para gestionar facturas"""

    def __init__(self, parent, api, client_mode: bool = False):

        columns = [
            {"name": "id", "width": 60, "anchor": "center"},
            {"name": "cliente_id", "width": 80, "anchor": "center"},
            {"name": "empleado_id", "width": 80, "anchor": "center"},
            {"name": "fecha", "width": 120},
            {"name": "total", "width": 120, "anchor": "e"},
            {"name": "estado", "width": 120},
        ]

        filters = [
            {"name": "cliente_id", "type": "number", "label": "Cliente"},
            {"name": "estado", "type": "text", "label": "Estado"},
        ]

        super().__init__(parent, api, "facturas", columns, filters, client_mode)

        self.clientes = []
        self.empleados = []

        if client_mode:
            self._load_my_facturas()
        else:
            self._load_related()

    # =====================================================================
    # DATOS RELACIONADOS
    # =====================================================================
    def _load_my_facturas(self):
        res = self.api.get_my_facturas()
        if res.get("success"):
            self.data = res.get("data", [])
            self.table.set_data(self.data)

    def _load_related(self):
        res_c = self.api.get_clientes()
        if res_c.get("success"):
            self.clientes = res_c.get("data", [])

        res_e = self.api.get_empleados()
        if res_e.get("success"):
            self.empleados = res_e.get("data", [])

    # =====================================================================
    # FORMULARIO CAMPOS
    # =====================================================================
    def _get_form_fields(self):
        return [
            {"name": "cliente_id", "label": "Cliente", "type": "select", "required": True},
            {"name": "empleado_id", "label": "Empleado", "type": "select", "required": True},
            {"name": "fecha", "label": "Fecha (YYYY-MM-DD)", "type": "date", "required": True},
            {"name": "total", "label": "Total (€)", "type": "number", "required": True},
            {"name": "estado", "label": "Estado", "type": "select", "required": True},
        ]

    # =====================================================================
    # FORMULARIO
    # =====================================================================
    def _on_select(self, item):
        pass
    
    def _show_form(self, item: Optional[Dict]):

        if self.client_mode:
            messagebox.showinfo("Información", "Los clientes no pueden crear o editar facturas.")
            return

        form = tk.Toplevel(self)
        form.title("Nueva Factura" if item is None else "Editar Factura")
        form.geometry("520x500")
        form.transient(self.winfo_toplevel())
        form.grab_set()

        form.update_idletasks()
        x = (form.winfo_screenwidth() // 2) - 260
        y = (form.winfo_screenheight() // 2) - 250
        form.geometry(f"520x500+{x}+{y}")

        main = ttk.Frame(form, padding=20)
        main.pack(fill=tk.BOTH, expand=True)

        fields = {}
        specs = self._get_form_fields()

        # =====================================================================
        # CREAR WIDGETS
        # =====================================================================
        for i, f in enumerate(specs):

            ttk.Label(main, text=f["label"] + ":").grid(
                row=i, column=0, sticky="w", padx=5, pady=6
            )

            # ---------------- SELECTS ----------------
            if f["type"] == "select":

                if f["name"] == "cliente_id":
                    opts = [
                        f"{c['id']} - {c.get('nombre', '')} {c.get('apellidos', '')}"
                        for c in self.clientes
                    ]

                elif f["name"] == "empleado_id":
                    opts = [
                        f"{e['id']} - {e.get('nombre', '')} {e.get('apellidos', '')}"
                        for e in self.empleados
                    ]

                elif f["name"] == "estado":
                    opts = ["PENDIENTE", "PAGADA", "CANCELADA"]

                else:
                    opts = []

                combo = ttk.Combobox(main, values=opts, width=40, state="readonly")
                combo.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                fields[f["name"]] = combo

                # Precargar datos
                if item and item.get(f["name"]) is not None:
                    saved = str(item[f["name"]])
                    for op in opts:
                        if op.split(" - ")[0] == saved:
                            combo.set(op)
                            break
                    else:
                        combo.set(saved)

            # ---------------- DATE ----------------
            elif f["type"] == "date":
                entry = ValidatedEntry(
                    main, validation_type="date",
                    required=f.get("required", False),
                    width=40
                )
                entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                fields[f["name"]] = entry

                if item and item.get(f["name"]):
                    entry.set_value(item[f["name"]])

            # ---------------- NUMBER ----------------
            elif f["type"] == "number":
                entry = ValidatedEntry(
                    main, validation_type="number",
                    required=f.get("required", False),
                    width=40
                )
                entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                fields[f["name"]] = entry

                if item and item.get(f["name"]):
                    entry.set_value(str(item[f["name"]]))

            # ---------------- TEXT GENÉRICO ----------------
            else:
                entry = ValidatedEntry(
                    main, validation_type="text",
                    required=f.get("required", False),
                    width=40
                )
                entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                fields[f["name"]] = entry

                if item and item.get(f["name"]):
                    entry.set_value(item[f["name"]])

        main.columnconfigure(1, weight=1)

        # =====================================================================
        # BOTONES
        # =====================================================================
        buttons = ttk.Frame(main)
        buttons.grid(row=len(specs), column=0, columnspan=2, pady=25)

        def save():
            data = {}

            for name, widget in fields.items():

                # ValidatedEntry
                if isinstance(widget, ValidatedEntry):
                    if not widget.validate_input():
                        messagebox.showerror("Error", f"El campo '{name}' no es válido")
                        return

                    value = widget.get_value()
                    if value != "":
                        if name == "total":
                            try:
                                data[name] = float(value)
                            except:
                                messagebox.showerror("Error", "El total debe ser numérico")
                                return
                        else:
                            data[name] = value

                # ComboBox
                else:
                    value = widget.get()
                    if value != "":
                        if name in ("cliente_id", "empleado_id"):
                            data[name] = int(value.split(" - ")[0])
                        else:
                            data[name] = value

            # Guardar
            if item:
                res = self.api.update("facturas", item["id"], data)
            else:
                res = self.api.create("facturas", data)

            if res.get("success"):
                messagebox.showinfo("Éxito", "Factura guardada correctamente")
                form.destroy()
                self._load_data()
            else:
                messagebox.showerror("Error", res.get("error", "Error desconocido"))

        ttk.Button(buttons, text="Guardar", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons, text="Cancelar", command=form.destroy).pack(side=tk.LEFT, padx=5)
