"""
Estados del BLoC de Finanzas
"""
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class ResumenFinanciero:
    """Resumen financiero del período"""
    total_ingresos: int  # En centavos de Bs
    total_egresos: int
    utilidad_neta: int
    total_pedidos: int
    pedidos_completados: int
    pedidos_cancelados: int
    pedidos_pendientes: int
    vouchers_aprobados: int
    vouchers_rechazados: int
    vouchers_pendientes: int


@dataclass
class PedidoResumen:
    """Resumen de un pedido para tabla"""
    id: int
    codigo: str
    cliente: str
    fecha: datetime
    estado: str
    monto_total: int  # En centavos de Bs
    tiene_voucher: bool
    voucher_estado: Optional[str]
    tiene_oferta: bool


class EstadoFinanzas:
    """Estado base"""
    pass


class EstadoFinanzasInicial(EstadoFinanzas):
    """Estado inicial"""
    pass


@dataclass
class EstadoFinanzasCargando(EstadoFinanzas):
    """Estado de carga"""
    mensaje: str = "Cargando datos financieros..."


@dataclass
class EstadoFinanzasCargado(EstadoFinanzas):
    """Estado con datos cargados"""
    resumen: ResumenFinanciero
    pedidos: List[PedidoResumen]
    filtro_estado: Optional[str] = None
    filtro_fecha_inicio: Optional[datetime] = None
    filtro_fecha_fin: Optional[datetime] = None
    busqueda_codigo: Optional[str] = None
    pedido_seleccionado: Optional[PedidoResumen] = None


@dataclass
class EstadoFinanzasError(EstadoFinanzas):
    """Estado de error"""
    mensaje: str
    error: Optional[Exception] = None
