"""
Modelo de datos para Producto
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Producto:
    """Modelo de Producto que mapea con la entidad Java"""
    
    id: Optional[int] = None  # Se mapea desde id_producto del backend
    nombre: str = ""
    descripcion: Optional[str] = None
    categoria: Optional[str] = None
    precio: float = 0.0
    activo: bool = False
    
    @classmethod
    def from_dict(cls, data: dict) -> "Producto":
        """Crea un Producto desde un diccionario (JSON del backend)"""
        # El backend devuelve id_producto, lo mapeamos a id
        producto_id = data.get("id_producto") or data.get("id")
        
        # Normalizar activo (puede venir como boolean o string)
        activo = data.get("activo", False)
        if isinstance(activo, str):
            activo = activo.lower() in ("true", "1", "yes", "sí")
        elif activo is None:
            activo = False
        
        return cls(
            id=producto_id,
            nombre=data.get("nombre", ""),
            descripcion=data.get("descripcion"),
            categoria=data.get("categoria"),
            precio=float(data.get("precio", 0.0)),
            activo=bool(activo),
        )
    
    def to_dict(self) -> dict:
        """Convierte el Producto a diccionario para enviar al backend"""
        result = {
            "nombre": self.nombre,
        }
        
        if self.descripcion is not None:
            result["descripcion"] = self.descripcion
        if self.categoria is not None:
            result["categoria"] = self.categoria
        if self.precio is not None and self.precio >= 0:
            result["precio"] = self.precio
        if self.activo is not None:
            result["activo"] = self.activo
        if self.id is not None:
            # Para PUT, el backend espera id_producto
            result["id_producto"] = self.id
            
        return result

