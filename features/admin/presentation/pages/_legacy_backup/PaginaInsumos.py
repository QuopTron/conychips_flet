import flet as ft
from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION,
    MODELO_INSUMO,
    MODELO_SUCURSAL,
)
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
class PaginaInsumos(ft.Column):
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
                ft.Text("Insumos", size=TAMANOS.TEXTO_3XL, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.Button("Menú", icon=ICONOS.DASHBOARD, on_click=self._IR_MENU),
                ft.Button("Salir", icon=ICONOS.CERRAR_SESION, on_click=self._SALIR, bgcolor=COLORES.PELIGRO, color=COLORES.TEXTO_BLANCO),
                ft.Button("Nuevo", icon=ICONOS.AGREGAR, on_click=self._NUEVO),
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
        insumos = sesion.query(MODELO_INSUMO).all()
        sucursales = {s.ID: s.NOMBRE for s in sesion.query(MODELO_SUCURSAL).all()}
        self._LISTA.controls.clear()

        for insumo in insumos:
            suc = sucursales.get(insumo.SUCURSAL_ID, "")
            self._LISTA.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(insumo.NOMBRE),
                            ft.Text(insumo.UNIDAD, size=TAMANOS.TEXTO_SM, color=COLORES.GRIS),
                            ft.Text(str(insumo.STOCK)),
                            ft.Text(f"{insumo.COSTO_UNITARIO} Bs"),
                            ft.Text(suc, size=TAMANOS.TEXTO_SM, color=COLORES.GRIS),
                            ft.TextButton(
                                "Editar",
                                on_click=lambda e, i=insumo: self._EDITAR(i),
                            ),
                            ft.TextButton(
                                "Eliminar",
                                on_click=lambda e, i=insumo: self._ELIMINAR(i),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=TAMANOS.PADDING_MD,
                    bgcolor=COLORES.FONDO_BLANCO,
                    border_radius=TAMANOS.RADIO_SM,
                    border=ft.Border.all(1, COLORES.BORDE),
                )
            )

        sesion.close()
        if getattr(self, "_PAGINA", None):
            self._PAGINA.update()

    def _NUEVO(self, e):
        self._ABRIR_FORM()

    def _EDITAR(self, INSUMO):
        self._ABRIR_FORM(INSUMO)

    def _ELIMINAR(self, INSUMO):
        sesion = OBTENER_SESION()
        obj = sesion.query(MODELO_INSUMO).filter_by(ID=INSUMO.ID).first()
        if obj:
            sesion.delete(obj)
            sesion.commit()
        sesion.close()
        self._CARGAR()

    def _ABRIR_FORM(self, INSUMO=None):
        sesion = OBTENER_SESION()
        sucursales = sesion.query(MODELO_SUCURSAL).all()
        sesion.close()

        campo_nombre = ft.TextField(label="Nombre", value=INSUMO.NOMBRE if INSUMO else "")
        campo_unidad = ft.TextField(label="Unidad", value=INSUMO.UNIDAD if INSUMO else "unidad")
        campo_stock = ft.TextField(label="Stock", value=str(INSUMO.STOCK) if INSUMO else "0")
        campo_costo = ft.TextField(label="Costo Unitario", value=str(INSUMO.COSTO_UNITARIO) if INSUMO else "0")
        opciones = [ft.dropdown.Option(s.ID, s.NOMBRE) for s in sucursales]
        campo_sucursal = ft.Dropdown(label="Sucursal", options=opciones, value=INSUMO.SUCURSAL_ID if INSUMO else None)

        def GUARDAR(e):
            sesion = OBTENER_SESION()
            if INSUMO:
                obj = sesion.query(MODELO_INSUMO).filter_by(ID=INSUMO.ID).first()
            else:
                obj = MODELO_INSUMO()
                sesion.add(obj)

            obj.NOMBRE = campo_nombre.value.strip()
            obj.UNIDAD = campo_unidad.value.strip()
            obj.STOCK = int(campo_stock.value or 0)
            obj.COSTO_UNITARIO = int(campo_costo.value or 0)
            obj.SUCURSAL_ID = campo_sucursal.value
            sesion.commit()
            sesion.close()
            self._CERRAR_DIALOGO()
            self._CARGAR()

        dlg = ft.AlertDialog(
            title=ft.Text("Insumo"),
            content=ft.Container(
                content=ft.Column(
                    controls=[campo_nombre, campo_unidad, campo_stock, campo_costo, campo_sucursal],
                    spacing=TAMANOS.ESPACIADO_MD,
                    tight=True,
                ),
                width=420,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self._CERRAR_DIALOGO()),
                ft.Button("Guardar", on_click=GUARDAR),
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
