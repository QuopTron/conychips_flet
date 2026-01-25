import flet as ft
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_PROVEEDOR
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
class PaginaProveedores(ft.Column):
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
                ft.Text("Proveedores", size=TAMANOS.TEXTO_3XL, weight=ft.FontWeight.BOLD),
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
        proveedores = sesion.query(MODELO_PROVEEDOR).all()
        self._LISTA.controls.clear()

        for p in proveedores:
            self._LISTA.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(p.NOMBRE),
                            ft.Text(p.TELEFONO or "", size=TAMANOS.TEXTO_SM, color=COLORES.GRIS),
                            ft.Text(p.EMAIL or "", size=TAMANOS.TEXTO_SM, color=COLORES.GRIS),
                            ft.TextButton("Editar", on_click=lambda e, x=p: self._EDITAR(x)),
                            ft.TextButton("Eliminar", on_click=lambda e, x=p: self._ELIMINAR(x)),
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
        self._ABRIR_FORM()

    def _EDITAR(self, PROV):
        self._ABRIR_FORM(PROV)

    def _ELIMINAR(self, PROV):
        sesion = OBTENER_SESION()
        obj = sesion.query(MODELO_PROVEEDOR).filter_by(ID=PROV.ID).first()
        if obj:
            sesion.delete(obj)
            sesion.commit()
        sesion.close()
        self._CARGAR()

    def _ABRIR_FORM(self, PROV=None):
        campo_nombre = ft.TextField(label="Nombre", value=PROV.NOMBRE if PROV else "")
        campo_tel = ft.TextField(label="Teléfono", value=PROV.TELEFONO if PROV else "")
        campo_email = ft.TextField(label="Email", value=PROV.EMAIL if PROV else "")
        campo_dir = ft.TextField(label="Dirección", value=PROV.DIRECCION if PROV else "")
        campo_ubi = ft.TextField(label="Ubicación", value=PROV.UBICACION if PROV else "")

        def GUARDAR(e):
            sesion = OBTENER_SESION()
            if PROV:
                obj = sesion.query(MODELO_PROVEEDOR).filter_by(ID=PROV.ID).first()
            else:
                obj = MODELO_PROVEEDOR()
                sesion.add(obj)

            obj.NOMBRE = campo_nombre.value.strip()
            obj.TELEFONO = campo_tel.value.strip()
            obj.EMAIL = campo_email.value.strip()
            obj.DIRECCION = campo_dir.value.strip()
            obj.UBICACION = campo_ubi.value.strip()
            sesion.commit()
            sesion.close()
            self._CERRAR_DIALOGO()
            self._CARGAR()

        dlg = ft.AlertDialog(
            title=ft.Text("Proveedor"),
            content=ft.Container(
                content=ft.Column(
                    controls=[campo_nombre, campo_tel, campo_email, campo_dir, campo_ubi],
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
