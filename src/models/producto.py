"""
Modelo de datos para Producto
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Producto:
    """Modelo de Producto que mapea con la entidad Java"""
    
    id: Optional[int] = None
    nombre: str = ""
    descripcion: Optional[str] = None
    precio: float = 0.0
    stock: int = 0
    
    @classmethod
    def from_dict(cls, data: dict) -> "Producto":
        """Crea un Producto desde un diccionario (JSON del backend)"""
        return cls(
            id=data.get("id"),
            nombre=data.get("nombre", ""),
            descripcion=data.get("descripcion"),
            precio=float(data.get("precio", 0.0)),
            stock=int(data.get("stock", 0)),
        )
    
    def to_dict(self) -> dict:
        """Convierte el Producto a diccionario para enviar al backend"""
        result = {
            "nombre": self.nombre,
            "precio": self.precio,
            "stock": self.stock,
        }
        
        if self.descripcion is not None:
            result["descripcion"] = self.descripcion
        if self.id is not None:
            result["id"] = self.id
            
        return result

