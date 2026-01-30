
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date

from .entities.EstadisticasDashboard import (
    EstadisticasGenerales,
    EstadisticaRol,
    EstadisticaSucursal,
    EstadisticaDiaria,
    EstadisticaInventario,
    DashboardCompleto,
)

class RepositorioAdmin(ABC):

    @abstractmethod
    def OBTENER_ESTADISTICAS_GENERALES(self) -> EstadisticasGenerales:
        pass

    @abstractmethod
    def OBTENER_ESTADISTICAS_ROLES(self) -> List[EstadisticaRol]:
        pass

    @abstractmethod
    def OBTENER_ESTADISTICAS_SUCURSALES(self) -> List[EstadisticaSucursal]:
        pass

    @abstractmethod
    def OBTENER_ESTADISTICAS_SEMANALES(self) -> List[EstadisticaDiaria]:
        pass

    @abstractmethod
    def OBTENER_ESTADISTICAS_INVENTARIO(self) -> EstadisticaInventario:
        pass

    @abstractmethod
    def OBTENER_DASHBOARD_COMPLETO(self, sucursal_id: Optional[int] = None) -> DashboardCompleto:
        pass

    @abstractmethod
    def ACTUALIZAR_ROL_USUARIO(self, usuario_id: int, nombre_rol: str) -> bool:
        pass

    @abstractmethod
    def OBTENER_ROLES_DISPONIBLES(self) -> List:
        pass
