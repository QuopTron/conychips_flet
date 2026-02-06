"""Repositorio abstracto para gestión de usuarios"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class RepositorioUsuarios(ABC):
    """Interface del repositorio de usuarios"""
    
    @abstractmethod
    def OBTENER_USUARIOS(
        self,
        rol_filtro: Optional[str] = None,
        estado_filtro: Optional[bool] = None,
        sucursal_id: Optional[int] = None
    ) -> List:
        """Obtiene lista de usuarios con filtros opcionales"""
        pass
    
    @abstractmethod
    def OBTENER_USUARIO_POR_ID(self, usuario_id: int):
        """Obtiene un usuario por su ID"""
        pass
    
    @abstractmethod
    def CREAR_USUARIO(
        self,
        nombre_usuario: str,
        email: str,
        contrasena: str,
        nombre_completo: str,
        rol: str,
        sucursal_id: int,
        activo: bool = True
    ) -> int:
        """Crea un nuevo usuario y retorna su ID"""
        pass
    
    @abstractmethod
    def ACTUALIZAR_USUARIO(self, usuario_id: int, datos: Dict) -> bool:
        """Actualiza un usuario existente"""
        pass
    
    @abstractmethod
    def ELIMINAR_USUARIO(self, usuario_id: int) -> bool:
        """Elimina (soft delete) un usuario"""
        pass
    
    @abstractmethod
    def CAMBIAR_ESTADO_USUARIO(self, usuario_id: int, activo: bool) -> bool:
        """Cambia el estado activo/inactivo de un usuario"""
        pass
    
    @abstractmethod
    def CAMBIAR_ROL_USUARIO(self, usuario_id: int, nuevo_rol: str) -> bool:
        """Cambia el rol de un usuario"""
        pass
    
    @abstractmethod
    def RESETEAR_CONTRASENA(self, usuario_id: int, nueva_contrasena: str) -> bool:
        """Resetea la contraseña de un usuario"""
        pass
    
    @abstractmethod
    def OBTENER_ROLES_DISPONIBLES(self) -> List:
        """Obtiene la lista de roles disponibles"""
        pass
