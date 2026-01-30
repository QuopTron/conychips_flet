import jwt
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import os
from dotenv import load_dotenv

load_dotenv()

class ManejadorJWT:
    
    def __init__(self):
        self._CLAVE_PRIVADA = self._CARGAR_CLAVE_PRIVADA()
        self._CLAVE_PUBLICA = self._CARGAR_CLAVE_PUBLICA()
        self._ALGORITMO = os.getenv("JWT_ALGORITHM", "RS256")
        
        self._ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
        self._REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))
        self._APP_TOKEN_EXPIRE_DAYS = int(os.getenv("APP_TOKEN_EXPIRE_DAYS", "30"))
        
        self._EMISOR = "conychips-api"
        self._AUDIENCIA = "conychips-app"
    
    
    def _CARGAR_CLAVE_PRIVADA(self):
        RUTA = os.getenv("JWT_PRIVATE_KEY_PATH", "config/keys/jwt_private.pem")
        
        if not os.path.exists(RUTA):
            raise FileNotFoundError(
                f"Clave privada no encontrada en {RUTA}. "
                "Ejecuta: python generar_claves_jwt.py"
            )
        
        with open(RUTA, 'rb') as f:
            return serialization.load_pem_private_key(
                f.read(),
                password=None,
                backend=default_backend()
            )
    
    
    def _CARGAR_CLAVE_PUBLICA(self):
        RUTA = os.getenv("JWT_PUBLIC_KEY_PATH", "config/keys/jwt_public.pem")
        
        if not os.path.exists(RUTA):
            raise FileNotFoundError(
                f"Clave pública no encontrada en {RUTA}. "
                "Ejecuta: python generar_claves_jwt.py"
            )
        
        with open(RUTA, 'rb') as f:
            return serialization.load_pem_public_key(
                f.read(),
                backend=default_backend()
            )
    
    
    def GENERAR_APP_TOKEN(self, DISPOSITIVO_ID: str, METADATA: Optional[Dict] = None) -> str:
        AHORA = datetime.now(timezone.utc)
        TOKEN_ID = str(uuid.uuid4())
        
        PAYLOAD = {
            "jti": TOKEN_ID,
            "tipo": "app",
            "dispositivo_id": DISPOSITIVO_ID,
            "iss": self._EMISOR,
            "aud": self._AUDIENCIA,
            "iat": AHORA,
            "nbf": AHORA,
            "exp": AHORA + timedelta(days=self._APP_TOKEN_EXPIRE_DAYS),
        }
        
        if METADATA:
            PAYLOAD["metadata"] = METADATA
        
        return jwt.encode(PAYLOAD, self._CLAVE_PRIVADA, algorithm=self._ALGORITMO)
    
    
    def GENERAR_ACCESS_TOKEN(
        self,
        USUARIO_ID: int,
        EMAIL: str,
        ROLES: list,
        PERMISOS: list,
        APP_TOKEN_ID: Optional[str] = None
    ) -> str:
        AHORA = datetime.now(timezone.utc)
        TOKEN_ID = str(uuid.uuid4())
        
        PAYLOAD = {
            "jti": TOKEN_ID,
            "tipo": "access",
            "usuario_id": USUARIO_ID,
            "email": EMAIL,
            "roles": ROLES,
            "permisos": PERMISOS,
            "iss": self._EMISOR,
            "aud": self._AUDIENCIA,
            "iat": AHORA,
            "nbf": AHORA,
            "exp": AHORA + timedelta(minutes=self._ACCESS_TOKEN_EXPIRE_MINUTES),
        }
        
        if APP_TOKEN_ID:
            PAYLOAD["app_token_id"] = APP_TOKEN_ID
        
        return jwt.encode(PAYLOAD, self._CLAVE_PRIVADA, algorithm=self._ALGORITMO)
    
    
    def CREAR_ACCESS_TOKEN(self, USUARIO_ID: int, EMAIL: str, ROLES: list, HUELLA_DISPOSITIVO: str) -> str:
        from core.Constantes import ROLES as ROLES_CONST, OBTENER_PERMISOS_ROL
        
        PERMISOS_TOTALES = set()
        for ROL in ROLES:
            if ROL == ROLES_CONST.SUPERADMIN:
                PERMISOS_TOTALES = {"*"}
                break
            PERMISOS_TOTALES.update(OBTENER_PERMISOS_ROL(ROL))
        
        return self.GENERAR_ACCESS_TOKEN(
            USUARIO_ID=USUARIO_ID,
            EMAIL=EMAIL,
            ROLES=ROLES,
            PERMISOS=list(PERMISOS_TOTALES),
            APP_TOKEN_ID=HUELLA_DISPOSITIVO
        )
    
    
    def GENERAR_REFRESH_TOKEN(
        self,
        USUARIO_ID: int,
        APP_TOKEN_ID: Optional[str] = None
    ) -> str:
        AHORA = datetime.now(timezone.utc)
        TOKEN_ID = str(uuid.uuid4())
        
        PAYLOAD = {
            "jti": TOKEN_ID,
            "tipo": "refresh",
            "usuario_id": USUARIO_ID,
            "iss": self._EMISOR,
            "aud": self._AUDIENCIA,
            "iat": AHORA,
            "nbf": AHORA,
            "exp": AHORA + timedelta(days=self._REFRESH_TOKEN_EXPIRE_DAYS),
        }
        
        if APP_TOKEN_ID:
            PAYLOAD["app_token_id"] = APP_TOKEN_ID
        
        return jwt.encode(PAYLOAD, self._CLAVE_PRIVADA, algorithm=self._ALGORITMO)
    
    
    def CREAR_REFRESH_TOKEN(self, USUARIO_ID: int, HUELLA_DISPOSITIVO: str) -> str:
        return self.GENERAR_REFRESH_TOKEN(
            USUARIO_ID=USUARIO_ID,
            APP_TOKEN_ID=HUELLA_DISPOSITIVO
        )
    
    
    def VERIFICAR_TOKEN(self, TOKEN: str) -> Optional[Dict[str, Any]]:
        try:
            PAYLOAD = jwt.decode(
                TOKEN,
                self._CLAVE_PUBLICA,
                algorithms=[self._ALGORITMO],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_nbf": True,
                    "verify_iat": True,
                    "verify_aud": False,
                    "verify_iss": False,
                    "require": ["exp", "iss", "aud", "jti", "tipo"]
                }
            )
            
            if PAYLOAD.get("iss") != self._EMISOR:
                return None
            
            AUD = PAYLOAD.get("aud")
            if isinstance(AUD, list):
                if self._AUDIENCIA not in AUD:
                    return None
            elif AUD != self._AUDIENCIA:
                return None
            
            from core.cache.GestorRedis import REDIS_GLOBAL
            if REDIS_GLOBAL.ESTA_EN_BLACKLIST(PAYLOAD.get("jti", "")):
                return None
            
            return PAYLOAD
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError as e:
            print(f"Token inválido: {e}")
            return None
        except Exception as e:
            print(f"Error verificando token: {e}")
            return None
    
    
    def REVOCAR_TOKEN(self, TOKEN: str) -> bool:
        try:
            PAYLOAD = jwt.decode(
                TOKEN,
                self._CLAVE_PUBLICA,
                algorithms=[self._ALGORITMO],
                options={
                    "verify_exp": False,
                    "verify_aud": False,
                    "verify_iss": False,
                    "verify_signature": True
                }
            )
            
            TOKEN_ID = PAYLOAD.get("jti")
            EXP = PAYLOAD.get("exp")
            
            if TOKEN_ID and EXP:
                TTL = int(EXP - datetime.now(timezone.utc).timestamp())
                if TTL > 0:
                    from core.cache.GestorRedis import REDIS_GLOBAL
                    return REDIS_GLOBAL.AGREGAR_TOKEN_BLACKLIST(TOKEN_ID, TTL)
            
            return False
            
        except Exception as e:
            print(f"Error revocando token: {e}")
            return False
    
    
    def EXTRAER_USUARIO_ID(self, TOKEN: str) -> Optional[int]:
        try:
            PAYLOAD = jwt.decode(
                TOKEN,
                options={"verify_signature": False}
            )
            return PAYLOAD.get("usuario_id") or PAYLOAD.get("USUARIO_ID")
        except:
            return None
    
    
    def EXTRAER_TOKEN_ID(self, TOKEN: str) -> Optional[str]:
        try:
            PAYLOAD = jwt.decode(
                TOKEN,
                options={"verify_signature": False}
            )
            return PAYLOAD.get("jti")
        except:
            return None
    
    
    def OBTENER_TIEMPO_RESTANTE(self, TOKEN: str) -> Optional[int]:
        try:
            PAYLOAD = jwt.decode(
                TOKEN,
                options={"verify_signature": False}
            )
            EXP = PAYLOAD.get("exp")
            if EXP:
                RESTANTE = int(EXP - datetime.now(timezone.utc).timestamp())
                return max(0, RESTANTE)
            return None
        except:
            return None

MANEJADOR_JWT_GLOBAL = ManejadorJWT()
