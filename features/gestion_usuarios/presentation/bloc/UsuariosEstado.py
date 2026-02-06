"""Estados del BLoC de Gestión de Usuarios"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class UsuariosEstado:
    """Estado base para la gestión de usuarios"""
    pass


@dataclass
class UsuariosInicial(UsuariosEstado):
    """Estado inicial - sin datos cargados"""
    pass


@dataclass
class UsuariosCargando(UsuariosEstado):
    """Estado de carga - mostrando indicador de progreso"""
    pass


@dataclass
class UsuariosCargados(UsuariosEstado):
    """Estado con usuarios cargados exitosamente"""
    usuarios: List
    total: int
    mensaje: str = ""


@dataclass
class UsuarioCreado(UsuariosEstado):
    """Estado después de crear un usuario"""
    mensaje: str
    usuario_id: int


@dataclass
class UsuarioActualizado(UsuariosEstado):
    """Estado después de actualizar un usuario"""
    mensaje: str
    usuario_id: int


@dataclass
class UsuarioEliminado(UsuariosEstado):
    """Estado después de eliminar un usuario"""
    mensaje: str
    usuario_id: int


@dataclass
class UsuarioError(UsuariosEstado):
    """Estado de error"""
    mensaje: str
    detalles: Optional[str] = None
