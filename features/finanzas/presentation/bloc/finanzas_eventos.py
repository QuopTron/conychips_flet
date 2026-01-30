"""
Eventos del BLoC de Finanzas
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


class EventoFinanzas:
    """Evento base"""
    pass


class CargarResumenFinanciero(EventoFinanzas):
    """Cargar resumen financiero completo"""
    pass


@dataclass
class FiltrarPorEstado(EventoFinanzas):
    """Filtrar pedidos por estado"""
    estado: Optional[str]  # None = todos, "COMPLETADO", "PENDIENTE", "CANCELADO"


@dataclass
class FiltrarPorFecha(EventoFinanzas):
    """Filtrar por rango de fechas"""
    fecha_inicio: datetime
    fecha_fin: datetime


@dataclass
class BuscarPorCodigo(EventoFinanzas):
    """Buscar pedido por código"""
    codigo: str


@dataclass
class VerDetallePedido(EventoFinanzas):
    """Ver detalle de un pedido específico"""
    pedido_id: int


@dataclass
class FiltrarConOfertas(EventoFinanzas):
    """Filtrar solo pedidos con ofertas aplicadas"""
    solo_con_ofertas: bool = True


@dataclass
class FiltrarVoucherEstado(EventoFinanzas):
    """Filtrar por estado de voucher"""
    voucher_estado: Optional[str]  # "APROBADO", "RECHAZADO", "PENDIENTE"
