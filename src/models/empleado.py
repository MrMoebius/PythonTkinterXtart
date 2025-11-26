"""
Modelo de datos para Empleado
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Empleado:
    """Modelo de Empleado que mapea con la entidad Java"""
    
    id: Optional[int] = None
    nombre: str = ""
    apellidos: str = ""
    email: str = ""
    telefono: Optional[str] = None
    rol_id: Optional[int] = None
    username: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "Empleado":
        """Crea un Empleado desde un diccionario (JSON del backend)"""
        return cls(
            id=data.get("id"),
            nombre=data.get("nombre", ""),
            apellidos=data.get("apellidos", ""),
            email=data.get("email", ""),
            telefono=data.get("telefono"),
            rol_id=data.get("rol_id"),
            username=data.get("username"),
        )
    
    def to_dict(self) -> dict:
        """Convierte el Empleado a diccionario para enviar al backend"""
        result = {
            "nombre": self.nombre,
            "apellidos": self.apellidos,
            "email": self.email,
        }
        
        if self.telefono is not None:
            result["telefono"] = self.telefono
        if self.rol_id is not None:
            result["rol_id"] = self.rol_id
        if self.username is not None:
            result["username"] = self.username
        if self.id is not None:
            result["id"] = self.id
            
        return result

