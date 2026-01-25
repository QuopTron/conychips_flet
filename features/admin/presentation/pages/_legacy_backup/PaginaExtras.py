import flet as ft
from datetime import datetime

from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION,
    MODELO_EXTRA,
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
class PaginaExtras(ft.Column):

    def __init__(self, PAGINA: ft.Page, USUARIO: Usuario):
        super().__init__()
        self._PAGINA = PAGINA
        self._USUARIO = USUARIO
        self._LISTA = ft.Column(spacing=TAMANOS.ESPACIADO_MD)
        self._CONSTRUIR()


    def _CONSTRUIR(self):
        HEADER = ft.Row(
            controls=[
                ft.Icon(
                    ft.Icons.ADD_CIRCLE,
                    size=TAMANOS.ICONO_LG,
                    color=COLORES.PRIMARIO
                ),
                ft.Text(
                    "Gestión de Extras",
                    size=TAMANOS.TEXTO_3XL,
                    weight=ft.FontWeight.BOLD,
                    color=COLORES.TEXTO
                ),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Menú",
                    icon=ICONOS.DASHBOARD,
                    on_click=self._IR_MENU,
                    bgcolor=COLORES.PRIMARIO,
                    color=COLORES.TEXTO_BLANCO
                ),
                ft.ElevatedButton(
                    "Salir",
                    icon=ICONOS.CERRAR_SESION,
                    on_click=self._SALIR,
                    bgcolor=COLORES.PELIGRO,
                    color=COLORES.TEXTO_BLANCO
                ),
                ft.ElevatedButton(
                    "Nuevo Extra",
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
        extras = sesion.query(MODELO_EXTRA).all()
        sesion.close()

        if not extras:
            self._LISTA.controls.append(
                ft.Container(
                    content=ft.Text(
                        "No hay extras registrados",
                        size=TAMANOS.TEXTO_LG,
                        color=COLORES.TEXTO_SECUNDARIO,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    alignment=ft.alignment.center,
                    padding=TAMANOS.PADDING_2XL,
                )
            )
        else:
            for ex in extras:
                self._LISTA.controls.append(self._CREAR_CARD(ex))

        if hasattr(self, "update"):
            self.update()


    def _CREAR_CARD(self, EXTRA):
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.ADD_CIRCLE,
                        size=TAMANOS.ICONO_XL,
                        color=COLORES.PRIMARIO
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(
                                EXTRA.NOMBRE,
                                size=TAMANOS.TEXTO_LG,
                                weight=ft.FontWeight.BOLD,
                                color=COLORES.TEXTO
                            ),
                            ft.Text(
                                EXTRA.DESCRIPCION or "",
                                size=TAMANOS.TEXTO_SM,
                                color=COLORES.TEXTO_SECUNDARIO
                            ),
                            ft.Row(
                                controls=[
                                        ft.Text(
                                            f"Precio: ${getattr(EXTRA, 'PRECIO', getattr(EXTRA, 'PRECIO_ADICIONAL', 0)):.2f}",
                                            size=TAMANOS.TEXTO_SM,
                                            color=COLORES.EXITO,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                    ft.Container(
                                        content=ft.Text(
                                            "DISPONIBLE" if EXTRA.DISPONIBLE else "NO DISPONIBLE",
                                            size=TAMANOS.TEXTO_XS,
                                            color=COLORES.TEXTO_BLANCO,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        bgcolor=COLORES.EXITO if EXTRA.DISPONIBLE else COLORES.PELIGRO,
                                        padding=5,
                                        border_radius=TAMANOS.RADIO_SM,
                                    ),
                                ],
                                spacing=TAMANOS.ESPACIADO_MD,
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
                                on_click=lambda e, ex=EXTRA: self._EDITAR(ex),
                            ),
                            ft.IconButton(
                                icon=ICONOS.ELIMINAR,
                                icon_color=COLORES.PELIGRO,
                                tooltip="Eliminar",
                                on_click=lambda e, ex=EXTRA: self._ELIMINAR(ex),
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
            border=ft.border.all(1, COLORES.BORDE),
        )


    def _NUEVA(self, e):
        self._ABRIR_FORMULARIO(None)


    def _EDITAR(self, EXTRA):
        self._ABRIR_FORMULARIO(EXTRA)


    def _ABRIR_FORMULARIO(self, EXTRA):
        ES_EDICION = EXTRA is not None

        CAMPO_NOMBRE = ft.TextField(
            label="Nombre",
            value=EXTRA.NOMBRE if ES_EDICION else "",
            width=TAMANOS.ANCHO_INPUT,
        )
        
        CAMPO_DESCRIPCION = ft.TextField(
            label="Descripción",
            value=EXTRA.DESCRIPCION if ES_EDICION else "",
            width=TAMANOS.ANCHO_INPUT,
            multiline=True,
            max_lines=3,
        )
        
        CAMPO_PRECIO = ft.TextField(
            label="Precio",
            value=str(EXTRA.PRECIO) if ES_EDICION else "",
            width=TAMANOS.ANCHO_INPUT,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        
        CAMPO_DISPONIBLE = ft.Checkbox(
            label="Disponible",
            value=EXTRA.DISPONIBLE if ES_EDICION else True,
        )

        def GUARDAR(e):
            if not CAMPO_NOMBRE.value:
                self._MOSTRAR_ERROR(ERRORES_VALIDACION.CAMPO_REQUERIDO)
                return

            try:
                precio = float(CAMPO_PRECIO.value) if CAMPO_PRECIO.value else 0.0
            except ValueError:
                self._MOSTRAR_ERROR("El precio debe ser un número válido")
                return

            sesion = OBTENER_SESION()
            
            if ES_EDICION:
                extra = sesion.query(MODELO_EXTRA).filter_by(ID=EXTRA.ID).first()
                extra.NOMBRE = CAMPO_NOMBRE.value
                extra.DESCRIPCION = CAMPO_DESCRIPCION.value
                extra.PRECIO = precio
                extra.DISPONIBLE = CAMPO_DISPONIBLE.value
            else:
                nuevo = MODELO_EXTRA(
                    NOMBRE=CAMPO_NOMBRE.value,
                    DESCRIPCION=CAMPO_DESCRIPCION.value,
                    PRECIO=precio,
                    DISPONIBLE=CAMPO_DISPONIBLE.value,
                )
                sesion.add(nuevo)

            sesion.commit()
            sesion.close()
            
            self._CERRAR_DIALOGO()
            self._CARGAR_DATOS()
            self._MOSTRAR_EXITO(MENSAJES_EXITO.GUARDADO_EXITOSO)

        DLG = ft.AlertDialog(
            title=ft.Text(
                "Editar Extra" if ES_EDICION else "Nuevo Extra",
                color=COLORES.TEXTO
            ),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        CAMPO_NOMBRE,
                        CAMPO_DESCRIPCION,
                        CAMPO_PRECIO,
                        CAMPO_DISPONIBLE,
                    ],
                    spacing=TAMANOS.ESPACIADO_MD,
                    tight=True,
                ),
                width=400,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self._CERRAR_DIALOGO()),
                ft.ElevatedButton(
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


    def _ELIMINAR(self, EXTRA):
        def CONFIRMAR(e):
            sesion = OBTENER_SESION()
            extra = sesion.query(MODELO_EXTRA).filter_by(ID=EXTRA.ID).first()
            
            if extra:
                sesion.delete(extra)
                sesion.commit()
            
            sesion.close()
            self._CERRAR_DIALOGO()
            self._CARGAR_DATOS()
            self._MOSTRAR_EXITO(MENSAJES_EXITO.ELIMINADO_EXITOSO)

        DLG = ft.AlertDialog(
            title=ft.Text("Confirmar Eliminación", color=COLORES.PELIGRO),
            content=ft.Text(
                f"¿Estás seguro que deseas eliminar el extra '{EXTRA.NOMBRE}'?",
                color=COLORES.TEXTO
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self._CERRAR_DIALOGO()),
                ft.ElevatedButton(
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
