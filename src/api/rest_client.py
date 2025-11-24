"""
Cliente REST para comunicación con el backend Java
"""

import requests
from typing import Dict, Any
from enum import Enum


class UserRole(Enum):
    ADMIN = "ADMIN"
    EMPLEADO = "EMPLEADO"
    CLIENTE = "CLIENTE"


class RESTClient:
    """
    Cliente real para consumir la API Java Spring.
    Totalmente compatible con DemoClient.
    """

    BASE_URL = "http://localhost:8080/democrudapi"

    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_role = None
        self.user_id = None
        self.username = None

    # -----------------------------------------------------
    # LOGIN
    # -----------------------------------------------------
    def login(self, username: str, password: str) -> Dict[str, Any]:
        try:
            response = self.session.post(
                f"{self.BASE_URL}/auth/login",
                json={"username": username, "password": password},
                headers={"Content-Type": "application/json"}
            )

            if response.status_code != 200:
                return {"success": False, "error": response.text}

            data = response.json()

            # Guardar sesión interna
            self.token = data.get("token")
            self.user_role = data.get("rol", "").upper()
            self.user_id = data.get("id")
            self.username = data.get("username", username)

            if self.token:
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})

            return {"success": True, "data": data}

        except Exception as e:
            return {"success": False, "error": str(e)}

    # -----------------------------------------------------
    # LOGOUT
    # -----------------------------------------------------
    def logout(self):
        self.token = None
        self.user_role = None
        self.user_id = None
        self.username = None
        self.session.headers.pop("Authorization", None)

    # -----------------------------------------------------
    # PETICIÓN GENÉRICA
    # -----------------------------------------------------
    def _req(self, method, endpoint, **kwargs):
        try:
            url = f"{self.BASE_URL}{endpoint}"
            resp = self.session.request(method, url, **kwargs)

            if resp.status_code in (200, 201):
                return {"success": True, "data": resp.json()}

            if resp.status_code == 204:
                return {"success": True, "data": None}

            return {"success": False, "error": resp.text}

        except Exception as e:
            return {"success": False, "error": str(e)}

    # -----------------------------------------------------
    # CRUD GENÉRICO
    # -----------------------------------------------------
    def get_all(self, entity: str, params=None):
        return self._req("GET", f"/{entity}", params=params)

    def get_by_id(self, entity: str, entity_id: int):
        return self._req("GET", f"/{entity}/{entity_id}")

    def create(self, entity: str, payload: Dict):
        return self._req("POST", f"/{entity}", json=payload)

    def update(self, entity: str, entity_id: int, payload: Dict):
        return self._req("PUT", f"/{entity}/{entity_id}", json=payload)

    def delete(self, entity: str, entity_id: int):
        return self._req("DELETE", f"/{entity}/{entity_id}")

    # -----------------------------------------------------
    # ENDPOINTS ESPECÍFICOS (idénticos a DemoClient)
    # -----------------------------------------------------
    def get_roles_empleado(self): return self.get_all("roles_empleado")
    def get_empleados(self): return self.get_all("empleados")
    def get_clientes(self): return self.get_all("clientes")
    def get_cliente_by_id(self, cid): return self.get_by_id("clientes", cid)
    def get_productos(self): return self.get_all("productos")
    def get_presupuestos(self): return self.get_all("presupuestos")
    def get_facturas(self): return self.get_all("facturas")
    def get_factura_productos(self, fid=None): 
        return self.get_all("factura_productos", params={"factura_id": fid} if fid else None)
    def get_pagos(self): return self.get_all("pagos")
    def get_my_facturas(self): return self.get_all("facturas", params={"cliente_id": self.user_id})
    def get_my_pagos(self): return self.get_all("pagos", params={"cliente_id": self.user_id})

    def get_dashboard_stats(self):
        stats = {}
        for entity in ["clientes", "empleados", "productos", "presupuestos", "facturas", "pagos"]:
            result = self.get_all(entity)
            stats[entity] = len(result["data"]) if result["success"] else 0
        return {"success": True, "data": stats}
