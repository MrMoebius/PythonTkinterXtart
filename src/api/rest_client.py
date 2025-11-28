"""
Cliente REST profesional para comunicación con el backend Java/Jakarta
"""

import requests
import logging
from typing import Dict, Any, Optional
from enum import Enum

from src.api.endpoints import Endpoints
from src.utils.exceptions import APIError, AuthenticationError, NetworkError


# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserRole(Enum):
    """Roles de usuario"""
    ADMIN = "ADMIN"
    EMPLEADO = "EMPLEADO"
    CLIENTE = "CLIENTE"


class RESTClient:
    """
    Cliente REST profesional para consumir la API Java/Jakarta.
    Maneja errores, timeouts, logging y autenticación.
    """

    def __init__(self, base_url: Optional[str] = None, timeout: int = 30):
        """
        Args:
            base_url: URL base del backend (opcional, usa Endpoints.BASE_URL por defecto)
            timeout: Timeout en segundos para las peticiones
        """
        self.session = requests.Session()
        self.timeout = timeout
        self.token: Optional[str] = None
        self.user_role: Optional[str] = None
        self.user_id: Optional[int] = None
        self.username: Optional[str] = None
        
        if base_url:
            Endpoints.BASE_URL = base_url

    # -----------------------------------------------------
    # AUTENTICACIÓN
    # -----------------------------------------------------
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Autentica un usuario en el backend.
        
        Args:
            username: Nombre de usuario
            password: Contraseña
            
        Returns:
            Dict con 'success' y 'data' o 'error'
            
        Raises:
            AuthenticationError: Si las credenciales son inválidas
            NetworkError: Si hay problemas de conexión
        """
        try:
            url = Endpoints.build_url(Endpoints.AUTH_LOGIN)
            logger.info(f"Intentando login para usuario: {username}")
            logger.info(f"URL de login: {url}")
            
            response = self.session.post(
                url,
                json={"email": username, "password": password},
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )

            if response.status_code == 401:
                error_msg = "Credenciales inválidas"
                logger.warning(f"Login fallido para {username}: {error_msg}")
                return {"success": False, "error": error_msg}

            if response.status_code == 404:
                error_msg = f"Endpoint no encontrado (404). Verifique que el backend esté ejecutándose y la URL sea correcta.\nURL intentada: {url}\nBase URL: {Endpoints.BASE_URL}"
                logger.error(f"Error en login: {error_msg}")
                return {"success": False, "error": error_msg}

            if response.status_code != 200:
                error_msg = response.text or f"Error HTTP {response.status_code}"
                logger.error(f"Error en login (HTTP {response.status_code}): {error_msg}")
                logger.error(f"URL intentada: {url}")
                return {"success": False, "error": f"Error HTTP {response.status_code}: {error_msg[:200]}"}

            data = response.json()

            # El backend Java devuelve {"success": true, "data": {...}} para login
            # Extraer datos del usuario desde la respuesta
            user_data = data.get("data", data)  # Login usa "data", no "dataObj"
            
            # Guardar sesión interna
            # El backend Java usa sesiones HTTP (JSESSIONID), no tokens JWT
            self.token = user_data.get("token") or data.get("token")
            self.user_role = user_data.get("rol", "").upper()
            self.user_id = user_data.get("id")
            self.username = user_data.get("nombre", username)

            # El backend Java mantiene la sesión mediante cookies (JSESSIONID)
            # No necesitamos token para autenticación, la sesión HTTP se mantiene automáticamente
            if self.token:
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                logger.info(f"Login exitoso para {username} (rol: {self.user_role})")
            else:
                # El backend Java usa sesiones HTTP, no tokens
                # La sesión se mantiene mediante cookies automáticamente
                logger.info(f"Login exitoso para {username} (rol: {self.user_role}) - Sesión HTTP activa")

            return {"success": True, "data": user_data}

        except requests.exceptions.Timeout:
            error_msg = "Timeout al conectar con el servidor"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        except requests.exceptions.ConnectionError:
            error_msg = "No se pudo conectar con el servidor"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        except requests.exceptions.RequestException as e:
            error_msg = f"Error de red: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"Error inesperado: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"success": False, "error": error_msg}

    def logout(self):
        """Cierra la sesión del usuario"""
        if self.token:
            try:
                url = Endpoints.build_url(Endpoints.AUTH_LOGOUT)
                self.session.post(url, timeout=self.timeout)
            except Exception as e:
                logger.warning(f"Error al hacer logout en el servidor: {e}")
        
        self.token = None
        self.user_role = None
        self.user_id = None
        self.username = None
        self.session.headers.pop("Authorization", None)
        logger.info("Sesión cerrada")

    # -----------------------------------------------------
    # PETICIÓN GENÉRICA
    # -----------------------------------------------------
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Realiza una petición HTTP genérica.
        
        Args:
            method: Método HTTP (GET, POST, PUT, DELETE)
            endpoint: Endpoint relativo (ej: "/clientes")
            **kwargs: Argumentos adicionales para requests (json, params, etc.)
            
        Returns:
            Dict con 'success' y 'data' o 'error'
        """
        try:
            url = Endpoints.build_url(endpoint)
            logger.debug(f"{method} {url}")
            
            # Asegurar que el timeout esté en kwargs
            if "timeout" not in kwargs:
                kwargs["timeout"] = self.timeout
            
            response = self.session.request(method, url, **kwargs)

            # Respuestas exitosas
            if response.status_code in (200, 201):
                try:
                    json_data = response.json() if response.content else None
                    if json_data:
                        # El backend Java devuelve {"success": true, "dataObj": {...}}
                        # Convertir "dataObj" a "data" para mantener compatibilidad
                        if "dataObj" in json_data:
                            data_value = json_data.pop("dataObj")
                            json_data["data"] = data_value if data_value is not None else []
                        # Si ya tiene "data", mantenerlo
                        elif "data" not in json_data:
                            # Si no tiene "data" ni "dataObj", puede ser una lista directa
                            if isinstance(json_data, list):
                                return {"success": True, "data": json_data}
                            # Si solo tiene "success", el dataObj puede estar vacío
                            json_data["data"] = []
                    
                    # Extraer data de manera segura
                    if json_data:
                        data = json_data.get("data")
                        # Si data es None, devolver lista vacía para listas, None para objetos
                        if data is None and isinstance(json_data, dict) and "success" in json_data:
                            data = []
                        return {"success": True, "data": data}
                    return {"success": True, "data": None}
                except ValueError:
                    # Si no es JSON válido, devolver el texto
                    return {"success": True, "data": response.text}

            # Sin contenido (204)
            if response.status_code == 204:
                return {"success": True, "data": None}

            # Errores
            error_msg = response.text or f"Error HTTP {response.status_code}"
            logger.warning(f"Error {response.status_code} en {method} {endpoint}: {error_msg}")
            return {"success": False, "error": error_msg}

        except requests.exceptions.Timeout:
            error_msg = f"Timeout al realizar {method} {endpoint}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        except requests.exceptions.ConnectionError:
            error_msg = "No se pudo conectar con el servidor"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        except requests.exceptions.RequestException as e:
            error_msg = f"Error de red: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"Error inesperado: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"success": False, "error": error_msg}

    # -----------------------------------------------------
    # CRUD GENÉRICO
    # -----------------------------------------------------
    def get_all(self, entity: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Obtiene todos los registros de una entidad"""
        return self._request("GET", f"/{entity}", params=params)

    def get_by_id(self, entity: str, entity_id: int) -> Dict[str, Any]:
        """Obtiene un registro por ID usando query param (formato Java backend)"""
        # El backend Java usa query params: /clientes?id=1
        return self._request("GET", f"/{entity}", params={"id": entity_id})

    def create(self, entity: str, payload: Dict) -> Dict[str, Any]:
        """Crea un nuevo registro"""
        return self._request("POST", f"/{entity}", json=payload)

    def update(self, entity: str, entity_id: int, payload: Dict) -> Dict[str, Any]:
        """Actualiza un registro existente"""
        # El backend Java espera el ID en el payload para PUT
        # Mapeo de nombres de ID según el documento ANALISIS_SERVLETS.md
        id_mapping = {
            "clientes": "id_cliente",
            "empleados": "id_empleado",
            "productos": "id_producto",
            "facturas": "id_factura",
            "presupuestos": "id_Presupuesto",
            "pagos": "id_pago",
            "factura_productos": "id_factura_producto",
            "roles": "id_rol"
        }
        
        # Caso especial: PagosServlet usa query param id_pago
        if entity == "pagos":
            return self._request("PUT", f"/{entity}", json=payload, params={"id_pago": entity_id})
        
        # Para otros endpoints, agregar el ID al payload
        payload_with_id = payload.copy()
        id_key = id_mapping.get(entity, f"id_{entity[:-1]}" if entity.endswith("s") else f"id_{entity}")
        payload_with_id[id_key] = entity_id
        
        return self._request("PUT", f"/{entity}", json=payload_with_id)

    def delete(self, entity: str, entity_id: int) -> Dict[str, Any]:
        """Elimina un registro usando query param (formato Java backend)"""
        # El backend Java usa query params: /clientes?id=1
        return self._request("DELETE", f"/{entity}", params={"id": entity_id})
    
    # ---------------------------------------------------------
    # Dashboard Stats
    # ---------------------------------------------------------
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales para admin/empleado."""
        # El backend Java no tiene endpoint de dashboard/stats
        # Calculamos las estadísticas desde los endpoints individuales
        try:
            stats = {}
            
            # Obtener conteos de cada entidad
            clientes_res = self.get_all("clientes")
            if clientes_res.get("success"):
                clientes_data = clientes_res.get("data", [])
                stats["clientes"] = len(clientes_data) if isinstance(clientes_data, list) else 0
            
            empleados_res = self.get_all("empleados")
            if empleados_res.get("success"):
                empleados_data = empleados_res.get("data", [])
                stats["empleados"] = len(empleados_data) if isinstance(empleados_data, list) else 0
            
            productos_res = self.get_all("productos")
            if productos_res.get("success"):
                productos_data = productos_res.get("data", [])
                stats["productos"] = len(productos_data) if isinstance(productos_data, list) else 0
            
            presupuestos_res = self.get_all("presupuestos")
            if presupuestos_res.get("success"):
                presupuestos_data = presupuestos_res.get("data", [])
                stats["presupuestos"] = len(presupuestos_data) if isinstance(presupuestos_data, list) else 0
            
            facturas_res = self.get_all("facturas")
            if facturas_res.get("success"):
                facturas_data = facturas_res.get("data", [])
                stats["facturas"] = len(facturas_data) if isinstance(facturas_data, list) else 0
            
            pagos_res = self.get_all("pagos")
            if pagos_res.get("success"):
                pagos_data = pagos_res.get("data", [])
                stats["pagos"] = len(pagos_data) if isinstance(pagos_data, list) else 0
            
            return {"success": True, "data": stats}
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {"success": False, "data": {}}
    
    # ---------------------------------------------------------
    # Métodos para Dashboard de Cliente
    # ---------------------------------------------------------
    def get_my_facturas(self, cliente_id: Optional[int] = None) -> Dict[str, Any]:
        """Obtiene las facturas del cliente actual"""
        if cliente_id is None:
            cliente_id = self.user_id
        
        if cliente_id is None:
            return {"success": False, "error": "No se pudo identificar el cliente"}
        
        # Obtener todas las facturas y filtrar por cliente
        result = self.get_all("facturas")
        if result.get("success") and result.get("data"):
            facturas = result["data"]
            # Asegurar que facturas es una lista
            if not isinstance(facturas, list):
                facturas = []
            
            # Filtrar facturas del cliente
            # El backend Java devuelve facturas con cliente_pagador como objeto
            my_facturas = []
            for factura in facturas:
                if not isinstance(factura, dict):
                    continue
                cliente_pagador = factura.get("cliente_pagador", {})
                if isinstance(cliente_pagador, dict):
                    if cliente_pagador.get("id_cliente") == cliente_id:
                        my_facturas.append(factura)
                elif cliente_pagador == cliente_id:
                    my_facturas.append(factura)
            
            return {"success": True, "data": my_facturas}
        
        # Si no hay éxito o no hay data, devolver lista vacía
        return {"success": True, "data": []}
    
    def get_my_pagos(self, cliente_id: Optional[int] = None) -> Dict[str, Any]:
        """Obtiene los pagos del cliente actual"""
        if cliente_id is None:
            cliente_id = self.user_id
        
        if cliente_id is None:
            return {"success": False, "error": "No se pudo identificar el cliente"}
        
        # Obtener todas las facturas del cliente primero
        facturas_res = self.get_my_facturas(cliente_id)
        if not facturas_res.get("success"):
            return {"success": True, "data": []}
        
        facturas = facturas_res.get("data")
        # Asegurar que facturas es una lista
        if facturas is None:
            facturas = []
        elif not isinstance(facturas, list):
            facturas = []
        
        factura_ids = [f.get("id_factura") for f in facturas if isinstance(f, dict) and f.get("id_factura")]
        
        if not factura_ids:
            return {"success": True, "data": []}
        
        # Obtener todos los pagos y filtrar por facturas del cliente
        pagos_res = self.get_all("pagos")
        if pagos_res.get("success") and pagos_res.get("data"):
            pagos = pagos_res["data"]
            # Asegurar que pagos es una lista
            if not isinstance(pagos, list):
                pagos = []
            
            my_pagos = []
            for pago in pagos:
                if not isinstance(pago, dict):
                    continue
                factura = pago.get("factura", {})
                if isinstance(factura, dict):
                    if factura.get("id_factura") in factura_ids:
                        my_pagos.append(pago)
                elif factura in factura_ids:
                    my_pagos.append(pago)
            
            return {"success": True, "data": my_pagos}
        
        return {"success": True, "data": []}

