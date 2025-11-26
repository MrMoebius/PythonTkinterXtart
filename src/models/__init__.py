"""
Modelos de datos para la aplicación
"""

from .cliente import Cliente
from .empleado import Empleado
from .producto import Producto
from .factura import Factura
from .factura_detalle import FacturaDetalle

__all__ = [
    "Cliente",
    "Empleado",
    "Producto",
    "Factura",
    "FacturaDetalle",
]

