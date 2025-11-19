"""
Cliente REST para comunicación con el backend Java
"""

import requests
import json
from typing import Dict, List, Optional, Any
from enum import Enum

class UserRole(Enum):
    """Roles de usuario del sistema"""
    EMPLEADO = "EMPLEADO"
    CLIENTE = "CLIENTE"

class RESTClient:
    """Cliente para comunicación con la API REST del backend"""
    
    BASE_URL = "http://localhost:8080/democrudapi"
    
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_role = None
        self.user_id = None
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Autentica al usuario en el sistema
        
        Args:
            username: Nombre de usuario
            password: Contraseña
            
        Returns:
            Dict con información del usuario y token si es exitoso
        """
        try:
            response = self.session.post(
                f"{self.BASE_URL}/auth/login",
                json={"username": username, "password": password},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                self.user_role = UserRole.EMPLEADO if data.get("rol") == "EMPLEADO" else UserRole.CLIENTE
                self.user_id = data.get("id")
                
                # Configurar token en headers para futuras peticiones
                if self.token:
                    self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                
                return {"success": True, "data": data}
            else:
                return {"success": False, "error": response.text}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "No se pudo conectar con el servidor"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def logout(self):
        """Cierra la sesión del usuario"""
        self.token = None
        self.user_role = None
        self.user_id = None
        self.session.headers.pop("Authorization", None)
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Realiza una petición HTTP al backend
        
        Args:
            method: Método HTTP (GET, POST, PUT, DELETE)
            endpoint: Endpoint relativo (ej: "/clientes")
            **kwargs: Argumentos adicionales para requests
            
        Returns:
            Dict con la respuesta
        """
        try:
            url = f"{self.BASE_URL}{endpoint}"
            response = self.session.request(method, url, **kwargs)
            
            if response.status_code in [200, 201]:
                try:
                    return {"success": True, "data": response.json()}
                except:
                    return {"success": True, "data": response.text}
            elif response.status_code == 204:
                return {"success": True, "data": None}
            else:
                return {"success": False, "error": response.text, "status": response.status_code}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "No se pudo conectar con el servidor"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Métodos genéricos CRUD
    def get_all(self, entity: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Obtiene todos los registros de una entidad"""
        return self._make_request("GET", f"/{entity}", params=params)
    
    def get_by_id(self, entity: str, entity_id: int) -> Dict[str, Any]:
        """Obtiene un registro por ID"""
        return self._make_request("GET", f"/{entity}/{entity_id}")
    
    def create(self, entity: str, data: Dict) -> Dict[str, Any]:
        """Crea un nuevo registro"""
        return self._make_request("POST", f"/{entity}", json=data)
    
    def update(self, entity: str, entity_id: int, data: Dict) -> Dict[str, Any]:
        """Actualiza un registro existente"""
        return self._make_request("PUT", f"/{entity}/{entity_id}", json=data)
    
    def delete(self, entity: str, entity_id: int) -> Dict[str, Any]:
        """Elimina un registro"""
        return self._make_request("DELETE", f"/{entity}/{entity_id}")
    
    # Métodos específicos por entidad
    def get_roles_empleado(self) -> Dict[str, Any]:
        """Obtiene todos los roles de empleado"""
        return self.get_all("roles_empleado")
    
    def get_empleados(self) -> Dict[str, Any]:
        """Obtiene todos los empleados"""
        return self.get_all("empleados")
    
    def get_clientes(self) -> Dict[str, Any]:
        """Obtiene todos los clientes"""
        return self.get_all("clientes")
    
    def get_cliente_by_id(self, cliente_id: int) -> Dict[str, Any]:
        """Obtiene un cliente por ID"""
        return self.get_by_id("clientes", cliente_id)
    
    def get_productos(self) -> Dict[str, Any]:
        """Obtiene todos los productos"""
        return self.get_all("productos")
    
    def get_presupuestos(self) -> Dict[str, Any]:
        """Obtiene todos los presupuestos"""
        return self.get_all("presupuestos")
    
    def get_facturas(self) -> Dict[str, Any]:
        """Obtiene todas las facturas"""
        return self.get_all("facturas")
    
    def get_factura_productos(self, factura_id: Optional[int] = None) -> Dict[str, Any]:
        """Obtiene los productos de facturas"""
        if factura_id:
            return self.get_all("factura_productos", params={"factura_id": factura_id})
        return self.get_all("factura_productos")
    
    def get_pagos(self) -> Dict[str, Any]:
        """Obtiene todos los pagos"""
        return self.get_all("pagos")
    
    def get_my_facturas(self) -> Dict[str, Any]:
        """Obtiene las facturas del cliente actual"""
        return self.get_all("facturas", params={"cliente_id": self.user_id})
    
    def get_my_pagos(self) -> Dict[str, Any]:
        """Obtiene los pagos del cliente actual"""
        return self.get_all("pagos", params={"cliente_id": self.user_id})
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas para el dashboard"""
        stats = {}
        
        # Contar entidades
        for entity in ["clientes", "empleados", "productos", "presupuestos", "facturas", "pagos"]:
            result = self.get_all(entity)
            if result["success"]:
                stats[entity] = len(result["data"]) if isinstance(result["data"], list) else 0
        
        return {"success": True, "data": stats}

