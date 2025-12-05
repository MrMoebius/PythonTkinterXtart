"""
Excepciones personalizadas para la aplicación
"""


class APIError(Exception):
    """Error genérico de la API"""
    pass


class AuthenticationError(APIError):
    """Error de autenticación"""
    pass


class NetworkError(APIError):
    """Error de red/conexión"""
    pass


