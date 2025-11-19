"""
Ventana de gestión de facturas
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional
from src.api.rest_client import RESTClient
from src.ui.entities.base_crud_window import BaseCRUDWindow
from src.components.validated_entry import ValidatedEntry

class FacturasWindow(BaseCRUDWindow):
    """Ventana para gestionar facturas"""
    
    def __init__(self, parent, api: RESTClient, client_mode: bool = False):
        columns = [
            {"name": "id", "width": 50, "anchor": "center"},
            {"name": "cliente_id", "width": 80, "anchor": "center"},
            {"name": "empleado_id", "width": 80, "anchor": "center"},
            {"name": "fecha", "width": 120},
            {"name": "total", "width": 100, "anchor": "e"},
            {"name": "estado", "width": 100},
        ]
        
        filters = [
            {"name": "cliente_id", "type": "number", "label": "Cliente ID"},
            {"name": "estado", "type": "text", "label": "Estado"},
        ]
        
        super().__init__(parent, api, "facturas", columns, filters, client_mode)
        
        if client_mode:
            # Cargar solo facturas del cliente
            self._load_my_facturas()
        
        # Cargar datos relacionados
        self.clientes = []
        self.empleados = []
        if not client_mode:
            self._load_related_data()
    
    def _load_my_facturas(self):
        """Carga las facturas del cliente actual"""
        result = self.api.get_my_facturas()
        if result.get("success"):
            self.data = result.get("data", [])
            self.table.set_data(self.data)
    
    def _load_related_data(self):
        """Carga clientes y empleados para el formulario"""
        clientes_result = self.api.get_clientes()
        if clientes_result.get("success"):
            self.clientes = clientes_result.get("data", [])
        
        empleados_result = self.api.get_empleados()
        if empleados_result.get("success"):
            self.empleados = empleados_result.get("data", [])
    
    def _get_form_fields(self) -> list:
        """Retorna los campos del formulario"""
        return [
            {"name": "cliente_id", "label": "Cliente", "type": "select", "required": True},
            {"name": "empleado_id", "label": "Empleado", "type": "select", "required": True},
            {"name": "fecha", "label": "Fecha", "type": "date", "required": True},
            {"name": "total", "label": "Total", "type": "number", "required": True},
            {"name": "estado", "label": "Estado", "type": "select", "required": True},
        ]
    
    def _show_form(self, item: Optional[Dict]):
        """Muestra el formulario de factura"""
        if self.client_mode:
            messagebox.showinfo("Información", "Los clientes no pueden crear o editar facturas")
            return
        
        form_window = tk.Toplevel(self)
        form_window.title("Nueva Factura" if not item else "Editar Factura")
        form_window.geometry("500x450")
        form_window.transient(self.winfo_toplevel())
        form_window.grab_set()
        
        # Centrar ventana
        form_window.update_idletasks()
        x = (form_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (form_window.winfo_screenheight() // 2) - (450 // 2)
        form_window.geometry(f"500x450+{x}+{y}")
        
        # Frame principal
        main_frame = ttk.Frame(form_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        fields = {}
        form_fields = self._get_form_fields()
        
        # Crear campos
        for i, field_config in enumerate(form_fields):
            label = ttk.Label(main_frame, text=field_config["label"] + ":")
            label.grid(row=i, column=0, sticky="w", pady=5, padx=5)
            
            if field_config["type"] == "select":
                if field_config["name"] == "cliente_id":
                    options = [f"{c['id']} - {c.get('nombre', '')} {c.get('apellidos', '')}" 
                              for c in self.clientes]
                    combo = ttk.Combobox(main_frame, values=options, width=37, state="readonly")
                elif field_config["name"] == "empleado_id":
                    options = [f"{e['id']} - {e.get('nombre', '')} {e.get('apellidos', '')}" 
                              for e in self.empleados]
                    combo = ttk.Combobox(main_frame, values=options, width=37, state="readonly")
                elif field_config["name"] == "estado":
                    combo = ttk.Combobox(main_frame, values=["PENDIENTE", "PAGADA", "CANCELADA"], 
                                        width=37, state="readonly")
                else:
                    combo = ttk.Combobox(main_frame, width=37, state="readonly")
                
                combo.grid(row=i, column=1, pady=5, padx=5, sticky="ew")
                fields[field_config["name"]] = combo
                
                if item and field_config["name"] in item:
                    # Buscar el valor correspondiente
                    if field_config["name"] == "cliente_id":
                        for c in self.clientes:
                            if c["id"] == item[field_config["name"]]:
                                combo.set(f"{c['id']} - {c.get('nombre', '')} {c.get('apellidos', '')}")
                                break
                    elif field_config["name"] == "empleado_id":
                        for e in self.empleados:
                            if e["id"] == item[field_config["name"]]:
                                combo.set(f"{e['id']} - {e.get('nombre', '')} {e.get('apellidos', '')}")
                                break
                    else:
                        combo.set(str(item[field_config["name"]]))
            elif field_config["type"] == "date":
                entry = ValidatedEntry(main_frame, validation_type="date", 
                                     required=field_config.get("required", False),
                                     width=40)
                entry.grid(row=i, column=1, pady=5, padx=5, sticky="ew")
                fields[field_config["name"]] = entry
                
                if item and field_config["name"] in item:
                    entry.set_value(item[field_config["name"]])
            elif field_config["type"] == "number":
                entry = ValidatedEntry(main_frame, validation_type="number", 
                                     required=field_config.get("required", False),
                                     width=40)
                entry.grid(row=i, column=1, pady=5, padx=5, sticky="ew")
                fields[field_config["name"]] = entry
                
                if item and field_config["name"] in item:
                    entry.set_value(item[field_config["name"]])
            else:
                entry = ValidatedEntry(main_frame, validation_type="text", 
                                     required=field_config.get("required", False),
                                     width=40)
                entry.grid(row=i, column=1, pady=5, padx=5, sticky="ew")
                fields[field_config["name"]] = entry
                
                if item and field_config["name"] in item:
                    entry.set_value(item[field_config["name"]])
        
        main_frame.columnconfigure(1, weight=1)
        
        # Botones
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=len(form_fields), column=0, columnspan=2, pady=20)
        
        def save():
            # Validar campos
            data = {}
            for name, widget in fields.items():
                if isinstance(widget, ValidatedEntry):
                    if not widget.validate_input():
                        messagebox.showerror("Error", f"El campo {name} no es válido")
                        return
                    value = widget.get_value()
                    if value:
                        if name == "total":
                            try:
                                data[name] = float(value)
                            except:
                                messagebox.showerror("Error", "El total debe ser un número")
                                return
                        else:
                            data[name] = value
                elif isinstance(widget, ttk.Combobox):
                    value = widget.get()
                    if value:
                        if name in ["cliente_id", "empleado_id"]:
                            # Extraer ID del formato "ID - Nombre"
                            data[name] = int(value.split(" - ")[0])
                        else:
                            data[name] = value
            
            # Guardar
            if item:
                result = self.api.update("facturas", item["id"], data)
            else:
                result = self.api.create("facturas", data)
            
            if result.get("success"):
                messagebox.showinfo("Éxito", "Factura guardada correctamente")
                form_window.destroy()
                self._load_data()
            else:
                messagebox.showerror("Error", f"Error al guardar: {result.get('error')}")
        
        ttk.Button(buttons_frame, text="Guardar", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Cancelar", command=form_window.destroy).pack(side=tk.LEFT, padx=5)

