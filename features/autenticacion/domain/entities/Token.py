from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

@dataclass
class Token:

    ACCESS_TOKEN: str
    REFRESH_TOKEN: str
    TIPO_TOKEN: str = "Bearer"
    EXPIRA_EN: int = 900
    FECHA_CREACION: Optional[datetime] = None
    USUARIO_ID: Optional[int] = None

    def ESTA_EXPIRADO(self) -> bool:

        if not self.FECHA_CREACION:
            return True

        AHORA = datetime.now(timezone.utc)
        DIFERENCIA = (AHORA - self.FECHA_CREACION).total_seconds()

        return DIFERENCIA >= self.EXPIRA_EN

    def TIEMPO_RESTANTE(self) -> int:

        if not self.FECHA_CREACION:
            return 0

        AHORA = datetime.now(timezone.utc)
        DIFERENCIA = (AHORA - self.FECHA_CREACION).total_seconds()
        RESTANTE = self.EXPIRA_EN - DIFERENCIA

        return max(0, int(RESTANTE))

    def PORCENTAJE_VIDA(self) -> float:

        RESTANTE = self.TIEMPO_RESTANTE()
        return RESTANTE / self.EXPIRA_EN

    def DEBE_REFRESCAR(self, UMBRAL: float = 0.2) -> bool:

        return self.PORCENTAJE_VIDA() < UMBRAL

    def TO_DICT(self) -> dict:

        return {
            "access_token": self.ACCESS_TOKEN,
            "refresh_token": self.REFRESH_TOKEN,
            "token_type": self.TIPO_TOKEN,
            "expires_in": self.EXPIRA_EN,
        }
