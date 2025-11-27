"""
Modelo de datos para Factura
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class Factura:
    """Modelo de Factura que mapea con la entidad Java"""
    
    id: Optional[int] = None
    cliente_id: int = 0
    empleado_id: Optional[int] = None
    fecha: Optional[str] = None  # Formato: YYYY-MM-DD
    total: float = 0.0
    estado: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "Factura":
        """Crea una Factura desde un diccionario (JSON del backend)"""
        return cls(
            id=data.get("id"),
            cliente_id=int(data.get("cliente_id", 0)),
            empleado_id=data.get("empleado_id"),
            fecha=data.get("fecha"),
            total=float(data.get("total", 0.0)),
            estado=data.get("estado"),
        )
    
    def to_dict(self) -> dict:
        """Convierte la Factura a diccionario para enviar al backend"""
        result = {
            "cliente_id": self.cliente_id,
            "total": self.total,
        }
        
        if self.empleado_id is not None:
            result["empleado_id"] = self.empleado_id
        if self.fecha is not None:
            result["fecha"] = self.fecha
        if self.estado is not None:
            result["estado"] = self.estado
        if self.id is not None:
            result["id"] = self.id
            
        return result

