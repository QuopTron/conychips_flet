
from typing import List, Optional

from ..domain.RepositorioVouchers import RepositorioVouchers
from ..domain.entities.Voucher import Voucher
from .datasources.FuenteVouchersLocal import FuenteVouchersLocal

class RepositorioVouchersImpl(RepositorioVouchers):
    
    def __init__(self):
        self._fuente_local = FuenteVouchersLocal()
    
    def obtener_por_estado(self, estado: str, limite: int = 50, offset: int = 0, sucursal_id: int | None = None) -> List[Voucher]:
        return self._fuente_local.obtener_por_estado(estado, limite, offset, sucursal_id)
    
    def obtener_por_id(self, voucher_id: int) -> Optional[Voucher]:
        return self._fuente_local.obtener_por_id(voucher_id)
    
    def contar_por_estado(self, estado: str) -> int:
        return self._fuente_local.contar_por_estado(estado)
    
    def aprobar_voucher(self, voucher_id: int, validador_id: int) -> bool:
        return self._fuente_local.aprobar_voucher(voucher_id, validador_id)
    
    def rechazar_voucher(self, voucher_id: int, validador_id: int, motivo: str = "") -> bool:
        return self._fuente_local.rechazar_voucher(voucher_id, validador_id, motivo)
    
    def obtener_estadisticas(self) -> dict:
        return self._fuente_local.obtener_estadisticas()

REPOSITORIO_VOUCHERS_IMPL = RepositorioVouchersImpl()
