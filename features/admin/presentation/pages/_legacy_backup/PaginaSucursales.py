import flet as ft
from datetime import datetime

from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION,
    MODELO_SUCURSAL,
)
from core.Constantes import (
    COLORES,
    TAMANOS,
    ICONOS,
    ERRORES_VALIDACION,
    MENSAJES_EXITO,
)
from core.Constantes import ROLES
from features.autenticacion.domain.entities.Usuario import Usuario
from core.decoradores.DecoradorVistas import REQUIERE_ROL

@REQUIERE_ROL(ROLES.SUPERADMIN, ROLES.ADMIN)
class PaginaSucursales(ft.Column):

    def __init__(self, PAGINA: ft.Page, USUARIO: Usuario):
        super().__init__()
        self._PAGINA = PAGINA
        self._USUARIO = USUARIO
        self._LISTA = ft.Column(spacing=TAMANOS.ESPACIADO_MD)
        self._CONSTRUIR()

    def _CONSTRUIR(self):
        HEADER = ft.Row(
            controls=[
                ft.Icon(ft.icons.Icons.STORE,
                    size=TAMANOS.ICONO_LG,
                    color=COLORES.PRIMARIO
                ),
                ft.Text(
                    "Gestión de Sucursales",
                    size=TAMANOS.TEXTO_3XL,
                    weight=ft.FontWeight.BOLD,
                    color=COLORES.TEXTO
                ),
                ft.Container(expand=True),
                ft.Button(
                    "Menú",
                    icon=ICONOS.DASHBOARD,
                    on_click=self._IR_MENU,
                    bgcolor=COLORES.PRIMARIO,
                    color=COLORES.TEXTO_BLANCO
                ),
                ft.Button(
                    "Salir",
                    icon=ICONOS.CERRAR_SESION,
                    on_click=self._SALIR,
                    bgcolor=COLORES.PELIGRO,
                    color=COLORES.TEXTO_BLANCO
                ),
                ft.Button(
                    "Nueva Sucursal",
                    icon=ICONOS.AGREGAR,
                    on_click=self._NUEVA,
                    bgcolor=COLORES.EXITO,
                    color=COLORES.TEXTO_BLANCO
                ),
            ],
            spacing=TAMANOS.ESPACIADO_MD,
        )

        self.controls = [
            ft.Container(
                content=ft.Column(
                    controls=[
                        HEADER,
                        ft.Divider(height=1, color=COLORES.BORDE),
                        self._LISTA,
                    ],
                    spacing=TAMANOS.ESPACIADO_LG,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=TAMANOS.PADDING_XL,
                expand=True,
                bgcolor=COLORES.FONDO,
            )
        ]
        self.expand = True
        self._CARGAR_DATOS()

    def _CARGAR_DATOS(self):
        self._LISTA.controls.clear()
        
        sesion = OBTENER_SESION()
        sucursales = sesion.query(MODELO_SUCURSAL).all()
        sesion.close()

        if not sucursales:
            self._LISTA.controls.append(
                ft.Container(
                    content=ft.Text(
                        "No hay sucursales registradas",
                        size=TAMANOS.TEXTO_LG,
                        color=COLORES.TEXTO_SECUNDARIO,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    alignment=ft.Alignment(0, 0),
                    padding=TAMANOS.PADDING_2XL,
                )
            )
        else:
            for s in sucursales:
                self._LISTA.controls.append(self._CREAR_CARD(s))

        if getattr(self, "_PAGINA", None):
            self._PAGINA.update()

    def _CREAR_CARD(self, SUCURSAL):
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.icons.Icons.STORE,
                        size=TAMANOS.ICONO_XL,
                        color=COLORES.PRIMARIO
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(
                                SUCURSAL.NOMBRE,
                                size=TAMANOS.TEXTO_LG,
                                weight=ft.FontWeight.BOLD,
                                color=COLORES.TEXTO
                            ),
                            ft.Text(
                                SUCURSAL.DIRECCION or "",
                                size=TAMANOS.TEXTO_SM,
                                color=COLORES.TEXTO_SECUNDARIO
                            ),
                            ft.Text(
                                        f"Teléfono: {getattr(SUCURSAL, 'TELEFONO', 'N/A')}",
                                size=TAMANOS.TEXTO_SM,
                                color=COLORES.TEXTO_SECUNDARIO
                            ),
                        ],
                        spacing=TAMANOS.ESPACIADO_XS,
                        expand=True,
                    ),
                    ft.Row(
                        controls=[
                            ft.IconButton(
                                icon=ICONOS.EDITAR,
                                icon_color=COLORES.INFO,
                                tooltip="Editar",
                                on_click=lambda e, suc=SUCURSAL: self._EDITAR(suc),
                            ),
                            ft.IconButton(
                                icon=ICONOS.ELIMINAR,
                                icon_color=COLORES.PELIGRO,
                                tooltip="Eliminar",
                                on_click=lambda e, suc=SUCURSAL: self._ELIMINAR(suc),
                            ),
                        ],
                        spacing=TAMANOS.ESPACIADO_SM,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=TAMANOS.PADDING_LG,
            bgcolor=COLORES.FONDO_BLANCO,
            border_radius=TAMANOS.RADIO_MD,
            border=ft.Border.all(1, COLORES.BORDE),
        )

    def _NUEVA(self, e):
        self._ABRIR_FORMULARIO(None)

    def _EDITAR(self, SUCURSAL):
        self._ABRIR_FORMULARIO(SUCURSAL)

    def _ABRIR_FORMULARIO(self, SUCURSAL):
        ES_EDICION = SUCURSAL is not None

        CAMPO_NOMBRE = ft.TextField(
            label="Nombre",
            value=SUCURSAL.NOMBRE if ES_EDICION else "",
            width=TAMANOS.ANCHO_INPUT,
        )
        
        CAMPO_DIRECCION = ft.TextField(
            label="Dirección",
            value=SUCURSAL.DIRECCION if ES_EDICION else "",
            width=TAMANOS.ANCHO_INPUT,
            multiline=True,
            max_lines=3,
        )
        
        CAMPO_TELEFONO = ft.TextField(
            label="Teléfono",
            value=SUCURSAL.TELEFONO if ES_EDICION else "",
            width=TAMANOS.ANCHO_INPUT,
        )
        
        CAMPO_UBICACION = ft.TextField(
            label="Ubicación (coordenadas o referencia)",
            value=SUCURSAL.UBICACION if ES_EDICION else "",
            width=TAMANOS.ANCHO_INPUT,
        )

        def GUARDAR(e):
            if not CAMPO_NOMBRE.value:
                self._MOSTRAR_ERROR(ERRORES_VALIDACION.CAMPO_REQUERIDO)
                return

            sesion = OBTENER_SESION()
            
            if ES_EDICION:
                sucursal = sesion.query(MODELO_SUCURSAL).filter_by(ID=SUCURSAL.ID).first()
                sucursal.NOMBRE = CAMPO_NOMBRE.value
                sucursal.DIRECCION = CAMPO_DIRECCION.value
                sucursal.TELEFONO = CAMPO_TELEFONO.value
                sucursal.UBICACION = CAMPO_UBICACION.value
            else:
                nueva = MODELO_SUCURSAL(
                    NOMBRE=CAMPO_NOMBRE.value,
                    DIRECCION=CAMPO_DIRECCION.value,
                    TELEFONO=CAMPO_TELEFONO.value,
                    UBICACION=CAMPO_UBICACION.value,
                )
                sesion.add(nueva)

            sesion.commit()
            sesion.close()
            
            self._CERRAR_DIALOGO()
            self._CARGAR_DATOS()
            self._MOSTRAR_EXITO(MENSAJES_EXITO.GUARDADO_EXITOSO)

        DLG = ft.AlertDialog(
            title=ft.Text(
                "Editar Sucursal" if ES_EDICION else "Nueva Sucursal",
                color=COLORES.TEXTO
            ),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        CAMPO_NOMBRE,
                        CAMPO_DIRECCION,
                        CAMPO_TELEFONO,
                        CAMPO_UBICACION,
                    ],
                    spacing=TAMANOS.ESPACIADO_MD,
                    tight=True,
                ),
                width=400,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self._CERRAR_DIALOGO()),
                ft.Button(
                    "Guardar",
                    icon=ICONOS.GUARDAR,
                    on_click=GUARDAR,
                    bgcolor=COLORES.PRIMARIO,
                    color=COLORES.TEXTO_BLANCO
                ),
            ],
        )

        self._PAGINA.dialog = DLG
        DLG.open = True
        self._PAGINA.update()

    def _ELIMINAR(self, SUCURSAL):
        def CONFIRMAR(e):
            sesion = OBTENER_SESION()
            sucursal = sesion.query(MODELO_SUCURSAL).filter_by(ID=SUCURSAL.ID).first()
            
            if sucursal:
                sesion.delete(sucursal)
                sesion.commit()
            
            sesion.close()
            self._CERRAR_DIALOGO()
            self._CARGAR_DATOS()
            self._MOSTRAR_EXITO(MENSAJES_EXITO.ELIMINADO_EXITOSO)

        DLG = ft.AlertDialog(
            title=ft.Text("Confirmar Eliminación", color=COLORES.PELIGRO),
            content=ft.Text(
                f"¿Estás seguro que deseas eliminar la sucursal '{SUCURSAL.NOMBRE}'?",
                color=COLORES.TEXTO
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self._CERRAR_DIALOGO()),
                ft.Button(
                    "Eliminar",
                    icon=ICONOS.ELIMINAR,
                    on_click=CONFIRMAR,
                    bgcolor=COLORES.PELIGRO,
                    color=COLORES.TEXTO_BLANCO
                ),
            ],
        )

        self._PAGINA.dialog = DLG
        DLG.open = True
        self._PAGINA.update()

    def _CERRAR_DIALOGO(self):
        if hasattr(self._PAGINA, "dialog") and self._PAGINA.dialog:
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

    def _MOSTRAR_ERROR(self, MENSAJE: str):
        snackbar = ft.SnackBar(
            content=ft.Text(MENSAJE, color=COLORES.TEXTO_BLANCO),
            bgcolor=COLORES.PELIGRO,
        )
        self._PAGINA.overlay.append(snackbar)
        snackbar.open = True
        self._PAGINA.update()

    def _MOSTRAR_EXITO(self, MENSAJE: str):
        snackbar = ft.SnackBar(
            content=ft.Text(MENSAJE, color=COLORES.TEXTO_BLANCO),
            bgcolor=COLORES.EXITO,
        )
        self._PAGINA.overlay.append(snackbar)
        snackbar.open = True
        self._PAGINA.update()
