
from dataclasses import dataclass

@dataclass
class VouchersEvento:
    pass

@dataclass
class CargarVouchers(VouchersEvento):
    estado: str = "PENDIENTE"
    offset: int = 0
    sucursal_id: int | None = None

@dataclass
class CargarMasVouchers(VouchersEvento):
    pass

@dataclass
class AprobarVoucherEvento(VouchersEvento):
    voucher_id: int
    validador_id: int

@dataclass
class RechazarVoucherEvento(VouchersEvento):
    voucher_id: int
    validador_id: int
    motivo: str

@dataclass
class CambiarEstadoFiltro(VouchersEvento):
    nuevo_estado: str

@dataclass
class CargarEstadisticas(VouchersEvento):
    pass
