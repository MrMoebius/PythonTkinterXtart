"""
Modelo de datos para FacturaDetalle (detalle de factura)
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class FacturaDetalle:
    """Modelo de FacturaDetalle que mapea con la entidad Java"""
    
    id: Optional[int] = None
    factura_id: int = 0
    producto_id: int = 0
    cantidad: int = 0
    precio_unitario: float = 0.0
    subtotal: float = 0.0
    
    @classmethod
    def from_dict(cls, data: dict) -> "FacturaDetalle":
        """Crea un FacturaDetalle desde un diccionario (JSON del backend)"""
        return cls(
            id=data.get("id"),
            factura_id=int(data.get("factura_id", 0)),
            producto_id=int(data.get("producto_id", 0)),
            cantidad=int(data.get("cantidad", 0)),
            precio_unitario=float(data.get("precio_unitario", 0.0)),
            subtotal=float(data.get("subtotal", 0.0)),
        )
    
    def to_dict(self) -> dict:
        """Convierte el FacturaDetalle a diccionario para enviar al backend"""
        result = {
            "factura_id": self.factura_id,
            "producto_id": self.producto_id,
            "cantidad": self.cantidad,
            "precio_unitario": self.precio_unitario,
            "subtotal": self.subtotal,
        }
        
        if self.id is not None:
            result["id"] = self.id
            
        return result

