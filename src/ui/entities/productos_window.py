"""
Ventana de gestión de productos
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional, List

from src.ui.entities.base_crud_window import BaseCRUDWindow
from src.widgets.validated_entry import ValidatedEntry


class ProductosWindow(BaseCRUDWindow):
    """Gestión de productos."""

    def __init__(self, parent, api):
        columns = [
            {"name": "id", "width": 60, "anchor": "center"},
            {"name": "nombre", "width": 200},
            {"name": "descripcion", "width": 250},
            {"name": "categoria", "width": 120},
            {"name": "precio", "width": 100, "anchor": "e"},
            {"name": "activo", "width": 80, "anchor": "center"},
        ]

        # Filtros iniciales (se actualizarán después de cargar datos)
        filters = [
            {"name": "nombre", "type": "select", "label": "Nombre", "options": []},
            {"name": "precio_desde", "type": "select", "label": "Precio Desde", "options": []},
            {"name": "precio_hasta", "type": "select", "label": "Precio Hasta", "options": []},
        ]

        super().__init__(parent, api, "productos", columns, filters, client_mode=False)
        
        # Cargar datos y actualizar opciones de filtros
        self._load_data()
        self._update_filter_options()

    # =====================================================================
    # ACTUALIZAR OPCIONES DE FILTROS
    # =====================================================================
    SIN_FILTRO = "(Sin filtro)"
    
    def _update_filter_options(self):
        """Actualiza las opciones de los filtros select con datos dinámicos."""
        if not hasattr(self, 'filter_panel'):
            return

        # Usar datos ya cargados si están disponibles, sino cargar
        productos = self.data if self.data else []
        if not productos:
            result = self.api.get_all("productos")
            if not result.get("success"):
                return
            productos = result.get("data", [])

        # 1. OPCIONES PARA FILTRO "nombre"
        nombres = sorted({p.get("nombre", "") for p in productos if p.get("nombre")})
        nombre_widget = self.filter_panel.filter_widgets.get("nombre")
        if nombre_widget and isinstance(nombre_widget, ttk.Combobox):
            nombre_widget["values"] = [self.SIN_FILTRO] + nombres
            nombre_widget.current(0)

        # 2. OPCIONES PARA FILTROS "precio_desde" y "precio_hasta"
        precios = []
        for p in productos:
            precio = p.get("precio")
            if precio is not None:
                try:
                    precio_num = float(precio)
                    precios.append(precio_num)
                except (ValueError, TypeError):
                    continue

        if precios:
            precio_max = int(max(precios))
            
            # Generar opciones: 0, 500, 1000, 1500, ... hasta el máximo
            opciones_precio = [self.SIN_FILTRO]
            valor = 0
            while valor <= precio_max:
                opciones_precio.append(str(valor))
                valor += 500
            
            # Asegurar que el máximo esté incluido
            if str(precio_max) not in opciones_precio:
                opciones_precio.append(str(precio_max))

            # Aplicar a ambos combobox
            for filtro_name in ["precio_desde", "precio_hasta"]:
                precio_widget = self.filter_panel.filter_widgets.get(filtro_name)
                if precio_widget and isinstance(precio_widget, ttk.Combobox):
                    precio_widget["values"] = opciones_precio
                    precio_widget.current(0)

    # =====================================================================
    # SOBRESCRIBIR _on_filter PARA MANEJAR LOS NUEVOS FILTROS
    # =====================================================================
    def _on_filter(self, filter_values: Dict):
        """Maneja el filtrado con los nuevos filtros de productos."""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Filtros recibidos: {filter_values}")
        
        # Si no hay filtros, recargar todo
        nombre = filter_values.get("nombre")
        precio_desde = filter_values.get("precio_desde")
        precio_hasta = filter_values.get("precio_hasta")
        
        if (not nombre or nombre == self.SIN_FILTRO) and \
           (not precio_desde or precio_desde == self.SIN_FILTRO) and \
           (not precio_hasta or precio_hasta == self.SIN_FILTRO):
            logger.info("No hay filtros, recargando todos los datos")
            self._load_data()
            return

        # Cargar todos los productos primero (backend puede no soportar filtros)
        result = self.api.get_all("productos")
        
        if not result.get("success"):
            error_msg = result.get("error", "Error desconocido")
            logger.error(f"Error al cargar productos: {error_msg}")
            messagebox.showerror("Error", f"Error al cargar productos:\n{error_msg}")
            return

        data = result.get("data", [])
        if data is None:
            data = []
        elif not isinstance(data, list):
            data = [data] if data else []

        # Aplicar filtros en el frontend
        filtered_data = data.copy()
        
        # Filtro por nombre (búsqueda parcial, case-insensitive)
        if nombre and nombre != self.SIN_FILTRO:
            nombre_filter = nombre.lower()
            filtered_data = [
                p for p in filtered_data
                if nombre_filter in str(p.get("nombre", "")).lower()
            ]
            logger.info(f"Filtro por nombre '{nombre}': {len(filtered_data)} productos")
        
        # Filtros por precio (rango)
        if precio_desde and precio_desde != self.SIN_FILTRO:
            try:
                precio_min = float(precio_desde)
                filtered_data = [
                    p for p in filtered_data
                    if self._get_precio(p) >= precio_min
                ]
                logger.info(f"Filtro precio_min={precio_min}: {len(filtered_data)} productos")
            except (ValueError, TypeError):
                pass

        if precio_hasta and precio_hasta != self.SIN_FILTRO:
            try:
                precio_max = float(precio_hasta)
                filtered_data = [
                    p for p in filtered_data
                    if self._get_precio(p) <= precio_max
                ]
                logger.info(f"Filtro precio_max={precio_max}: {len(filtered_data)} productos")
            except (ValueError, TypeError):
                pass

        # Normalizar IDs y campos
        for row in filtered_data:
            if isinstance(row, dict):
                # Normalizar id_producto a id
                if "id_producto" in row and "id" not in row:
                    row["id"] = row["id_producto"]
                
                # Guardar el valor boolean original de activo antes de convertirlo para la tabla
                activo_original = None
                if "activo" in row:
                    activo = row["activo"]
                    if isinstance(activo, bool):
                        activo_original = activo
                    elif isinstance(activo, str):
                        activo_original = activo.lower() in ("true", "1", "yes", "sí", "si")
                    else:
                        activo_original = bool(activo) if activo is not None else False
                else:
                    activo_original = False
                
                # Guardar el valor original para cuando se edite
                row["_activo_original"] = activo_original
                # Convertir a texto para mostrar en la tabla
                row["activo"] = "Sí" if activo_original else "No"
                
                # Asegurar que categoria esté presente (puede ser null)
                if "categoria" not in row or row["categoria"] is None:
                    row["categoria"] = ""

        self.data = filtered_data
        logger.info(f"Productos filtrados: {len(self.data)} registros")
        self.table.set_data(self.data)
    
    def _get_precio(self, producto: Dict) -> float:
        """Extrae el precio de un producto de forma segura"""
        precio = producto.get("precio")
        if precio is None:
            return 0.0
        try:
            return float(precio)
        except (ValueError, TypeError):
            return 0.0

    # =====================================================================
    # SOBRESCRIBIR _load_data PARA ACTUALIZAR FILTROS DESPUÉS
    # =====================================================================
    def _load_data(self):
        """Carga los datos y actualiza las opciones de filtros."""
        import logging
        logger = logging.getLogger(__name__)
        
        result = self.api.get_all("productos")

        if not result.get("success"):
            messagebox.showerror("Error", f"Error al cargar datos: {result.get('error')}")
            return

        data = result.get("data", [])
        
        # Asegurar que data es una lista
        if data is None:
            data = []
        elif not isinstance(data, list):
            data = [data] if data else []
        
        # Normalizar IDs y campos
        for row in data:
            if isinstance(row, dict):
                # Normalizar id_producto a id
                if "id_producto" in row and "id" not in row:
                    row["id"] = row["id_producto"]
                # Normalizar activo (puede venir como boolean o string)
                if "activo" in row:
                    activo = row["activo"]
                    if isinstance(activo, str):
                        activo_bool = activo.lower() in ("true", "1", "yes", "sí")
                    elif activo is None:
                        activo_bool = False
                    else:
                        activo_bool = bool(activo)
                    row["activo"] = "Sí" if activo_bool else "No"
                else:
                    row["activo"] = "No"
                # Asegurar que categoria esté presente (puede ser null)
                if "categoria" not in row or row["categoria"] is None:
                    row["categoria"] = ""
        
        logger.info(f"Productos cargados: {len(data)} registros")
        logger.debug(f"Primer producto (ejemplo): {data[0] if data else 'No hay datos'}")
        
        self.data = data
        self.table.set_data(self.data)
        
        # Actualizar opciones de filtros después de cargar
        self._update_filter_options()

    # =====================================================================
    # CAMPOS DEL FORMULARIO
    # =====================================================================
    def _get_form_fields(self):
        """
        Definición de los campos del formulario de productos.
        
        Campos que el backend Java acepta:
        - nombre (obligatorio)
        - descripcion (opcional)
        - categoria (opcional): "Ciclo Formativo" o "Formación complementaria"
        - precio (opcional, debe ser >= 0)
        - activo (opcional, boolean, por defecto false)
        """
        return [
            {"name": "nombre", "label": "Nombre", "type": "text", "required": True},
            {"name": "descripcion", "label": "Descripción", "type": "text", "required": False},
            {"name": "categoria", "label": "Categoría", "type": "select", "options": ["Ciclo Formativo", "Formación complementaria"], "required": False},
            {"name": "precio", "label": "Precio", "type": "number", "required": False},
            {"name": "activo", "label": "Activo", "type": "checkbox", "required": False},
        ]

    # =====================================================================
    # FORMULARIO
    # =====================================================================
    def _on_select(self, item):
        pass
    
    def _show_form(self, item: Optional[Dict]):
        # Validar que item es un diccionario si no es None
        if item is not None and not isinstance(item, dict):
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error: item debe ser un diccionario o None, pero recibió: {type(item)}")
            from tkinter import messagebox
            messagebox.showerror("Error", f"Error al cargar datos del formulario: tipo inesperado {type(item)}")
            return
        
        form = tk.Toplevel(self)
        form.title("Nuevo Producto" if item is None else "Editar Producto")
        form.geometry("600x340")
        form.transient(self.winfo_toplevel())
        form.grab_set()

        # Centrar ventana
        form.update_idletasks()
        x = (form.winfo_screenwidth() // 2) - 300
        y = (form.winfo_screenheight() // 2) - 180
        form.geometry(f"600x340+{x}+{y}")

        # Frame principal
        main = ttk.Frame(form, padding=15)
        main.pack(fill=tk.BOTH, expand=True)

        fields = {}
        specs = self._get_form_fields()

        # Crear campos
        for i, f in enumerate(specs):
            ttk.Label(main, text=f["label"] + ":").grid(
                row=i, column=0, sticky="w", pady=4, padx=5
            )

            field_type = f.get("type", "text")
            
            if field_type == "select":
                # Combobox para campo categoria
                options = f.get("options", [])
                combo = ttk.Combobox(main, values=options, state="readonly", width=30)
                combo.grid(row=i, column=1, pady=4, padx=5, sticky="ew")
                
                # Cargar valor si se está editando
                if item and isinstance(item, dict):
                    categoria = item.get("categoria")
                    if categoria and categoria in options:
                        combo.set(categoria)
                    elif options:
                        combo.current(0)  # Seleccionar primera opción por defecto
                elif options:
                    combo.current(0)  # Seleccionar primera opción por defecto
                
                fields[f["name"]] = combo
            elif field_type == "checkbox":
                # Checkbox para campo activo
                var = tk.BooleanVar()
                checkbox = ttk.Checkbutton(main, variable=var)
                checkbox.grid(row=i, column=1, pady=4, padx=5, sticky="w")
                
                # Cargar valor si se está editando
                if item and isinstance(item, dict):
                    # Usar el valor original guardado si existe, sino intentar obtenerlo
                    activo = item.get("_activo_original")
                    if activo is None:
                        # Si no hay valor original, intentar obtenerlo del campo activo
                        activo = item.get("activo")
                        if isinstance(activo, bool):
                            var.set(activo)
                        elif isinstance(activo, str):
                            # Si viene como "Sí"/"No" de la tabla, convertir a boolean
                            var.set(activo.lower() in ("sí", "si", "yes", "true", "1"))
                        elif activo is None:
                            # Si es None, usar False por defecto
                            var.set(False)
                        else:
                            var.set(bool(activo))
                    else:
                        var.set(bool(activo))
                    
                    # Guardar el valor cargado en el item para referencia futura
                    if "_activo_original" not in item:
                        item["_activo_original"] = var.get()
                else:
                    # Si es un nuevo producto, activo por defecto es False
                    var.set(False)
                
                fields[f["name"]] = var
            elif field_type == "number":
                entry = ValidatedEntry(main, validation_type="number",
                                       required=f.get("required", False),
                                       width=30)
                entry.grid(row=i, column=1, pady=4, padx=5, sticky="ew")
                
                # Cargar valor si se está editando
                if item and isinstance(item, dict):
                    field_name = f["name"]
                    value = item.get(field_name)
                    if value is not None:
                        entry.set_value(str(value))
                
                fields[f["name"]] = entry
            else:
                entry = ValidatedEntry(main, validation_type="text",
                                       required=f.get("required", False),
                                       width=30)
                entry.grid(row=i, column=1, pady=4, padx=5, sticky="ew")
                
                # Cargar valor si se está editando
                if item and isinstance(item, dict):
                    field_name = f["name"]
                    value = item.get(field_name)
                    if value is not None:
                        entry.set_value(str(value))
                
                fields[f["name"]] = entry

        main.columnconfigure(1, weight=1)

        # =====================================================================
        # BOTONES
        # =====================================================================
        btns = ttk.Frame(main)
        btns.grid(row=len(specs), column=0, columnspan=2, pady=15)

        def save():
            import logging
            logger = logging.getLogger(__name__)
            
            # Asegurar que messagebox esté disponible en el closure
            from tkinter import messagebox as mb
            
            data = {}

            # Validar y recoger datos
            for name, widget in fields.items():
                field_config = next((f for f in specs if f["name"] == name), {})
                field_type = field_config.get("type", "text")
                
                # Manejar checkbox (activo)
                if field_type == "checkbox":
                    # Checkbox devuelve BooleanVar
                    if isinstance(widget, tk.BooleanVar):
                        activo_value = widget.get()
                        data[name] = activo_value
                        logger.debug(f"Campo 'activo' capturado: {activo_value} (tipo: {type(activo_value)})")
                    continue
                
                # Manejar Combobox (categoria)
                if field_type == "select":
                    if isinstance(widget, ttk.Combobox):
                        value = widget.get()
                        # Solo agregar si tiene un valor seleccionado
                        if value and value.strip():
                            data[name] = value.strip()
                        # Si está vacío y no es requerido, no agregar al data
                    continue
                
                # Manejar ValidatedEntry
                if not widget.validate_input():
                    mb.showerror("Error", f"El campo '{field_config.get('label', name)}' no es válido")
                    return

                value = widget.get_value()

                # Si el campo es requerido y está vacío, mostrar error
                if field_config.get("required", False) and (not value or (isinstance(value, str) and value.strip() == "")):
                    mb.showerror("Error", f"El campo '{field_config.get('label', name)}' es obligatorio")
                    return

                # Para campos opcionales, solo agregar si tienen valor
                if not value or (isinstance(value, str) and value.strip() == ""):
                    if not field_config.get("required", False):
                        continue
                    else:
                        mb.showerror("Error", f"El campo '{field_config.get('label', name)}' es obligatorio")
                        return

                # Convertir valores según el tipo
                if name == "precio":
                    try:
                        precio_val = float(value)
                        if precio_val < 0:
                            mb.showerror("Error", "El precio no puede ser negativo")
                            return
                        data[name] = precio_val
                    except ValueError:
                        mb.showerror("Error", "Precio debe ser un número válido")
                        return
                else:
                    # Campos de texto (nombre, descripcion, categoria)
                    data[name] = value.strip() if isinstance(value, str) else value

            # Validar que nombre esté presente (obligatorio)
            if not data.get("nombre"):
                mb.showerror("Error", "El campo 'Nombre' es obligatorio")
                return
            
            # Filtrar datos: NO enviar campos que no existen en el backend
            # El backend acepta: nombre, descripcion, categoria, precio, activo
            # NO acepta: stock (no existe)
            filtered_data = {}
            allowed_fields = ["nombre", "descripcion", "categoria", "precio", "activo"]
            for key, value in data.items():
                if key in allowed_fields:
                    filtered_data[key] = value
            
            # Asegurar que 'activo' siempre se envíe explícitamente (incluso si es False)
            # Esto es crítico para que el backend actualice correctamente el estado
            if "activo" in data:
                # Si está en data, usar ese valor (puede ser True o False)
                filtered_data["activo"] = data["activo"]
                logger.debug(f"Campo 'activo' incluido desde data: {data['activo']}")
            elif item is not None:
                # Si estamos editando y no se capturó activo del checkbox, usar el valor original
                activo_original = item.get("_activo_original")
                if activo_original is None:
                    activo_original = item.get("activo")
                    if isinstance(activo_original, str):
                        activo_original = activo_original.lower() in ("sí", "si", "yes", "true", "1")
                    elif activo_original is None:
                        activo_original = False
                    else:
                        activo_original = bool(activo_original)
                filtered_data["activo"] = activo_original
                logger.debug(f"Campo 'activo' no capturado del checkbox, usando valor original: {activo_original}")
            else:
                # Si es un nuevo producto y no se capturó activo, usar False por defecto
                filtered_data["activo"] = False
                logger.debug("Campo 'activo' no capturado, usando False por defecto para nuevo producto")
            
            logger.debug(f"Datos filtrados antes de enviar: {filtered_data}")
            
            # Guardar en API
            if item is None:
                # POST: Crear nuevo producto
                # No enviar id_producto (se genera automáticamente)
                logger.info(f"Datos a enviar al backend (POST): {filtered_data}")
                result = self.api.create("productos", filtered_data)
            else:
                # PUT: Actualizar producto existente
                # Obtener id_producto del item
                producto_id = item.get("id_producto") or item.get("id")
                if not producto_id:
                    mb.showerror("Error", "No se pudo obtener el ID del producto")
                    return
                
                # Agregar id_producto al payload (obligatorio para PUT)
                update_data = filtered_data.copy()
                update_data["id_producto"] = producto_id
                
                logger.info(f"Datos a enviar al backend (PUT): {update_data}")
                result = self.api.update("productos", producto_id, update_data)

            logger.info(f"Resultado del backend: {result}")
            
            if result.get("success"):
                mb.showinfo("Éxito", "Producto guardado correctamente")
                form.destroy()
                self._load_data()
                self._update_filter_options()
            else:
                error_msg = result.get("error", "Error desconocido")
                # Si el error viene en data.error, extraerlo
                if isinstance(error_msg, dict):
                    error_msg = error_msg.get("error", str(error_msg))
                logger.error(f"Error al guardar producto: {error_msg}")
                mb.showerror("Error", f"No se pudo guardar el producto:\n{error_msg}")

        ttk.Button(btns, text="Guardar", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="Cancelar", command=form.destroy).pack(side=tk.LEFT, padx=5)
