"""
Ventana de gestión de clientes
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional
from src.api.rest_client import RESTClient
from src.ui.entities.base_crud_window import BaseCRUDWindow
from src.components.validated_entry import ValidatedEntry

class ClientesWindow(BaseCRUDWindow):
    """Ventana para gestionar clientes"""
    
    def __init__(self, parent, api: RESTClient, client_mode: bool = False):
        columns = [
            {"name": "id", "width": 50, "anchor": "center"},
            {"name": "nombre", "width": 150},
            {"name": "apellidos", "width": 150},
            {"name": "email", "width": 200},
            {"name": "telefono", "width": 120},
            {"name": "direccion", "width": 200},
        ]
        
        filters = [
            {"name": "nombre", "type": "text", "label": "Nombre"},
            {"name": "email", "type": "text", "label": "Email"},
            {"name": "telefono", "type": "text", "label": "Teléfono"},
        ]
        
        super().__init__(parent, api, "clientes", columns, filters, client_mode)
        
        if client_mode:
            # Cargar solo el perfil del cliente actual
            self._load_my_profile()
    
    def _load_my_profile(self):
        """Carga el perfil del cliente actual"""
        result = self.api.get_cliente_by_id(self.api.user_id)
        if result.get("success"):
            self.data = [result.get("data")]
            self.table.set_data(self.data)
    
    def _get_form_fields(self) -> list:
        """Retorna los campos del formulario"""
        return [
            {"name": "nombre", "label": "Nombre", "type": "text", "required": True},
            {"name": "apellidos", "label": "Apellidos", "type": "text", "required": True},
            {"name": "email", "label": "Email", "type": "email", "required": True},
            {"name": "telefono", "label": "Teléfono", "type": "phone", "required": False},
            {"name": "direccion", "label": "Dirección", "type": "text", "required": False},
        ]
    
    def _show_form(self, item: Optional[Dict]):
        """Muestra el formulario de cliente"""
        form_window = tk.Toplevel(self)
        form_window.title("Nuevo Cliente" if not item else "Editar Cliente")
        form_window.geometry("500x400")
        form_window.transient(self.winfo_toplevel())
        form_window.grab_set()
        
        # Centrar ventana
        form_window.update_idletasks()
        x = (form_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (form_window.winfo_screenheight() // 2) - (400 // 2)
        form_window.geometry(f"500x400+{x}+{y}")
        
        # Frame principal
        main_frame = ttk.Frame(form_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        fields = {}
        form_fields = self._get_form_fields()
        
        # Crear campos
        for i, field_config in enumerate(form_fields):
            label = ttk.Label(main_frame, text=field_config["label"] + ":")
            label.grid(row=i, column=0, sticky="w", pady=5, padx=5)
            
            if field_config["type"] == "email":
                entry = ValidatedEntry(main_frame, validation_type="email", 
                                     required=field_config.get("required", False),
                                     width=40)
            elif field_config["type"] == "phone":
                entry = ValidatedEntry(main_frame, validation_type="phone", 
                                     required=field_config.get("required", False),
                                     width=40)
            else:
                entry = ValidatedEntry(main_frame, validation_type="text", 
                                     required=field_config.get("required", False),
                                     width=40)
            
            entry.grid(row=i, column=1, pady=5, padx=5, sticky="ew")
            
            # Cargar valor si existe
            if item and field_config["name"] in item:
                entry.set_value(item[field_config["name"]])
            
            fields[field_config["name"]] = entry
        
        main_frame.columnconfigure(1, weight=1)
        
        # Botones
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=len(form_fields), column=0, columnspan=2, pady=20)
        
        def save():
            # Validar campos
            data = {}
            for name, entry in fields.items():
                if not entry.validate_input():
                    messagebox.showerror("Error", f"El campo {name} no es válido")
                    return
                value = entry.get_value()
                if value:
                    data[name] = value
            
            # Guardar
            if item:
                result = self.api.update("clientes", item["id"], data)
            else:
                result = self.api.create("clientes", data)
            
            if result.get("success"):
                messagebox.showinfo("Éxito", "Cliente guardado correctamente")
                form_window.destroy()
                self._load_data()
            else:
                messagebox.showerror("Error", f"Error al guardar: {result.get('error')}")
        
        ttk.Button(buttons_frame, text="Guardar", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Cancelar", command=form_window.destroy).pack(side=tk.LEFT, padx=5)

