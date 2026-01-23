from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime


class RepositorioAutenticacion(ABC):
    """
    """
    
    @abstractmethod
    async def OBTENER_POR_EMAIL(self, EMAIL: str):
        """
        Obtiene usuario por email
        
        Args:
            EMAIL: Email del usuario
            
        Returns:
            Usuario o None si no existe
        """
        pass
    
    @abstractmethod
    async def OBTENER_POR_ID(self, USUARIO_ID: int):
        """
        Obtiene usuario por ID
        
        Args:
            USUARIO_ID: ID del usuario
            
        Returns:
            Usuario o None si no existe
        """
        pass
    
    @abstractmethod
    async def OBTENER_POR_NOMBRE_USUARIO(self, NOMBRE_USUARIO: str):
        """
        Obtiene usuario por nombre de usuario
        
        Args:
            NOMBRE_USUARIO: Nombre de usuario único
            
        Returns:
            Usuario o None si no existe
        """
        pass
    
    @abstractmethod
    async def CREAR_USUARIO(
        self,
        EMAIL: str,
        NOMBRE_USUARIO: str,
        CONTRASENA_HASH: str,
        HUELLA_DISPOSITIVO: str
    ):
        """
        Crea nuevo usuario en BD
        
        Args:
            EMAIL: Email del usuario
            NOMBRE_USUARIO: Nombre de usuario
            CONTRASENA_HASH: Hash bcrypt de la contraseña
            HUELLA_DISPOSITIVO: Huella del dispositivo
            
        Returns:
            Usuario creado
        """
        pass
    
    @abstractmethod
    async def ACTUALIZAR_ULTIMA_CONEXION(self, USUARIO_ID: int):
        """
        Actualiza timestamp de última conexión
        
        Args:
            USUARIO_ID: ID del usuario
        """
        pass
    
    @abstractmethod
    async def CREAR_SESION(
        self,
        USUARIO_ID: int,
        REFRESH_TOKEN: str,
        HUELLA_DISPOSITIVO: str
    ):
        """
        Crea nueva sesión en BD
        
        Args:
            USUARIO_ID: ID del usuario
            REFRESH_TOKEN: Token de refresco
            HUELLA_DISPOSITIVO: Huella del dispositivo
        """
        pass
    
    @abstractmethod
    async def VERIFICAR_SESION(
        self,
        USUARIO_ID: int,
        REFRESH_TOKEN: str
    ) -> bool:
        """
        Verifica si existe sesión activa
        
        Args:
            USUARIO_ID: ID del usuario
            REFRESH_TOKEN: Token de refresco
            
        Returns:
            True si la sesión es válida, False si no
        """
        pass
    
    @abstractmethod
    async def CERRAR_SESION(self, REFRESH_TOKEN: str):
        """
        Cierra sesión (marca como inactiva)
        
        Args:
            REFRESH_TOKEN: Token de la sesión a cerrar
        """
        pass
    
    @abstractmethod
    async def ASIGNAR_ROL(self, USUARIO_ID: int, NOMBRE_ROL: str):
        """
        Asigna rol a usuario
        
        Args:
            USUARIO_ID: ID del usuario
            NOMBRE_ROL: Nombre del rol
        """
        pass
    
    @abstractmethod
    async def REMOVER_ROL(self, USUARIO_ID: int, NOMBRE_ROL: str):
        """
        Remueve rol de usuario
        
        Args:
            USUARIO_ID: ID del usuario
            NOMBRE_ROL: Nombre del rol
        """
        pass
    
    @abstractmethod
    async def OBTENER_SESIONES_ACTIVAS(self, USUARIO_ID: int) -> List:
        """
        Obtiene todas las sesiones activas de un usuario
        
        Args:
            USUARIO_ID: ID del usuario
            
        Returns:
            Lista de sesiones activas
        """
        pass