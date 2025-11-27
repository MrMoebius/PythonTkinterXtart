"""
Ventana de gestión de pagos
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional

from src.ui.entities.base_crud_window import BaseCRUDWindow
from src.widgets.validated_entry import ValidatedEntry


class PagosWindow(BaseCRUDWindow):
    """Ventana para gestionar pagos"""

    def __init__(self, parent, api, client_mode: bool = False):

        columns = [
            {"name": "id", "width": 60, "anchor": "center"},
            {"name": "factura_id", "width": 80, "anchor": "center"},
            {"name": "cliente_id", "width": 80, "anchor": "center"},
            {"name": "fecha", "width": 120},
            {"name": "importe", "width": 120, "anchor": "e"},
            {"name": "metodo_pago", "width": 140},
            {"name": "estado", "width": 120},
        ]

        filters = [
            {"name": "cliente_id", "type": "number", "label": "Cliente"},
            {"name": "metodo_pago", "type": "text", "label": "Método"},
            {"name": "estado", "type": "text", "label": "Estado"},
        ]

        super().__init__(parent, api, "pagos", columns, filters, client_mode)

        self.facturas = []
        self.clientes = []

        if client_mode:
            self._load_my_pagos()
        else:
            self._load_related()

    # =====================================================================
    # DATOS RELACIONADOS
    # =====================================================================
    def _load_my_pagos(self):
        res = self.api.get_my_pagos()
        if res.get("success"):
            self.data = res.get("data", [])
            self.table.set_data(self.data)

    def _load_related(self):
        res_f = self.api.get_facturas()
        if res_f.get("success"):
            self.facturas = res_f.get("data", [])

        res_c = self.api.get_clientes()
        if res_c.get("success"):
            self.clientes = res_c.get("data", [])

    # =====================================================================
    # CAMPOS DEL FORMULARIO
    # =====================================================================
    def _get_form_fields(self):
        return [
            {"name": "factura_id", "label": "Factura", "type": "select", "required": True},
            {"name": "cliente_id", "label": "Cliente", "type": "select", "required": True},
            {"name": "fecha", "label": "Fecha (YYYY-MM-DD)", "type": "date", "required": True},
            {"name": "importe", "label": "Importe (€)", "type": "number", "required": True},
            {"name": "metodo_pago", "label": "Método de pago", "type": "select", "required": True},
            {"name": "estado", "label": "Estado", "type": "select", "required": True},
        ]

    # =====================================================================
    # FORMULARIO
    # =====================================================================
    def _on_select(self, item):
        pass
    
    def _show_form(self, item: Optional[Dict]):

        # Los clientes solo visualizan
        if self.client_mode:
            messagebox.showinfo("Información", "Los clientes no pueden crear o editar pagos.")
            return

        form = tk.Toplevel(self)
        form.title("Nuevo Pago" if item is None else "Editar Pago")
        form.geometry("520x520")
        form.transient(self.winfo_toplevel())
        form.grab_set()

        form.update_idletasks()
        x = (form.winfo_screenwidth() // 2) - 260
        y = (form.winfo_screenheight() // 2) - 260
        form.geometry(f"520x520+{x}+{y}")

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

                # Factura
                if f["name"] == "factura_id":
                    opts = [
                        f"{fa['id']} - Cliente {fa.get('cliente_id')}"
                        for fa in self.facturas
                    ]

                # Cliente
                elif f["name"] == "cliente_id":
                    opts = [
                        f"{c['id']} - {c.get('nombre', '')} {c.get('apellidos', '')}"
                        for c in self.clientes
                    ]

                # Método
                elif f["name"] == "metodo_pago":
                    opts = ["TARJETA", "TRANSFERENCIA", "EFECTIVO", "CHEQUE"]

                # Estado
                elif f["name"] == "estado":
                    opts = ["PENDIENTE", "COMPLETADO", "CANCELADO"]

                else:
                    opts = []

                combo = ttk.Combobox(main, values=opts, width=40, state="readonly")
                combo.grid(row=i, column=1, sticky="ew", padx=5, pady=5)
                fields[f["name"]] = combo

                # PRECARGAR
                if item and item.get(f["name"]) is not None:
                    saved = str(item[f["name"]])
                    for op in opts:
                        if op.split(" - ")[0] == saved:
                            combo.set(op)
                            break
                    else:
                        combo.set(saved)

            # ------------------ DATE ------------------
            elif f["type"] == "date":
                entry = ValidatedEntry(
                    main, validation_type="date",
                    required=f.get("required", False),
                    width=40
                )
                entry.grid(row=i, column=1, sticky="ew", padx=5, pady=5)
                fields[f["name"]] = entry

                if item and item.get(f["name"]):
                    entry.set_value(item[f["name"]])

            # ------------------ NUMBER ------------------
            elif f["type"] == "number":
                entry = ValidatedEntry(
                    main, validation_type="number",
                    required=f.get("required", False),
                    width=40
                )
                entry.grid(row=i, column=1, sticky="ew", padx=5, pady=5)
                fields[f["name"]] = entry

                if item and item.get(f["name"]):
                    entry.set_value(str(item[f["name"]]))

            # ------------------ TEXT ------------------
            else:
                entry = ValidatedEntry(
                    main, validation_type="text",
                    required=f.get("required", False),
                    width=40
                )
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

                # ValidatedEntry
                if isinstance(widget, ValidatedEntry):
                    if not widget.validate_input():
                        messagebox.showerror("Error", f"El campo '{name}' no es válido")
                        return

                    value = widget.get_value()
                    if value != "":
                        if name == "importe":
                            try:
                                data[name] = float(value)
                            except:
                                messagebox.showerror("Error", "Importe debe ser numérico")
                                return
                        else:
                            data[name] = value

                # ComboBox
                else:
                    value = widget.get()
                    if value != "":
                        if name in ("factura_id", "cliente_id"):
                            data[name] = int(value.split(" - ")[0])
                        else:
                            data[name] = value

            # Guardar
            if item:
                res = self.api.update("pagos", item["id"], data)
            else:
                res = self.api.create("pagos", data)

            if res.get("success"):
                messagebox.showinfo("Éxito", "Pago guardado correctamente")
                form.destroy()
                self._load_data()
            else:
                messagebox.showerror("Error", res.get("error", "Error desconocido"))

        ttk.Button(btns, text="Guardar", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="Cancelar", command=form.destroy).pack(side=tk.LEFT, padx=5)
