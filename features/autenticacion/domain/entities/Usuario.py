"""
ENTIDAD DE DOMINIO: USUARIO
===========================
Representa un usuario del sistema con sus roles y permisos
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Usuario:
    """
    Entidad de usuario del dominio (Clean Architecture)
    
    Esta es la representación de usuario en la capa de dominio,
    independiente de framework o base de datos.
    """
    
    ID: Optional[int] = None
    EMAIL: str = ""
    NOMBRE_USUARIO: str = ""
    ROLES: List[str] = field(default_factory=list)
    ACTIVO: bool = True
    VERIFICADO: bool = False
    FECHA_CREACION: Optional[datetime] = None
    ULTIMA_CONEXION: Optional[datetime] = None
    
    def TIENE_ROL(self, ROL: str) -> bool:
        """Verifica si el usuario tiene un rol específico"""
        return ROL in self.ROLES
    
    def TIENE_PERMISO(self, PERMISO: str) -> bool:
        """
        Verifica si el usuario tiene un permiso específico
        basándose en sus roles
        """
        from core.Constantes import PERMISOS_POR_ROL
        
        for ROL in self.ROLES:
            PERMISOS_ROL = PERMISOS_POR_ROL.get(ROL, [])
            
            # Si el rol tiene permiso "*", tiene todos los permisos
            if "*" in PERMISOS_ROL:
                return True
            
            if PERMISO in PERMISOS_ROL:
                return True
        
        return False
    
    def OBTENER_PERMISOS(self) -> List[str]:
        """Retorna lista de todos los permisos del usuario"""
        from core.Constantes import PERMISOS_POR_ROL
        
        PERMISOS_TOTALES = set()
        for ROL in self.ROLES:
            PERMISOS_TOTALES.update(PERMISOS_POR_ROL.get(ROL, []))
        
        return list(PERMISOS_TOTALES)
    
    def ES_ADMIN(self) -> bool:
        """Verifica si es administrador o super admin"""
        from core.Constantes import ROLES
        return self.TIENE_ROL(ROLES.ADMIN) or self.TIENE_ROL(ROLES.SUPER_ADMIN)
    
    def PUEDE_GESTIONAR_USUARIOS(self) -> bool:
        """Verifica si puede crear/editar usuarios"""
        return self.TIENE_PERMISO("usuarios.crear") or self.TIENE_PERMISO("usuarios.editar")
    
    def AGREGAR_ROL(self, ROL: str):
        """Agrega un rol al usuario si no lo tiene"""
        if ROL not in self.ROLES:
            self.ROLES.append(ROL)
    
    def REMOVER_ROL(self, ROL: str):
        """Remueve un rol del usuario"""
        if ROL in self.ROLES:
            self.ROLES.remove(ROL)
    
    def __str__(self) -> str:
        return f"Usuario(ID={self.ID}, EMAIL={self.EMAIL}, ROLES={self.ROLES})"