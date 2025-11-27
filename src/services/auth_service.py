"""
Servicio de autenticación
"""

from typing import Dict, Any, Optional
from src.api.rest_client import RESTClient


class AuthService:
    """Servicio para manejar autenticación"""
    
    def __init__(self, rest_client: RESTClient):
        """
        Args:
            rest_client: Cliente REST configurado
        """
        self.client = rest_client
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Autentica un usuario.
        
        Args:
            username: Nombre de usuario
            password: Contraseña
            
        Returns:
            Dict con 'success' y 'data' o 'error'
        """
        return self.client.login(username, password)
    
    def logout(self):
        """Cierra la sesión del usuario actual"""
        self.client.logout()
    
    def is_authenticated(self) -> bool:
        """Verifica si hay un usuario autenticado"""
        return self.client.token is not None
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Obtiene información del usuario actual"""
        if not self.is_authenticated():
            return None
        
        return {
            "id": self.client.user_id,
            "username": self.client.username,
            "rol": self.client.user_role,
        }
    
    def get_user_role(self) -> Optional[str]:
        """Obtiene el rol del usuario actual"""
        return self.client.user_role
    
    def get_user_id(self) -> Optional[int]:
        """Obtiene el ID del usuario actual"""
        return self.client.user_id

