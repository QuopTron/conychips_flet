from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Usuario:

    ID: Optional[int] = None
    EMAIL: str = ""
    NOMBRE_USUARIO: str = ""
    ROLES: List[str] = field(default_factory=list)
    ACTIVO: bool = True
    VERIFICADO: bool = False
    FECHA_CREACION: Optional[datetime] = None
    ULTIMA_CONEXION: Optional[datetime] = None

    def TIENE_ROL(self, ROL: str) -> bool:

        return ROL in self.ROLES

    def TIENE_PERMISO(self, PERMISO: str) -> bool:

        from core.Constantes import PERMISOS_POR_ROL

        for ROL in self.ROLES:
            PERMISOS_ROL = PERMISOS_POR_ROL.get(ROL, [])

            if "*" in PERMISOS_ROL:
                return True

            if PERMISO in PERMISOS_ROL:
                return True

        return False

    def OBTENER_PERMISOS(self) -> List[str]:

        from core.Constantes import PERMISOS_POR_ROL

        PERMISOS_TOTALES = set()
        for ROL in self.ROLES:
            PERMISOS_TOTALES.update(PERMISOS_POR_ROL.get(ROL, []))

        return list(PERMISOS_TOTALES)

    def ES_ADMIN(self) -> bool:

        from core.Constantes import ROLES

        return self.TIENE_ROL(ROLES.ADMIN) or self.TIENE_ROL(ROLES.SUPER_ADMIN)

    def PUEDE_GESTIONAR_USUARIOS(self) -> bool:

        return self.TIENE_PERMISO("usuarios.crear") or self.TIENE_PERMISO(
            "usuarios.editar"
        )

    def AGREGAR_ROL(self, ROL: str):

        if ROL not in self.ROLES:
            self.ROLES.append(ROL)

    def REMOVER_ROL(self, ROL: str):

        if ROL in self.ROLES:
            self.ROLES.remove(ROL)

    def __str__(self) -> str:
        return f"Usuario(ID={self.ID}, EMAIL={self.EMAIL}, ROLES={self.ROLES})"
