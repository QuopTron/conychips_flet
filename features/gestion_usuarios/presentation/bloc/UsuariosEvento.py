"""Eventos del BLoC de Gestión de Usuarios"""
from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class UsuariosEvento:
    """Evento base para la gestión de usuarios"""
    pass


@dataclass
class CargarUsuarios(UsuariosEvento):
    """Evento para cargar lista de usuarios"""
    rol_filtro: Optional[str] = None
    estado_filtro: Optional[bool] = None  # True=Activos, False=Inactivos, None=Todos
    sucursal_id: Optional[int] = None


@dataclass
class CrearUsuario(UsuariosEvento):
    """Evento para crear un nuevo usuario"""
    nombre_usuario: str
    email: str
    contrasena: str
    nombre_completo: str
    rol: str
    sucursal_id: int
    activo: bool = True


@dataclass
class ActualizarUsuario(UsuariosEvento):
    """Evento para actualizar un usuario existente"""
    usuario_id: int
    datos: Dict  # {email, nombre_completo, rol, activo, contrasena_nueva (opcional)}


@dataclass
class EliminarUsuario(UsuariosEvento):
    """Evento para eliminar un usuario"""
    usuario_id: int


@dataclass
class CambiarEstadoUsuario(UsuariosEvento):
    """Evento para activar/desactivar usuario"""
    usuario_id: int
    activo: bool


@dataclass
class CambiarRolUsuario(UsuariosEvento):
    """Evento para cambiar el rol de un usuario"""
    usuario_id: int
    nuevo_rol: str


@dataclass
class ResetearContrasena(UsuariosEvento):
    """Evento para resetear contraseña de usuario"""
    usuario_id: int
    nueva_contrasena: str
