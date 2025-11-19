"""
Ventana de gestión de pagos
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional
from src.api.rest_client import RESTClient
from src.ui.entities.base_crud_window import BaseCRUDWindow
from src.components.validated_entry import ValidatedEntry

class PagosWindow(BaseCRUDWindow):
    """Ventana para gestionar pagos"""
    
    def __init__(self, parent, api: RESTClient, client_mode: bool = False):
        columns = [
            {"name": "id", "width": 50, "anchor": "center"},
            {"name": "factura_id", "width": 80, "anchor": "center"},
            {"name": "cliente_id", "width": 80, "anchor": "center"},
            {"name": "fecha", "width": 120},
            {"name": "importe", "width": 100, "anchor": "e"},
            {"name": "metodo_pago", "width": 120},
            {"name": "estado", "width": 100},
        ]
        
        filters = [
            {"name": "cliente_id", "type": "number", "label": "Cliente ID"},
            {"name": "metodo_pago", "type": "text", "label": "Método"},
            {"name": "estado", "type": "text", "label": "Estado"},
        ]
        
        super().__init__(parent, api, "pagos", columns, filters, client_mode)
        
        if client_mode:
            # Cargar solo pagos del cliente
            self._load_my_pagos()
        
        # Cargar datos relacionados
        self.facturas = []
        self.clientes = []
        if not client_mode:
            self._load_related_data()
    
    def _load_my_pagos(self):
        """Carga los pagos del cliente actual"""
        result = self.api.get_my_pagos()
        if result.get("success"):
            self.data = result.get("data", [])
            self.table.set_data(self.data)
    
    def _load_related_data(self):
        """Carga facturas y clientes para el formulario"""
        facturas_result = self.api.get_facturas()
        if facturas_result.get("success"):
            self.facturas = facturas_result.get("data", [])
        
        clientes_result = self.api.get_clientes()
        if clientes_result.get("success"):
            self.clientes = clientes_result.get("data", [])
    
    def _get_form_fields(self) -> list:
        """Retorna los campos del formulario"""
        return [
            {"name": "factura_id", "label": "Factura", "type": "select", "required": True},
            {"name": "cliente_id", "label": "Cliente", "type": "select", "required": True},
            {"name": "fecha", "label": "Fecha", "type": "date", "required": True},
            {"name": "importe", "label": "Importe", "type": "number", "required": True},
            {"name": "metodo_pago", "label": "Método de Pago", "type": "select", "required": True},
            {"name": "estado", "label": "Estado", "type": "select", "required": True},
        ]
    
    def _show_form(self, item: Optional[Dict]):
        """Muestra el formulario de pago"""
        if self.client_mode:
            messagebox.showinfo("Información", "Los clientes no pueden crear o editar pagos directamente")
            return
        
        form_window = tk.Toplevel(self)
        form_window.title("Nuevo Pago" if not item else "Editar Pago")
        form_window.geometry("500x500")
        form_window.transient(self.winfo_toplevel())
        form_window.grab_set()
        
        # Centrar ventana
        form_window.update_idletasks()
        x = (form_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (form_window.winfo_screenheight() // 2) - (500 // 2)
        form_window.geometry(f"500x500+{x}+{y}")
        
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
                if field_config["name"] == "factura_id":
                    options = [f"{f['id']} - Cliente {f.get('cliente_id', '')}" 
                              for f in self.facturas]
                    combo = ttk.Combobox(main_frame, values=options, width=37, state="readonly")
                elif field_config["name"] == "cliente_id":
                    options = [f"{c['id']} - {c.get('nombre', '')} {c.get('apellidos', '')}" 
                              for c in self.clientes]
                    combo = ttk.Combobox(main_frame, values=options, width=37, state="readonly")
                elif field_config["name"] == "metodo_pago":
                    combo = ttk.Combobox(main_frame, 
                                        values=["TARJETA", "TRANSFERENCIA", "EFECTIVO", "CHEQUE"], 
                                        width=37, state="readonly")
                elif field_config["name"] == "estado":
                    combo = ttk.Combobox(main_frame, values=["PENDIENTE", "COMPLETADO", "CANCELADO"], 
                                        width=37, state="readonly")
                else:
                    combo = ttk.Combobox(main_frame, width=37, state="readonly")
                
                combo.grid(row=i, column=1, pady=5, padx=5, sticky="ew")
                fields[field_config["name"]] = combo
                
                if item and field_config["name"] in item:
                    # Buscar el valor correspondiente
                    if field_config["name"] == "factura_id":
                        for f in self.facturas:
                            if f["id"] == item[field_config["name"]]:
                                combo.set(f"{f['id']} - Cliente {f.get('cliente_id', '')}")
                                break
                    elif field_config["name"] == "cliente_id":
                        for c in self.clientes:
                            if c["id"] == item[field_config["name"]]:
                                combo.set(f"{c['id']} - {c.get('nombre', '')} {c.get('apellidos', '')}")
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
                        if name == "importe":
                            try:
                                data[name] = float(value)
                            except:
                                messagebox.showerror("Error", "El importe debe ser un número")
                                return
                        else:
                            data[name] = value
                elif isinstance(widget, ttk.Combobox):
                    value = widget.get()
                    if value:
                        if name in ["factura_id", "cliente_id"]:
                            # Extraer ID del formato "ID - ..."
                            data[name] = int(value.split(" - ")[0])
                        else:
                            data[name] = value
            
            # Guardar
            if item:
                result = self.api.update("pagos", item["id"], data)
            else:
                result = self.api.create("pagos", data)
            
            if result.get("success"):
                messagebox.showinfo("Éxito", "Pago guardado correctamente")
                form_window.destroy()
                self._load_data()
            else:
                messagebox.showerror("Error", f"Error al guardar: {result.get('error')}")
        
        ttk.Button(buttons_frame, text="Guardar", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Cancelar", command=form_window.destroy).pack(side=tk.LEFT, padx=5)

