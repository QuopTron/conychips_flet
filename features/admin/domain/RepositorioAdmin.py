"""
Interfaz de Repositorio Admin
Domain Layer - Clean Architecture
Define el contrato para acceso a datos de administración
"""

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
    """
    Interface que define operaciones de administración
    Implementación en la capa de datos
    """

    @abstractmethod
    def OBTENER_ESTADISTICAS_GENERALES(self) -> EstadisticasGenerales:
        """Obtiene estadísticas generales del sistema"""
        pass

    @abstractmethod
    def OBTENER_ESTADISTICAS_ROLES(self) -> List[EstadisticaRol]:
        """Obtiene distribución de usuarios por rol"""
        pass

    @abstractmethod
    def OBTENER_ESTADISTICAS_SUCURSALES(self) -> List[EstadisticaSucursal]:
        """Obtiene pedidos por sucursal"""
        pass

    @abstractmethod
    def OBTENER_ESTADISTICAS_SEMANALES(self) -> List[EstadisticaDiaria]:
        """Obtiene pedidos de la última semana"""
        pass

    @abstractmethod
    def OBTENER_ESTADISTICAS_INVENTARIO(self) -> EstadisticaInventario:
        """Obtiene estadísticas de inventario"""
        pass

    @abstractmethod
    def OBTENER_DASHBOARD_COMPLETO(self) -> DashboardCompleto:
        """Obtiene todas las estadísticas del dashboard"""
        pass

    @abstractmethod
    def ACTUALIZAR_ROL_USUARIO(self, usuario_id: int, nombre_rol: str) -> bool:
        """Actualiza el rol de un usuario"""
        pass

    @abstractmethod
    def OBTENER_ROLES_DISPONIBLES(self) -> List:
        """Obtiene lista de roles disponibles"""
        pass
