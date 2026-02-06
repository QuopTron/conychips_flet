
import flet as ft
from core.Constantes import COLORES, TAMANOS

class CardEstadistica(ft.Container):

    def __init__(
        self,
        icono: str = None,
        valor: str = "",
        etiqueta: str = None,
        color_icono: str = COLORES.PRIMARIO,
        *,
        titulo: str = None,
        color: str = None,
    ):
        super().__init__()
        if titulo is not None and etiqueta is None:
            etiqueta = titulo
        if color is not None:
            color_icono = color

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
        self.border_radius = TAMANOS.RADIO_BORDE
        self.border = ft.Border.all(1, COLORES.BORDE)

    def ACTUALIZAR_VALOR(self, nuevo_valor: str):
        if self.content and len(self.content.controls) > 1:
            self.content.controls[1].value = nuevo_valor
            try:
                if hasattr(self, 'page') and self.page:
                    self.update()
            except Exception as e:
                pass
