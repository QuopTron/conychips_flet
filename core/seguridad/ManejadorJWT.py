import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional
from core.Constantes import (
    ALGORITMO_JWT, 
    EXPIRACION_ACCESS_TOKEN, 
    EXPIRACION_REFRESH_TOKEN,
    PERMISOS_POR_ROL
)
import os
import secrets

class ManejadorJWT:
    
    
    def __init__(self):
        self._CLAVE_SECRETA = os.getenv('JWT_SECRET_KEY', self._GENERAR_CLAVE_SEGURA())
    
    def _GENERAR_CLAVE_SEGURA(self) -> str:
        
        return secrets.token_urlsafe(32)
    
    def CREAR_ACCESS_TOKEN(
        self, 
        USUARIO_ID: int, 
        EMAIL: str, 
        ROLES: list, 
        HUELLA_DISPOSITIVO: str
    ) -> str:
        
        AHORA = datetime.utcnow()
        EXPIRACION = AHORA + timedelta(seconds=EXPIRACION_ACCESS_TOKEN)
        
        PERMISOS_TOTALES = set()
        for ROL in ROLES:
            PERMISOS_TOTALES.update(PERMISOS_POR_ROL.get(ROL, []))
        
        PAYLOAD = {
            "USUARIO_ID": USUARIO_ID,
            "EMAIL": EMAIL,
            "ROLES": ROLES,
            "PERMISOS": list(PERMISOS_TOTALES),
            "HUELLA_DISPOSITIVO": HUELLA_DISPOSITIVO,
            "TIPO": "access",
            "exp": EXPIRACION,
            "iat": AHORA
        }
        
        return jwt.encode(PAYLOAD, self._CLAVE_SECRETA, algorithm=ALGORITMO_JWT)
    
    def CREAR_REFRESH_TOKEN(self, USUARIO_ID: int, HUELLA_DISPOSITIVO: str) -> str:
        
        AHORA = datetime.utcnow()
        EXPIRACION = AHORA + timedelta(seconds=EXPIRACION_REFRESH_TOKEN)
        
        PAYLOAD = {
            "USUARIO_ID": USUARIO_ID,
            "HUELLA_DISPOSITIVO": HUELLA_DISPOSITIVO,
            "TIPO": "refresh",
            "exp": EXPIRACION,
            "iat": AHORA
        }
        
        return jwt.encode(PAYLOAD, self._CLAVE_SECRETA, algorithm=ALGORITMO_JWT)
    
    def VERIFICAR_TOKEN(self, TOKEN: str, TIPO_ESPERADO: str = "access") -> Optional[Dict]:
        
        try:
            PAYLOAD = jwt.decode(TOKEN, self._CLAVE_SECRETA, algorithms=[ALGORITMO_JWT])
            
            if PAYLOAD.get("TIPO") != TIPO_ESPERADO:
                print(f"❌ Tipo de token incorrecto")
                return None
            
            return PAYLOAD
            
        except jwt.ExpiredSignatureError:
            print("❌ Token expirado")
            return None
        except jwt.InvalidTokenError as ERROR:
            print(f"❌ Token inválido: {ERROR}")
            return None
    
    def EXTRAER_USUARIO_ID(self, TOKEN: str) -> Optional[int]:
        
        try:
            PAYLOAD = jwt.decode(
                TOKEN, 
                self._CLAVE_SECRETA, 
                algorithms=[ALGORITMO_JWT],
                options={"verify_exp": False}
            )
            return PAYLOAD.get("USUARIO_ID")
        except:
            return None
