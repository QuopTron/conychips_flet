
from ..RepositorioVouchers import RepositorioVouchers

class ObtenerEstadisticasVouchers:
    
    def __init__(self, repositorio: RepositorioVouchers):
        self._repositorio = repositorio
    
    def ejecutar(self) -> dict:
        return self._repositorio.obtener_estadisticas()
