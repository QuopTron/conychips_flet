
import flet as ft

from core.Constantes import COLORES, TAMANOS, ICONOS
from ...domain.entities.EstadisticasDashboard import EstadisticaInventario

class GraficoInventario(ft.Column):

    def __init__(self, estadisticas: EstadisticaInventario = None):
        super().__init__()
        self.spacing = TAMANOS.ESPACIADO_SM
        if estadisticas:
            self.ACTUALIZAR_DATOS(estadisticas)

    def ACTUALIZAR_DATOS(self, estadisticas: EstadisticaInventario):
        self.controls.clear()
        
        items = [
            ("Insumos", estadisticas.total_insumos, ICONOS.INSUMOS, COLORES.INFO),
            ("Proveedores", estadisticas.total_proveedores, ICONOS.PROVEEDORES, COLORES.SECUNDARIO),
            ("Ofertas Activas", estadisticas.ofertas_activas, ft.icons.Icons.LOCAL_OFFER, COLORES.ADVERTENCIA),
            ("Extras", estadisticas.total_extras, ft.icons.Icons.ADD_CIRCLE, COLORES.PRIMARIO),
        ]
        
        for nombre, cantidad, icono, color in items:
            self.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(icono, size=TAMANOS.ICONO_SM, color=color),
                            ft.Text(
                                nombre,
                                size=TAMANOS.TEXTO_MD,
                                expand=True,
                            ),
                            ft.Container(
                                content=ft.Text(
                                    str(cantidad),
                                    size=TAMANOS.TEXTO_SM,
                                    color=COLORES.TEXTO_BLANCO,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                padding=ft.Padding.symmetric(
                                    horizontal=TAMANOS.PADDING_MD,
                                    vertical=TAMANOS.PADDING_XS
                                ),
                                bgcolor=color,
                                border_radius=TAMANOS.RADIO_FULL,
                            ),
                        ],
                        spacing=TAMANOS.ESPACIADO_SM,
                    ),
                    padding=ft.Padding.symmetric(vertical=TAMANOS.PADDING_XS),
                )
            )
        
        try:
            if hasattr(self, 'page') and self.page:
                self.update()
        except Exception as e:
            pass
