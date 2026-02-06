from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Rol:

    ID: Optional[int] = None
    NOMBRE: str = ""
    DESCRIPCION: str = ""
    PERMISOS: List[str] = field(default_factory=list)
    ACTIVO: bool = True

    def TIENE_PERMISO(self, PERMISO: str) -> bool:

        if "*" in self.PERMISOS:
            return True

        return PERMISO in self.PERMISOS

    def AGREGAR_PERMISO(self, PERMISO: str):

        if PERMISO not in self.PERMISOS:
            self.PERMISOS.append(PERMISO)

    def REMOVER_PERMISO(self, PERMISO: str):

        if PERMISO in self.PERMISOS:
            self.PERMISOS.remove(PERMISO)

    def ES_SUPER_ADMIN(self) -> bool:

        from core.Constantes import ROLES

        return "*" in self.PERMISOS or self.NOMBRE == ROLES.SUPERADMIN

    def __str__(self) -> str:
        return f"Rol(NOMBRE={self.NOMBRE}, PERMISOS={len(self.PERMISOS)})"
