"""
DECORADORES DE PERMISOS
=======================
Control de acceso basado en roles y permisos
"""

import functools
from typing import Callable
from core.Constantes import ROLES, PERMISOS_POR_ROL


def REQUIERE_PERMISOS(*PERMISOS_REQUERIDOS: str):
    """
    Decorador que verifica permisos específicos
    
    Uso:
        @REQUIERE_PERMISOS('usuarios.crear', 'usuarios.editar')
        async def CREAR_USUARIO(PAYLOAD_JWT: dict, **kwargs):
            return {"mensaje": "Usuario creado"}
    """
    def DECORADOR(FUNCION: Callable) -> Callable:
        @functools.wraps(FUNCION)
        async def ENVOLTURA(*ARGS, **KWARGS):
            PAYLOAD_JWT = KWARGS.get('PAYLOAD_JWT', {})
            PERMISOS_USUARIO = set(PAYLOAD_JWT.get('PERMISOS', []))
            
            # Si tiene permiso "*" (super admin), permitir todo
            if "*" in PERMISOS_USUARIO:
                return await FUNCION(*ARGS, **KWARGS)
            
            PERMISOS_NECESARIOS = set(PERMISOS_REQUERIDOS)
            
            if not PERMISOS_NECESARIOS.issubset(PERMISOS_USUARIO):
                FALTANTES = PERMISOS_NECESARIOS - PERMISOS_USUARIO
                return {
                    "EXITO": False,
                    "ERROR": f"Permisos insuficientes. Faltan: {', '.join(FALTANTES)}",
                    "CODIGO": 403
                }
            
            return await FUNCION(*ARGS, **KWARGS)
        
        return ENVOLTURA
    return DECORADOR


def REQUIERE_ROL(*ROLES_REQUERIDOS: str):
    """
    Decorador que verifica roles específicos
    
    Uso:
        @REQUIERE_ROL('admin', 'moderador')
        async def MODERAR_CONTENIDO(PAYLOAD_JWT: dict, **kwargs):
            return {"mensaje": "Contenido moderado"}
    """
    def DECORADOR(FUNCION: Callable) -> Callable:
        @functools.wraps(FUNCION)
        async def ENVOLTURA(*ARGS, **KWARGS):
            PAYLOAD_JWT = KWARGS.get('PAYLOAD_JWT', {})
            ROLES_USUARIO = set(PAYLOAD_JWT.get('ROLES', []))
            ROLES_NECESARIOS = set(ROLES_REQUERIDOS)
            
            if not ROLES_NECESARIOS.intersection(ROLES_USUARIO):
                return {
                    "EXITO": False,
                    "ERROR": f"Se requiere uno de estos roles: {', '.join(ROLES_NECESARIOS)}",
                    "CODIGO": 403
                }
            
            return await FUNCION(*ARGS, **KWARGS)
        
        return ENVOLTURA
    return DECORADOR


def SOLO_SUPER_ADMIN(FUNCION: Callable) -> Callable:
    """Decorador que permite solo a super administradores"""
    @functools.wraps(FUNCION)
    async def ENVOLTURA(*ARGS, **KWARGS):
        PAYLOAD_JWT = KWARGS.get('PAYLOAD_JWT', {})
        ROLES_USUARIO = PAYLOAD_JWT.get('ROLES', [])
        
        if ROLES.SUPER_ADMIN not in ROLES_USUARIO:
            return {
                "EXITO": False,
                "ERROR": "Esta acción requiere privilegios de super administrador",
                "CODIGO": 403
            }
        
        return await FUNCION(*ARGS, **KWARGS)
    
    return ENVOLTURA


def VALIDAR_HUELLA_DISPOSITIVO(FUNCION: Callable) -> Callable:
    """Valida que la petición venga del dispositivo correcto"""
    @functools.wraps(FUNCION)
    async def ENVOLTURA(*ARGS, **KWARGS):
        from core.seguridad.ValidadorDispositivo import ValidadorDispositivo
        
        PAYLOAD_JWT = KWARGS.get('PAYLOAD_JWT', {})
        HUELLA_JWT = PAYLOAD_JWT.get('HUELLA_DISPOSITIVO')
        
        if not ValidadorDispositivo.VALIDAR_HUELLA(HUELLA_JWT):
            return {
                "EXITO": False,
                "ERROR": "Dispositivo no autorizado",
                "CODIGO": 403
            }
        
        return await FUNCION(*ARGS, **KWARGS)
    
    return ENVOLTURA