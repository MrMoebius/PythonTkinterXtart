"""
Ventana de gestión de pagos
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Optional

from src.ui.entities.base_crud_window import BaseCRUDWindow
from src.widgets.validated_entry import ValidatedEntry
from src.ui.entities.pagos.pagos_export import PagoExporter
from src.ui.entities.pagos.pagos_filters import filter_pagos_by_cliente, normalize_pago_data


class PagosWindow(BaseCRUDWindow):
    """Ventana para gestionar pagos"""

    def __init__(self, parent, api, client_mode: bool = False):

        columns = [
            {"name": "id", "width": 60, "anchor": "center"},
            {"name": "factura_id", "width": 80, "anchor": "center"},
            {"name": "cliente_nombre", "width": 200, "label": "Cliente"},
            {"name": "fecha", "width": 120},
            {"name": "importe", "width": 120, "anchor": "e"},
            {"name": "metodo_pago", "width": 140},
            {"name": "estado", "width": 120},
        ]

        filters = [
            {"name": "cliente_nombre", "type": "text", "label": "Nombre Cliente"},
        ]

        super().__init__(parent, api, "pagos", columns, filters, client_mode)

        self.facturas = []
        self.clientes = []

        if client_mode:
            self._load_my_pagos()
        else:
            self._load_related()
            # Cargar datos iniciales
            self.after(100, self._load_data)
        
        # Agregar botones de exportación
        if not client_mode:
            self.after(150, self._add_export_buttons_delayed)

    # =====================================================================
    # DATOS RELACIONADOS
    # =====================================================================
    def _load_my_pagos(self):
        # Cargar clientes y facturas para normalizar datos
        if not self.clientes or not self.facturas:
            self._load_related()
        
        res = self.api.get_my_pagos()
        if res.get("success"):
            data = res.get("data", [])
            
            # Normalizar datos usando el módulo de filtros
            if isinstance(data, list):
                data = [normalize_pago_data(row, self.clientes, self.facturas) for row in data]
                
                # Asegurar que fecha esté presente y redondear importe
                for row in data:
                    if isinstance(row, dict):
                        if "fecha" not in row or not row.get("fecha"):
                            row["fecha"] = row.get("fecha_pago") or None
                        
                        # Redondear importe a 2 decimales
                        if "importe" in row and row.get("importe") is not None:
                            try:
                                importe_value = float(row["importe"])
                                row["importe"] = round(importe_value, 2)
                            except (ValueError, TypeError):
                                pass
            
            self.data = data
            self.table.set_data(self.data)

    def _load_related(self):
        res_f = self.api.get_all("facturas")
        if res_f.get("success"):
            facturas_data = res_f.get("data", [])
            # Normalizar IDs
            for f in facturas_data:
                if isinstance(f, dict) and "id_factura" in f and "id" not in f:
                    f["id"] = f["id_factura"]
            self.facturas = facturas_data

        res_c = self.api.get_clientes()
        if res_c.get("success"):
            clientes_data = res_c.get("data", [])
            # Normalizar IDs
            for c in clientes_data:
                if isinstance(c, dict) and "id_cliente" in c and "id" not in c:
                    c["id"] = c["id_cliente"]
            self.clientes = clientes_data
    
    def _load_data(self):
        """Carga datos de pagos"""
        # En modo cliente, cargar solo los pagos del cliente
        if self.client_mode:
            self._load_my_pagos()
            return
        
        result = self.api.get_all("pagos")
        
        if not result.get("success"):
            messagebox.showerror("Error", f"Error al cargar datos: {result.get('error')}")
            return
        
        data = result.get("data", [])
        
        # Normalizar datos usando el módulo de filtros
        if isinstance(data, list):
            data = [normalize_pago_data(row, self.clientes, self.facturas) for row in data]
            
            # Asegurar que fecha esté presente y redondear importe
            for row in data:
                if isinstance(row, dict):
                    if "fecha" not in row or not row.get("fecha"):
                        row["fecha"] = row.get("fecha_pago") or None
                    
                    # Redondear importe a 2 decimales
                    if "importe" in row and row.get("importe") is not None:
                        try:
                            importe_value = float(row["importe"])
                            row["importe"] = round(importe_value, 2)
                        except (ValueError, TypeError):
                            pass  # Mantener el valor original si no es numérico
        
        self.data = data
        self.table.set_data(self.data)

    # =====================================================================
    # FILTRADO
    # =====================================================================
    def _on_filter(self, filter_values: Dict):
        """Filtra pagos en memoria por nombre de cliente."""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Filtros recibidos (pagos): {filter_values}")
        
        # Si no hay filtros, mostrar todos los datos
        if not filter_values or not any(v and str(v).strip() for v in filter_values.values()):
            logger.info("No hay filtros, mostrando todos los datos")
            self._load_data()
            return
        
        # Cargar todos los datos primero
        result = self.api.get_all("pagos")
        
        if not result.get("success"):
            logger.error(f"Error al cargar pagos: {result.get('error')}")
            return
        
        data = result.get("data", [])
        
        # Filtrar usando el módulo de filtros
        filtered_data = filter_pagos_by_cliente(data, self.clientes, self.facturas, filter_values)
        
        # Asegurar que fecha esté presente y redondear importe
        for row in filtered_data:
            if isinstance(row, dict):
                if "fecha" not in row or not row.get("fecha"):
                    row["fecha"] = row.get("fecha_pago") or None
                
                # Redondear importe a 2 decimales
                if "importe" in row and row.get("importe") is not None:
                    try:
                        importe_value = float(row["importe"])
                        row["importe"] = round(importe_value, 2)
                    except (ValueError, TypeError):
                        pass  # Mantener el valor original si no es numérico
        
        logger.info(f"Datos filtrados: {len(filtered_data)} de {len(data)}")
        
        self.data = filtered_data
        self.table.set_data(self.data)

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

        # Si estamos editando, obtener el registro completo del backend
        if item:
            pago_id = item.get("id") or item.get("id_pago")
            if pago_id:
                result = self.api.get_by_id("pagos", pago_id)
                if result.get("success"):
                    pago_data = result.get("data", {})
                    if isinstance(pago_data, dict):
                        # Extraer IDs de objetos anidados si existen
                        factura_obj = pago_data.get("factura")
                        if isinstance(factura_obj, dict):
                            pago_data["factura_id"] = factura_obj.get("id_factura") or factura_obj.get("id")
                        
                        cliente_obj = pago_data.get("cliente_pagador") or pago_data.get("cliente")
                        if isinstance(cliente_obj, dict):
                            pago_data["cliente_id"] = cliente_obj.get("id_cliente") or cliente_obj.get("id")
                        
                        # Normalizar ID de pago
                        if "id_pago" in pago_data and "id" not in pago_data:
                            pago_data["id"] = pago_data["id_pago"]
                        
                        # Normalizar campo fecha (puede venir como fecha_pago)
                        if "fecha_pago" in pago_data and "fecha" not in pago_data:
                            pago_data["fecha"] = pago_data["fecha_pago"]
                        elif "fecha" not in pago_data:
                            pago_data["fecha"] = pago_data.get("fecha_pago")
                        
                        # Normalizar método de pago (asegurar que esté en minúsculas)
                        if "metodo_pago" in pago_data:
                            metodo = pago_data["metodo_pago"]
                            if isinstance(metodo, str):
                                pago_data["metodo_pago"] = metodo.upper().strip()
                        
                        # Normalizar estado (asegurar que esté en mayúsculas)
                        if "estado" in pago_data:
                            estado = pago_data["estado"]
                            if isinstance(estado, str):
                                pago_data["estado"] = estado.upper().strip()
                        
                        # Redondear importe a 2 decimales
                        if "importe" in pago_data and pago_data.get("importe") is not None:
                            try:
                                importe_value = float(pago_data["importe"])
                                pago_data["importe"] = round(importe_value, 2)
                            except (ValueError, TypeError):
                                pass
                        
                        # También intentar obtener desde campos directos si no están normalizados
                        if not pago_data.get("factura_id"):
                            pago_data["factura_id"] = pago_data.get("id_factura")
                        if not pago_data.get("cliente_id"):
                            pago_data["cliente_id"] = pago_data.get("id_cliente")
                        
                        item = pago_data

        form = tk.Toplevel(self)
        form.title("Nuevo Pago" if item is None else "Editar Pago")
        form.geometry("620x380")
        form.transient(self.winfo_toplevel())
        form.grab_set()

        form.update_idletasks()
        x = (form.winfo_screenwidth() // 2) - 310
        y = (form.winfo_screenheight() // 2) - 200
        form.geometry(f"620x380+{x}+{y}")

        main = ttk.Frame(form, padding=15)
        main.pack(fill=tk.BOTH, expand=True)

        fields = {}
        specs = self._get_form_fields()

        for i, f in enumerate(specs):

            ttk.Label(main, text=f["label"] + ":").grid(
                row=i, column=0, sticky="w", padx=5, pady=4
            )

            # ------------------ SELECTS ------------------
            if f["type"] == "select":

                # Factura
                if f["name"] == "factura_id":
                    opts = [
                        f"{fa.get('id')} - Total: €{fa.get('total', 0):.2f}"
                        for fa in self.facturas
                    ]

                # Cliente
                elif f["name"] == "cliente_id":
                    opts = []
                    for c in self.clientes:
                        nombre = c.get("nombre", "")
                        apellidos = c.get("apellidos", "")
                        razon_social = c.get("razon_social", "")
                        if razon_social:
                            display_name = razon_social
                        elif apellidos:
                            display_name = f"{nombre} {apellidos}".strip()
                        else:
                            display_name = nombre or "N/A"
                        opts.append(f"{c.get('id')} - {display_name}")

                # Método
                elif f["name"] == "metodo_pago":
                    # Valores permitidos por el backend: TRANSFERENCIA, TARJETA, EFECTIVO
                    opts = ["TRANSFERENCIA", "TARJETA", "EFECTIVO"]

                # Estado
                elif f["name"] == "estado":
                    # Estados válidos en backend: PENDIENTE, PAGADA, CANCELADA
                    opts = ["PENDIENTE", "PAGADA", "CANCELADA"]

                else:
                    opts = []

                combo = ttk.Combobox(main, values=opts, width=30, state="readonly")
                combo.grid(row=i, column=1, sticky="ew", padx=5, pady=4)
                fields[f["name"]] = combo

                # PRECARGAR
                if item and item.get(f["name"]) is not None:
                    saved_value = item.get(f["name"])
                    
                    # Para factura_id y cliente_id, buscar por ID
                    if f["name"] in ("factura_id", "cliente_id"):
                        try:
                            saved_id_int = int(saved_value)
                        except (ValueError, TypeError):
                            saved_id_int = None
                        
                        found = False
                        for op in opts:
                            op_id_str = op.split(" - ")[0]
                            try:
                                op_id_int = int(op_id_str)
                                if op_id_int == saved_id_int:
                                    combo.set(op)
                                    found = True
                                    break
                            except (ValueError, TypeError):
                                if op_id_str == str(saved_value):
                                    combo.set(op)
                                    found = True
                                    break
                        
                        if not found:
                            combo.set(str(saved_value))
                    else:
                        # Para método_pago y estado, buscar por valor (case-insensitive)
                        saved_str = str(saved_value).lower().strip()
                        found = False
                        for op in opts:
                            if op.lower() == saved_str:
                                combo.set(op)
                                found = True
                                break
                        
                        if not found:
                            # Intentar con el valor tal cual
                            combo.set(str(saved_value))

            # ------------------ DATE ------------------
            elif f["type"] == "date":
                entry = ValidatedEntry(
                    main, validation_type="date",
                    required=f.get("required", False),
                    width=30
                )
                entry.grid(row=i, column=1, sticky="ew", padx=5, pady=4)
                fields[f["name"]] = entry

                if item and item.get(f["name"]):
                    entry.set_value(item[f["name"]])

            # ------------------ NUMBER ------------------
            elif f["type"] == "number":
                entry = ValidatedEntry(
                    main, validation_type="number",
                    required=f.get("required", False),
                    width=30
                )
                entry.grid(row=i, column=1, sticky="ew", padx=5, pady=4)
                fields[f["name"]] = entry

                if item and item.get(f["name"]) is not None:
                    value = item[f["name"]]
                    # Redondear importe a 2 decimales si es numérico
                    if f["name"] == "importe":
                        try:
                            value = round(float(value), 2)
                        except (ValueError, TypeError):
                            pass
                    entry.set_value(str(value))

            # ------------------ TEXT ------------------
            else:
                entry = ValidatedEntry(
                    main, validation_type="text",
                    required=f.get("required", False),
                    width=30
                )
                entry.grid(row=i, column=1, sticky="ew", padx=5, pady=4)
                fields[f["name"]] = entry

                if item and item.get(f["name"]):
                    entry.set_value(item[f["name"]])

        main.columnconfigure(1, weight=1)

        # =====================================================================
        # BOTONES
        # =====================================================================
        btns = ttk.Frame(main)
        btns.grid(row=len(specs), column=0, columnspan=2, pady=15)

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
                            except ValueError:
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
    
    # =====================================================================
    # BOTONES DE EXPORTACIÓN
    # =====================================================================
    def _create_widgets(self):
        """Sobrescribe _create_widgets para ocultar botones CRUD y agregar botones de exportación"""
        # Crear toolbar sin los botones CRUD (Nuevo, Editar, Eliminar)
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, pady=5)
        
        # Solo mostrar botón Actualizar (sin Nuevo, Editar, Eliminar)
        ttk.Button(toolbar, text="Actualizar", command=self._load_data).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Agregar botones de exportación
        if not self.client_mode:
            ttk.Button(toolbar, text="Exportar PDF", command=self._export_pdf).pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="Exportar PNG", command=self._export_png).pack(side=tk.LEFT, padx=2)
        
        # Filtros (solo empleados/admin)
        if self.filters and not self.client_mode:
            from src.widgets.filter_panel import FilterPanel
            self.filter_panel = FilterPanel(self, self.filters, self._on_filter)
            self.filter_panel.pack(fill=tk.X, pady=5)
        
        # Tabla (sin doble click para editar)
        from src.widgets.data_table import DataTable
        self.table = DataTable(
            self,
            self.columns,
            on_select=self._on_select,
            on_double_click=None  # No permitir edición con doble click
        )
        self.table.pack(fill=tk.BOTH, expand=True, pady=5)
    
    def _add_export_buttons_delayed(self):
        """Método placeholder para compatibilidad"""
        pass
    
    def _export_pdf(self):
        """Exporta el pago seleccionado a PDF"""
        selected = self.table.get_selected()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un pago para exportar")
            return
        
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            initialfile=f"pago_{selected.get('id', 'N')}.pdf"
        )
        if path:
            try:
                exporter = PagoExporter(self.api, self.clientes, self.facturas)
                exporter.export_pdf(selected, path)
                messagebox.showinfo("Éxito", f"Pago exportado a PDF:\n{path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar PDF:\n{str(e)}")
    
    def _export_png(self):
        """Exporta el pago seleccionado a PNG"""
        selected = self.table.get_selected()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un pago para exportar")
            return
        
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png")],
            initialfile=f"pago_{selected.get('id', 'N')}.png"
        )
        if path:
            try:
                exporter = PagoExporter(self.api, self.clientes, self.facturas)
                exporter.export_png(selected, path)
                messagebox.showinfo("Éxito", f"Pago exportado a PNG:\n{path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar PNG:\n{str(e)}")
