"""
Componente de entrada de texto con validación
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

class ValidatedEntry(ttk.Entry):
    """Entry con validación en tiempo real"""
    
    def __init__(self, parent, validation_type: str = "text", 
                 required: bool = False, max_length: Optional[int] = None,
                 validator: Optional[Callable] = None, **kwargs):
        """
        Args:
            parent: Widget padre
            validation_type: Tipo de validación (text, email, phone, date, number)
            required: Si el campo es obligatorio
            max_length: Longitud máxima permitida
            validator: Función de validación personalizada
        """
        self.validation_type = validation_type
        self.required = required
        self.max_length = max_length
        self.validator = validator
        self.is_valid = True
        
        # Variables para el estado visual
        self.valid_color = "#d4edda"
        self.invalid_color = "#f8d7da"
        self.normal_color = "white"
        
        super().__init__(parent, **kwargs)
        
        # Configurar estilo inválido si no existe
        try:
            style = ttk.Style()
            style.configure("Invalid.TEntry", 
                          fieldbackground="#f8d7da",
                          bordercolor="#dc3545")
        except:
            pass
        
        # Bind eventos
        self.bind("<KeyRelease>", self._on_key_release)
        self.bind("<FocusOut>", self._on_focus_out)
        self.bind("<FocusIn>", self._on_focus_in)
        
        self._update_visual_state()
    
    def _on_key_release(self, event):
        """Valida mientras el usuario escribe"""
        if self.max_length and len(self.get()) > self.max_length:
            self.delete(self.max_length, tk.END)
            return
        
        self.validate_input()
    
    def _on_focus_out(self, event):
        """Valida al perder el foco"""
        self.validate_input()
    
    def _on_focus_in(self, event):
        """Resetea el color al obtener el foco"""
        if self.is_valid:
            self.config(style="TEntry")
    
    def validate_input(self) -> bool:
        """Valida el contenido del campo"""
        value = self.get().strip()
        
        # Validar campo requerido
        if self.required and not value:
            self.is_valid = False
            self._update_visual_state()
            return False
        
        if not value and not self.required:
            self.is_valid = True
            self._update_visual_state()
            return True
        
        # Validación personalizada
        if self.validator:
            self.is_valid = self.validator(value)
            self._update_visual_state()
            return self.is_valid
        
        # Validaciones por tipo
        if self.validation_type == "email":
            self.is_valid = self._validate_email(value)
        elif self.validation_type == "phone":
            self.is_valid = self._validate_phone(value)
        elif self.validation_type == "date":
            self.is_valid = self._validate_date(value)
        elif self.validation_type == "number":
            self.is_valid = self._validate_number(value)
        else:
            self.is_valid = True
        
        self._update_visual_state()
        return self.is_valid
    
    def _validate_email(self, email: str) -> bool:
        """Valida formato de email"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _validate_phone(self, phone: str) -> bool:
        """Valida formato de teléfono"""
        import re
        # Acepta números con o sin espacios, guiones, paréntesis
        pattern = r'^[\d\s\-\(\)\+]{9,15}$'
        return bool(re.match(pattern, phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")))
    
    def _validate_date(self, date: str) -> bool:
        """Valida formato de fecha (YYYY-MM-DD)"""
        import re
        pattern = r'^\d{4}-\d{2}-\d{2}$'
        if not re.match(pattern, date):
            return False
        try:
            from datetime import datetime
            datetime.strptime(date, "%Y-%m-%d")
            return True
        except:
            return False
    
    def _validate_number(self, number: str) -> bool:
        """Valida que sea un número"""
        try:
            float(number)
            return True
        except:
            return False
    
    def _update_visual_state(self):
        """Actualiza el estado visual del campo"""
        if not self.is_valid:
            self.config(style="Invalid.TEntry")
        else:
            self.config(style="TEntry")
    
    def get_value(self):
        """Obtiene el valor validado"""
        return self.get().strip()
    
    def set_value(self, value):
        """Establece un valor"""
        self.delete(0, tk.END)
        self.insert(0, str(value) if value else "")
        self.validate_input()

