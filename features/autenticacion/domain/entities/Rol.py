"""
ENTIDAD DE DOMINIO: ROL
=======================
Representa un rol del sistema con sus permisos asociados
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Rol:
    """
    Entidad que representa un rol del sistema
    """
    
    ID: Optional[int] = None
    NOMBRE: str = ""
    DESCRIPCION: str = ""
    PERMISOS: List[str] = field(default_factory=list)
    ACTIVO: bool = True
    
    def TIENE_PERMISO(self, PERMISO: str) -> bool:
        """
        Verifica si el rol tiene un permiso específico
        
        Args:
            PERMISO: Nombre del permiso a verificar
            
        Returns:
            True si tiene el permiso, False si no
        """
        # Permiso comodín - tiene todos los permisos
        if "*" in self.PERMISOS:
            return True
        
        return PERMISO in self.PERMISOS
    
    def AGREGAR_PERMISO(self, PERMISO: str):
        """Agrega un permiso al rol"""
        if PERMISO not in self.PERMISOS:
            self.PERMISOS.append(PERMISO)
    
    def REMOVER_PERMISO(self, PERMISO: str):
        """Remueve un permiso del rol"""
        if PERMISO in self.PERMISOS:
            self.PERMISOS.remove(PERMISO)
    
    def ES_SUPER_ADMIN(self) -> bool:
        """Verifica si es rol de super administrador"""
        return "*" in self.PERMISOS or self.NOMBRE == "super_admin"
    
    def __str__(self) -> str:
        return f"Rol(NOMBRE={self.NOMBRE}, PERMISOS={len(self.PERMISOS)})"