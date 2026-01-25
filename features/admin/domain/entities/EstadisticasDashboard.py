"""
Entidad: Estadísticas del Dashboard
Domain Layer - Clean Architecture
"""

from dataclasses import dataclass
from typing import List, Dict
from datetime import date


@dataclass
class EstadisticasGenerales:
    """Estadísticas generales del sistema"""
    total_usuarios: int
    total_pedidos_hoy: int
    ganancias_hoy: float
    total_productos: int


@dataclass
class EstadisticaRol:
    """Estadística de usuarios por rol"""
    nombre_rol: str
    cantidad_usuarios: int
    porcentaje: float


@dataclass
class EstadisticaSucursal:
    """Estadística de pedidos por sucursal"""
    id: int
    nombre: str
    total_pedidos: int


@dataclass
class EstadisticaDiaria:
    """Estadística de pedidos por día"""
    fecha: date
    nombre_dia: str
    total_pedidos: int


@dataclass
class EstadisticaInventario:
    """Estadística de inventario"""
    total_insumos: int
    total_proveedores: int
    ofertas_activas: int
    total_extras: int


@dataclass
class DashboardCompleto:
    """Todas las estadísticas del dashboard"""
    estadisticas_generales: EstadisticasGenerales
    estadisticas_roles: List[EstadisticaRol]
    estadisticas_sucursales: List[EstadisticaSucursal]
    estadisticas_semanales: List[EstadisticaDiaria]
    estadisticas_inventario: EstadisticaInventario
