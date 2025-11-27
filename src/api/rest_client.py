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

            if response.status_code != 200:
                error_msg = response.text or f"Error HTTP {response.status_code}"
                logger.error(f"Error en login: {error_msg}")
                return {"success": False, "error": error_msg}

            data = response.json()

            # Guardar sesión interna
            self.token = data.get("token")
            self.user_role = data.get("rol", "").upper()
            self.user_id = data.get("id")
            self.username = data.get("username", username)

            if self.token:
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                logger.info(f"Login exitoso para {username} (rol: {self.user_role})")
            else:
                logger.warning("Login exitoso pero no se recibió token")

            return {"success": True, "data": data}

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
                    data = response.json() if response.content else None
                    return {"success": True, "data": data}
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
        """Obtiene un registro por ID"""
        endpoint = f"/{entity}/{entity_id}"
        return self._request("GET", endpoint)

    def create(self, entity: str, payload: Dict) -> Dict[str, Any]:
        """Crea un nuevo registro"""
        return self._request("POST", f"/{entity}", json=payload)

    def update(self, entity: str, entity_id: int, payload: Dict) -> Dict[str, Any]:
        """Actualiza un registro existente"""
        endpoint = f"/{entity}/{entity_id}"
        return self._request("PUT", endpoint, json=payload)

    def delete(self, entity: str, entity_id: int) -> Dict[str, Any]:
        """Elimina un registro"""
        endpoint = f"/{entity}/{entity_id}"
        return self._request("DELETE", endpoint)
