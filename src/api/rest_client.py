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
        
        # Helper para métodos específicos
        from src.api.rest_helpers import RESTHelpers
        self.helpers = RESTHelpers(self)
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
            logger.info(f"Respuesta del backend (login): {data}")

            # El backend Java devuelve {"success": true, "data": {...}} para login
            # Extraer datos del usuario desde la respuesta
            user_data = data.get("data", data)  # Login usa "data", no "dataObj"
            
            logger.info(f"user_data extraído: {user_data}")
            
            # Normalizar estructura del backend Java a formato esperado
            # El backend Java devuelve: id_empleado, id_rol como objeto, etc.
            normalized_data = {}
            
            # ID: puede venir como id, id_empleado o id_cliente
            user_id = (
                user_data.get("id") or 
                user_data.get("id_empleado") or 
                user_data.get("id_cliente")
            )
            normalized_data["id"] = user_id
            
            # Rol: puede venir como rol (string) o id_rol (objeto con nombre_rol)
            rol_obj = user_data.get("id_rol")
            if isinstance(rol_obj, dict):
                # Si id_rol es un objeto, extraer nombre_rol
                normalized_data["rol"] = rol_obj.get("nombre_rol", "").upper()
            else:
                # Si viene como string directo
                normalized_data["rol"] = (user_data.get("rol") or "").upper()
            
            # Tipo: determinar si es empleado o cliente
            # Si tiene id_empleado, es empleado; si tiene id_cliente, es cliente
            if user_data.get("id_empleado"):
                normalized_data["tipo"] = "empleado"
            elif user_data.get("id_cliente"):
                normalized_data["tipo"] = "cliente"
            else:
                # Por defecto, si tiene rol, es empleado
                normalized_data["tipo"] = "empleado" if normalized_data.get("rol") else "cliente"
            
            # Copiar otros campos
            normalized_data["nombre"] = user_data.get("nombre", "")
            normalized_data["email"] = user_data.get("email", username)
            normalized_data["telefono"] = user_data.get("telefono", "")
            
            # Guardar sesión interna
            # El backend Java usa sesiones HTTP (JSESSIONID), no tokens JWT
            self.token = user_data.get("token") or data.get("token")
            self.user_role = normalized_data.get("rol", "").upper().strip()
            self.user_id = user_id  # Usar la variable directamente
            self.username = normalized_data.get("nombre", username)

            logger.info(f"user_id: {self.user_id}, user_role: {self.user_role}, username: {self.username}")
            logger.info(f"normalized_data: {normalized_data}")
            
            # Retornar datos normalizados
            user_data = normalized_data

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
        """Realiza una petición HTTP y devuelve siempre un dict {'success', 'data'|'error'}."""
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
                    logger.debug(f"Respuesta JSON cruda: {json_data}")
                    if json_data:
                        # El backend Java ahora devuelve {"success": true, "data": {...}} 
                        # o {"success": true, "dataObj": {...}} (formato antiguo)
                        # Priorizar "data" sobre "dataObj" para compatibilidad
                        if "data" in json_data:
                            data_value = json_data["data"]
                            logger.debug(f"data encontrado: {data_value} (type: {type(data_value)})")
                            # Si data es null, convertir a lista vacía (backend devuelve [] cuando no hay datos)
                            if data_value is None:
                                json_data["data"] = []
                                logger.debug("data era None, convertido a lista vacía []")
                        elif "dataObj" in json_data:
                            # Compatibilidad con formato antiguo
                            data_value = json_data.pop("dataObj")
                            logger.debug(f"dataObj extraído: {data_value} (type: {type(data_value)})")
                            if data_value is None:
                                json_data["data"] = []
                                logger.debug("dataObj era None, convertido a lista vacía []")
                            else:
                                json_data["data"] = data_value
                        # Si no tiene "data" ni "dataObj", puede ser una lista directa
                        elif isinstance(json_data, list):
                            return {"success": True, "data": json_data}
                        # Si solo tiene "success", el dataObj puede estar vacío
                        else:
                            json_data["data"] = []
                    
                    # Extraer data de manera segura
                    if json_data:
                        data = json_data.get("data")
                        logger.debug(f"Data extraída antes de validación: {data} (type: {type(data)})")
                        # Si data es None, devolver lista vacía para operaciones de lista
                        # (el backend Java devuelve null cuando no hay resultados)
                        if data is None:
                            data = []
                            logger.debug("Data era None, convertido a lista vacía []")
                        logger.debug(f"Data final: {data} (type: {type(data)})")
                        return {"success": True, "data": data}
                    return {"success": True, "data": []}
                except ValueError:
                    # Si no es JSON válido, devolver el texto
                    return {"success": True, "data": response.text}

            # Sin contenido (204)
            if response.status_code == 204:
                return {"success": True, "data": None}

            # Errores
            error_msg = response.text or f"Error HTTP {response.status_code}"

            # Para los informes, un 404 simplemente significa que el backend
            # aún no tiene esos endpoints. Lo tratamos como warning para no
            # asustar al usuario: el frontend usará datos demo.
            if endpoint.startswith("/informes/") and response.status_code == 404:
                logger.warning(
                    "Endpoint de informes no encontrado (%s). "
                    "Se usarán datos demo en la ventana de Informes.",
                    endpoint,
                )
            else:
                logger.error(f"Error {response.status_code} en {method} {endpoint}: {error_msg}")
            
            # Intentar extraer el mensaje de error del JSON si está disponible
            try:
                error_json = response.json()
                if isinstance(error_json, dict):
                    # El backend puede devolver {"success": false, "data": {"error": "..."}}
                    if "data" in error_json and isinstance(error_json["data"], dict):
                        error_msg = error_json["data"].get("error", error_msg)
                    elif "error" in error_json:
                        error_msg = error_json["error"]
            except:
                pass  # Si no es JSON, usar el texto original
            
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
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Realiza una petición GET genérica a cualquier endpoint.
        
        Args:
            endpoint: Endpoint relativo (ej: "/informes/ventas-empleado")
            params: Parámetros de consulta opcionales
            
        Returns:
            Dict con 'success' y 'data' o 'error'
        """
        return self._request("GET", endpoint, params=params)
    
    # -----------------------------------------------------
    # MÉTODOS ESPECÍFICOS POR ENTIDAD (con filtros)
    # -----------------------------------------------------
    def get_clientes(
        self, 
        cliente_id: Optional[int] = None,
        nombre: Optional[str] = None,
        email: Optional[str] = None,
        telefono: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtiene clientes con filtros opcionales.
        
        Args:
            cliente_id: ID específico (devuelve un solo cliente, tiene prioridad sobre filtros)
            nombre: Filtro por nombre (búsqueda parcial, case-insensitive)
            email: Filtro por email (búsqueda parcial, case-insensitive)
            telefono: Filtro por teléfono (búsqueda parcial)
            
        Returns:
            Dict con 'success' y 'data' (lista o objeto Cliente) o 'error'
            
        Ejemplos:
            # Todos los clientes
            api.get_clientes()
            
            # Por ID
            api.get_clientes(cliente_id=1)
            
            # Filtrar por nombre
            api.get_clientes(nombre="Juan")
            
            # Filtrar por email
            api.get_clientes(email="example.com")
            
            # Combinar filtros (AND)
            api.get_clientes(nombre="Juan", email="example")
        """
        params = {}
        
        # Si se especifica ID, tiene prioridad y se ignora el resto
        if cliente_id:
            params['id'] = cliente_id
        else:
            # Construir filtros opcionales
            if nombre:
                params['nombre'] = nombre
            if email:
                params['email'] = email
            if telefono:
                params['telefono'] = telefono
        
        logger.info(f"get_clientes - Parámetros: {params}")
        result = self._request("GET", "/clientes", params=params if params else None)
        logger.info(f"get_clientes - Resultado: success={result.get('success')}, data type={type(result.get('data'))}")
        return result

    def get_by_id(self, entity: str, entity_id: int) -> Dict[str, Any]:
        """Obtiene un registro por ID usando query param (formato Java backend)"""
        # El backend Java usa query params: /clientes?id=1
        return self._request("GET", f"/{entity}", params={"id": entity_id})

    def create(self, entity: str, payload: Dict) -> Dict[str, Any]:
        """Crea un nuevo registro"""
        logger.info(f"create({entity}) - Payload: {payload}")
        result = self._request("POST", f"/{entity}", json=payload)
        logger.info(f"create({entity}) - Resultado: success={result.get('success')}, error={result.get('error')}")
        logger.info(f"create({entity}) - Data recibida: {result.get('data')}")
        return result

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
        
        # Para otros endpoints, agregar el ID al payload solo si no está ya presente
        payload_with_id = payload.copy()
        id_key = id_mapping.get(entity, f"id_{entity[:-1]}" if entity.endswith("s") else f"id_{entity}")
        # Solo agregar si no está ya presente (evitar duplicación)
        if id_key not in payload_with_id:
            payload_with_id[id_key] = entity_id
        
        logger.info(f"update({entity}) - Payload final: {payload_with_id}")
        result = self._request("PUT", f"/{entity}", json=payload_with_id)
        logger.info(f"update({entity}) - Resultado: success={result.get('success')}, error={result.get('error')}")
        logger.info(f"update({entity}) - Data recibida: {result.get('data')}")
        return result

    def delete(self, entity: str, entity_id: int) -> Dict[str, Any]:
        """Elimina un registro usando query param (formato Java backend)"""
        # El backend Java usa query params: /clientes?id=1
        return self._request("DELETE", f"/{entity}", params={"id": entity_id})
    
    # ---------------------------------------------------------
    # Dashboard Stats
    # ---------------------------------------------------------
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales para admin/empleado."""
        return self.helpers.get_dashboard_stats()
    
    def get_my_facturas(self, cliente_id: Optional[int] = None) -> Dict[str, Any]:
        """Obtiene las facturas del cliente actual"""
        return self.helpers.get_my_facturas(cliente_id)
    
    def get_my_pagos(self, cliente_id: Optional[int] = None) -> Dict[str, Any]:
        """Obtiene los pagos del cliente actual"""
        return self.helpers.get_my_pagos(cliente_id)
    
    def get_roles_empleado(self) -> Dict[str, Any]:
        """Obtiene todos los roles de empleado."""
        return self.helpers.get_roles_empleado()

