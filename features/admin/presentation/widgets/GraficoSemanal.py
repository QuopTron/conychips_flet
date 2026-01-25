"""
Widget: Gráfico Semanal
Presentation Layer - Componente reutilizable
"""

import flet as ft
from typing import List

from core.Constantes import COLORES, TAMANOS
from ...domain.entities.EstadisticasDashboard import EstadisticaDiaria


class GraficoSemanal(ft.Column):
    """
    Widget para mostrar pedidos de la última semana
    Componente reutilizable
    """

    def __init__(self, estadisticas: List[EstadisticaDiaria] = None):
        super().__init__()
        self.spacing = TAMANOS.ESPACIADO_SM
        if estadisticas:
            self.ACTUALIZAR_DATOS(estadisticas)

    def ACTUALIZAR_DATOS(self, estadisticas: List[EstadisticaDiaria]):
        """Actualiza los datos mostrados"""
        self.controls.clear()
        
        for stat in estadisticas:
            self.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(
                                stat.nombre_dia,
                                size=TAMANOS.TEXTO_SM,
                                width=40,
                            ),
                            ft.Container(
                                content=ft.Text(
                                    str(stat.total_pedidos),
                                    size=TAMANOS.TEXTO_SM,
                                    color=COLORES.TEXTO_BLANCO,
                                ),
                                padding=ft.padding.symmetric(
                                    horizontal=TAMANOS.PADDING_SM,
                                    vertical=TAMANOS.PADDING_XS
                                ),
                                bgcolor=COLORES.EXITO,
                                border_radius=TAMANOS.RADIO_SM,
                                width=max(stat.total_pedidos * 10, 30),
                            ),
                        ],
                        spacing=TAMANOS.ESPACIADO_SM,
                    ),
                    padding=ft.padding.symmetric(vertical=TAMANOS.PADDING_XS),
                )
            )
        
        if hasattr(self, 'update'):
            self.update()
