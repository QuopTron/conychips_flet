"""
Widget: Card de Estadística
Presentation Layer - Componente reutilizable
"""

import flet as ft
from core.Constantes import COLORES, TAMANOS


class CardEstadistica(ft.Container):
    """
    Widget reutilizable para mostrar una estadística
    Principio DRY - Don't Repeat Yourself
    """

    def __init__(
        self,
        icono: str,
        valor: str,
        etiqueta: str,
        color_icono: str = COLORES.PRIMARIO,
    ):
        super().__init__()
        
        self.content = ft.Column(
            controls=[
                ft.Icon(icono, size=TAMANOS.ICONO_LG, color=color_icono),
                ft.Text(
                    valor,
                    size=TAMANOS.TEXTO_4XL,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Text(
                    etiqueta,
                    size=TAMANOS.TEXTO_SM,
                    color=COLORES.TEXTO_SECUNDARIO
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=TAMANOS.ESPACIADO_XS,
        )
        
        self.padding = TAMANOS.PADDING_LG
        self.bgcolor = COLORES.FONDO_BLANCO
        self.border_radius = TAMANOS.RADIO_MD
        self.border = ft.border.all(1, COLORES.BORDE)

    def ACTUALIZAR_VALOR(self, nuevo_valor: str):
        """Actualiza el valor mostrado"""
        self.content.controls[1].value = nuevo_valor
        if hasattr(self, 'update'):
            self.update()
