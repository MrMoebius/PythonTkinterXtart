"""
Servicio para gestión de empleados
"""

from typing import Dict, Any, Optional
from src.api.rest_client import RESTClient
from src.models.empleado import Empleado


class EmpleadoService:
    """Servicio para manejar operaciones CRUD de empleados"""
    
    def __init__(self, rest_client: RESTClient):
        """
        Args:
            rest_client: Cliente REST configurado
        """
        self.client = rest_client
    
    def get_all(self, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Obtiene todos los empleados.
        
        Args:
            filters: Filtros opcionales
            
        Returns:
            Dict con 'success' y 'data' (lista de Empleado) o 'error'
        """
        result = self.client.get_all("empleados", params=filters)
        
        if result.get("success") and result.get("data"):
            empleados = [Empleado.from_dict(item) for item in result["data"]]
            return {"success": True, "data": empleados}
        
        return result
    
    def get_by_id(self, empleado_id: int) -> Dict[str, Any]:
        """Obtiene un empleado por ID"""
        result = self.client.get_by_id("empleados", empleado_id)
        
        if result.get("success") and result.get("data"):
            empleado = Empleado.from_dict(result["data"])
            return {"success": True, "data": empleado}
        
        return result
    
    def create(self, empleado: Empleado) -> Dict[str, Any]:
        """Crea un nuevo empleado"""
        payload = empleado.to_dict()
        payload.pop("id", None)
        
        result = self.client.create("empleados", payload)
        
        if result.get("success") and result.get("data"):
            empleado_creado = Empleado.from_dict(result["data"])
            return {"success": True, "data": empleado_creado}
        
        return result
    
    def update(self, empleado_id: int, empleado: Empleado) -> Dict[str, Any]:
        """Actualiza un empleado existente"""
        payload = empleado.to_dict()
        payload.pop("id", None)
        
        result = self.client.update("empleados", empleado_id, payload)
        
        if result.get("success") and result.get("data"):
            empleado_actualizado = Empleado.from_dict(result["data"])
            return {"success": True, "data": empleado_actualizado}
        
        return result
    
    def delete(self, empleado_id: int) -> Dict[str, Any]:
        """Elimina un empleado"""
        return self.client.delete("empleados", empleado_id)
    
    def get_roles(self) -> Dict[str, Any]:
        """Obtiene todos los roles de empleado"""
        return self.client.get_all("roles_empleado")

