
from abc import ABC, abstractmethod
from typing import List, Optional
from .entities.Voucher import Voucher

class RepositorioVouchers(ABC):
    
    @abstractmethod
    def obtener_por_estado(self, estado: str, limite: int = 50, offset: int = 0) -> List[Voucher]:
        pass
    
    @abstractmethod
    def obtener_por_id(self, voucher_id: int) -> Optional[Voucher]:
        pass
    
    @abstractmethod
    def contar_por_estado(self, estado: str) -> int:
        pass
    
    @abstractmethod
    def aprobar_voucher(self, voucher_id: int, validador_id: int) -> bool:
        pass
    
    @abstractmethod
    def rechazar_voucher(self, voucher_id: int, validador_id: int, motivo: str = "") -> bool:
        pass
    
    @abstractmethod
    def obtener_estadisticas(self) -> dict:
        pass
