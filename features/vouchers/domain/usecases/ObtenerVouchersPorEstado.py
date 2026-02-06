
from typing import List
from ..RepositorioVouchers import RepositorioVouchers
from ..entities.Voucher import Voucher

class ObtenerVouchersPorEstado:
    
    def __init__(self, repositorio: RepositorioVouchers):
        self._repositorio = repositorio
    
    def ejecutar(self, estado: str, limite: int = 50, offset: int = 0, sucursal_id: int | None = None) -> List[Voucher]:
        if estado not in ["PENDIENTE", "APROBADO", "RECHAZADO"]:
            raise ValueError(f"Estado inválido: {estado}")
        
        if limite <= 0 or limite > 100:
            limite = 50
        
        return self._repositorio.obtener_por_estado(estado, limite, offset, sucursal_id)
