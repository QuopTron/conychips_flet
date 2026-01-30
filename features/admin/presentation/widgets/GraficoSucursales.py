
import flet as ft
from typing import List

from core.Constantes import COLORES, TAMANOS, ICONOS
from ...domain.entities.EstadisticasDashboard import EstadisticaSucursal

class GraficoSucursales(ft.Column):

    def __init__(self, estadisticas: List[EstadisticaSucursal] = None):
        super().__init__()
        self.spacing = TAMANOS.ESPACIADO_SM
        if estadisticas:
            self.ACTUALIZAR_DATOS(estadisticas)

    def ACTUALIZAR_DATOS(self, estadisticas: List[EstadisticaSucursal]):
        self.controls.clear()
        
        for stat in estadisticas:
            self.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.icons.Icons.STORE,
                                size=TAMANOS.ICONO_SM,
                                color=COLORES.PRIMARIO
                            ),
                            ft.Text(
                                stat.nombre,
                                size=TAMANOS.TEXTO_MD,
                                expand=True,
                            ),
                            ft.Text(
                                f"{stat.total_pedidos} pedidos",
                                size=TAMANOS.TEXTO_SM,
                                color=COLORES.TEXTO_SECUNDARIO,
                            ),
                        ],
                    ),
                    padding=ft.Padding.symmetric(vertical=TAMANOS.PADDING_XS),
                )
            )
        
        try:
            if hasattr(self, 'page') and self.page:
                self.update()
        except Exception as e:
            pass
