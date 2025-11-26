"""
Servicio para gestión de productos
"""

from typing import Dict, Any, Optional
from src.api.rest_client import RESTClient
from src.models.producto import Producto


class ProductoService:
    """Servicio para manejar operaciones CRUD de productos"""
    
    def __init__(self, rest_client: RESTClient):
        """
        Args:
            rest_client: Cliente REST configurado
        """
        self.client = rest_client
    
    def get_all(self, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Obtiene todos los productos.
        
        Args:
            filters: Filtros opcionales
            
        Returns:
            Dict con 'success' y 'data' (lista de Producto) o 'error'
        """
        result = self.client.get_all("productos", params=filters)
        
        if result.get("success") and result.get("data"):
            productos = [Producto.from_dict(item) for item in result["data"]]
            return {"success": True, "data": productos}
        
        return result
    
    def get_by_id(self, producto_id: int) -> Dict[str, Any]:
        """Obtiene un producto por ID"""
        result = self.client.get_by_id("productos", producto_id)
        
        if result.get("success") and result.get("data"):
            producto = Producto.from_dict(result["data"])
            return {"success": True, "data": producto}
        
        return result
    
    def create(self, producto: Producto) -> Dict[str, Any]:
        """Crea un nuevo producto"""
        payload = producto.to_dict()
        payload.pop("id", None)
        
        result = self.client.create("productos", payload)
        
        if result.get("success") and result.get("data"):
            producto_creado = Producto.from_dict(result["data"])
            return {"success": True, "data": producto_creado}
        
        return result
    
    def update(self, producto_id: int, producto: Producto) -> Dict[str, Any]:
        """Actualiza un producto existente"""
        payload = producto.to_dict()
        payload.pop("id", None)
        
        result = self.client.update("productos", producto_id, payload)
        
        if result.get("success") and result.get("data"):
            producto_actualizado = Producto.from_dict(result["data"])
            return {"success": True, "data": producto_actualizado}
        
        return result
    
    def delete(self, producto_id: int) -> Dict[str, Any]:
        """Elimina un producto"""
        return self.client.delete("productos", producto_id)

