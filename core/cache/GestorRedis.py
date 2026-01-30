import redis
import json
from typing import Optional, Any
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

class GestorRedis:
    
    _INSTANCIA: Optional['GestorRedis'] = None
    _CLIENTE: Optional[redis.Redis] = None
    
    
    def __new__(cls):
        if cls._INSTANCIA is None:
            cls._INSTANCIA = super().__new__(cls)
            cls._INSTANCIA._INICIALIZADO = False
        return cls._INSTANCIA
    
    
    def __init__(self):
        if self._INICIALIZADO:
            return
        
        REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        
        try:
            self._CLIENTE = redis.from_url(
                REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
                health_check_interval=30
            )
            self._CLIENTE.ping()
            self.CONEXION = self._CLIENTE
            print(f"✓ Conexión Redis establecida: {REDIS_URL}")
        except Exception as e:
            print(f"✗ Error conectando a Redis: {e}")
            print("⚠ Usando modo fallback sin cache")
            self._CLIENTE = None
            self.CONEXION = None
        
        self._INICIALIZADO = True
        
        self.PREFIJO_SESSION = os.getenv("REDIS_SESSION_PREFIX", "session:")
        self.PREFIJO_CACHE = os.getenv("REDIS_CACHE_PREFIX", "cache:")
        self.PREFIJO_BLACKLIST = os.getenv("REDIS_TOKEN_BLACKLIST_PREFIX", "blacklist:")
    
    
    def ESTA_DISPONIBLE(self) -> bool:
        return self._CLIENTE is not None
    
    
    def GUARDAR_SESION(self, USUARIO_ID: int, TOKEN: str, DATOS: dict, TTL_SECONDS: int = 900):
        if not self.ESTA_DISPONIBLE():
            return False
        
        try:
            CLAVE = f"{self.PREFIJO_SESSION}{USUARIO_ID}:{TOKEN[:20]}"
            VALOR = json.dumps(DATOS)
            self._CLIENTE.setex(CLAVE, TTL_SECONDS, VALOR)
            return True
        except Exception as e:
            print(f"Error guardando sesión: {e}")
            return False
    
    
    def OBTENER_SESION(self, USUARIO_ID: int, TOKEN: str) -> Optional[dict]:
        if not self.ESTA_DISPONIBLE():
            return None
        
        try:
            CLAVE = f"{self.PREFIJO_SESSION}{USUARIO_ID}:{TOKEN[:20]}"
            VALOR = self._CLIENTE.get(CLAVE)
            if VALOR:
                return json.loads(VALOR)
            return None
        except Exception as e:
            print(f"Error obteniendo sesión: {e}")
            return None
    
    
    def ELIMINAR_SESION(self, USUARIO_ID: int, TOKEN: str) -> bool:
        if not self.ESTA_DISPONIBLE():
            return False
        
        try:
            CLAVE = f"{self.PREFIJO_SESSION}{USUARIO_ID}:{TOKEN[:20]}"
            self._CLIENTE.delete(CLAVE)
            return True
        except Exception as e:
            print(f"Error eliminando sesión: {e}")
            return False
    
    
    def ELIMINAR_TODAS_SESIONES_USUARIO(self, USUARIO_ID: int) -> bool:
        if not self.ESTA_DISPONIBLE():
            return False
        
        try:
            PATRON = f"{self.PREFIJO_SESSION}{USUARIO_ID}:*"
            CLAVES = self._CLIENTE.keys(PATRON)
            if CLAVES:
                self._CLIENTE.delete(*CLAVES)
            return True
        except Exception as e:
            print(f"Error eliminando sesiones del usuario: {e}")
            return False
    
    
    def AGREGAR_TOKEN_BLACKLIST(self, TOKEN_ID: str, TTL_SECONDS: int):
        if not self.ESTA_DISPONIBLE():
            return False
        
        try:
            CLAVE = f"{self.PREFIJO_BLACKLIST}{TOKEN_ID}"
            self._CLIENTE.setex(CLAVE, TTL_SECONDS, "1")
            return True
        except Exception as e:
            print(f"Error agregando token a blacklist: {e}")
            return False
    
    
    def ESTA_EN_BLACKLIST(self, TOKEN_ID: str) -> bool:
        if not self.ESTA_DISPONIBLE():
            return False
        
        try:
            CLAVE = f"{self.PREFIJO_BLACKLIST}{TOKEN_ID}"
            return self._CLIENTE.exists(CLAVE) > 0
        except Exception as e:
            print(f"Error verificando blacklist: {e}")
            return False
    
    
    def GUARDAR_CACHE(self, CLAVE: str, VALOR: Any, TTL_SECONDS: int = 300):
        if not self.ESTA_DISPONIBLE():
            return False
        
        try:
            CLAVE_COMPLETA = f"{self.PREFIJO_CACHE}{CLAVE}"
            if isinstance(VALOR, (dict, list)):
                VALOR = json.dumps(VALOR)
            self._CLIENTE.setex(CLAVE_COMPLETA, TTL_SECONDS, VALOR)
            return True
        except Exception as e:
            print(f"Error guardando cache: {e}")
            return False
    
    
    def OBTENER_CACHE(self, CLAVE: str) -> Optional[Any]:
        if not self.ESTA_DISPONIBLE():
            return None
        
        try:
            CLAVE_COMPLETA = f"{self.PREFIJO_CACHE}{CLAVE}"
            VALOR = self._CLIENTE.get(CLAVE_COMPLETA)
            if VALOR:
                try:
                    return json.loads(VALOR)
                except:
                    return VALOR
            return None
        except Exception as e:
            print(f"Error obteniendo cache: {e}")
            return None
    
    
    def INVALIDAR_CACHE(self, PATRON: str):
        if not self.ESTA_DISPONIBLE():
            return False
        
        try:
            PATRON_COMPLETO = f"{self.PREFIJO_CACHE}{PATRON}"
            CLAVES = self._CLIENTE.keys(PATRON_COMPLETO)
            if CLAVES:
                self._CLIENTE.delete(*CLAVES)
            return True
        except Exception as e:
            print(f"Error invalidando cache: {e}")
            return False
    
    
    def CERRAR(self):
        if self._CLIENTE:
            try:
                self._CLIENTE.close()
            except:
                pass

REDIS_GLOBAL = GestorRedis()
