"""
Ventana de gestión de empleados
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional
from src.api.rest_client import RESTClient
from src.ui.entities.base_crud_window import BaseCRUDWindow
from src.components.validated_entry import ValidatedEntry

class EmpleadosWindow(BaseCRUDWindow):
    """Ventana para gestionar empleados"""
    
    def __init__(self, parent, api: RESTClient):
        columns = [
            {"name": "id", "width": 50, "anchor": "center"},
            {"name": "nombre", "width": 150},
            {"name": "apellidos", "width": 150},
            {"name": "email", "width": 200},
            {"name": "telefono", "width": 120},
            {"name": "rol_empleado", "width": 150},
        ]
        
        filters = [
            {"name": "nombre", "type": "text", "label": "Nombre"},
            {"name": "email", "type": "text", "label": "Email"},
            {"name": "rol_empleado", "type": "text", "label": "Rol"},
        ]
        
        super().__init__(parent, api, "empleados", columns, filters)
        
        # Cargar roles para el formulario
        self.roles = []
        self._load_roles()
    
    def _load_roles(self):
        """Carga los roles de empleado"""
        result = self.api.get_roles_empleado()
        if result.get("success"):
            self.roles = result.get("data", [])
    
    def _get_form_fields(self) -> list:
        """Retorna los campos del formulario"""
        return [
            {"name": "nombre", "label": "Nombre", "type": "text", "required": True},
            {"name": "apellidos", "label": "Apellidos", "type": "text", "required": True},
            {"name": "email", "label": "Email", "type": "email", "required": True},
            {"name": "telefono", "label": "Teléfono", "type": "phone", "required": False},
            {"name": "rol_empleado", "label": "Rol", "type": "select", "required": True},
        ]
    
    def _show_form(self, item: Optional[Dict]):
        """Muestra el formulario de empleado"""
        form_window = tk.Toplevel(self)
        form_window.title("Nuevo Empleado" if not item else "Editar Empleado")
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
                if field_config["name"] == "rol_empleado":
                    options = [r.get("nombre", "") for r in self.roles]
                    combo = ttk.Combobox(main_frame, values=options, width=37, state="readonly")
                    combo.grid(row=i, column=1, pady=5, padx=5, sticky="ew")
                    fields[field_config["name"]] = combo
                    
                    if item and field_config["name"] in item:
                        combo.set(str(item[field_config["name"]]))
            elif field_config["type"] == "email":
                entry = ValidatedEntry(main_frame, validation_type="email", 
                                     required=field_config.get("required", False),
                                     width=40)
                entry.grid(row=i, column=1, pady=5, padx=5, sticky="ew")
                fields[field_config["name"]] = entry
                
                if item and field_config["name"] in item:
                    entry.set_value(item[field_config["name"]])
            elif field_config["type"] == "phone":
                entry = ValidatedEntry(main_frame, validation_type="phone", 
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
                        data[name] = value
                elif isinstance(widget, ttk.Combobox):
                    value = widget.get()
                    if value:
                        # Buscar el ID del rol
                        for rol in self.roles:
                            if rol.get("nombre") == value:
                                data[name] = rol.get("id")
                                break
            
            # Guardar
            if item:
                result = self.api.update("empleados", item["id"], data)
            else:
                result = self.api.create("empleados", data)
            
            if result.get("success"):
                messagebox.showinfo("Éxito", "Empleado guardado correctamente")
                form_window.destroy()
                self._load_data()
            else:
                messagebox.showerror("Error", f"Error al guardar: {result.get('error')}")
        
        ttk.Button(buttons_frame, text="Guardar", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Cancelar", command=form_window.destroy).pack(side=tk.LEFT, padx=5)

