import flet as ft
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_USUARIO
from core.Constantes import (
    COLORES,
    TAMANOS,
    ICONOS,
    ERRORES_AUTENTICACION,
    ERRORES_VALIDACION,
    MENSAJES_EXITO,
    MENSAJES_CONFIRMACION,
)


class PaginaPerfil(ft.Column):
    def __init__(self, PAGINA: ft.Page, USUARIO):
        super().__init__()
        self._PAGINA = PAGINA
        self._USUARIO = USUARIO
        self._CAMPO_NOMBRE = ft.TextField(
            label="Nombre de usuario", value=self._USUARIO.NOMBRE_USUARIO
        )
        self._CAMPO_EMAIL = ft.TextField(label="Email", value=self._USUARIO.EMAIL)
        self._CAMPO_FOTO = ft.TextField(
            label="URL Foto de perfil",
            value=getattr(self._USUARIO, "FOTO_PERFIL", "") or "",
        )
        self._TEXTO_ESTATUS = ft.Text("", size=12)
        self._CONSTRUIR()

    def _CONSTRUIR(self):
        HEADER = ft.Text("Mi Perfil", size=TAMANOS.TEXTO_3XL, weight=ft.FontWeight.BOLD)

        AVATAR = ft.CircleAvatar(
            content=ft.Text(
                self._USUARIO.NOMBRE_USUARIO[0].upper(),
                size=28,
                weight=ft.FontWeight.BOLD,
                color=COLORES.TEXTO_BLANCO,
            ),
            bgcolor=COLORES.PRIMARIO,
            radius=48,
        )

        BOTONES = ft.Row(
            [
                ft.Button("Guardar cambios", on_click=self._GUARDAR),
                ft.TextButton("Cancelar", on_click=self._CANCELAR),
            ],
            spacing=10,
        )

        tarjeta = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            AVATAR,
                            ft.Container(
                                content=ft.Column(
                                    [
                                        self._CAMPO_NOMBRE,
                                        self._CAMPO_EMAIL,
                                        self._CAMPO_FOTO,
                                    ]
                                ),
                                padding=10,
                            ),
                        ],
                        spacing=20,
                    ),
                    self._TEXTO_ESTATUS,
                    BOTONES,
                ],
                spacing=15,
            ),
            padding=TAMANOS.PADDING_XL,
            bgcolor=COLORES.FONDO_BLANCO,
            border_radius=TAMANOS.RADIO_MD,
            border=ft.border.all(1, COLORES.BORDE),
        )

        self.controls = [
            ft.Container(
                content=ft.Column(
                    [HEADER, ft.Container(height=TAMANOS.ESPACIADO_MD), tarjeta], spacing=TAMANOS.ESPACIADO_MD
                ),
                padding=TAMANOS.PADDING_XL,
                expand=True,
            )
        ]
        self.expand = True

    def _CANCELAR(self, e):

        if getattr(self._PAGINA, "page", None) or True:
            self._PAGINA.controls.clear()

            from features.autenticacion.presentation.pages.PaginaDashboard import (
                PaginaDashboard,
            )
            from features.autenticacion.presentation.bloc.AutenticacionBloc import (
                AutenticacionBloc,
            )

            try:
                bloc = AutenticacionBloc()
            except Exception:
                bloc = None
            self._PAGINA.controls.append(
                PaginaDashboard(self._PAGINA, self._USUARIO, bloc)
            )
            self._PAGINA.update()

    def _GUARDAR(self, e):
        sesion = OBTENER_SESION()
        modelo = sesion.query(MODELO_USUARIO).filter_by(ID=self._USUARIO.ID).first()
        if not modelo:
            self._TEXTO_ESTATUS.value = "Usuario no encontrado"
            if getattr(self, "page", None):
                self.update()
            return

        modelo.NOMBRE_USUARIO = self._CAMPO_NOMBRE.value
        modelo.EMAIL = self._CAMPO_EMAIL.value
        modelo.FOTO_PERFIL = self._CAMPO_FOTO.value
        sesion.commit()

        self._TEXTO_ESTATUS.value = "Perfil guardado correctamente"
        if getattr(self, "page", None):
            self.update()
