from typing import List, Dict
from features.autenticacion.domain.RepositorioAutenticacion import RepositorioAutenticacion
from core.Constantes import PERMISOS_POR_ROL

class VerificarPermisos:
    
    
    def __init__(self, REPOSITORIO: RepositorioAutenticacion):
        
        self._REPOSITORIO = REPOSITORIO
    
    async def EJECUTAR(
        self, 
        USUARIO_ID: int, 
        PERMISOS_REQUERIDOS: List[str]
    ) -> Dict:
        
        try:
            USUARIO = await self._REPOSITORIO.OBTENER_POR_ID(USUARIO_ID)
            
            if not USUARIO:
                return {
                    "TIENE_PERMISOS": False,
                    "PERMISOS_FALTANTES": PERMISOS_REQUERIDOS,
                    "ROLES_USUARIO": []
                }
            
            ROLES_USUARIO = [ROL.NOMBRE for ROL in USUARIO.ROLES]
            
            PERMISOS_USUARIO = set()
            for ROL in ROLES_USUARIO:
                PERMISOS_USUARIO.update(PERMISOS_POR_ROL.get(ROL, []))
            
            if "*" in PERMISOS_USUARIO:
                return {
                    "TIENE_PERMISOS": True,
                    "PERMISOS_FALTANTES": [],
                    "ROLES_USUARIO": ROLES_USUARIO
                }
            
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
        
        from core.Constantes import ROLES
        
        USUARIO = await self._REPOSITORIO.OBTENER_POR_ID(USUARIO_ID)
        
        if not USUARIO:
            return False
        
        ROLES_USUARIO = [ROL.NOMBRE for ROL in USUARIO.ROLES]
        
        return (ROLES.ADMIN in ROLES_USUARIO or 
                ROLES.SUPER_ADMIN in ROLES_USUARIO)
