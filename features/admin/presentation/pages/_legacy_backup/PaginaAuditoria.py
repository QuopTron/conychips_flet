import flet as ft
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_AUDITORIA
from core.Constantes import (
    COLORES,
    TAMANOS,
    ICONOS,
    ERRORES_AUTENTICACION,
    ERRORES_VALIDACION,
    MENSAJES_EXITO,
)
from core.decoradores.DecoradorVistas import REQUIERE_ROL
from core.Constantes import ROLES


@REQUIERE_ROL(ROLES.SUPERADMIN)
class PaginaAuditoria(ft.Column):
    def __init__(self, PAGINA: ft.Page, USUARIO):
        super().__init__()
        self._PAGINA = PAGINA
        self._USUARIO = USUARIO
        self._LISTA = ft.Column(spacing=10)
        self._CONSTRUIR()
        self._CARGAR()

    def _CONSTRUIR(self):
        header = ft.Row(
            controls=[
                ft.Text("Auditoría", size=TAMANOS.TEXTO_3XL, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.ElevatedButton("Menú", icon=ICONOS.DASHBOARD, on_click=self._IR_MENU),
                ft.ElevatedButton("Salir", icon=ICONOS.CERRAR_SESION, on_click=self._SALIR, bgcolor=COLORES.PELIGRO, color=COLORES.TEXTO_BLANCO),
            ],
            spacing=TAMANOS.ESPACIADO_MD,
        )

        self.controls = [
            ft.Container(
                content=ft.Column(
                    controls=[header, self._LISTA],
                    spacing=TAMANOS.ESPACIADO_LG,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=TAMANOS.PADDING_XL,
                expand=True,
            )
        ]
        self.expand = True

    def _CARGAR(self):
        sesion = OBTENER_SESION()
        eventos = sesion.query(MODELO_AUDITORIA).order_by(MODELO_AUDITORIA.FECHA.desc()).all()
        self._LISTA.controls.clear()

        for ev in eventos:
            self._LISTA.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(ev.ACCION),
                            ft.Text(ev.ENTIDAD or "", size=TAMANOS.TEXTO_SM, color=COLORES.GRIS),
                            ft.Text(str(ev.ENTIDAD_ID or ""), size=TAMANOS.TEXTO_SM, color=COLORES.GRIS),
                            ft.Text(ev.FECHA.strftime("%d/%m %H:%M"), size=TAMANOS.TEXTO_SM, color=COLORES.GRIS),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=TAMANOS.PADDING_MD,
                    bgcolor=COLORES.FONDO_BLANCO,
                    border_radius=TAMANOS.RADIO_SM,
                    border=ft.border.all(1, COLORES.BORDE),
                )
            )

        sesion.close()
        if getattr(self, "page", None):
            self.update()

    def _IR_MENU(self, e):
        from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin

        self._PAGINA.controls.clear()
        self._PAGINA.controls.append(PaginaAdmin(self._PAGINA, self._USUARIO))
        self._PAGINA.update()

    def _SALIR(self, e):
        from features.autenticacion.presentation.pages.PaginaLogin import PaginaLogin

        self._PAGINA.controls.clear()
        self._PAGINA.controls.append(PaginaLogin(self._PAGINA))
        self._PAGINA.update()
