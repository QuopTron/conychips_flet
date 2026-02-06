
from typing import Optional

from ..RepositorioAdmin import RepositorioAdmin
from ..entities.EstadisticasDashboard import DashboardCompleto

class CargarEstadisticasDashboard:

    def __init__(self, repositorio: RepositorioAdmin):
        self._repositorio = repositorio

    def EJECUTAR(self, sucursal_id: Optional[int] = None) -> Optional[DashboardCompleto]:
        try:
            resultado = self._repositorio.OBTENER_DASHBOARD_COMPLETO(sucursal_id=sucursal_id)
            return resultado
        except Exception as error:
            print(f"[CargarEstadisticas] Error: {error}")
            import traceback
            traceback.print_exc()
            return None
