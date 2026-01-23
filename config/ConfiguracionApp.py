"""
CONFIGURACIÓN DE LA APLICACIÓN
===============================
Configuración centralizada de la aplicación
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class ConfiguracionApp:
    """Configuración global de la aplicación"""
    
    # Información de la app
    NOMBRE_APP = "Sistema Seguro"
    VERSION = "1.0.0"
    DESCRIPCION = "Sistema de autenticación de doble capa con roles"
    
    # Seguridad
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'clave-super-secreta-cambiar-en-produccion')
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 15
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    # Base de datos
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./app_segura.db')
    
    # WebSocket
    WEBSOCKET_URL = os.getenv('WEBSOCKET_URL', 'ws://localhost:8765')
    
    # API Externa (opcional)
    API_BASE_URL = os.getenv('API_BASE_URL', 'https://api.ejemplo.com')
    API_TIMEOUT = 30
    
    # Logs
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Límites
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15
    
    # Email (para verificación - opcional)
    SMTP_HOST = os.getenv('SMTP_HOST', '')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USER = os.getenv('SMTP_USER', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    EMAIL_FROM = os.getenv('EMAIL_FROM', 'noreply@example.com')
    
    @classmethod
    def ES_DESARROLLO(cls) -> bool:
        """Indica si está en modo desarrollo"""
        return os.getenv('ENVIRONMENT', 'development') == 'development'
    
    @classmethod
    def ES_PRODUCCION(cls) -> bool:
        """Indica si está en modo producción"""
        return os.getenv('ENVIRONMENT', 'development') == 'production'


# Instancia global
CONFIGURACION_APP = ConfiguracionApp()