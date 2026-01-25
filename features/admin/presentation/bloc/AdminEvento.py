"""
Eventos del Admin BLoC
Presentation Layer - Clean Architecture
"""

from dataclasses import dataclass


@dataclass
class AdminEvento:
    """Evento base del Admin"""
    pass


@dataclass
class CargarDashboard(AdminEvento):
    """Evento para cargar el dashboard"""
    pass


@dataclass
class ActualizarRol(AdminEvento):
    """Evento para actualizar rol de usuario"""
    usuario_id: int
    nombre_rol: str


@dataclass
class RecargarDashboard(AdminEvento):
    """Evento para recargar las estadísticas"""
    pass


@dataclass
class NavegerA(AdminEvento):
    """Evento para navegar a otra vista"""
    ruta: str
