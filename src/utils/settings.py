"""
Configuración de la aplicación
"""

import os
from typing import Optional


class Settings:
    """Configuración centralizada de la aplicación"""
    
    # API Configuration
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8080/crudxtart_war")
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))
    
    # Application
    APP_NAME: str = "CRM XTART"
    APP_VERSION: str = "2.0.0"
    
    # UI
    WINDOW_WIDTH: int = 1200
    WINDOW_HEIGHT: int = 800
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def get_api_url(cls) -> str:
        """Obtiene la URL base de la API"""
        return cls.API_BASE_URL
    
    @classmethod
    def get_timeout(cls) -> int:
        """Obtiene el timeout para las peticiones"""
        return cls.API_TIMEOUT

