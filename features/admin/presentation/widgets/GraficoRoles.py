
import flet as ft
from typing import List

from core.Constantes import COLORES, TAMANOS
from ...domain.entities.EstadisticasDashboard import EstadisticaRol

class GraficoRoles(ft.Column):

    def __init__(self, estadisticas: List[EstadisticaRol] = None):
        super().__init__()
        self.spacing = TAMANOS.ESPACIADO_SM
        if estadisticas:
            self.ACTUALIZAR_DATOS(estadisticas)

    def ACTUALIZAR_DATOS(self, estadisticas: List[EstadisticaRol]):
        self.controls.clear()
        
        for stat in estadisticas:
            self.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(
                                stat.nombre_rol,
                                size=TAMANOS.TEXTO_MD,
                                weight=ft.FontWeight.BOLD,
                                expand=True,
                            ),
                            ft.Text(
                                f"{stat.cantidad_usuarios} ({stat.porcentaje:.1f}%)",
                                size=TAMANOS.TEXTO_SM,
                                color=COLORES.TEXTO_SECUNDARIO,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=ft.Padding.symmetric(vertical=TAMANOS.PADDING_XS),
                )
            )
        
        try:
            if hasattr(self, 'page') and self.page:
                self.update()
        except Exception as e:
            pass
