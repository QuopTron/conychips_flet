"""
DECORADORES DE AUTENTICACIÓN
============================
Sistema de decoradores para proteger endpoints y métodos
"""

import functools
from typing import Callable
from core.seguridad.ManejadorJWT import ManejadorJWT


def REQUIERE_AUTENTICACION(FUNCION: Callable) -> Callable:
    """
    Decorador que requiere un token JWT válido
    
    Uso:
        @REQUIERE_AUTENTICACION
        async def MI_ENDPOINT(TOKEN: str, **kwargs):
            return {"mensaje": "Acceso permitido"}
    """
    @functools.wraps(FUNCION)
    async def ENVOLTURA(*ARGS, **KWARGS):
        TOKEN = KWARGS.get('TOKEN') or (ARGS[0] if ARGS else None)
        
        if not TOKEN:
            return {
                "EXITO": False,
                "ERROR": "Token no proporcionado",
                "CODIGO": 401
            }
        
        MANEJADOR = ManejadorJWT()
        PAYLOAD = MANEJADOR.VERIFICAR_TOKEN(TOKEN)
        
        if not PAYLOAD:
            return {
                "EXITO": False,
                "ERROR": "Token inválido o expirado",
                "CODIGO": 401
            }
        
        KWARGS['USUARIO_ID'] = PAYLOAD.get('USUARIO_ID')
        KWARGS['PAYLOAD_JWT'] = PAYLOAD
        
        return await FUNCION(*ARGS, **KWARGS)
    
    return ENVOLTURA


def REQUIERE_REFRESH_TOKEN(FUNCION: Callable) -> Callable:
    """Decorador que valida refresh token"""
    @functools.wraps(FUNCION)
    async def ENVOLTURA(*ARGS, **KWARGS):
        REFRESH_TOKEN = KWARGS.get('REFRESH_TOKEN')
        
        if not REFRESH_TOKEN:
            return {
                "EXITO": False,
                "ERROR": "Refresh token no proporcionado",
                "CODIGO": 401
            }
        
        MANEJADOR = ManejadorJWT()
        PAYLOAD = MANEJADOR.VERIFICAR_TOKEN(REFRESH_TOKEN, "refresh")
        
        if not PAYLOAD:
            return {
                "EXITO": False,
                "ERROR": "Refresh token inválido o expirado",
                "CODIGO": 401
            }
        
        KWARGS['USUARIO_ID'] = PAYLOAD.get('USUARIO_ID')
        KWARGS['HUELLA_DISPOSITIVO'] = PAYLOAD.get('HUELLA_DISPOSITIVO')
        
        return await FUNCION(*ARGS, **KWARGS)
    
    return ENVOLTURA