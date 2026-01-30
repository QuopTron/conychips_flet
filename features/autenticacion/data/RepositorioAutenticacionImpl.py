from typing import Optional, List
from features.autenticacion.domain.RepositorioAutenticacion import (
    RepositorioAutenticacion,
)
from features.autenticacion.data.datasources.FuenteAutenticacionLocal import (
    FuenteAutenticacionLocal,
)
from datetime import datetime

class RepositorioAutenticacionImpl(RepositorioAutenticacion):

    def __init__(self):

        self._FUENTE_LOCAL = FuenteAutenticacionLocal()

    async def OBTENER_POR_EMAIL(self, EMAIL: str):

        return await self._FUENTE_LOCAL.OBTENER_USUARIO_POR_EMAIL(EMAIL)

    async def OBTENER_POR_ID(self, USUARIO_ID: int):

        return await self._FUENTE_LOCAL.OBTENER_USUARIO_POR_ID(USUARIO_ID)

    async def OBTENER_POR_NOMBRE_USUARIO(self, NOMBRE_USUARIO: str):

        return await self._FUENTE_LOCAL.OBTENER_USUARIO_POR_NOMBRE(NOMBRE_USUARIO)

    async def CREAR_USUARIO(
        self,
        EMAIL: str,
        NOMBRE_USUARIO: str,
        CONTRASENA_HASH: str,
        HUELLA_DISPOSITIVO: str,
    ):

        return await self._FUENTE_LOCAL.CREAR_USUARIO(
            EMAIL=EMAIL,
            NOMBRE_USUARIO=NOMBRE_USUARIO,
            CONTRASENA_HASH=CONTRASENA_HASH,
            HUELLA_DISPOSITIVO=HUELLA_DISPOSITIVO,
        )

    async def ACTUALIZAR_ULTIMA_CONEXION(self, USUARIO_ID: int):

        await self._FUENTE_LOCAL.ACTUALIZAR_ULTIMA_CONEXION(USUARIO_ID)

    async def CREAR_SESION(
        self, USUARIO_ID: int, REFRESH_TOKEN: str, HUELLA_DISPOSITIVO: str
    ):

        await self._FUENTE_LOCAL.CREAR_SESION(
            USUARIO_ID=USUARIO_ID,
            REFRESH_TOKEN=REFRESH_TOKEN,
            HUELLA_DISPOSITIVO=HUELLA_DISPOSITIVO,
        )

    async def VERIFICAR_SESION(self, USUARIO_ID: int, REFRESH_TOKEN: str) -> bool:

        return await self._FUENTE_LOCAL.VERIFICAR_SESION_ACTIVA(
            USUARIO_ID=USUARIO_ID, REFRESH_TOKEN=REFRESH_TOKEN
        )

    async def CERRAR_SESION(self, REFRESH_TOKEN: str):

        await self._FUENTE_LOCAL.CERRAR_SESION(REFRESH_TOKEN)

    async def ASIGNAR_ROL(self, USUARIO_ID: int, NOMBRE_ROL: str):

        await self._FUENTE_LOCAL.ASIGNAR_ROL_A_USUARIO(USUARIO_ID, NOMBRE_ROL)

    async def REMOVER_ROL(self, USUARIO_ID: int, NOMBRE_ROL: str):

        await self._FUENTE_LOCAL.REMOVER_ROL_DE_USUARIO(USUARIO_ID, NOMBRE_ROL)

    async def OBTENER_SESIONES_ACTIVAS(self, USUARIO_ID: int) -> List:

        return await self._FUENTE_LOCAL.OBTENER_SESIONES_ACTIVAS(USUARIO_ID)

    async def ACTUALIZAR_TOKEN_RESET(
        self, USUARIO_ID: int, TOKEN: str, EXPIRA: datetime
    ):
        await self._FUENTE_LOCAL.ACTUALIZAR_TOKEN_RESET(USUARIO_ID, TOKEN, EXPIRA)

    async def OBTENER_USUARIO_POR_TOKEN_RESET(self, TOKEN: str):
        return await self._FUENTE_LOCAL.OBTENER_USUARIO_POR_TOKEN_RESET(TOKEN)

    async def ACTUALIZAR_CONTRASENA(self, USUARIO_ID: int, NUEVA_CONTRASENA_HASH: str):
        await self._FUENTE_LOCAL.ACTUALIZAR_CONTRASENA(
            USUARIO_ID, NUEVA_CONTRASENA_HASH
        )

    async def LIMPIAR_TOKEN_RESET(self, USUARIO_ID: int):
        await self._FUENTE_LOCAL.LIMPIAR_TOKEN_RESET(USUARIO_ID)

    async def VERIFICAR_EMAIL(self, USUARIO_ID: int):
        await self._FUENTE_LOCAL.VERIFICAR_EMAIL(USUARIO_ID)
