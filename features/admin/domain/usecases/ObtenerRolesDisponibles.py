
from typing import List, Optional

from ..RepositorioAdmin import RepositorioAdmin

class ObtenerRolesDisponibles:

    def __init__(self, repositorio: RepositorioAdmin):
        self._repositorio = repositorio

    def EJECUTAR(self) -> Optional[List]:
        try:
            return self._repositorio.OBTENER_ROLES_DISPONIBLES()
        except Exception as error:
            print(f"Error en ObtenerRolesDisponibles: {error}")
            return None
