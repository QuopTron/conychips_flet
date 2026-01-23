"""
IMPLEMENTACIÓN DEL REPOSITORIO DE AUTENTICACIÓN
===============================================
Implementa la interfaz del repositorio usando las fuentes de datos
"""

from typing import Optional, List
from features.autenticacion.domain.RepositorioAutenticacion import RepositorioAutenticacion
from features.autenticacion.data.datasources.FuenteAutenticacionLocal import FuenteAutenticacionLocal


class RepositorioAutenticacionImpl(RepositorioAutenticacion):
    """
    Implementación concreta del repositorio de autenticación
    
    Usa FuenteAutenticacionLocal (SQLite) como fuente principal.
    Podría combinarse con FuenteAutenticacionRemota para sincronización.
    """
    
    def __init__(self):
        """Inicializa el repositorio con sus fuentes de datos"""
        self._FUENTE_LOCAL = FuenteAutenticacionLocal()
        # self._FUENTE_REMOTA = FuenteAutenticacionRemota("https://api.ejemplo.com")
    
    async def OBTENER_POR_EMAIL(self, EMAIL: str):
        """Obtiene usuario por email"""
        return await self._FUENTE_LOCAL.OBTENER_USUARIO_POR_EMAIL(EMAIL)
    
    async def OBTENER_POR_ID(self, USUARIO_ID: int):
        """Obtiene usuario por ID"""
        return await self._FUENTE_LOCAL.OBTENER_USUARIO_POR_ID(USUARIO_ID)
    
    async def OBTENER_POR_NOMBRE_USUARIO(self, NOMBRE_USUARIO: str):
        """Obtiene usuario por nombre de usuario"""
        return await self._FUENTE_LOCAL.OBTENER_USUARIO_POR_NOMBRE(NOMBRE_USUARIO)
    
    async def CREAR_USUARIO(
        self,
        EMAIL: str,
        NOMBRE_USUARIO: str,
        CONTRASENA_HASH: str,
        HUELLA_DISPOSITIVO: str
    ):
        """Crea nuevo usuario"""
        return await self._FUENTE_LOCAL.CREAR_USUARIO(
            EMAIL=EMAIL,
            NOMBRE_USUARIO=NOMBRE_USUARIO,
            CONTRASENA_HASH=CONTRASENA_HASH,
            HUELLA_DISPOSITIVO=HUELLA_DISPOSITIVO
        )
    
    async def ACTUALIZAR_ULTIMA_CONEXION(self, USUARIO_ID: int):
        """Actualiza última conexión"""
        await self._FUENTE_LOCAL.ACTUALIZAR_ULTIMA_CONEXION(USUARIO_ID)
    
    async def CREAR_SESION(
        self,
        USUARIO_ID: int,
        REFRESH_TOKEN: str,
        HUELLA_DISPOSITIVO: str
    ):
        """Crea nueva sesión"""
        await self._FUENTE_LOCAL.CREAR_SESION(
            USUARIO_ID=USUARIO_ID,
            REFRESH_TOKEN=REFRESH_TOKEN,
            HUELLA_DISPOSITIVO=HUELLA_DISPOSITIVO
        )
    
    async def VERIFICAR_SESION(
        self,
        USUARIO_ID: int,
        REFRESH_TOKEN: str
    ) -> bool:
        """Verifica si sesión es válida"""
        return await self._FUENTE_LOCAL.VERIFICAR_SESION_ACTIVA(
            USUARIO_ID=USUARIO_ID,
            REFRESH_TOKEN=REFRESH_TOKEN
        )
    
    async def CERRAR_SESION(self, REFRESH_TOKEN: str):
        """Cierra sesión"""
        await self._FUENTE_LOCAL.CERRAR_SESION(REFRESH_TOKEN)
    
    async def ASIGNAR_ROL(self, USUARIO_ID: int, NOMBRE_ROL: str):
        """Asigna rol a usuario"""
        await self._FUENTE_LOCAL.ASIGNAR_ROL_A_USUARIO(USUARIO_ID, NOMBRE_ROL)
    
    async def REMOVER_ROL(self, USUARIO_ID: int, NOMBRE_ROL: str):
        """Remueve rol de usuario"""
        await self._FUENTE_LOCAL.REMOVER_ROL_DE_USUARIO(USUARIO_ID, NOMBRE_ROL)
    
    async def OBTENER_SESIONES_ACTIVAS(self, USUARIO_ID: int) -> List:
        """Obtiene sesiones activas del usuario"""
        return await self._FUENTE_LOCAL.OBTENER_SESIONES_ACTIVAS(USUARIO_ID)