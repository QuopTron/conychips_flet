"""
FUENTE DE DATOS REMOTA (API)
=============================
Implementación de operaciones con API externa (opcional)
"""

import aiohttp
from typing import Dict, Optional


class FuenteAutenticacionRemota:
    """
    Fuente de datos remota para sincronización con API
    
    Esta clase se usaría si tienes un backend separado.
    Por ahora es una implementación básica.
    """
    
    def __init__(self, URL_BASE: str):
        """
        Inicializa la fuente remota
        
        Args:
            URL_BASE: URL base del API (ej: https://api.miapp.com)
        """
        self._URL_BASE = URL_BASE
        self._TIMEOUT = aiohttp.ClientTimeout(total=30)
    
    async def AUTENTICAR_USUARIO(self, EMAIL: str, CONTRASENA: str) -> Dict:
        """
        Autentica usuario contra API remota
        
        Args:
            EMAIL: Email del usuario
            CONTRASENA: Contraseña
            
        Returns:
            Respuesta del servidor
        """
        URL = f"{self._URL_BASE}/auth/login"
        
        DATOS = {
            "email": EMAIL,
            "password": CONTRASENA
        }
        
        try:
            async with aiohttp.ClientSession(timeout=self._TIMEOUT) as sesion:
                async with sesion.post(URL, json=DATOS) as respuesta:
                    if respuesta.status == 200:
                        return await respuesta.json()
                    else:
                        return {
                            "EXITO": False,
                            "ERROR": f"Error del servidor: {respuesta.status}"
                        }
        except Exception as ERROR:
            print(f"❌ Error al conectar con API remota: {ERROR}")
            return {
                "EXITO": False,
                "ERROR": "No se pudo conectar con el servidor"
            }
    
    async def REGISTRAR_USUARIO(
        self, 
        EMAIL: str, 
        NOMBRE_USUARIO: str, 
        CONTRASENA: str
    ) -> Dict:
        """
        Registra usuario en API remota
        
        Args:
            EMAIL: Email del usuario
            NOMBRE_USUARIO: Nombre de usuario
            CONTRASENA: Contraseña
            
        Returns:
            Respuesta del servidor
        """
        URL = f"{self._URL_BASE}/auth/register"
        
        DATOS = {
            "email": EMAIL,
            "username": NOMBRE_USUARIO,
            "password": CONTRASENA
        }
        
        try:
            async with aiohttp.ClientSession(timeout=self._TIMEOUT) as sesion:
                async with sesion.post(URL, json=DATOS) as respuesta:
                    return await respuesta.json()
        except Exception as ERROR:
            print(f"❌ Error al registrar en API remota: {ERROR}")
            return {
                "EXITO": False,
                "ERROR": "No se pudo conectar con el servidor"
            }
    
    async def VERIFICAR_TOKEN(self, TOKEN: str) -> Dict:
        """
        Verifica token contra API remota
        
        Args:
            TOKEN: Token JWT a verificar
            
        Returns:
            Información del token
        """
        URL = f"{self._URL_BASE}/auth/verify"
        
        HEADERS = {
            "Authorization": f"Bearer {TOKEN}"
        }
        
        try:
            async with aiohttp.ClientSession(timeout=self._TIMEOUT) as sesion:
                async with sesion.get(URL, headers=HEADERS) as respuesta:
                    return await respuesta.json()
        except Exception as ERROR:
            print(f"❌ Error al verificar token: {ERROR}")
            return {
                "EXITO": False,
                "ERROR": "No se pudo verificar el token"
            }