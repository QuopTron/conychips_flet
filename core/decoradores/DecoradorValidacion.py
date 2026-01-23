"""
DECORADORES DE VALIDACIÓN
=========================
Valida datos de entrada antes de procesar
"""

import functools
from typing import Callable
import re


def VALIDAR_EMAIL(FUNCION: Callable) -> Callable:
    """Valida formato de email"""
    @functools.wraps(FUNCION)
    async def ENVOLTURA(*ARGS, **KWARGS):
        EMAIL = KWARGS.get('EMAIL', '')
        
        PATRON = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(PATRON, EMAIL):
            return {
                "EXITO": False,
                "ERROR": "Formato de email inválido",
                "CODIGO": 400
            }
        
        return await FUNCION(*ARGS, **KWARGS)
    
    return ENVOLTURA


def VALIDAR_CONTRASENA_FUERTE(FUNCION: Callable) -> Callable:
    """
    Valida que la contraseña cumpla requisitos de seguridad
    - Mínimo 8 caracteres
    - Al menos una mayúscula
    - Al menos una minúscula
    - Al menos un número
    - Al menos un carácter especial
    """
    @functools.wraps(FUNCION)
    async def ENVOLTURA(*ARGS, **KWARGS):
        CONTRASENA = KWARGS.get('CONTRASENA', '')
        
        if len(CONTRASENA) < 8:
            return {
                "EXITO": False,
                "ERROR": "La contraseña debe tener al menos 8 caracteres",
                "CODIGO": 400
            }
        
        if not re.search(r'[A-Z]', CONTRASENA):
            return {
                "EXITO": False,
                "ERROR": "La contraseña debe contener al menos una mayúscula",
                "CODIGO": 400
            }
        
        if not re.search(r'[a-z]', CONTRASENA):
            return {
                "EXITO": False,
                "ERROR": "La contraseña debe contener al menos una minúscula",
                "CODIGO": 400
            }
        
        if not re.search(r'\d', CONTRASENA):
            return {
                "EXITO": False,
                "ERROR": "La contraseña debe contener al menos un número",
                "CODIGO": 400
            }
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', CONTRASENA):
            return {
                "EXITO": False,
                "ERROR": "La contraseña debe contener al menos un carácter especial",
                "CODIGO": 400
            }
        
        return await FUNCION(*ARGS, **KWARGS)
    
    return ENVOLTURA


def VALIDAR_CAMPOS_REQUERIDOS(*CAMPOS_REQUERIDOS):
    """Valida que campos requeridos estén presentes"""
    def DECORADOR(FUNCION: Callable) -> Callable:
        @functools.wraps(FUNCION)
        async def ENVOLTURA(*ARGS, **KWARGS):
            FALTANTES = []
            
            for CAMPO in CAMPOS_REQUERIDOS:
                if not KWARGS.get(CAMPO):
                    FALTANTES.append(CAMPO)
            
            if FALTANTES:
                return {
                    "EXITO": False,
                    "ERROR": f"Campos requeridos faltantes: {', '.join(FALTANTES)}",
                    "CODIGO": 400
                }
            
            return await FUNCION(*ARGS, **KWARGS)
        
        return ENVOLTURA
    return DECORADOR