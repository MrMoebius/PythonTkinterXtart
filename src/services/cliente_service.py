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
    
    def get_all(
        self, 
        filters: Optional[Dict] = None,
        nombre: Optional[str] = None,
        email: Optional[str] = None,
        telefono: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtiene todos los clientes con filtros opcionales.
        
        Args:
            filters: Filtros opcionales como dict (ej: {"nombre": "Juan"})
                    Si se proporciona, se usa este dict directamente
            nombre: Filtro por nombre (búsqueda parcial, case-insensitive)
            email: Filtro por email (búsqueda parcial, case-insensitive)
            telefono: Filtro por teléfono (búsqueda parcial)
            
        Returns:
            Dict con 'success' y 'data' (lista de Cliente) o 'error'
            
        Nota:
            Si se proporciona 'filters', se usa directamente.
            Si no, se construyen los filtros desde los parámetros individuales.
        """
        # Si se proporciona filters dict, usarlo directamente
        if filters:
            result = self.client.get_all("clientes", params=filters)
        else:
            # Usar el método específico con parámetros individuales
            result = self.client.get_clientes(
                nombre=nombre,
                email=email,
                telefono=telefono
            )
        
        if result.get("success") and result.get("data"):
            # Convertir a modelos Cliente
            clientes_data = result["data"]
            # Asegurar que es una lista
            if not isinstance(clientes_data, list):
                clientes_data = [clientes_data]
            clientes = [Cliente.from_dict(item) for item in clientes_data]
            return {"success": True, "data": clientes}
        
        return result
    
    def get_by_id(self, cliente_id: int) -> Dict[str, Any]:
        """
        Obtiene un cliente por ID.
        
        Args:
            cliente_id: ID del cliente
            
        Returns:
            Dict con 'success' y 'data' (Cliente) o 'error'
            
        Nota:
            El backend devuelve un objeto individual cuando se busca por ID,
            no un array. Si viene como array, se toma el primer elemento.
        """
        # Usar el método específico get_clientes con ID
        result = self.client.get_clientes(cliente_id=cliente_id)
        
        if result.get("success"):
            cliente_data = result.get("data")
            
            # El backend devuelve un objeto individual cuando se busca por ID
            # Si viene como array (por compatibilidad), tomar el primero
            if isinstance(cliente_data, list):
                if cliente_data:
                    cliente_data = cliente_data[0]
                else:
                    return {"success": False, "error": "Cliente no encontrado"}
            
            # Si es un objeto/diccionario, convertirlo a Cliente
            if cliente_data and isinstance(cliente_data, dict):
                cliente = Cliente.from_dict(cliente_data)
                return {"success": True, "data": cliente}
            elif cliente_data is None:
                return {"success": False, "error": "Cliente no encontrado"}
        
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

