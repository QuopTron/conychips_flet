
from dataclasses import dataclass
from typing import List, Optional
from ...domain.entities.Voucher import Voucher

@dataclass
class VouchersEstado:
    pass

@dataclass
class VouchersInicial(VouchersEstado):
    pass

@dataclass
class VouchersCargando(VouchersEstado):
    estado_actual: str = "PENDIENTE"

@dataclass
class VouchersCargados(VouchersEstado):
    vouchers: List[Voucher]
    total: int
    tiene_mas: bool
    estado_actual: str

@dataclass
class VouchersError(VouchersEstado):
    mensaje: str

@dataclass
class VoucherValidando(VouchersEstado):
    voucher_id: int

@dataclass
class VoucherValidado(VouchersEstado):
    mensaje: str
    vouchers: List[Voucher]
    total: int
    tiene_mas: bool
    estado_actual: str

@dataclass
class EstadisticasCargadas(VouchersEstado):
    estadisticas: dict
