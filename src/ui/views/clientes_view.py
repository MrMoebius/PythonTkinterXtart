"""
Vista de gestión de clientes
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional

from src.ui.entities.base_crud_window import BaseCRUDWindow
from src.widgets.validated_entry import ValidatedEntry
from src.services.cliente_service import ClienteService
from src.models.cliente import Cliente


class ClientesView(BaseCRUDWindow):
    """Vista para gestionar clientes (Empleado/Admin) o perfil (Cliente)."""

    def __init__(self, parent, cliente_service: ClienteService, client_mode: bool = False):
        """
        Args:
            parent: Widget padre
            cliente_service: Servicio de clientes
            client_mode: True si es cliente final (solo su registro)
        """
        # Guardar servicio
        self.cliente_service = cliente_service
        
        # Columnas visibles en la tabla
        columns = [
            {"name": "id", "width": 60, "anchor": "center"},
            {"name": "nombre", "width": 150},
            {"name": "apellidos", "width": 150},
            {"name": "email", "width": 200},
            {"name": "telefono", "width": 130},
            {"name": "direccion", "width": 220},
        ]

        # Filtros → solo empleados/admin
        filters = [
            {"name": "nombre", "type": "text", "label": "Nombre"},
            {"name": "email", "type": "text", "label": "Email"},
            {"name": "telefono", "type": "text", "label": "Teléfono"},
        ] if not client_mode else []

        # Usar API directamente para BaseCRUDWindow (compatibilidad temporal)
        # En el futuro se puede refactorizar BaseCRUDWindow para usar servicios
        api_mock = type('obj', (object,), {
            'get_all': lambda entity, params=None: self._get_all_wrapper(params),
            'get_by_id': lambda entity, entity_id: self._get_by_id_wrapper(entity_id),
            'create': lambda entity, payload: self._create_wrapper(payload),
            'update': lambda entity, entity_id, payload: self._update_wrapper(entity_id, payload),
            'delete': lambda entity, entity_id: self._delete_wrapper(entity_id),
            'user_id': getattr(cliente_service.client, 'user_id', None),
        })()
        
        super().__init__(parent, api_mock, "clientes", columns, filters, client_mode)

    def _get_all_wrapper(self, params=None):
        """Wrapper para get_all usando servicio"""
        result = self.cliente_service.get_all(filters=params)
        if result.get("success"):
            # Convertir modelos a dicts para la tabla
            data = [self._model_to_dict(c) for c in result["data"]]
            return {"success": True, "data": data}
        return result

    def _get_by_id_wrapper(self, cliente_id):
        """Wrapper para get_by_id usando servicio"""
        result = self.cliente_service.get_by_id(cliente_id)
        if result.get("success"):
            return {"success": True, "data": self._model_to_dict(result["data"])}
        return result

    def _create_wrapper(self, payload):
        """Wrapper para create usando servicio"""
        cliente = Cliente.from_dict(payload)
        result = self.cliente_service.create(cliente)
        if result.get("success"):
            return {"success": True, "data": self._model_to_dict(result["data"])}
        return result

    def _update_wrapper(self, cliente_id, payload):
        """Wrapper para update usando servicio"""
        cliente = Cliente.from_dict(payload)
        result = self.cliente_service.update(cliente_id, cliente)
        if result.get("success"):
            return {"success": True, "data": self._model_to_dict(result["data"])}
        return result

    def _delete_wrapper(self, cliente_id):
        """Wrapper para delete usando servicio"""
        return self.cliente_service.delete(cliente_id)

    def _model_to_dict(self, cliente: Cliente) -> Dict:
        """Convierte un modelo Cliente a dict para la tabla"""
        return {
            "id": cliente.id,
            "nombre": cliente.nombre,
            "apellidos": cliente.apellidos,
            "email": cliente.email,
            "telefono": cliente.telefono or "",
            "direccion": cliente.direccion or "",
        }

    def _get_form_fields(self) -> list:
        """Definición de los campos del formulario de clientes."""
        return [
            {"name": "nombre", "label": "Nombre", "type": "text", "required": True},
            {"name": "apellidos", "label": "Apellidos", "type": "text", "required": True},
            {"name": "email", "label": "Email", "type": "email", "required": True},
            {"name": "telefono", "label": "Teléfono", "type": "phone"},
            {"name": "direccion", "label": "Dirección", "type": "text"},
        ]

    def _on_select(self, item):
        pass

    def _show_form(self, item: Optional[Dict]):
        """Ventana de creación o edición de clientes."""

        form_window = tk.Toplevel(self)
        form_window.title("Nuevo Cliente" if item is None else "Editar Cliente")
        form_window.geometry("500x420")
        form_window.transient(self.winfo_toplevel())
        form_window.grab_set()

        # Centrar
        form_window.update_idletasks()
        x = (form_window.winfo_screenwidth() // 2) - 250
        y = (form_window.winfo_screenheight() // 2) - 210
        form_window.geometry(f"500x420+{x}+{y}")

        # Frame principal
        main = ttk.Frame(form_window, padding=20)
        main.pack(fill=tk.BOTH, expand=True)

        fields = {}
        form_fields = self._get_form_fields()

        # Crear campos
        for i, field in enumerate(form_fields):
            ttk.Label(main, text=field["label"] + ":").grid(
                row=i, column=0, sticky="w", pady=6, padx=5
            )

            entry = ValidatedEntry(
                main,
                validation_type=field["type"],
                required=field.get("required", False),
                width=40,
            )
            entry.grid(row=i, column=1, padx=5, pady=6, sticky="ew")

            # Rellenar si se está editando
            if item and field["name"] in item:
                entry.set_value(item[field["name"]])

            fields[field["name"]] = entry

        main.columnconfigure(1, weight=1)

        # Botones
        btns = ttk.Frame(main)
        btns.grid(row=len(form_fields), column=0, columnspan=2, pady=20)

        def save():
            data = {}

            # Validar y recoger datos
            for key, entry in fields.items():
                if not entry.validate_input():
                    messagebox.showerror("Error", f"El campo '{key}' no es válido.")
                    return

                value = entry.get_value()
                if value is not None:
                    data[key] = value

            # Crear o actualizar usando servicio
            if item is None:
                result = self._create_wrapper(data)
            else:
                result = self._update_wrapper(item["id"], data)

            if result.get("success"):
                messagebox.showinfo("Éxito", "Cliente guardado correctamente.")
                form_window.destroy()
                self._load_data()
            else:
                error_msg = result.get("error", "Error desconocido")
                messagebox.showerror("Error", f"No se pudo guardar:\n{error_msg}")

        ttk.Button(btns, text="Guardar", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="Cancelar", command=form_window.destroy).pack(side=tk.LEFT, padx=5)

