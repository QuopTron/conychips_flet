
from dataclasses import dataclass
from typing import List, Dict
from datetime import date

@dataclass
class EstadisticasGenerales:
    total_usuarios: int
    total_pedidos_hoy: int
    ganancias_hoy: float
    total_productos: int

@dataclass
class EstadisticaRol:
    nombre_rol: str
    cantidad_usuarios: int
    porcentaje: float

@dataclass
class EstadisticaSucursal:
    id: int
    nombre: str
    total_pedidos: int

@dataclass
class EstadisticaDiaria:
    fecha: date
    nombre_dia: str
    total_pedidos: int

@dataclass
class EstadisticaInventario:
    total_insumos: int
    total_proveedores: int
    ofertas_activas: int
    total_extras: int

@dataclass
class DashboardCompleto:
    estadisticas_generales: EstadisticasGenerales
    estadisticas_roles: List[EstadisticaRol]
    estadisticas_sucursales: List[EstadisticaSucursal]
    estadisticas_semanales: List[EstadisticaDiaria]
    estadisticas_inventario: EstadisticaInventario
