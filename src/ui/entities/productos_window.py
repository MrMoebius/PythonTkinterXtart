"""
Ventana de gestión de productos
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional, List

from src.ui.entities.base_crud_window import BaseCRUDWindow
from src.components.validated_entry import ValidatedEntry


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
        params = {}

        # Filtro por nombre (exacto)
        nombre = filter_values.get("nombre")
        if nombre and nombre != self.SIN_FILTRO:
            params["nombre"] = nombre

        # Filtros por precio (rango)
        precio_desde = filter_values.get("precio_desde")
        precio_hasta = filter_values.get("precio_hasta")

        if precio_desde and precio_desde != self.SIN_FILTRO:
            try:
                params["precio_min"] = float(precio_desde)
            except (ValueError, TypeError):
                pass

        if precio_hasta and precio_hasta != self.SIN_FILTRO:
            try:
                params["precio_max"] = float(precio_hasta)
            except (ValueError, TypeError):
                pass

        # Si no hay filtros, recargar todo
        if not params:
            self._load_data()
            return

        # Aplicar filtros
        result = self.api.get_all("productos", params=params)

        if not result.get("success"):
            messagebox.showerror("Error", "No se pudo aplicar filtros.")
            return

        self.data = result.get("data", [])
        self.table.set_data(self.data)

    # =====================================================================
    # SOBRESCRIBIR _load_data PARA ACTUALIZAR FILTROS DESPUÉS
    # =====================================================================
    def _load_data(self):
        """Carga los datos y actualiza las opciones de filtros."""
        result = self.api.get_all("productos")

        if not result.get("success"):
            messagebox.showerror("Error", f"Error al cargar datos: {result.get('error')}")
            return

        self.data = result.get("data", [])
        self.table.set_data(self.data)
        
        # Actualizar opciones de filtros después de cargar
        self._update_filter_options()

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
