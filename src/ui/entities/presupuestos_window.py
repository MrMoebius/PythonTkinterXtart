"""
Ventana de gestión de presupuestos
"""

import tkinter as tk
import os
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Optional
from datetime import datetime

from src.ui.entities.base_crud_window import BaseCRUDWindow
from src.widgets.validated_entry import ValidatedEntry
from src.ui.entities.presupuestos.presupuestos_export import PresupuestoExporter
from src.ui.entities.presupuestos.presupuestos_filters import filter_presupuestos_by_cliente, normalize_presupuesto_data
from src.ui.entities.presupuestos.presupuestos_facturacion import PresupuestoFacturacion
from src.ui.entities.cliente_form import abrir_formulario_cliente


class PresupuestosWindow(BaseCRUDWindow):
    """Gestión de presupuestos."""

    def __init__(self, parent, api, client_mode: bool = False):
        # Columnas según documentación del backend
        # El backend devuelve: id_Presupuesto, presupuesto, estado, fecha_apertura, fecha_cierre
        # Las relaciones (empleado, clientes, producto) NO aparecen por @JsonIgnore
        # Necesitamos cargar datos de clientes para mostrar el nombre
        columns = [
            {"name": "id", "width": 80, "anchor": "center"},
            {"name": "cliente_nombre", "width": 200, "label": "Cliente Pagador"},
            {"name": "presupuesto", "width": 120, "anchor": "e"},
            {"name": "estado", "width": 120},
            {"name": "fecha_apertura", "width": 120},
            {"name": "fecha_cierre", "width": 120},
        ]

        # El backend NO soporta filtros, pero dejamos los filtros para filtrado local
        # Solo filtro por nombre de cliente
        filters = [
            {"name": "nombre", "type": "text", "label": "Nombre Cliente"},
        ]

        super().__init__(parent, api, "presupuestos", columns, filters, client_mode=client_mode)

        # Instancia del módulo de facturación
        self.facturacion = PresupuestoFacturacion(api, self)

        # Relaciones
        self.clientes = []
        self.clientes_persona = []  # Solo personas para beneficiario
        self.clientes_empresa_persona = []  # Empresas y personas para pagador
        self.empleados = []
        self.productos = []
        
        if client_mode:
            # En modo cliente, cargar solo los presupuestos del cliente
            self.after(100, self._load_my_presupuestos)
        else:
            self._load_related()
            # Cargar datos iniciales después de que se hayan creado los widgets
            self.after(100, self._load_data)
        
        # Agregar botones de exportación después de crear widgets
        self.after(150, self._add_export_buttons_delayed)
        
        # Botón para generar factura (solo para empleados/admin, NO para clientes)
        self.btn_generar_factura = None
        if not client_mode:
            self.after(200, self._add_generar_factura_button)
    
    def _create_widgets(self):
        """Sobrescribe _create_widgets para agregar botones de exportación"""
        # Llamar al método de la clase base
        super()._create_widgets()
        
        # Agregar botones de exportación al toolbar
        # El toolbar es el primer Frame hijo
        for widget in self.winfo_children():
            if isinstance(widget, ttk.Frame):
                # Verificar si tiene botones (es el toolbar)
                has_buttons = False
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button):
                        has_buttons = True
                        break
                if has_buttons:
                    # Agregar botones de exportación
                    ttk.Separator(widget, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
                    ttk.Button(widget, text="Exportar PDF", command=self._export_pdf).pack(side=tk.LEFT, padx=2)
                    ttk.Button(widget, text="Exportar PNG", command=self._export_png).pack(side=tk.LEFT, padx=2)
                    break

    # =====================================================================
    # DATOS RELACIONADOS
    # =====================================================================
    def _load_related(self):
        """Carga clientes, empleados y productos."""
        # Cargar clientes
        res_c = self.api.get_clientes()
        if res_c.get("success"):
            clientes_data = res_c.get("data", [])
            # Normalizar IDs de clientes para el combobox
            for c in clientes_data:
                if isinstance(c, dict):
                    if "id_cliente" in c and "id" not in c:
                        c["id"] = c["id_cliente"]
            self.clientes = clientes_data
            # Filtrar por tipo
            self.clientes_persona = [c for c in clientes_data if c.get("tipo_cliente", "").upper() == "PARTICULAR"]
            self.clientes_empresa_persona = clientes_data  # Todos para pagador

        # Cargar empleados
        res_e = self.api.get_all("empleados")
        if res_e.get("success"):
            empleados_data = res_e.get("data", [])
            # Normalizar IDs de empleados para el combobox
            for e in empleados_data:
                if isinstance(e, dict):
                    if "id_empleado" in e and "id" not in e:
                        e["id"] = e["id_empleado"]
            self.empleados = empleados_data
        
        # Cargar productos
        res_p = self.api.get_all("productos")
        if res_p.get("success"):
            productos_data = res_p.get("data", [])
            # Normalizar IDs de productos para el combobox
            for p in productos_data:
                if isinstance(p, dict):
                    if "id_producto" in p and "id" not in p:
                        p["id"] = p["id_producto"]
            self.productos = productos_data

    # =====================================================================
    # CARGA DE DATOS CON NOMBRES DE CLIENTES
    # =====================================================================
    def _load_my_presupuestos(self):
        """Carga presupuestos del cliente actual"""
        # Cargar clientes primero para normalizar
        res_c = self.api.get_clientes()
        if res_c.get("success"):
            clientes_data = res_c.get("data", [])
            for c in clientes_data:
                if isinstance(c, dict) and "id_cliente" in c and "id" not in c:
                    c["id"] = c["id_cliente"]
            self.clientes = clientes_data
        
        # Cargar todos los presupuestos y filtrar por cliente
        result = self.api.get_all("presupuestos")
        
        if not result.get("success"):
            messagebox.showerror("Error", f"Error al cargar datos: {result.get('error')}")
            return
        
        data = result.get("data", [])
        
        # Filtrar presupuestos del cliente actual
        cliente_id = getattr(self.api, "user_id", None)
        if cliente_id and isinstance(data, list):
            data = [
                p for p in data
                if isinstance(p, dict) and (
                    p.get("id_cliente_pagador") == cliente_id or
                    p.get("id_cliente_beneficiario") == cliente_id
                )
            ]
        
        if isinstance(data, list):
            data = [normalize_presupuesto_data(row, self.clientes) for row in data]
        
        self.data = data
        self.table.set_data(self.data)
    
    def _load_data(self):
        """Carga datos y agrega nombres de clientes"""
        # En modo cliente, cargar solo los presupuestos del cliente
        if self.client_mode:
            self._load_my_presupuestos()
            return
        
        result = self.api.get_all("presupuestos")
        
        if not result.get("success"):
            messagebox.showerror("Error", f"Error al cargar datos: {result.get('error')}")
            return
        
        data = result.get("data", [])
        
        if isinstance(data, list):
            data = [normalize_presupuesto_data(row, self.clientes) for row in data]
        
        self.data = data
        self.table.set_data(self.data)
        
        # Actualizar estado del botón después de cargar datos
        selected = self.table.get_selected()
        if self.btn_generar_factura:
            if selected and isinstance(selected, dict) and selected.get("estado", "").upper() == "APROBADO":
                self.btn_generar_factura.config(state="normal")
            else:
                self.btn_generar_factura.config(state="disabled")

    # =====================================================================
    # FILTRADO (local, el backend NO soporta filtros)
    # =====================================================================
    def _on_filter(self, filter_values: Dict):
        """Filtra presupuestos en memoria usando nombre/teléfono/email de cliente."""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Filtros recibidos (presupuestos): {filter_values}")
        
        # Si no hay filtros, mostrar todos los datos
        if not filter_values or not any(v and str(v).strip() for v in filter_values.values()):
            logger.info("No hay filtros, mostrando todos los datos")
            self._load_data()
            return
        
        # Cargar todos los datos primero (el backend no soporta filtros)
        result = self.api.get_all("presupuestos")
        
        if not result.get("success"):
            logger.error(f"Error al cargar presupuestos: {result.get('error')}")
            return
        
        data = result.get("data", [])
        
        filtered_data = filter_presupuestos_by_cliente(
            data,
            self.clientes,
            filter_values,
            self.api
        )
        
        logger.info(f"Datos filtrados: {len(filtered_data)} de {len(data)}")
        
        self.data = filtered_data
        self.table.set_data(self.data)
        
        # Actualizar estado del botón después de filtrar
        selected = self.table.get_selected()
        if self.btn_generar_factura:
            if selected and isinstance(selected, dict) and selected.get("estado", "").upper() == "APROBADO":
                self.btn_generar_factura.config(state="normal")
            else:
                self.btn_generar_factura.config(state="disabled")

    # =====================================================================
    # BOTONES DE EXPORTACIÓN
    # =====================================================================
    def _add_export_buttons_delayed(self):
        """Agrega botones de exportación después de que se haya creado el toolbar"""
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
                    # Verificar si ya tiene los botones de exportación
                    has_export = False
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.Button) and child.cget("text") in ["Exportar PDF", "Exportar PNG"]:
                            has_export = True
                            break
                    if not has_export:
                        ttk.Separator(widget, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
                        ttk.Button(widget, text="Exportar PDF", command=self._export_pdf).pack(side=tk.LEFT, padx=2)
                        ttk.Button(widget, text="Exportar PNG", command=self._export_png).pack(side=tk.LEFT, padx=2)
                    break
    
    def _add_generar_factura_button(self):
        """Agrega el botón 'Generar Factura' al toolbar"""
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
                    # Verificar si ya tiene el botón de generar factura
                    has_factura_btn = False
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.Button) and child.cget("text") == "Generar Factura":
                            has_factura_btn = True
                            self.btn_generar_factura = child
                            break
                    if not has_factura_btn:
                        ttk.Separator(widget, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
                        self.btn_generar_factura = ttk.Button(
                            widget, 
                            text="Generar Factura", 
                            command=self._generar_factura,
                            state="disabled"
                        )
                        self.btn_generar_factura.pack(side=tk.LEFT, padx=2)
                    break
    
    def _export_pdf(self):
        """Exporta el presupuesto seleccionado a PDF"""
        selected = self.table.get_selected()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un presupuesto para exportar")
            return
        
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            initialfile=f"presupuesto_{selected.get('id', 'N')}.pdf"
        )
        if path:
            try:
                exporter = PresupuestoExporter(self.api, self.clientes, self.empleados, self.productos)
                exporter.export_pdf(selected, path)
                messagebox.showinfo("Éxito", f"Presupuesto exportado a PDF:\n{path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar PDF:\n{str(e)}")
    
    def _export_png(self):
        """Exporta el presupuesto seleccionado a PNG"""
        selected = self.table.get_selected()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un presupuesto para exportar")
            return
        
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png")],
            initialfile=f"presupuesto_{selected.get('id', 'N')}.png"
        )
        if path:
            try:
                exporter = PresupuestoExporter(self.api, self.clientes, self.empleados, self.productos)
                exporter.export_png(selected, path)
                messagebox.showinfo("Éxito", f"Presupuesto exportado a PNG:\n{path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar PNG:\n{str(e)}")

    # =====================================================================
    # GENERAR FACTURA DESDE PRESUPUESTO
    # =====================================================================
    def _generar_factura(self):
        """Abre ventana modal para generar factura(s) desde presupuesto aprobado"""
        selected = self.table.get_selected()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un presupuesto para generar la factura")
            return
        
        # Verificar que el estado sea APROBADO
        estado = selected.get("estado", "").upper()
        if estado != "APROBADO":
            messagebox.showwarning(
                "Advertencia", 
                f"Solo se pueden generar facturas de presupuestos con estado 'APROBADO'.\n"
                f"El presupuesto seleccionado tiene estado: '{selected.get('estado', 'N/A')}'"
            )
            return
        
        # Obtener datos completos del presupuesto
        presupuesto_id = selected.get("id_Presupuesto") or selected.get("id")
        if not presupuesto_id:
            messagebox.showerror("Error", "No se pudo obtener el ID del presupuesto")
            return
        
        # Obtener presupuesto completo del backend
        result = self.api.get_by_id("presupuestos", presupuesto_id)
        if not result.get("success"):
            messagebox.showerror("Error", f"Error al obtener presupuesto: {result.get('error', 'Error desconocido')}")
            return
        
        presupuesto = result.get("data", {})
        if not isinstance(presupuesto, dict):
            messagebox.showerror("Error", "Datos del presupuesto inválidos")
            return
        
        # Validar datos requeridos
        cliente_pagador_id = presupuesto.get("id_cliente_pagador")
        empleado_id = presupuesto.get("id_empleado")
        total = float(presupuesto.get("presupuesto", 0))
        
        if not cliente_pagador_id:
            messagebox.showerror("Error", "El presupuesto no tiene un cliente pagador asignado")
            return
        
        if not empleado_id:
            messagebox.showerror("Error", "El presupuesto no tiene un empleado asignado")
            return
        
        # Obtener nombre del cliente
        cliente_nombre = selected.get("cliente_nombre", "N/A")
        
        # Obtener productos del presupuesto
        productos_info = []
        presupuesto_productos = presupuesto.get("presupuestoProductos") or presupuesto.get("presupuesto_productos") or []
        
        if presupuesto_productos:
            for pp in presupuesto_productos:
                if not isinstance(pp, dict):
                    continue
                producto_id = pp.get("id_producto")
                cantidad = pp.get("cantidad", 1)
                subtotal = pp.get("subtotal", 0)
                
                producto = next(
                    (p for p in self.productos if (p.get("id") == producto_id or p.get("id_producto") == producto_id)),
                    None
                )
                if producto:
                    productos_info.append({
                        "nombre": f"{producto.get('nombre', 'N/A')} x{cantidad}",
                        "precio": subtotal
                    })
        else:
            # Fallback: formato antiguo con id_producto único
            producto_id = presupuesto.get("id_producto")
            if producto_id:
                producto = next(
                    (p for p in self.productos if (p.get("id") == producto_id or p.get("id_producto") == producto_id)),
                    None
                )
                if producto:
                    productos_info.append({
                        "nombre": producto.get("nombre", "N/A"),
                        "precio": float(producto.get("precio", 0))
                    })
        
        # Si no hay productos, mostrar información genérica
        if not productos_info:
            productos_info.append({
                "nombre": "Productos del presupuesto",
                "precio": total
            })
        
        # Abrir ventana modal para seleccionar plazos usando el módulo de facturación
        self.facturacion.abrir_ventana_generar_factura(
            presupuesto,
            cliente_nombre,
            productos_info,
            total,
            cliente_pagador_id,
            empleado_id,
            on_success_callback=self._load_data
        )

    # =====================================================================
    # FORMULARIO
    # =====================================================================
    def _on_select(self, item):
        """Actualiza el estado del botón 'Generar Factura' según el estado del presupuesto seleccionado"""
        if self.btn_generar_factura:
            if item and isinstance(item, dict) and item.get("estado", "").upper() == "APROBADO":
                self.btn_generar_factura.config(state="normal")
            else:
                self.btn_generar_factura.config(state="disabled")
    
    def _show_form(self, item: Optional[Dict]):
        # Asegurar que los datos relacionados estén cargados
        if not self.productos or not self.clientes or not self.empleados:
            self._load_related()
        
        # Si se está editando, cargar datos completos del presupuesto
        if item:
            presupuesto_id = item.get("id_Presupuesto") or item.get("id")
            if presupuesto_id:
                # Obtener presupuesto completo del backend
                result = self.api.get_by_id("presupuestos", presupuesto_id)
                if result.get("success"):
                    presup_data = result.get("data", {})
                    if isinstance(presup_data, dict):
                        # Actualizar item con datos completos (incluye IDs de clientes y productos)
                        item.update(presup_data)
                        # Normalizar ID
                        if "id_Presupuesto" in item and "id" not in item:
                            item["id"] = item["id_Presupuesto"]
        
        form = tk.Toplevel(self)
        form.title("Nuevo Presupuesto" if item is None else "Editar Presupuesto")
        # Altura suficiente para mostrar todos los campos y botones
        form.geometry("750x650")
        form.transient(self.winfo_toplevel())
        form.grab_set()

        form.update_idletasks()
        x = (form.winfo_screenwidth() // 2) - 375
        y = (form.winfo_screenheight() // 2) - 325
        form.geometry(f"750x650+{x}+{y}")

        # Frame principal sin scroll
        main_frame = ttk.Frame(form, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        main = main_frame
        
        # Configurar columnas para que se expandan
        main.columnconfigure(0, weight=0)
        main.columnconfigure(1, weight=1)
        fields = {}
        productos_seleccionados = []  # Lista de productos: [{"id_producto": X, "precio": Y}, ...]
        
        row = 0

        # =====================================================================
        # EMPLEADO (auto-asignado, solo mostrar si es nuevo)
        # =====================================================================
        if item is None:
            # Auto-asignar empleado logueado
            empleado_id = getattr(self.api, "user_id", None)
            if empleado_id:
                empleado_nombre = next(
                    (e.get("nombre", "") for e in self.empleados if e.get("id") == empleado_id),
                    f"ID {empleado_id}"
                )
                ttk.Label(main, text="Empleado:").grid(row=row, column=0, sticky="w", padx=5, pady=4)
                ttk.Label(main, text=f"{empleado_id} - {empleado_nombre} (Asignado automáticamente)", 
                         foreground="gray").grid(row=row, column=1, sticky="w", padx=5, pady=4)
                fields["id_empleado"] = empleado_id
                row += 1

        # =====================================================================
        # CLIENTE PAGADOR (empresa o persona + opción Nuevo cliente)
        # =====================================================================
        ttk.Label(main, text="Cliente Pagador:").grid(row=row, column=0, sticky="w", padx=5, pady=4)
        opts_pagador = [
            f"{c.get('id', c.get('id_cliente', ''))} - {c.get('nombre', '')} ({c.get('tipo_cliente', 'N/A')})"
            for c in self.clientes_empresa_persona
        ]
        # Insertar opción para crear un nuevo cliente pagador
        opts_pagador.insert(0, "Nuevo cliente...")
        combo_pagador = ttk.Combobox(main, values=opts_pagador, width=40, state="readonly")
        combo_pagador.grid(row=row, column=1, sticky="ew", padx=5, pady=4)
        fields["id_cliente_pagador"] = combo_pagador
        
        # Evento para detectar selección de "Nuevo cliente..."
        def on_pagador_change(event):
            valor = combo_pagador.get()
            if valor == "Nuevo cliente...":
                crear_nuevo_cliente_pagador()
        
        combo_pagador.bind("<<ComboboxSelected>>", on_pagador_change)
        
        # Precargar si edita
        if item and item.get("id_cliente_pagador"):
            try_id = str(item["id_cliente_pagador"])
            for op in opts_pagador:
                if op != "Nuevo cliente..." and op.split(" - ")[0] == try_id:
                    combo_pagador.set(op)
                    break
        row += 1

        # =====================================================================
        # CLIENTE BENEFICIARIO (solo persona + opción Nuevo cliente)
        # =====================================================================
        ttk.Label(main, text="Cliente Beneficiario:").grid(row=row, column=0, sticky="w", padx=5, pady=4)
        opts_beneficiario = [
            f"{c.get('id', c.get('id_cliente', ''))} - {c.get('nombre', '')}"
            for c in self.clientes_persona
        ]
        opts_beneficiario.insert(0, "Nuevo cliente...")
        combo_beneficiario = ttk.Combobox(main, values=opts_beneficiario, width=40, state="readonly")
        combo_beneficiario.grid(row=row, column=1, sticky="ew", padx=5, pady=4)
        fields["id_cliente_beneficiario"] = combo_beneficiario
        
        # Evento para detectar selección de "Nuevo cliente..."
        def on_beneficiario_change(event):
            valor = combo_beneficiario.get()
            if valor == "Nuevo cliente...":
                # Abrir ventana para crear nuevo cliente beneficiario
                crear_nuevo_cliente_beneficiario()
        
        combo_beneficiario.bind("<<ComboboxSelected>>", on_beneficiario_change)
        
        # Función para crear nuevo cliente pagador (persona o empresa)
        def crear_nuevo_cliente_pagador():
            def on_success(cliente_guardado):
                """Callback cuando el cliente se crea exitosamente."""
                cliente_id = cliente_guardado.get("id_cliente") or cliente_guardado.get("id")
                nombre = cliente_guardado.get("nombre", "")
                tipo_cliente = cliente_guardado.get("tipo_cliente", "N/A")
                
                if cliente_id:
                    # Recargar lista completa desde el backend
                    self._load_related()
                    # Reconstruir opciones de pagador
                    nuevos_opts_pagador = [
                        f"{c.get('id', c.get('id_cliente', ''))} - {c.get('nombre', '')} ({c.get('tipo_cliente', 'N/A')})"
                        for c in self.clientes_empresa_persona
                    ]
                    nuevos_opts_pagador.insert(0, "Nuevo cliente...")
                    combo_pagador["values"] = nuevos_opts_pagador
                    nuevo_texto = f"{cliente_id} - {nombre} ({tipo_cliente})"
                    combo_pagador.set(nuevo_texto)
            
            abrir_formulario_cliente(
                parent=form,
                api=self.api,
                titulo="Nuevo Cliente Pagador",
                tipo_cliente_fijo=None,  # Permite elegir entre persona/empresa
                on_success=on_success
            )
        
        # Función para crear nuevo cliente beneficiario (solo persona)
        def crear_nuevo_cliente_beneficiario():
            def on_success(cliente_guardado):
                """Callback cuando el cliente se crea exitosamente."""
                cliente_id = cliente_guardado.get("id_cliente") or cliente_guardado.get("id")
                nombre = cliente_guardado.get("nombre", "")
                
                if cliente_id:
                    # Actualizar combobox y seleccionar
                    nuevo_texto = f"{cliente_id} - {nombre}"
                    # Actualizar la lista de opciones
                    current_values = list(combo_beneficiario["values"])
                    if "Nuevo cliente..." in current_values:
                        current_values.remove("Nuevo cliente...")
                    current_values.append(nuevo_texto)
                    combo_beneficiario["values"] = current_values
                    combo_beneficiario.set(nuevo_texto)
                    # Recargar lista de clientes
                    self._load_related()
            
            abrir_formulario_cliente(
                parent=form,
                api=self.api,
                titulo="Nuevo Cliente Beneficiario",
                tipo_cliente_fijo="PARTICULAR",  # Solo permite crear PARTICULAR
                on_success=on_success
            )
        
        # Precargar si edita
        if item and item.get("id_cliente_beneficiario"):
            try_id = str(item["id_cliente_beneficiario"])
            for op in opts_beneficiario:
                if op != "Nuevo cliente..." and op.split(" - ")[0] == try_id:
                    combo_beneficiario.set(op)
                    break
        row += 1

        # =====================================================================
        # PRODUCTOS (múltiples)
        # =====================================================================
        ttk.Label(main, text="Productos:").grid(row=row, column=0, sticky="nw", padx=5, pady=5)
        
        # Frame para lista de productos
        productos_frame = ttk.Frame(main)
        productos_frame.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        
        # Lista de productos seleccionados
        productos_listbox = tk.Listbox(productos_frame, height=4, width=35)
        productos_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar_productos = ttk.Scrollbar(productos_frame, orient="vertical", command=productos_listbox.yview)
        productos_listbox.configure(yscrollcommand=scrollbar_productos.set)
        scrollbar_productos.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Variable para almacenar función actualizar_total (se definirá después)
        actualizar_total_fn = None
        
        # Botón para agregar producto
        def agregar_producto():
            # Ventana para seleccionar producto
            producto_window = tk.Toplevel(form)
            producto_window.title("Agregar Producto")
            # Aumentar altura vertical para que el botón sea visible
            producto_window.geometry("500x280")
            producto_window.transient(form)
            producto_window.grab_set()
            
            # Centrar ventana
            producto_window.update_idletasks()
            x = (producto_window.winfo_screenwidth() // 2) - 250
            y = (producto_window.winfo_screenheight() // 2) - 140
            producto_window.geometry(f"500x280+{x}+{y}")
            
            # Frame principal con padding
            main_producto = ttk.Frame(producto_window, padding=15)
            main_producto.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(main_producto, text="Seleccionar Producto:").pack(pady=5)
            
            opts_producto = [
                f"{p.get('id', p.get('id_producto', ''))} - {p.get('nombre', '')} (€{p.get('precio', 0)})"
                for p in self.productos
            ]
            
            combo_producto = ttk.Combobox(main_producto, values=opts_producto, width=30, state="readonly")
            combo_producto.pack(pady=5)
            
            ttk.Label(main_producto, text="Cantidad:").pack(pady=5)
            entry_cantidad = ValidatedEntry(main_producto, validation_type="number", required=True, width=10)
            entry_cantidad.set_value("1")
            entry_cantidad.pack(pady=5)
            
            def confirmar_producto():
                valor = combo_producto.get()
                if not valor:
                    messagebox.showwarning("Advertencia", "Seleccione un producto")
                    return
                
                if not entry_cantidad.validate_input():
                    messagebox.showerror("Error", "La cantidad debe ser un número válido")
                    return
                
                try:
                    producto_id = int(valor.split(" - ")[0])
                    cantidad = int(entry_cantidad.get_value() or "1")
                    if cantidad <= 0:
                        messagebox.showerror("Error", "La cantidad debe ser mayor que 0")
                        return
                    
                    # Buscar producto para obtener precio
                    producto = next((p for p in self.productos if p.get("id") == producto_id), None)
                    if producto:
                        precio_unitario = float(producto.get("precio", 0))
                        subtotal = precio_unitario * cantidad
                        productos_seleccionados.append({
                            "id_producto": producto_id,
                            "cantidad": cantidad,
                            "precio_unitario": precio_unitario,
                            "subtotal": subtotal
                        })
                        # Actualizar lista
                        productos_listbox.insert(tk.END, f"{producto.get('nombre', '')} x{cantidad} - €{subtotal:.2f}")
                        # Recalcular total (si la función ya está definida)
                        if actualizar_total_fn:
                            actualizar_total_fn()
                except (ValueError, IndexError) as e:
                    messagebox.showerror("Error", f"Error al procesar el producto: {str(e)}")
                
                producto_window.destroy()
            
            # Frame para botones al final
            btns_producto = ttk.Frame(main_producto)
            btns_producto.pack(side=tk.BOTTOM, pady=(15, 0))
            
            ttk.Button(btns_producto, text="Agregar", command=confirmar_producto).pack(side=tk.LEFT, padx=5)
            ttk.Button(btns_producto, text="Cancelar", command=producto_window.destroy).pack(side=tk.LEFT, padx=5)
        
        # Frame para botones de productos
        productos_btns_frame = ttk.Frame(main)
        productos_btns_frame.grid(row=row+1, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Button(productos_btns_frame, text="+ Agregar Producto", command=agregar_producto).pack(side=tk.LEFT, padx=5)
        
        # Botón para eliminar producto seleccionado
        def eliminar_producto():
            seleccionado = productos_listbox.curselection()
            if not seleccionado:
                messagebox.showwarning("Advertencia", "Seleccione un producto para eliminar")
                return
            
            # Obtener índice del producto seleccionado
            indice = seleccionado[0]
            
            # Eliminar de la lista y del listbox
            productos_seleccionados.pop(indice)
            productos_listbox.delete(indice)
            
            # Recalcular total
            if actualizar_total_fn:
                actualizar_total_fn()
        
        ttk.Button(productos_btns_frame, text="- Eliminar Producto", command=eliminar_producto).pack(side=tk.LEFT, padx=5)
        
        row += 2

        # =====================================================================
        # PRESUPUESTO (total automático)
        # =====================================================================
        ttk.Label(main, text="Presupuesto Total (€):").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        # Usar Entry normal con readonly para que no sea editable manualmente
        entry_presupuesto = tk.Entry(main, width=30, state="readonly", readonlybackground="white")
        entry_presupuesto.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        # Wrapper para mantener compatibilidad con ValidatedEntry
        class ReadOnlyPresupuesto:
            def __init__(self, entry):
                self.entry = entry
            def set_value(self, value):
                self.entry.config(state="normal")
                self.entry.delete(0, tk.END)
                self.entry.insert(0, str(value))
                self.entry.config(state="readonly")
            def get_value(self):
                return self.entry.get()
            def validate_input(self):
                return True
        presupuesto_wrapper = ReadOnlyPresupuesto(entry_presupuesto)
        fields["presupuesto"] = presupuesto_wrapper
        
        # Función para actualizar total (debe estar después de crear presupuesto_wrapper)
        def actualizar_total():
            total = sum(p.get("subtotal", p.get("precio", 0) * p.get("cantidad", 1)) for p in productos_seleccionados)
            presupuesto_wrapper.set_value(f"{total:.2f}")
        
        # Asignar función a la variable para que esté disponible en agregar_producto
        actualizar_total_fn = actualizar_total
        
        # Cargar productos si se está editando (después de definir actualizar_total)
        if item:
            import logging
            logger = logging.getLogger(__name__)
            
            # Intentar cargar desde presupuestoProductos (nuevo formato)
            presupuesto_productos = item.get("presupuestoProductos") or item.get("presupuesto_productos") or []
            if presupuesto_productos:
                logger.info(f"Editando presupuesto - {len(presupuesto_productos)} productos encontrados")
                for pp in presupuesto_productos:
                    if not isinstance(pp, dict):
                        continue
                    producto_id = pp.get("id_producto")
                    cantidad = pp.get("cantidad", 1)
                    precio_unitario = pp.get("precio_unitario", 0)
                    subtotal = pp.get("subtotal", precio_unitario * cantidad)
                    
                    # Buscar producto para obtener nombre
                    producto = None
                    for p in self.productos:
                        p_id = p.get("id") or p.get("id_producto")
                        if p_id == producto_id:
                            producto = p
                            break
                    
                    if producto:
                        productos_seleccionados.append({
                            "id_producto": producto_id,
                            "cantidad": cantidad,
                            "precio_unitario": precio_unitario,
                            "subtotal": subtotal
                        })
                        productos_listbox.insert(tk.END, f"{producto.get('nombre', '')} x{cantidad} - €{subtotal:.2f}")
                        logger.info(f"Producto cargado: {producto.get('nombre')} x{cantidad} - €{subtotal:.2f}")
                    else:
                        logger.warning(f"Producto con ID {producto_id} no encontrado en la lista de productos")
                
                if productos_seleccionados:
                    actualizar_total()
            # Fallback: cargar desde id_producto (formato antiguo, para compatibilidad)
            elif item.get("id_producto"):
                producto_id = item.get("id_producto")
                logger.info(f"Editando presupuesto (formato antiguo) - producto_id: {producto_id}")
                
                producto = None
                for p in self.productos:
                    p_id = p.get("id") or p.get("id_producto")
                    if p_id == producto_id:
                        producto = p
                        break
                
                if producto:
                    precio = float(producto.get("precio", 0))
                    productos_seleccionados.append({
                        "id_producto": producto_id,
                        "cantidad": 1,
                        "precio_unitario": precio,
                        "subtotal": precio
                    })
                    productos_listbox.insert(tk.END, f"{producto.get('nombre', '')} - €{precio:.2f}")
                    logger.info(f"Producto cargado: {producto.get('nombre')} - €{precio:.2f}")
                    actualizar_total()
                else:
                    logger.warning(f"Producto con ID {producto_id} no encontrado en la lista de productos")
        
        # Auto-calcular si es nuevo
        if item is None:
            actualizar_total()
        elif item and item.get("presupuesto") and not productos_seleccionados:
            # Solo usar el presupuesto del item si no hay productos cargados
            presupuesto_wrapper.set_value(str(item["presupuesto"]))
        row += 1

        # =====================================================================
        # ESTADO (auto-asignado según lógica)
        # =====================================================================
        ttk.Label(main, text="Estado:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        # Estados: PENDIENTE (nuevo), APROBADO (con fecha_cierre), RECHAZADO
        estado_opts = ["PENDIENTE", "APROBADO", "RECHAZADO"]
        combo_estado = ttk.Combobox(main, values=estado_opts, width=40, state="readonly")
        combo_estado.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        fields["estado"] = combo_estado
        
        # Auto-asignar estado inicial
        if item is None:
            combo_estado.set("PENDIENTE")
        elif item and item.get("estado"):
            combo_estado.set(str(item["estado"]))
        row += 1

        # =====================================================================
        # FECHA APERTURA (auto-asignada)
        # =====================================================================
        ttk.Label(main, text="Fecha Apertura:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        entry_fecha_apertura = ValidatedEntry(main, validation_type="date", required=False, width=40)
        entry_fecha_apertura.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        fields["fecha_apertura"] = entry_fecha_apertura
        
        # Auto-asignar fecha actual si es nuevo
        if item is None:
            fecha_actual = datetime.now().strftime("%Y-%m-%d")
            entry_fecha_apertura.set_value(fecha_actual)
        elif item and item.get("fecha_apertura"):
            entry_fecha_apertura.set_value(str(item["fecha_apertura"]))
        row += 1

        # =====================================================================
        # FECHA CIERRE (opcional)
        # =====================================================================
        ttk.Label(main, text="Fecha Cierre (opcional):").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        entry_fecha_cierre = ValidatedEntry(main, validation_type="date", required=False, width=40)
        entry_fecha_cierre.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        fields["fecha_cierre"] = entry_fecha_cierre
        
        # Precargar si edita
        if item and item.get("fecha_cierre"):
            entry_fecha_cierre.set_value(str(item["fecha_cierre"]))
        row += 1

        main.columnconfigure(1, weight=1)

        # =====================================================================
        # BOTONES (al final del formulario, centrados)
        # =====================================================================
        # Frame contenedor para centrar los botones (se expande horizontalmente)
        btns_container = ttk.Frame(main)
        btns_container.grid(row=row, column=0, columnspan=2, pady=20, sticky="ew")
        
        # Frame de botones (centrado dentro del contenedor)
        btns = ttk.Frame(btns_container)
        btns.pack(anchor=tk.CENTER)
        
        # Crear botones inmediatamente
        btn_guardar = ttk.Button(btns, text="Guardar")
        btn_cancelar = ttk.Button(btns, text="Cancelar", command=form.destroy)
        
        btn_guardar.pack(side=tk.LEFT, padx=5)
        btn_cancelar.pack(side=tk.LEFT, padx=5)

        def save():
            # Validar que hay al menos un producto
            if not productos_seleccionados:
                messagebox.showerror("Error", "Debe agregar al menos un producto")
                return
            
            # Validar cliente beneficiario
            beneficiario_val = combo_beneficiario.get()
            if not beneficiario_val or beneficiario_val == "Nuevo cliente...":
                messagebox.showerror("Error", "Debe seleccionar o crear un cliente beneficiario")
                return
            
            data = {}

            # Empleado (ya asignado automáticamente si es nuevo)
            if item is None:
                data["id_empleado"] = fields.get("id_empleado")
            else:
                # En edición, mantener el empleado actual o permitir cambio
                # Por ahora, mantener el actual
                if item.get("id_empleado"):
                    data["id_empleado"] = item["id_empleado"]

            # Cliente pagador
            pagador_val = combo_pagador.get()
            if not pagador_val:
                messagebox.showerror("Error", "Debe seleccionar un cliente pagador")
                return
            try:
                data["id_cliente_pagador"] = int(pagador_val.split(" - ")[0])
            except (ValueError, IndexError):
                messagebox.showerror("Error", "Error al procesar cliente pagador")
                return

            # Cliente beneficiario
            if beneficiario_val == "Nuevo cliente...":
                messagebox.showerror("Error", "Debe crear primero el cliente beneficiario")
                return
            try:
                data["id_cliente_beneficiario"] = int(beneficiario_val.split(" - ")[0])
            except (ValueError, IndexError):
                messagebox.showerror("Error", "Error al procesar cliente beneficiario")
                return

            # Productos (array de productos)
            if productos_seleccionados:
                beneficiario_id = data.get("id_cliente_beneficiario")
                productos_array = []
                for prod in productos_seleccionados:
                    producto_data = {
                        "id_producto": prod["id_producto"],
                        "id_cliente_beneficiario": beneficiario_id,
                        "cantidad": prod.get("cantidad", 1),
                        "precio_unitario": prod.get("precio_unitario", prod.get("precio", 0)),
                        "subtotal": prod.get("subtotal", prod.get("precio", 0) * prod.get("cantidad", 1))
                    }
                    productos_array.append(producto_data)
                data["productos"] = productos_array

            # Presupuesto (total) - es readonly, no necesita validación
            presupuesto_val = presupuesto_wrapper.get_value()
            try:
                presupuesto_float = float(presupuesto_val)
                if presupuesto_float <= 0:
                    messagebox.showerror("Error", "El presupuesto debe ser mayor que 0")
                    return
                # Convertir a número (mantener decimales si los hay, pero asegurar que es un número válido)
                # Si es un entero, enviarlo como int, si tiene decimales, como float
                if presupuesto_float.is_integer():
                    data["presupuesto"] = int(presupuesto_float)
                else:
                    data["presupuesto"] = presupuesto_float
            except ValueError:
                messagebox.showerror("Error", "Presupuesto debe ser numérico")
                return

            # Estado
            estado_val = combo_estado.get()
            if not estado_val:
                messagebox.showerror("Error", "Debe seleccionar un estado")
                return
            data["estado"] = estado_val

            # Fecha apertura
            fecha_apertura_val = entry_fecha_apertura.get_value()
            if fecha_apertura_val:
                data["fecha_apertura"] = fecha_apertura_val

            # Fecha cierre (opcional)
            # Nota: El backend asigna automáticamente fecha_cierre cuando el estado cambia a APROBADO
            # Solo enviar fecha_cierre si el usuario la especificó explícitamente Y el estado NO es APROBADO
            # Si el estado es APROBADO y no hay fecha_cierre, dejar que el backend la asigne automáticamente
            fecha_cierre_val = entry_fecha_cierre.get_value()
            if fecha_cierre_val and estado_val != "APROBADO":
                data["fecha_cierre"] = fecha_cierre_val
            # Si el estado es APROBADO y no hay fecha_cierre, no enviar el campo para que el backend lo asigne

            # Guardar
            # Logging para debug
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Datos a enviar al backend (presupuestos): {data}")
            
            if item:
                presupuesto_id = item.get("id_Presupuesto") or item.get("id")
                if not presupuesto_id:
                    messagebox.showerror("Error", "No se pudo obtener el ID del presupuesto")
                    return
                # El método update ya agrega id_Presupuesto al payload, no es necesario agregarlo aquí
                # Pero lo agregamos por si acaso el backend lo necesita explícitamente
                # data["id_Presupuesto"] = presupuesto_id
                res = self.api.update("presupuestos", presupuesto_id, data)
            else:
                res = self.api.create("presupuestos", data)

            if res.get("success"):
                messagebox.showinfo("Éxito", "Presupuesto guardado correctamente")
                form.destroy()
                self._load_data()
            else:
                error_msg = res.get("error", "Error desconocido")
                messagebox.showerror("Error", f"Error al guardar:\n{error_msg}")

        # Asignar comando al botón Guardar después de definir save()
        btn_guardar.config(command=save)
