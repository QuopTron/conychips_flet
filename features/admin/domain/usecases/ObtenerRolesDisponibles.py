"""
Caso de Uso: Obtener Roles Disponibles
Domain Layer - Clean Architecture
"""

from typing import List, Optional

from ..RepositorioAdmin import RepositorioAdmin


class ObtenerRolesDisponibles:
    """
    Caso de uso para obtener la lista de roles del sistema
    Principio de Responsabilidad Única (SRP)
    """

    def __init__(self, repositorio: RepositorioAdmin):
        self._repositorio = repositorio

    def EJECUTAR(self) -> Optional[List]:
        """
        Ejecuta el caso de uso para obtener roles

        Returns:
            Lista de roles disponibles o None si hay error
        """
        try:
            return self._repositorio.OBTENER_ROLES_DISPONIBLES()
        except Exception as error:
            print(f"Error en ObtenerRolesDisponibles: {error}")
            return None
