"""
ENTIDAD DE DOMINIO: TOKEN
=========================
Representa un par de tokens JWT (Access + Refresh)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Token:
    """
    Entidad que representa tokens de autenticación
    """
    
    ACCESS_TOKEN: str
    REFRESH_TOKEN: str
    TIPO_TOKEN: str = "Bearer"
    EXPIRA_EN: int = 900  # 15 minutos en segundos
    FECHA_CREACION: Optional[datetime] = None
    USUARIO_ID: Optional[int] = None
    
    def ESTA_EXPIRADO(self) -> bool:
        """
        Verifica si el access token está expirado
        
        Returns:
            True si está expirado, False si no
        """
        if not self.FECHA_CREACION:
            return True
        
        AHORA = datetime.utcnow()
        DIFERENCIA = (AHORA - self.FECHA_CREACION).total_seconds()
        
        return DIFERENCIA >= self.EXPIRA_EN
    
    def TIEMPO_RESTANTE(self) -> int:
        """
        Calcula tiempo restante antes de expiración
        
        Returns:
            Segundos restantes (0 si ya expiró)
        """
        if not self.FECHA_CREACION:
            return 0
        
        AHORA = datetime.utcnow()
        DIFERENCIA = (AHORA - self.FECHA_CREACION).total_seconds()
        RESTANTE = self.EXPIRA_EN - DIFERENCIA
        
        return max(0, int(RESTANTE))
    
    def PORCENTAJE_VIDA(self) -> float:
        """
        Retorna porcentaje de vida útil del token
        
        Returns:
            Valor entre 0.0 (expirado) y 1.0 (nuevo)
        """
        RESTANTE = self.TIEMPO_RESTANTE()
        return RESTANTE / self.EXPIRA_EN
    
    def DEBE_REFRESCAR(self, UMBRAL: float = 0.2) -> bool:
        """
        Indica si debería refrescarse el token
        
        Args:
            UMBRAL: Porcentaje mínimo de vida (default 20%)
            
        Returns:
            True si debe refrescarse, False si no
        """
        return self.PORCENTAJE_VIDA() < UMBRAL
    
    def TO_DICT(self) -> dict:
        """Convierte a diccionario para serialización"""
        return {
            "access_token": self.ACCESS_TOKEN,
            "refresh_token": self.REFRESH_TOKEN,
            "token_type": self.TIPO_TOKEN,
            "expires_in": self.EXPIRA_EN
        }