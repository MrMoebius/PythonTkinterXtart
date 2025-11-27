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
        """Crea un Cliente desde un diccionario (JSON del backend)"""
        return cls(
            id=data.get("id"),
            nombre=data.get("nombre", ""),
            apellidos=data.get("apellidos", ""),
            email=data.get("email", ""),
            telefono=data.get("telefono"),
            direccion=data.get("direccion"),
        )
    
    def to_dict(self) -> dict:
        """Convierte el Cliente a diccionario para enviar al backend"""
        result = {
            "nombre": self.nombre,
            "apellidos": self.apellidos,
            "email": self.email,
        }
        
        if self.telefono is not None:
            result["telefono"] = self.telefono
        if self.direccion is not None:
            result["direccion"] = self.direccion
        if self.id is not None:
            result["id"] = self.id
            
        return result

