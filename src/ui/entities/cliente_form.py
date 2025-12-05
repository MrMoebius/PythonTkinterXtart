"""
Formulario reutilizable para crear/editar clientes
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional, Callable
import logging

from src.widgets.validated_entry import ValidatedEntry

logger = logging.getLogger(__name__)


def abrir_formulario_cliente(
    parent,
    api,
    item: Optional[Dict] = None,
    titulo: str = None,
    tipo_cliente_fijo: Optional[str] = None,
    on_success: Optional[Callable[[Dict], None]] = None,
    empleado_responsable: Optional[int] = None,
    exclude_fields: Optional[list] = None
):
    """
    Abre un formulario modal para crear o editar un cliente.
    
    Args:
        parent: Ventana padre (tkinter widget)
        api: Instancia de RESTClient para hacer llamadas al backend
        item: Diccionario con datos del cliente a editar (None para crear nuevo)
        titulo: Título de la ventana (por defecto "Nuevo Cliente" o "Editar Cliente")
        tipo_cliente_fijo: Si se especifica ("PARTICULAR" o "EMPRESA"), el tipo no se puede cambiar
        on_success: Callback que se ejecuta cuando el cliente se guarda exitosamente.
                   Recibe el diccionario del cliente creado/actualizado.
        empleado_responsable: ID del empleado responsable (se asigna automáticamente si no se especifica)
    
    Returns:
        None (la ventana se maneja internamente)
    """
    
    if item is not None and not isinstance(item, dict):
        logger.error(f"Error: item debe ser un diccionario o None, pero recibió: {type(item)}")
        messagebox.showerror("Error", f"Error al cargar datos del formulario: tipo inesperado {type(item)}")
        return

    form_window = tk.Toplevel(parent)
    form_window.title(titulo or ("Nuevo Cliente" if item is None else "Editar Cliente"))
    form_window.geometry("600x300")
    form_window.transient(parent.winfo_toplevel() if hasattr(parent, 'winfo_toplevel') else parent)
    form_window.grab_set()

    # Centrar
    form_window.update_idletasks()
    x = (form_window.winfo_screenwidth() // 2) - 300
    y = (form_window.winfo_screenheight() // 2) - 160
    form_window.geometry(f"600x300+{x}+{y}")

    # Frame principal
    main = ttk.Frame(form_window, padding=15)
    main.pack(fill=tk.BOTH, expand=True)

    fields = {}
    
    # Definición de campos
    form_fields = [
        {"name": "nombre", "label": "Nombre Completo", "type": "text", "required": True},
        {"name": "email", "label": "Email", "type": "email", "required": False},
        {"name": "telefono", "label": "Teléfono", "type": "phone"},
    ]
    
    # Agregar campo de tipo_cliente solo si no está fijo o si se está editando
    if tipo_cliente_fijo is None or item is not None:
        form_fields.append({
            "name": "tipo_cliente",
            "label": "Tipo Cliente",
            "type": "select",
            "options": ["PARTICULAR", "EMPRESA"],
            "required": False
        })
    
    # Filtrar campos excluidos
    exclude_fields = exclude_fields or []
    form_fields = [f for f in form_fields if f["name"] not in exclude_fields]

    # Crear campos
    for i, field in enumerate(form_fields):
        ttk.Label(main, text=field["label"] + ":").grid(
            row=i, column=0, sticky="w", pady=4, padx=5
        )

        field_type = field.get("type", "text")
        
        if field_type == "select":
            entry = ttk.Combobox(main, state="readonly", width=30)
            options = field.get("options", [])
            entry["values"] = options
            if options:
                entry.current(0)
        else:
            entry = ValidatedEntry(
                main,
                validation_type=field_type,
                required=field.get("required", False),
                width=30,
            )

        entry.grid(row=i, column=1, padx=5, pady=4, sticky="ew")

        # Rellenar si se está editando
        if item and isinstance(item, dict):
            field_name = field["name"]
            if field_name in item:
                value = item[field_name]
                if value is not None:
                    if field_type == "select":
                        # Normalizar valor para comparación
                        value_str = str(value).strip()
                        options = field.get("options", [])
                        # Buscar coincidencia (case-insensitive)
                        for opt in options:
                            if opt.lower() == value_str.lower():
                                entry.set(opt)
                                break
                        else:
                            if options:
                                entry.current(0)
                    else:
                        if hasattr(entry, "set_value"):
                            entry.set_value(str(value))
                        else:
                            entry.delete(0, tk.END)
                            entry.insert(0, str(value))

        fields[field["name"]] = entry

    main.columnconfigure(1, weight=1)

    # Botones
    btns = ttk.Frame(main)
    btns.grid(row=len(form_fields), column=0, columnspan=2, pady=15)

    def save():
        data = {}
        exclude_fields_list = exclude_fields or []

        # Validar y recoger datos
        for key, entry in fields.items():
            if isinstance(entry, ttk.Combobox):
                value = entry.get()
                if not value or not value.strip():
                    field_config = next((f for f in form_fields if f["name"] == key), {})
                    if field_config.get("required", False):
                        messagebox.showerror("Error", f"El campo '{field_config.get('label', key)}' es obligatorio.")
                        return
            else:
                if hasattr(entry, "validate_input") and not entry.validate_input():
                    messagebox.showerror("Error", f"El campo '{key}' no es válido.")
                    return
                value = entry.get_value() if hasattr(entry, "get_value") else entry.get()
            
            # Solo enviar campos que tienen valor y que el backend acepta
            # No enviar campos excluidos
            if value and str(value).strip() and key in ["nombre", "email", "telefono", "tipo_cliente"] and key not in exclude_fields_list:
                data[key] = str(value).strip()

        # Si tipo_cliente está fijo, agregarlo a los datos (normalizar a mayúsculas)
        if tipo_cliente_fijo:
            # Normalizar: "persona" -> "PARTICULAR", "empresa" -> "EMPRESA"
            tipo_normalizado = tipo_cliente_fijo.upper()
            if tipo_normalizado == "PERSONA":
                data["tipo_cliente"] = "PARTICULAR"
            else:
                data["tipo_cliente"] = tipo_normalizado

        # Crear o actualizar
        if item is None:
            # Validar que nombre esté presente (obligatorio)
            if not data.get("nombre"):
                messagebox.showerror("Error", "El campo 'Nombre' es obligatorio.")
                return
            
            # Asignar empleado responsable
            emp_id = empleado_responsable or getattr(api, "user_id", None)
            if emp_id:
                data["empleado_responsable"] = {"id_empleado": emp_id}
                logger.info(f"Empleado responsable asignado: {emp_id}")
            
            logger.info(f"Datos a enviar al backend: {data}")
            result = api.create("clientes", data)
            logger.info(f"Resultado del backend: {result}")
        else:
            # PUT: Actualización parcial
            update_data = data.copy()
            cliente_id = item.get("id_cliente") or item.get("id")
            if "id_cliente" not in update_data and cliente_id:
                update_data["id_cliente"] = cliente_id
            result = api.update("clientes", cliente_id, update_data)

        if result.get("success"):
            cliente_guardado = result.get("data", {})
            messagebox.showinfo("Éxito", "Cliente guardado correctamente.")
            
            # Ejecutar callback si existe
            if on_success and callable(on_success):
                try:
                    on_success(cliente_guardado)
                except Exception as e:
                    logger.error(f"Error en callback on_success: {e}")
            
            form_window.destroy()
        else:
            error_msg = result.get("error", "Error desconocido")
            if isinstance(error_msg, dict):
                error_msg = error_msg.get("error", str(error_msg))
            logger.error(f"Error al guardar cliente: {error_msg}")
            logger.error(f"Resultado completo: {result}")
            messagebox.showerror("Error", f"No se pudo guardar el cliente:\n{error_msg}")

    ttk.Button(btns, text="Guardar", command=save).pack(side=tk.LEFT, padx=5)
    ttk.Button(btns, text="Cancelar", command=form_window.destroy).pack(side=tk.LEFT, padx=5)
    
    # Permitir Enter para guardar
    form_window.bind("<Return>", lambda e: save())

