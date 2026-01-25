"""
Caso de Uso: Cargar Estadísticas del Dashboard
Domain Layer - Clean Architecture
"""

from typing import Optional

from ..RepositorioAdmin import RepositorioAdmin
from ..entities.EstadisticasDashboard import DashboardCompleto


class CargarEstadisticasDashboard:
    """
    Caso de uso para cargar todas las estadísticas del dashboard
    Principio de Responsabilidad Única (SRP)
    """

    def __init__(self, repositorio: RepositorioAdmin):
        self._repositorio = repositorio

    def EJECUTAR(self) -> Optional[DashboardCompleto]:
        """
        Ejecuta el caso de uso para obtener todas las estadísticas

        Returns:
            DashboardCompleto con todas las estadísticas o None si hay error
        """
        try:
            return self._repositorio.OBTENER_DASHBOARD_COMPLETO()
        except Exception as error:
            print(f"Error en CargarEstadisticasDashboard: {error}")
            return None
