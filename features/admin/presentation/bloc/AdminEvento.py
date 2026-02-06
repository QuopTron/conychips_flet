
from dataclasses import dataclass
from typing import Optional

@dataclass
class AdminEvento:
    pass

@dataclass
class CargarDashboard(AdminEvento):
    sucursal_id: Optional[int] = None

@dataclass
class ActualizarRol(AdminEvento):
    usuario_id: int
    nombre_rol: str

@dataclass
class RecargarDashboard(AdminEvento):
    sucursal_id: Optional[int] = None

@dataclass
class NavegerA(AdminEvento):
    ruta: str
