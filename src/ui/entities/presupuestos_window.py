"""
Ventana de gestión de presupuestos
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional

from src.ui.entities.base_crud_window import BaseCRUDWindow
from src.widgets.validated_entry import ValidatedEntry


class PresupuestosWindow(BaseCRUDWindow):
    """Gestión de presupuestos."""

    def __init__(self, parent, api):
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

        super().__init__(parent, api, "presupuestos", columns, filters, client_mode=False)

        # Relaciones
        self.clientes = []
        self.empleados = []
        self._load_related()

    # =====================================================================
    # DATOS RELACIONADOS
    # =====================================================================
    def _load_related(self):
        """Carga clientes y empleados."""
        res_c = self.api.get_clientes()
        if res_c.get("success"):
            self.clientes = res_c.get("data", [])

        res_e = self.api.get_empleados()
        if res_e.get("success"):
            self.empleados = res_e.get("data", [])

    # =====================================================================
    # CAMPOS DEL FORMULARIO
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
        form = tk.Toplevel(self)
        form.title("Nuevo Presupuesto" if item is None else "Editar Presupuesto")
        form.geometry("520x480")
        form.transient(self.winfo_toplevel())
        form.grab_set()

        form.update_idletasks()
        x = (form.winfo_screenwidth() // 2) - 260
        y = (form.winfo_screenheight() // 2) - 240
        form.geometry(f"520x480+{x}+{y}")

        main = ttk.Frame(form, padding=20)
        main.pack(fill=tk.BOTH, expand=True)

        fields = {}
        specs = self._get_form_fields()

        for i, f in enumerate(specs):
            ttk.Label(main, text=f["label"] + ":").grid(
                row=i, column=0, sticky="w", padx=5, pady=5
            )

            # ------------------ SELECTS ------------------
            if f["type"] == "select":
                # Cliente
                if f["name"] == "cliente_id":
                    opts = [
                        f"{c['id']} - {c.get('nombre', '')} {c.get('apellidos', '')}"
                        for c in self.clientes
                    ]
                # Empleado
                elif f["name"] == "empleado_id":
                    opts = [
                        f"{e['id']} - {e.get('nombre', '')} {e.get('apellidos', '')}"
                        for e in self.empleados
                    ]
                # Estado
                elif f["name"] == "estado":
                    opts = ["PENDIENTE", "APROBADO", "RECHAZADO"]
                else:
                    opts = []

                combo = ttk.Combobox(main, values=opts, width=40, state="readonly")
                combo.grid(row=i, column=1, sticky="ew", padx=5, pady=5)
                fields[f["name"]] = combo

                # Precargar valores
                if item and item.get(f["name"]) is not None:
                    if f["name"] in ("cliente_id", "empleado_id"):
                        try_id = str(item[f["name"]])
                        for op in opts:
                            if op.split(" - ")[0] == try_id:
                                combo.set(op)
                                break
                    else:
                        combo.set(str(item[f["name"]]))

            # ------------------ FECHA ------------------
            elif f["type"] == "date":
                entry = ValidatedEntry(main, validation_type="date",
                                       required=f.get("required", False),
                                       width=40)
                entry.grid(row=i, column=1, sticky="ew", padx=5, pady=5)
                fields[f["name"]] = entry

                if item and item.get(f["name"]):
                    entry.set_value(item[f["name"]])

            # ------------------ NÚMERO ------------------
            elif f["type"] == "number":
                entry = ValidatedEntry(main, validation_type="number",
                                       required=f.get("required", False),
                                       width=40)
                entry.grid(row=i, column=1, sticky="ew", padx=5, pady=5)
                fields[f["name"]] = entry

                if item and item.get(f["name"]):
                    entry.set_value(str(item[f["name"]]))

            # ------------------ TEXTO ------------------
            else:
                entry = ValidatedEntry(main, validation_type="text",
                                       required=f.get("required", False),
                                       width=40)
                entry.grid(row=i, column=1, sticky="ew", padx=5, pady=5)
                fields[f["name"]] = entry

                if item and item.get(f["name"]):
                    entry.set_value(item[f["name"]])

        main.columnconfigure(1, weight=1)

        # =====================================================================
        # BOTONES
        # =====================================================================
        btns = ttk.Frame(main)
        btns.grid(row=len(specs), column=0, columnspan=2, pady=20)

        def save():
            data = {}

            for name, widget in fields.items():

                # ----------- INPUTS VALIDATED -----------
                if isinstance(widget, ValidatedEntry):
                    if not widget.validate_input():
                        messagebox.showerror("Error", f"El campo '{name}' no es válido")
                        return
                    value = widget.get_value()

                    if value != "":
                        if name == "total":
                            try:
                                data[name] = float(value)
                            except ValueError:
                                messagebox.showerror("Error", "Total debe ser numérico")
                                return
                        else:
                            data[name] = value

                # ------------- COMBOBOX -----------------
                else:
                    value = widget.get()
                    if value != "":
                        if name in ("cliente_id", "empleado_id"):
                            data[name] = int(value.split(" - ")[0])
                        else:
                            data[name] = value

            # Guardar
            if item:
                res = self.api.update("presupuestos", item["id"], data)
            else:
                res = self.api.create("presupuestos", data)

            if res.get("success"):
                messagebox.showinfo("Éxito", "Presupuesto guardado correctamente")
                form.destroy()
                self._load_data()
            else:
                messagebox.showerror("Error", res.get("error", "Error desconocido"))

        ttk.Button(btns, text="Guardar", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="Cancelar", command=form.destroy).pack(side=tk.LEFT, padx=5)
