"""
Estados del Admin BLoC
Presentation Layer - Clean Architecture
"""

from dataclasses import dataclass
from typing import Optional

from ...domain.entities.EstadisticasDashboard import DashboardCompleto


@dataclass
class AdminEstado:
    """Estado base del Admin"""
    pass


@dataclass
class AdminInicial(AdminEstado):
    """Estado inicial - sin datos cargados"""
    pass


@dataclass
class AdminCargando(AdminEstado):
    """Estado de carga - obteniendo datos"""
    pass


@dataclass
class AdminCargado(AdminEstado):
    """Estado con datos cargados exitosamente"""
    dashboard: DashboardCompleto


@dataclass
class AdminError(AdminEstado):
    """Estado de error"""
    mensaje: str


@dataclass
class AdminActualizandoRol(AdminEstado):
    """Estado durante actualización de rol"""
    usuario_id: int


@dataclass
class AdminRolActualizado(AdminEstado):
    """Estado después de actualizar rol exitosamente"""
    mensaje: str
    dashboard: Optional[DashboardCompleto] = None
