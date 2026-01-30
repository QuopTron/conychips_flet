
from dataclasses import dataclass
from typing import Optional

from ...domain.entities.EstadisticasDashboard import DashboardCompleto

@dataclass
class AdminEstado:
    pass

@dataclass
class AdminInicial(AdminEstado):
    pass

@dataclass
class AdminCargando(AdminEstado):
    pass

@dataclass
class AdminCargado(AdminEstado):
    dashboard: DashboardCompleto

@dataclass
class AdminError(AdminEstado):
    mensaje: str

@dataclass
class AdminActualizandoRol(AdminEstado):
    usuario_id: int

@dataclass
class AdminRolActualizado(AdminEstado):
    mensaje: str
    dashboard: Optional[DashboardCompleto] = None
