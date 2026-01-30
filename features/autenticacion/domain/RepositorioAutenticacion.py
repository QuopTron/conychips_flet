from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime

class RepositorioAutenticacion(ABC):

    @abstractmethod
    async def OBTENER_POR_EMAIL(self, EMAIL: str):

        pass

    @abstractmethod
    async def OBTENER_POR_ID(self, USUARIO_ID: int):

        pass

    @abstractmethod
    async def OBTENER_POR_NOMBRE_USUARIO(self, NOMBRE_USUARIO: str):

        pass

    @abstractmethod
    async def CREAR_USUARIO(
        self,
        EMAIL: str,
        NOMBRE_USUARIO: str,
        CONTRASENA_HASH: str,
        HUELLA_DISPOSITIVO: str,
    ):

        pass

    @abstractmethod
    async def ACTUALIZAR_ULTIMA_CONEXION(self, USUARIO_ID: int):

        pass

    @abstractmethod
    async def CREAR_SESION(
        self, USUARIO_ID: int, REFRESH_TOKEN: str, HUELLA_DISPOSITIVO: str
    ):

        pass

    @abstractmethod
    async def VERIFICAR_SESION(self, USUARIO_ID: int, REFRESH_TOKEN: str) -> bool:

        pass

    @abstractmethod
    async def CERRAR_SESION(self, REFRESH_TOKEN: str):

        pass

    @abstractmethod
    async def ASIGNAR_ROL(self, USUARIO_ID: int, NOMBRE_ROL: str):

        pass

    @abstractmethod
    async def REMOVER_ROL(self, USUARIO_ID: int, NOMBRE_ROL: str):

        pass

    @abstractmethod
    async def OBTENER_SESIONES_ACTIVAS(self, USUARIO_ID: int) -> List:

        pass

    @abstractmethod
    async def ACTUALIZAR_TOKEN_RESET(self, USUARIO_ID: int, TOKEN: str, EXPIRA: datetime):

        pass

    @abstractmethod
    async def OBTENER_USUARIO_POR_TOKEN_RESET(self, TOKEN: str):

        pass

    @abstractmethod
    async def ACTUALIZAR_CONTRASENA(self, USUARIO_ID: int, NUEVA_CONTRASENA_HASH: str):

        pass

    @abstractmethod
    async def LIMPIAR_TOKEN_RESET(self, USUARIO_ID: int):

        pass

    @abstractmethod
    async def VERIFICAR_EMAIL(self, USUARIO_ID: int):

        pass
