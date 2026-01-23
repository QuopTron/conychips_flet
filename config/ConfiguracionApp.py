import os
from dotenv import load_dotenv

load_dotenv()


class ConfiguracionApp:

    NOMBRE_APP = "Sistema Seguro"
    VERSION = "1.0.0"
    DESCRIPCION = "Sistema de autenticación de doble capa con roles"

    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY", "clave-super-secreta-cambiar-en-produccion"
    )
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 15
    REFRESH_TOKEN_EXPIRE_DAYS = 7

    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app_segura.db")

    WEBSOCKET_URL = os.getenv("WEBSOCKET_URL", "ws://localhost:8765")

    API_BASE_URL = os.getenv("API_BASE_URL", "https://api.ejemplo.com")
    API_TIMEOUT = 30

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15

    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@example.com")

    @classmethod
    def ES_DESARROLLO(cls) -> bool:

        return os.getenv("ENVIRONMENT", "development") == "development"

    @classmethod
    def ES_PRODUCCION(cls) -> bool:

        return os.getenv("ENVIRONMENT", "development") == "production"


CONFIGURACION_APP = ConfiguracionApp()
