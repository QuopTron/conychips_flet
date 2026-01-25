"""
Módulo de páginas de visualización administrativa.
Vistas especializadas de solo lectura y reportes.
"""

from .AuditoriaPage import AuditoriaPage
from .FinanzasPage import FinanzasPage
from .PedidosPage import PedidosPage
from .VouchersPage import VouchersPage
from .ResenasPage import ResenasPage

__all__ = [
    "AuditoriaPage",
    "FinanzasPage",
    "PedidosPage",
    "VouchersPage",
    "ResenasPage",
]
