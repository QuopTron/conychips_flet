import aiohttp
from typing import Dict, Optional

class FuenteAutenticacionRemota:
    
    
    def __init__(self, URL_BASE: str):
        
        self._URL_BASE = URL_BASE
        self._TIMEOUT = aiohttp.ClientTimeout(total=30)
    
    async def AUTENTICAR_USUARIO(self, EMAIL: str, CONTRASENA: str) -> Dict:
        
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
