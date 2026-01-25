import flet as ft
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_CAJA_MOVIMIENTO, MODELO_SUCURSAL
from datetime import datetime
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
class PaginaCajaMovimientos(ft.Column):
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
                ft.Text("Caja", size=TAMANOS.TEXTO_3XL, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.ElevatedButton("Menú", icon=ICONOS.DASHBOARD, on_click=self._IR_MENU),
                ft.ElevatedButton("Salir", icon=ICONOS.CERRAR_SESION, on_click=self._SALIR, bgcolor=COLORES.PELIGRO, color=COLORES.TEXTO_BLANCO),
                ft.ElevatedButton("Nuevo", icon=ICONOS.AGREGAR, on_click=self._NUEVO),
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
        movimientos = sesion.query(MODELO_CAJA_MOVIMIENTO).order_by(MODELO_CAJA_MOVIMIENTO.FECHA.desc()).all()
        sucursales = {s.ID: s.NOMBRE for s in sesion.query(MODELO_SUCURSAL).all()}
        self._LISTA.controls.clear()

        for m in movimientos:
            suc = sucursales.get(m.SUCURSAL_ID, "")
            self._LISTA.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(m.TIPO.upper()),
                            ft.Text(m.CATEGORIA or "", size=TAMANOS.TEXTO_SM, color=COLORES.GRIS),
                            ft.Text(f"{m.MONTO} Bs"),
                            ft.Text(suc, size=TAMANOS.TEXTO_SM, color=COLORES.GRIS),
                            ft.Text(m.FECHA.strftime("%d/%m %H:%M"), size=TAMANOS.TEXTO_SM, color=COLORES.GRIS),
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
        if getattr(self, "_PAGINA", None):
            self._PAGINA.update()

    def _NUEVO(self, e):
        sesion = OBTENER_SESION()
        sucursales = sesion.query(MODELO_SUCURSAL).all()
        sesion.close()

        campo_tipo = ft.Dropdown(
            label="Tipo",
            options=[ft.dropdown.Option("ingreso", "Ingreso"), ft.dropdown.Option("egreso", "Egreso")],
            value="egreso",
        )
        campo_categoria = ft.TextField(label="Categoría", value="")
        campo_monto = ft.TextField(label="Monto", value="0")
        campo_desc = ft.TextField(label="Descripción", value="")
        opciones = [ft.dropdown.Option(s.ID, s.NOMBRE) for s in sucursales]
        campo_sucursal = ft.Dropdown(label="Sucursal", options=opciones)

        def GUARDAR(e):
            sesion = OBTENER_SESION()
            obj = MODELO_CAJA_MOVIMIENTO(
                USUARIO_ID=1,
                SUCURSAL_ID=campo_sucursal.value,
                TIPO=campo_tipo.value,
                CATEGORIA=campo_categoria.value.strip(),
                MONTO=int(campo_monto.value or 0),
                DESCRIPCION=campo_desc.value.strip(),
                FECHA=datetime.utcnow(),
            )
            sesion.add(obj)
            sesion.commit()
            sesion.close()
            self._CERRAR_DIALOGO()
            self._CARGAR()

        dlg = ft.AlertDialog(
            title=ft.Text("Movimiento de Caja"),
            content=ft.Container(
                content=ft.Column(
                    controls=[campo_tipo, campo_categoria, campo_monto, campo_desc, campo_sucursal],
                    spacing=TAMANOS.ESPACIADO_MD,
                    tight=True,
                ),
                width=420,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self._CERRAR_DIALOGO()),
                ft.ElevatedButton("Guardar", on_click=GUARDAR),
            ],
        )

        self._PAGINA.dialog = dlg
        dlg.open = True
        self._PAGINA.update()

    def _CERRAR_DIALOGO(self):
        if self._PAGINA.dialog:
            self._PAGINA.dialog.open = False
            self._PAGINA.update()

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
