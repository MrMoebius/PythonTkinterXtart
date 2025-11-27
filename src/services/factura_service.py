"""
Servicio para gestión de facturas
"""

from typing import Dict, Any, Optional
from src.api.rest_client import RESTClient
from src.models.factura import Factura
from src.models.factura_detalle import FacturaDetalle


class FacturaService:
    """Servicio para manejar operaciones CRUD de facturas"""
    
    def __init__(self, rest_client: RESTClient):
        """
        Args:
            rest_client: Cliente REST configurado
        """
        self.client = rest_client
    
    def get_all(self, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Obtiene todas las facturas.
        
        Args:
            filters: Filtros opcionales (ej: {"cliente_id": 1})
            
        Returns:
            Dict con 'success' y 'data' (lista de Factura) o 'error'
        """
        result = self.client.get_all("facturas", params=filters)
        
        if result.get("success") and result.get("data"):
            facturas = [Factura.from_dict(item) for item in result["data"]]
            return {"success": True, "data": facturas}
        
        return result
    
    def get_by_id(self, factura_id: int) -> Dict[str, Any]:
        """Obtiene una factura por ID"""
        result = self.client.get_by_id("facturas", factura_id)
        
        if result.get("success") and result.get("data"):
            factura = Factura.from_dict(result["data"])
            return {"success": True, "data": factura}
        
        return result
    
    def create(self, factura: Factura) -> Dict[str, Any]:
        """Crea una nueva factura"""
        payload = factura.to_dict()
        payload.pop("id", None)
        
        result = self.client.create("facturas", payload)
        
        if result.get("success") and result.get("data"):
            factura_creada = Factura.from_dict(result["data"])
            return {"success": True, "data": factura_creada}
        
        return result
    
    def update(self, factura_id: int, factura: Factura) -> Dict[str, Any]:
        """Actualiza una factura existente"""
        payload = factura.to_dict()
        payload.pop("id", None)
        
        result = self.client.update("facturas", factura_id, payload)
        
        if result.get("success") and result.get("data"):
            factura_actualizada = Factura.from_dict(result["data"])
            return {"success": True, "data": factura_actualizada}
        
        return result
    
    def delete(self, factura_id: int) -> Dict[str, Any]:
        """Elimina una factura"""
        return self.client.delete("facturas", factura_id)
    
    def get_detalles(self, factura_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Obtiene los detalles de factura (factura_productos).
        
        Args:
            factura_id: ID de factura (opcional, si se omite obtiene todos)
            
        Returns:
            Dict con 'success' y 'data' (lista de FacturaDetalle) o 'error'
        """
        params = {"factura_id": factura_id} if factura_id else None
        result = self.client.get_all("factura_productos", params=params)
        
        if result.get("success") and result.get("data"):
            detalles = [FacturaDetalle.from_dict(item) for item in result["data"]]
            return {"success": True, "data": detalles}
        
        return result
    
    def get_my_facturas(self, cliente_id: int) -> Dict[str, Any]:
        """Obtiene las facturas de un cliente específico"""
        return self.get_all(filters={"cliente_id": cliente_id})
    
    def get_presupuestos(self, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """Obtiene todos los presupuestos"""
        result = self.client.get_all("presupuestos", params=filters)
        
        if result.get("success") and result.get("data"):
            # Los presupuestos tienen la misma estructura que Factura
            presupuestos = [Factura.from_dict(item) for item in result["data"]]
            return {"success": True, "data": presupuestos}
        
        return result
    
    def get_pagos(self, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """Obtiene todos los pagos"""
        return self.client.get_all("pagos", params=filters)
    
    def get_my_pagos(self, cliente_id: int) -> Dict[str, Any]:
        """Obtiene los pagos de un cliente específico"""
        return self.get_pagos(filters={"cliente_id": cliente_id})
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas para el dashboard"""
        return self.client.get_all("dashboard/stats") if hasattr(self.client, 'get_all') else self.client.get_dashboard_stats()

