"""
Modelo de datos para Cliente
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Cliente:
    """Modelo de Cliente que mapea con la entidad Java"""
    
    id: Optional[int] = None
    nombre: str = ""
    apellidos: str = ""
    email: str = ""
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "Cliente":
        """
        Crea un Cliente desde un diccionario (JSON del backend)
        
        El backend Java usa 'id_cliente' en lugar de 'id'
        """
        # El backend Java devuelve 'id_cliente', pero el modelo usa 'id'
        cliente_id = data.get("id_cliente") or data.get("id")
        
        return cls(
            id=cliente_id,
            nombre=data.get("nombre", ""),
            apellidos=data.get("apellidos", ""),
            email=data.get("email", ""),
            telefono=data.get("telefono"),
            direccion=data.get("direccion"),
        )
    
    def to_dict(self) -> dict:
        """
        Convierte el Cliente a diccionario para enviar al backend
        
        Nota: El backend Java espera 'id_cliente' para PUT, pero NO debe enviarse en POST.
        Solo se envían los campos que el usuario modifica (actualización parcial en PUT).
        """
        result = {}
        
        # Campos básicos (siempre se envían si tienen valor)
        if self.nombre:
            result["nombre"] = self.nombre
        
        # Para PUT, se envía id_cliente si existe
        if self.id is not None:
            result["id_cliente"] = self.id
        
        # Campos opcionales (solo si tienen valor)
        if self.email:
            result["email"] = self.email
        if self.telefono is not None:
            result["telefono"] = self.telefono
        if self.direccion is not None:
            result["direccion"] = self.direccion
        
        # NO enviar: password (se asigna automáticamente), fecha_alta (se asigna automáticamente)
        # NO enviar: empleado_responsable (se ignora)
            
        return result

