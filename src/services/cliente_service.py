"""
Servicio para gestión de clientes
"""

from typing import Dict, Any, List, Optional
from src.api.rest_client import RESTClient
from src.models.cliente import Cliente


class ClienteService:
    """Servicio para manejar operaciones CRUD de clientes"""
    
    def __init__(self, rest_client: RESTClient):
        """
        Args:
            rest_client: Cliente REST configurado
        """
        self.client = rest_client
    
    def get_all(self, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Obtiene todos los clientes.
        
        Args:
            filters: Filtros opcionales (ej: {"nombre": "Juan"})
            
        Returns:
            Dict con 'success' y 'data' (lista de Cliente) o 'error'
        """
        result = self.client.get_all("clientes", params=filters)
        
        if result.get("success") and result.get("data"):
            # Convertir a modelos Cliente
            clientes = [Cliente.from_dict(item) for item in result["data"]]
            return {"success": True, "data": clientes}
        
        return result
    
    def get_by_id(self, cliente_id: int) -> Dict[str, Any]:
        """
        Obtiene un cliente por ID.
        
        Args:
            cliente_id: ID del cliente
            
        Returns:
            Dict con 'success' y 'data' (Cliente) o 'error'
        """
        result = self.client.get_by_id("clientes", cliente_id)
        
        if result.get("success") and result.get("data"):
            cliente = Cliente.from_dict(result["data"])
            return {"success": True, "data": cliente}
        
        return result
    
    def create(self, cliente: Cliente) -> Dict[str, Any]:
        """
        Crea un nuevo cliente.
        
        Args:
            cliente: Instancia de Cliente
            
        Returns:
            Dict con 'success' y 'data' (Cliente creado) o 'error'
        """
        payload = cliente.to_dict()
        # Remover id si está presente (el backend lo genera)
        payload.pop("id", None)
        
        result = self.client.create("clientes", payload)
        
        if result.get("success") and result.get("data"):
            cliente_creado = Cliente.from_dict(result["data"])
            return {"success": True, "data": cliente_creado}
        
        return result
    
    def update(self, cliente_id: int, cliente: Cliente) -> Dict[str, Any]:
        """
        Actualiza un cliente existente.
        
        Args:
            cliente_id: ID del cliente a actualizar
            cliente: Instancia de Cliente con los datos actualizados
            
        Returns:
            Dict con 'success' y 'data' (Cliente actualizado) o 'error'
        """
        payload = cliente.to_dict()
        # Remover id del payload (va en la URL)
        payload.pop("id", None)
        
        result = self.client.update("clientes", cliente_id, payload)
        
        if result.get("success") and result.get("data"):
            cliente_actualizado = Cliente.from_dict(result["data"])
            return {"success": True, "data": cliente_actualizado}
        
        return result
    
    def delete(self, cliente_id: int) -> Dict[str, Any]:
        """
        Elimina un cliente.
        
        Args:
            cliente_id: ID del cliente a eliminar
            
        Returns:
            Dict con 'success' o 'error'
        """
        return self.client.delete("clientes", cliente_id)

