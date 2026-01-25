import flet as ft
from typing import Optional, Callable


class BotonPrimario(ft.Column):

    def __init__(
        self,
        TEXTO: str,
        AL_HACER_CLIC: Optional[Callable] = None,
        ICONO: Optional[str] = None,
        ANCHO: Optional[float] = None,
        ALTURA: float = 50,
        COLOR_FONDO: str = ft.Colors.BLUE_600,
        COLOR_TEXTO: str = ft.Colors.WHITE,
        EXPANDIR: bool = False,
    ):
        super().__init__()
        self._TEXTO = TEXTO
        self._AL_HACER_CLIC = AL_HACER_CLIC
        self._ICONO = ICONO
        self._ANCHO = ANCHO
        self._ALTURA = ALTURA
        self._COLOR_FONDO = COLOR_FONDO
        self._COLOR_TEXTO = COLOR_TEXTO
        self._EXPANDIR = EXPANDIR

        self._CARGANDO = False
        self._BOTON: Optional[ft.Button] = None

        self._CONSTRUIR()

    def _CONSTRUIR(self):

        CONTENIDO = []

        if self._ICONO:
            CONTENIDO.append(ft.Icon(self._ICONO, color=self._COLOR_TEXTO, size=20))

        CONTENIDO.append(
            ft.Text(
                value=self._TEXTO,
                color=self._COLOR_TEXTO,
                size=16,
                weight=ft.FontWeight.W_600,
            )
        )

        self._BOTON = ft.Button(
            content=ft.Row(
                controls=CONTENIDO, alignment=ft.MainAxisAlignment.CENTER, spacing=10
            ),
            on_click=self._MANEJAR_CLIC,
            style=ft.ButtonStyle(
                color=self._COLOR_TEXTO,
                bgcolor=self._COLOR_FONDO,
                shape=ft.RoundedRectangleBorder(radius=10),
                elevation=3,
                padding=ft.Padding.symmetric(horizontal=20, vertical=15),
            ),
            width=self._ANCHO if not self._EXPANDIR else None,
            height=self._ALTURA,
            expand=self._EXPANDIR,
        )

        self.controls = [self._BOTON]

    async def _MANEJAR_CLIC(self, e):

        if self._CARGANDO or not self._AL_HACER_CLIC:
            return

        self.ESTABLECER_CARGANDO(True)

        try:
            if self._AL_HACER_CLIC:
                await self._AL_HACER_CLIC(e)
        finally:
            self.ESTABLECER_CARGANDO(False)

    def ESTABLECER_CARGANDO(self, CARGANDO: bool):

        self._CARGANDO = CARGANDO

        if self._BOTON:
            if CARGANDO:
                self._BOTON.content = ft.Row(
                    controls=[
                        ft.ProgressRing(
                            width=20, height=20, stroke_width=2, color=self._COLOR_TEXTO
                        ),
                        ft.Text(
                            value="Procesando...",
                            color=self._COLOR_TEXTO,
                            size=16,
                            weight=ft.FontWeight.W_600,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                )
                self._BOTON.disabled = True
            else:
                CONTENIDO = []

                if self._ICONO:
                    CONTENIDO.append(
                        ft.Icon(self._ICONO, color=self._COLOR_TEXTO, size=20)
                    )

                CONTENIDO.append(
                    ft.Text(
                        value=self._TEXTO,
                        color=self._COLOR_TEXTO,
                        size=16,
                        weight=ft.FontWeight.W_600,
                    )
                )

                self._BOTON.content = ft.Row(
                    controls=CONTENIDO,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                )
                self._BOTON.disabled = False

            self.update()

    def CAMBIAR_TEXTO(self, NUEVO_TEXTO: str):

        self._TEXTO = NUEVO_TEXTO
        if not self._CARGANDO and self._BOTON:
            CONTENIDO = []

            if self._ICONO:
                CONTENIDO.append(ft.Icon(self._ICONO, color=self._COLOR_TEXTO, size=20))

            CONTENIDO.append(
                ft.Text(
                    value=self._TEXTO,
                    color=self._COLOR_TEXTO,
                    size=16,
                    weight=ft.FontWeight.W_600,
                )
            )

            self._BOTON.content = ft.Row(
                controls=CONTENIDO, alignment=ft.MainAxisAlignment.CENTER, spacing=10
            )
            self.update()
