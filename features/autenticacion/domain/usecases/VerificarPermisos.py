"""
CASO DE USO: VERIFICAR PERMISOS
================================
Verifica si un usuario tiene permisos específicos
"""

from typing import List, Dict
from features.autenticacion.domain.RepositorioAutenticacion import RepositorioAutenticacion
from core.Constantes import PERMISOS_POR_ROL


class VerificarPermisos:
    """
    Caso de uso para verificar permisos de usuario
    """
    
    def __init__(self, REPOSITORIO: RepositorioAutenticacion):
        """
        Inicializa el caso de uso
        Args: REPOSITORIO: Repositorio de autenticación
        """
        self._REPOSITORIO = REPOSITORIO
    
    async def EJECUTAR(
        self, 
        USUARIO_ID: int, 
        PERMISOS_REQUERIDOS: List[str]
    ) -> Dict:
        """
        Verifica si un usuario tiene los permisos requeridos
        Args:   USUARIO_ID: ID del usuario
                PERMISOS_REQUERIDOS: Lista de permisos a verificar
            
        """
        try:
            # Obtener usuario de BD
            USUARIO = await self._REPOSITORIO.OBTENER_POR_ID(USUARIO_ID)
            
            if not USUARIO:
                return {
                    "TIENE_PERMISOS": False,
                    "PERMISOS_FALTANTES": PERMISOS_REQUERIDOS,
                    "ROLES_USUARIO": []
                }
            
            # Obtener roles del usuario
            ROLES_USUARIO = [ROL.NOMBRE for ROL in USUARIO.ROLES]
            
            # Compilar todos los permisos del usuario
            PERMISOS_USUARIO = set()
            for ROL in ROLES_USUARIO:
                PERMISOS_USUARIO.update(PERMISOS_POR_ROL.get(ROL, []))
            
            # Si tiene permiso comodín, tiene todos los permisos
            if "*" in PERMISOS_USUARIO:
                return {
                    "TIENE_PERMISOS": True,
                    "PERMISOS_FALTANTES": [],
                    "ROLES_USUARIO": ROLES_USUARIO
                }
            
            # Verificar permisos faltantes
            PERMISOS_FALTANTES = [
                PERMISO for PERMISO in PERMISOS_REQUERIDOS 
                if PERMISO not in PERMISOS_USUARIO
            ]
            
            return {
                "TIENE_PERMISOS": len(PERMISOS_FALTANTES) == 0,
                "PERMISOS_FALTANTES": PERMISOS_FALTANTES,
                "ROLES_USUARIO": ROLES_USUARIO
            }
        
        except Exception as ERROR:
            print(f"Error al verificar permisos: {ERROR}")
            return {
                "TIENE_PERMISOS": False,
                "PERMISOS_FALTANTES": PERMISOS_REQUERIDOS,
                "ROLES_USUARIO": []
            }
    
    async def USUARIO_ES_ADMIN(self, USUARIO_ID: int) -> bool:
        """Verifica si el usuario es administrador"""
        from core.Constantes import ROLES
        
        USUARIO = await self._REPOSITORIO.OBTENER_POR_ID(USUARIO_ID)
        
        if not USUARIO:
            return False
        
        ROLES_USUARIO = [ROL.NOMBRE for ROL in USUARIO.ROLES]
        
        return (ROLES.ADMIN in ROLES_USUARIO or 
                ROLES.SUPER_ADMIN in ROLES_USUARIO)