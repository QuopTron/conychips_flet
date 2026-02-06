"""Implementación del repositorio de usuarios"""
from typing import List, Dict, Optional
from ...domain.repositories.RepositorioUsuarios import RepositorioUsuarios
from ..datasources.FuenteUsuariosLocal import FuenteUsuariosLocal


class RepositorioUsuariosImpl(RepositorioUsuarios):
    """Implementación concreta del repositorio de usuarios"""
    
    def __init__(self):
        self._fuente_local = FuenteUsuariosLocal()
    
    def OBTENER_USUARIOS(
        self,
        rol_filtro: Optional[str] = None,
        estado_filtro: Optional[bool] = None,
        sucursal_id: Optional[int] = None
    ) -> List:
        return self._fuente_local.OBTENER_USUARIOS(
            rol_filtro=rol_filtro,
            estado_filtro=estado_filtro,
            sucursal_id=sucursal_id
        )
    
    def OBTENER_USUARIO_POR_ID(self, usuario_id: int):
        return self._fuente_local.OBTENER_USUARIO_POR_ID(usuario_id)
    
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
        return self._fuente_local.CREAR_USUARIO(
            nombre_usuario=nombre_usuario,
            email=email,
            contrasena=contrasena,
            nombre_completo=nombre_completo,
            rol=rol,
            sucursal_id=sucursal_id,
            activo=activo
        )
    
    def ACTUALIZAR_USUARIO(self, usuario_id: int, datos: Dict) -> bool:
        return self._fuente_local.ACTUALIZAR_USUARIO(usuario_id, datos)
    
    def ELIMINAR_USUARIO(self, usuario_id: int) -> bool:
        return self._fuente_local.ELIMINAR_USUARIO(usuario_id)
    
    def CAMBIAR_ESTADO_USUARIO(self, usuario_id: int, activo: bool) -> bool:
        return self._fuente_local.CAMBIAR_ESTADO_USUARIO(usuario_id, activo)
    
    def CAMBIAR_ROL_USUARIO(self, usuario_id: int, nuevo_rol: str) -> bool:
        return self._fuente_local.CAMBIAR_ROL_USUARIO(usuario_id, nuevo_rol)
    
    def RESETEAR_CONTRASENA(self, usuario_id: int, nueva_contrasena: str) -> bool:
        return self._fuente_local.RESETEAR_CONTRASENA(usuario_id, nueva_contrasena)
    
    def OBTENER_ROLES_DISPONIBLES(self) -> List:
        return self._fuente_local.OBTENER_ROLES_DISPONIBLES()


# Singleton
REPOSITORIO_USUARIOS = RepositorioUsuariosImpl()
