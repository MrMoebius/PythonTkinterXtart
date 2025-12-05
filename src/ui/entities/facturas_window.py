"""
Ventana de gestión de facturas
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Optional
from datetime import datetime

from src.ui.entities.base_crud_window import BaseCRUDWindow
from src.widgets.validated_entry import ValidatedEntry
from src.ui.entities.facturas.facturas_export import FacturaExporter
from src.ui.entities.facturas.facturas_filters import filter_facturas_by_cliente, normalize_factura_data
from src.ui.entities.facturas.facturas_pagos import FacturaPagoHandler


class FacturasWindow(BaseCRUDWindow):
    """Ventana para gestionar facturas"""

    def __init__(self, parent, api, client_mode: bool = False):

        columns = [
            {"name": "id", "width": 60, "anchor": "center"},
            {"name": "cliente_nombre", "width": 200, "label": "Cliente"},
            {"name": "empleado_nombre", "width": 200, "label": "Empleado"},
            {"name": "fecha", "width": 120},
            {"name": "total", "width": 120, "anchor": "e"},
            {"name": "estado", "width": 120},
        ]

        filters = [
            {"name": "cliente_nombre", "type": "text", "label": "Nombre Cliente"},
        ]

        super().__init__(parent, api, "facturas", columns, filters, client_mode)

        self.clientes = []
        self.empleados = []
        
        # Inicializar handler de pagos
        self.pago_handler = FacturaPagoHandler(api, self)

        if client_mode:
            self._load_my_facturas()
        else:
            self._load_related()
            # Cargar datos iniciales
            self.after(100, self._load_data)
        
        # Agregar botones de exportación
        if not client_mode:
            self.after(150, self._add_export_buttons_delayed)
        
        # Botón para pagar factura (disponible para todos, incluyendo clientes)
        self.btn_pagar = None
        self.after(200, self._add_pagar_button)

    # =====================================================================
    # DATOS RELACIONADOS
    # =====================================================================
    def _load_my_facturas(self):
        # Cargar clientes y empleados para normalizar datos
        if not self.clientes or not self.empleados:
            self._load_related()
        
        res = self.api.get_my_facturas()
        if res.get("success"):
            data = res.get("data", [])
            
            # Normalizar datos usando el módulo de filtros
            if isinstance(data, list):
                data = [normalize_factura_data(row, self.clientes) for row in data]
                
                # Agregar nombre del empleado
                for row in data:
                    if isinstance(row, dict):
                        empleado_id = row.get("empleado_id")
                        if empleado_id:
                            empleado = next(
                                (e for e in self.empleados if e.get("id") == empleado_id or e.get("id_empleado") == empleado_id),
                                None
                            )
                            if empleado:
                                nombre = empleado.get("nombre", "")
                                apellidos = empleado.get("apellidos", "")
                                row["empleado_nombre"] = f"{nombre} {apellidos}".strip() or "N/A"
                            else:
                                row["empleado_nombre"] = f"ID {empleado_id}"
                        else:
                            row["empleado_nombre"] = "N/A"
                        
                        # Asegurar que fecha esté presente
                        if "fecha" not in row or not row.get("fecha"):
                            row["fecha"] = row.get("fecha_emision") or None
                        
                        # Redondear total a 2 decimales
                        if "total" in row and row.get("total") is not None:
                            try:
                                total_value = float(row["total"])
                                row["total"] = round(total_value, 2)
                            except (ValueError, TypeError):
                                pass
            
            self.data = data
            self.table.set_data(self.data)

    def _load_related(self):
        res_c = self.api.get_clientes()
        if res_c.get("success"):
            clientes_data = res_c.get("data", [])
            # Normalizar IDs
            for c in clientes_data:
                if isinstance(c, dict) and "id_cliente" in c and "id" not in c:
                    c["id"] = c["id_cliente"]
            self.clientes = clientes_data

        res_e = self.api.get_all("empleados")
        if res_e.get("success"):
            empleados_data = res_e.get("data", [])
            # Normalizar IDs
            for e in empleados_data:
                if isinstance(e, dict) and "id_empleado" in e and "id" not in e:
                    e["id"] = e["id_empleado"]
            self.empleados = empleados_data
    
    def _load_data(self):
        """Carga datos de facturas"""
        # En modo cliente, cargar solo las facturas del cliente
        if self.client_mode:
            self._load_my_facturas()
            return
        
        result = self.api.get_all("facturas")
        
        if not result.get("success"):
            messagebox.showerror("Error", f"Error al cargar datos: {result.get('error')}")
            return
        
        data = result.get("data", [])
        
        # Normalizar datos usando el módulo de filtros
        if isinstance(data, list):
            data = [normalize_factura_data(row, self.clientes) for row in data]
            
            # Agregar nombre del empleado (no está en normalize_factura_data)
            for row in data:
                if isinstance(row, dict):
                    empleado_id = row.get("empleado_id")
                    if empleado_id:
                        empleado = next(
                            (e for e in self.empleados if e.get("id") == empleado_id or e.get("id_empleado") == empleado_id),
                            None
                        )
                        if empleado:
                            nombre = empleado.get("nombre", "")
                            apellidos = empleado.get("apellidos", "")
                            row["empleado_nombre"] = f"{nombre} {apellidos}".strip() or "N/A"
                        else:
                            row["empleado_nombre"] = f"ID {empleado_id}"
                    else:
                        row["empleado_nombre"] = "N/A"
                    
                    # Asegurar que fecha esté presente
                    if "fecha" not in row or not row.get("fecha"):
                        row["fecha"] = None
                    
                    # Redondear total a 2 decimales
                    if "total" in row and row.get("total") is not None:
                        try:
                            total_value = float(row["total"])
                            row["total"] = round(total_value, 2)
                        except (ValueError, TypeError):
                            pass  # Mantener el valor original si no es numérico
                    
                    # Actualizar estado automáticamente: PENDIENTE -> EMITIDA cuando llega la fecha
                    estado_actual = row.get("estado", "").strip().upper()
                    fecha_str = row.get("fecha")
                    
                    if estado_actual == "PENDIENTE" and fecha_str:
                        try:
                            fecha_factura = datetime.strptime(fecha_str, "%Y-%m-%d").date()
                            hoy = datetime.now().date()
                            if fecha_factura <= hoy:
                                # Actualizar en el backend
                                factura_id = row.get("id") or row.get("id_factura")
                                if factura_id:
                                    update_data = {"estado": "EMITIDA"}
                                    self.api.update("facturas", factura_id, update_data)
                                    row["estado"] = "EMITIDA"
                        except (ValueError, TypeError):
                            pass  # Ignorar errores de formato de fecha
        
        self.data = data
        self.table.set_data(self.data)

    # =====================================================================
    # FILTRADO
    # =====================================================================
    def _on_filter(self, filter_values: Dict):
        """Filtra facturas en memoria por nombre de cliente."""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Filtros recibidos (facturas): {filter_values}")
        
        # Si no hay filtros, mostrar todos los datos
        if not filter_values or not any(v and str(v).strip() for v in filter_values.values()):
            logger.info("No hay filtros, mostrando todos los datos")
            self._load_data()
            return
        
        # Cargar todos los datos primero
        result = self.api.get_all("facturas")
        
        if not result.get("success"):
            logger.error(f"Error al cargar facturas: {result.get('error')}")
            return
        
        data = result.get("data", [])
        
        # Filtrar usando el módulo de filtros
        filtered_data = filter_facturas_by_cliente(data, self.clientes, filter_values)
        
        # Agregar nombre del empleado (no está en normalize_factura_data)
        for row in filtered_data:
            if isinstance(row, dict):
                empleado_id = row.get("empleado_id")
                if empleado_id:
                    empleado = next(
                        (e for e in self.empleados if e.get("id") == empleado_id or e.get("id_empleado") == empleado_id),
                        None
                    )
                    if empleado:
                        nombre = empleado.get("nombre", "")
                        apellidos = empleado.get("apellidos", "")
                        row["empleado_nombre"] = f"{nombre} {apellidos}".strip() or "N/A"
                    else:
                        row["empleado_nombre"] = f"ID {empleado_id}"
                else:
                    row["empleado_nombre"] = "N/A"
                
                # Asegurar que fecha esté presente
                if "fecha" not in row or not row.get("fecha"):
                    row["fecha"] = None
                
                # Redondear total a 2 decimales
                if "total" in row and row.get("total") is not None:
                    try:
                        total_value = float(row["total"])
                        row["total"] = round(total_value, 2)
                    except (ValueError, TypeError):
                        pass  # Mantener el valor original si no es numérico
        
        logger.info(f"Datos filtrados: {len(filtered_data)} de {len(data)}")
        
        self.data = filtered_data
        self.table.set_data(self.data)

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

        # El item ya viene del backend desde base_crud_window._on_edit()
        # Solo necesitamos normalizar los IDs si no están presentes
        if item:
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Formulario factura - Clientes disponibles: {len(self.clientes)}, Empleados disponibles: {len(self.empleados)}")
            logger.info(f"Item a editar - cliente_id: {item.get('cliente_id')}, empleado_id: {item.get('empleado_id')}")
            
            # Normalizar IDs si no están presentes
            if "cliente_id" not in item or not item.get("cliente_id"):
                # Intentar obtener desde objetos anidados
                cliente_obj = item.get("cliente_pagador") or item.get("cliente")
                if isinstance(cliente_obj, dict):
                    item["cliente_id"] = cliente_obj.get("id_cliente") or cliente_obj.get("id")
                elif "id_cliente" in item:
                    item["cliente_id"] = item["id_cliente"]
            
            if "empleado_id" not in item or not item.get("empleado_id"):
                # Intentar obtener desde objetos anidados
                empleado_obj = item.get("empleado") or item.get("empleado_responsable")
                if isinstance(empleado_obj, dict):
                    item["empleado_id"] = empleado_obj.get("id_empleado") or empleado_obj.get("id")
                elif "id_empleado" in item:
                    item["empleado_id"] = item["id_empleado"]
            
            # Normalizar otros campos
            if "id_factura" in item and "id" not in item:
                item["id"] = item["id_factura"]
            
            if "fecha_emision" in item and "fecha" not in item:
                item["fecha"] = item["fecha_emision"]
            
            # Normalizar estado a mayúsculas
            if "estado" in item and isinstance(item["estado"], str):
                item["estado"] = item["estado"].upper().strip()
            
            # Redondear total a 2 decimales
            if "total" in item and item.get("total") is not None:
                try:
                    total_value = float(item["total"])
                    item["total"] = round(total_value, 2)
                except (ValueError, TypeError):
                    pass
            
            logger.info(f"Item normalizado - cliente_id: {item.get('cliente_id')}, empleado_id: {item.get('empleado_id')}")

        # Asegurar que los datos relacionados estén cargados ANTES de construir el formulario
        if not self.clientes or not self.empleados:
            self._load_related()
        
        # Verificar que los datos relacionados estén disponibles
        if not self.clientes or not self.empleados:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("Clientes o empleados no cargados antes de mostrar formulario")
        
        # Debug: Log del item antes de construir el formulario
        import logging
        logger = logging.getLogger(__name__)
        if item:
            logger.info(f"Item a editar - cliente_id: {item.get('cliente_id')}, empleado_id: {item.get('empleado_id')}")
            logger.info(f"Item completo: {item}")
        else:
            logger.info("Item es None - creando nueva factura")
        
        form = tk.Toplevel(self)
        form.title("Nueva Factura" if item is None else "Editar Factura")
        form.geometry("620x340")
        form.transient(self.winfo_toplevel())
        form.grab_set()

        form.update_idletasks()
        x = (form.winfo_screenwidth() // 2) - 310
        y = (form.winfo_screenheight() // 2) - 180
        form.geometry(f"620x340+{x}+{y}")

        main = ttk.Frame(form, padding=15)
        main.pack(fill=tk.BOTH, expand=True)

        fields = {}
        specs = self._get_form_fields()
        
        # Debug: verificar datos disponibles
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Formulario factura - Clientes disponibles: {len(self.clientes)}, Empleados disponibles: {len(self.empleados)}")
        if item:
            logger.info(f"Item a editar - cliente_id: {item.get('cliente_id')}, empleado_id: {item.get('empleado_id')}")

        # =====================================================================
        # CREAR WIDGETS
        # =====================================================================
        for i, f in enumerate(specs):

            ttk.Label(main, text=f["label"] + ":").grid(
                row=i, column=0, sticky="w", padx=5, pady=4
            )

            # ---------------- SELECTS ----------------
            if f["type"] == "select":

                if f["name"] == "cliente_id":
                    opts = []
                    for c in self.clientes:
                        # Usar id normalizado (puede ser id o id_cliente)
                        cliente_id = c.get("id") or c.get("id_cliente")
                        nombre = c.get("nombre", "")
                        apellidos = c.get("apellidos", "")
                        razon_social = c.get("razon_social", "")
                        if razon_social:
                            display_name = razon_social
                        elif apellidos:
                            display_name = f"{nombre} {apellidos}".strip()
                        else:
                            display_name = nombre or "N/A"
                        opts.append(f"{cliente_id} - {display_name}")

                elif f["name"] == "empleado_id":
                    opts = []
                    for e in self.empleados:
                        # Usar id normalizado (puede ser id o id_empleado)
                        empleado_id = e.get("id") or e.get("id_empleado")
                        nombre = e.get("nombre", "")
                        apellidos = e.get("apellidos", "")
                        display_name = f"{nombre} {apellidos}".strip() or "N/A"
                        opts.append(f"{empleado_id} - {display_name}")

                elif f["name"] == "estado":
                    # Estados permitidos en backend: PENDIENTE, EMITIDA, PAGADA, VENCIDA
                    opts = ["PENDIENTE", "EMITIDA", "PAGADA", "VENCIDA"]

                else:
                    opts = []

                combo = ttk.Combobox(main, values=opts, width=30, state="readonly")
                combo.grid(row=i, column=1, padx=5, pady=4, sticky="ew")
                fields[f["name"]] = combo

                # Precargar datos
                if item and item.get(f["name"]) is not None:
                    saved_value = item.get(f["name"])
                    
                    # Para cliente_id y empleado_id, buscar por ID
                    if f["name"] in ("cliente_id", "empleado_id"):
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.info(f"Precargando {f['name']}: saved_value={saved_value}, opts count={len(opts)}")
                        
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
                                    logger.info(f"Encontrado match: {op}")
                                    break
                            except (ValueError, TypeError):
                                if op_id_str == str(saved_value):
                                    combo.set(op)
                                    found = True
                                    logger.info(f"Encontrado match (string): {op}")
                                    break
                        
                        if not found:
                            logger.warning(f"No se encontró match para {f['name']}={saved_value} en {len(opts)} opciones")
                            if saved_id_int is not None:
                                # Si no se encuentra, intentar con el ID directamente
                                combo.set(str(saved_id_int))
                    else:
                        # Para estado, buscar por valor (case-insensitive)
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
                elif f["name"] == "empleado_id" and item is None:
                    # Auto-asignar empleado logueado al crear nueva factura
                    empleado_id = getattr(self.api, "user_id", None)
                    if empleado_id:
                        try:
                            empleado_id_int = int(empleado_id)
                        except (ValueError, TypeError):
                            empleado_id_int = None
                        
                        for op in opts:
                            op_id_str = op.split(" - ")[0]
                            try:
                                op_id_int = int(op_id_str)
                                if op_id_int == empleado_id_int:
                                    combo.set(op)
                                    break
                            except (ValueError, TypeError):
                                if op_id_str == str(empleado_id):
                                    combo.set(op)
                                    break

            # ---------------- DATE ----------------
            elif f["type"] == "date":
                entry = ValidatedEntry(
                    main, validation_type="date",
                    required=f.get("required", False),
                    width=30
                )
                entry.grid(row=i, column=1, padx=5, pady=4, sticky="ew")
                fields[f["name"]] = entry

                if item and item.get(f["name"]):
                    entry.set_value(item[f["name"]])

            # ---------------- NUMBER ----------------
            elif f["type"] == "number":
                entry = ValidatedEntry(
                    main, validation_type="number",
                    required=f.get("required", False),
                    width=30
                )
                entry.grid(row=i, column=1, padx=5, pady=4, sticky="ew")
                fields[f["name"]] = entry

                if item and item.get(f["name"]) is not None:
                    value = item[f["name"]]
                    # Redondear total a 2 decimales si es numérico
                    if f["name"] == "total":
                        try:
                            value = round(float(value), 2)
                        except (ValueError, TypeError):
                            pass
                    entry.set_value(str(value))

            # ---------------- TEXT GENÉRICO ----------------
            else:
                entry = ValidatedEntry(
                    main, validation_type="text",
                    required=f.get("required", False),
                    width=30
                )
                entry.grid(row=i, column=1, padx=5, pady=4, sticky="ew")
                fields[f["name"]] = entry

                if item and item.get(f["name"]):
                    entry.set_value(item[f["name"]])

        main.columnconfigure(1, weight=1)

        # =====================================================================
        # BOTONES
        # =====================================================================
        buttons = ttk.Frame(main)
        buttons.grid(row=len(specs), column=0, columnspan=2, pady=15)

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
                            except ValueError:
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
    
    # =====================================================================
    # BOTONES DE EXPORTACIÓN
    # =====================================================================
    def _create_widgets(self):
        """Sobrescribe _create_widgets para agregar botones de exportación"""
        super()._create_widgets()
        
        # Agregar botones de exportación al toolbar
        for widget in self.winfo_children():
            if isinstance(widget, ttk.Frame):
                has_buttons = False
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button):
                        has_buttons = True
                        break
                if has_buttons:
                    ttk.Separator(widget, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
                    ttk.Button(widget, text="Exportar PDF", command=self._export_pdf).pack(side=tk.LEFT, padx=2)
                    ttk.Button(widget, text="Exportar PNG", command=self._export_png).pack(side=tk.LEFT, padx=2)
                    break
    
    def _add_export_buttons_delayed(self):
        """Método placeholder para compatibilidad"""
        pass
    
    def _add_pagar_button(self):
        """Agrega el botón 'Pagar' al toolbar"""
        # Buscar el toolbar en los widgets hijos
        for widget in self.winfo_children():
            if isinstance(widget, ttk.Frame):
                # Verificar si tiene botones (es el toolbar)
                has_buttons = False
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button):
                        has_buttons = True
                        break
                if has_buttons:
                    # Verificar si ya tiene el botón de pagar
                    has_pagar_btn = False
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.Button) and child.cget("text") == "Pagar":
                            has_pagar_btn = True
                            self.btn_pagar = child
                            break
                    if not has_pagar_btn:
                        ttk.Separator(widget, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
                        self.btn_pagar = ttk.Button(
                            widget, 
                            text="Pagar", 
                            command=self._pagar_factura
                        )
                        self.btn_pagar.pack(side=tk.LEFT, padx=2)
                    break
    
    def _export_pdf(self):
        """Exporta la factura seleccionada a PDF"""
        selected = self.table.get_selected()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una factura para exportar")
            return
        
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            initialfile=f"factura_{selected.get('id', 'N')}.pdf"
        )
        if path:
            try:
                exporter = FacturaExporter(self.api, self.clientes, self.empleados)
                exporter.export_pdf(selected, path)
                messagebox.showinfo("Éxito", f"Factura exportada a PDF:\n{path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar PDF:\n{str(e)}")
    
    def _export_png(self):
        """Exporta la factura seleccionada a PNG"""
        selected = self.table.get_selected()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una factura para exportar")
            return
        
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png")],
            initialfile=f"factura_{selected.get('id', 'N')}.png"
        )
        if path:
            try:
                exporter = FacturaExporter(self.api, self.clientes, self.empleados)
                exporter.export_png(selected, path)
                messagebox.showinfo("Éxito", f"Factura exportada a PNG:\n{path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar PNG:\n{str(e)}")

    # =====================================================================
    # PAGAR FACTURA
    # =====================================================================
    def _pagar_factura(self):
        """Abre ventana modal para pagar la factura seleccionada"""
        selected = self.table.get_selected()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una factura para pagar")
            return
        
        # Obtener datos completos de la factura
        factura_id = selected.get("id_factura") or selected.get("id")
        if not factura_id:
            messagebox.showerror("Error", "No se pudo obtener el ID de la factura")
            return
        
        # Obtener factura completa del backend
        result = self.api.get_by_id("facturas", factura_id)
        if not result.get("success"):
            messagebox.showerror("Error", f"Error al obtener factura: {result.get('error', 'Error desconocido')}")
            return
        
        factura = result.get("data", {})
        if not isinstance(factura, dict):
            messagebox.showerror("Error", "Datos de la factura inválidos")
            return
        
        # Obtener datos del cliente
        cliente_id = factura.get("id_cliente") or factura.get("cliente_id")
        cliente_nombre = selected.get("cliente_nombre", "N/A")
        total = float(factura.get("total", 0))
        estado = factura.get("estado", "").upper()
        num_factura = factura.get("num_factura", factura_id)
        fecha = factura.get("fecha") or factura.get("fecha_emision", "N/A")
        
        # Abrir ventana modal usando el módulo de pagos
        self.pago_handler.abrir_ventana_pago(
            factura_id, cliente_id, cliente_nombre, num_factura, total, fecha, estado,
            on_success_callback=self._load_data
        )
