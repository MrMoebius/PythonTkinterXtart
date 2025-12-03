"""
Ventana de gestión de clientes
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional
import json
import customtkinter as ctk

from src.ui.entities.base_crud_window import BaseCRUDWindow
from src.ui.entities.cliente_form import abrir_formulario_cliente


class ClientesWindow(BaseCRUDWindow):
    """Ventana para gestionar clientes (Empleado/Admin) o perfil (Cliente)."""

    def __init__(self, parent, api, client_mode: bool = False):

        # ---------------------------------------------------------
        # Columnas visibles en la tabla
        # ---------------------------------------------------------
        columns = [
            {"name": "id", "width": 60, "anchor": "center"},
            {"name": "nombre", "width": 200},
            {"name": "email", "width": 200},
            {"name": "telefono", "width": 130},
            {"name": "tipo_cliente", "width": 120},
            {"name": "fecha_alta", "width": 120},
        ]

        # ---------------------------------------------------------
        # Filtros → solo empleados/admin (controlado por BaseCRUD)
        # ---------------------------------------------------------
        filters = [
            {"name": "nombre", "type": "text", "label": "Nombre"},
            {"name": "email", "type": "text", "label": "Email"},
            {"name": "telefono", "type": "text", "label": "Teléfono"},
        ]

        super().__init__(parent, api, "clientes", columns, filters, client_mode)
        
        # En modo cliente, cargar datos automáticamente
        if client_mode:
            self.after(100, self._load_my_profile)

    # =====================================================================
    # VISTA DE PERFIL (MODO CLIENTE)
    # =====================================================================
    def _create_widgets(self):
        """Sobrescribe _create_widgets para modo cliente"""
        if self.client_mode:
            # Vista personalizada para cliente
            self._create_profile_view()
        else:
            # Vista normal para empleados/admin
            super()._create_widgets()
    
    def _create_profile_view(self):
        """Crea la vista elegante del perfil del cliente con diseño moderno"""
        # Frame principal con fondo oscuro
        main_frame = ctk.CTkFrame(self, fg_color="#23243a")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Contenedor centrado con padding
        container = ctk.CTkFrame(main_frame, fg_color="#23243a")
        container.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)
        
        # Frame interno centrado verticalmente
        inner_container = ctk.CTkFrame(container, fg_color="#23243a")
        inner_container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Título con estilo moderno
        title_label = ctk.CTkLabel(
            inner_container,
            text="Mi Perfil",
            font=("Arial", 36, "bold"),
            text_color="white"
        )
        title_label.pack(pady=(0, 20))
        
        # Frame para los datos del perfil con estilo elegante y bordes redondeados
        profile_frame = ctk.CTkFrame(
            inner_container, 
            fg_color="#29304a",
            corner_radius=20,
            border_width=0
        )
        profile_frame.pack(padx=20, pady=(10, 5))
        
        # Título de la sección dentro del frame
        section_title = ctk.CTkLabel(
            profile_frame,
            text="Datos Personales",
            font=("Arial", 18, "bold"),
            text_color="#ffffff"
        )
        section_title.pack(pady=(15, 15))
        
        # Labels para mostrar datos (se actualizarán en _load_my_profile)
        self.profile_labels = {}
        
        # Campos a mostrar con iconos visuales
        fields = [
            ("nombre", "Nombre Completo", "#4CAF50"),
            ("email", "Email", "#2196F3"),
            ("telefono", "Teléfono", "#FF9800"),
            ("fecha_alta", "Fecha de Alta", "#9C27B0")
        ]
        
        for i, (field_name, field_label, color) in enumerate(fields):
            # Frame para cada campo con estilo moderno
            field_container = ctk.CTkFrame(
                profile_frame,
                fg_color="#1e2330",
                corner_radius=12,
                border_width=1,
                border_color="#3a3f52"
            )
            field_container.pack(fill=tk.X, padx=30, pady=6)
            
            # Label del campo con color
            label_widget = ctk.CTkLabel(
                field_container,
                text=f"{field_label}:",
                font=("Arial", 13, "bold"),
                text_color=color,
                anchor="w"
            )
            label_widget.pack(side=tk.LEFT, padx=(20, 15), pady=10)
            
            # Valor del campo con estilo elegante
            value_label = ctk.CTkLabel(
                field_container,
                text="Cargando...",
                font=("Arial", 14),
                text_color="#e0e0e0",
                anchor="w"
            )
            value_label.pack(side=tk.LEFT, padx=(0, 20), pady=10)
            self.profile_labels[field_name] = value_label
        
        # Botón Editar con estilo moderno y gradiente
        btn_frame = ctk.CTkFrame(inner_container, fg_color="#23243a")
        btn_frame.pack(pady=15)
        
        self.btn_edit_profile = ctk.CTkButton(
            btn_frame,
            text="✏️ Editar Perfil",
            command=self._on_edit_profile,
            width=200,
            height=45,
            font=("Arial", 16, "bold"),
            fg_color="#4CAF50",
            hover_color="#45a049",
            corner_radius=12,
            border_width=0
        )
        self.btn_edit_profile.pack()
    
    def _load_my_profile(self):
        """Carga los datos del perfil del cliente automáticamente"""
        cliente_id = getattr(self.api, "user_id", None)
        if not cliente_id:
            messagebox.showerror("Error", "No se pudo identificar el cliente")
            return
        
        # Obtener datos del cliente
        result = self.api.get_clientes(cliente_id=cliente_id)
        
        if not result.get("success"):
            messagebox.showerror("Error", f"Error al cargar perfil: {result.get('error', 'Error desconocido')}")
            return
        
        data = result.get("data", [])
        
        # Si es una lista, tomar el primer elemento
        if isinstance(data, list) and data:
            cliente_data = data[0]
        elif isinstance(data, dict):
            cliente_data = data
        else:
            messagebox.showerror("Error", "No se encontraron datos del cliente")
            return
        
        # Guardar datos para edición
        self.cliente_data = cliente_data
        
        # Actualizar labels con formato elegante
        nombre_completo = cliente_data.get("nombre", "N/A")
        apellidos = cliente_data.get("apellidos", "")
        if apellidos:
            nombre_completo = f"{nombre_completo} {apellidos}".strip()
        
        email = cliente_data.get("email", "N/A")
        telefono = cliente_data.get("telefono", "N/A")
        fecha_alta = cliente_data.get("fecha_alta", "N/A")
        
        # Formatear fecha si está disponible
        if fecha_alta and fecha_alta != "N/A":
            try:
                from datetime import datetime
                if isinstance(fecha_alta, str):
                    # Intentar parsear formato YYYY-MM-DD
                    try:
                        fecha_obj = datetime.strptime(fecha_alta.split("T")[0], "%Y-%m-%d")
                        fecha_alta = fecha_obj.strftime("%d/%m/%Y")
                    except (ValueError, AttributeError):
                        pass  # Mantener el valor original si no se puede formatear
            except Exception:
                pass  # Mantener el valor original si no se puede formatear
        
        # Actualizar labels con estilo mejorado
        self.profile_labels["nombre"].configure(text=nombre_completo)
        self.profile_labels["email"].configure(text=email)
        self.profile_labels["telefono"].configure(text=telefono)
        self.profile_labels["fecha_alta"].configure(text=fecha_alta)
    
    def _on_edit_profile(self):
        """Abre el formulario de edición del perfil (sin fecha de alta)"""
        if not hasattr(self, "cliente_data"):
            messagebox.showwarning("Advertencia", "Cargue primero los datos del perfil")
            return
        
        def on_success(cliente_guardado):
            """Callback cuando el cliente se guarda exitosamente."""
            self._load_my_profile()
        
        # Abrir formulario sin permitir editar fecha de alta
        abrir_formulario_cliente(
            parent=self,
            api=self.api,
            item=self.cliente_data,
            on_success=on_success,
            exclude_fields=["fecha_alta"]  # No permitir editar fecha de alta
        )

    # =====================================================================
    # FORMULARIO: CREAR / EDITAR (MODO EMPLEADO/ADMIN)
    # =====================================================================
    def _on_select(self, item):
        pass    
    
    def _show_form(self, item: Optional[Dict]):
        """Ventana de creación o edición de clientes."""
        def on_success(cliente_guardado):
            """Callback cuando el cliente se guarda exitosamente."""
            self._load_data()
        
        abrir_formulario_cliente(
            parent=self,
            api=self.api,
            item=item,
            on_success=on_success
        )
