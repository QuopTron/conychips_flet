import flet as ft
from datetime import datetime

from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION,
    MODELO_OFERTA,
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
class PaginaOfertas(ft.Column):

    def __init__(self, PAGINA: ft.Page, USUARIO: Usuario):
        super().__init__()
        self._PAGINA = PAGINA
        self._USUARIO = USUARIO
        self._LISTA = ft.Column(spacing=TAMANOS.ESPACIADO_MD)
        self._CONSTRUIR()

    def _CONSTRUIR(self):
        HEADER = ft.Row(
            controls=[
                ft.Icon(ft.icons.Icons.LOCAL_OFFER,
                    size=TAMANOS.ICONO_LG,
                    color=COLORES.ADVERTENCIA
                ),
                ft.Text(
                    "Gestión de Ofertas",
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
                    "Nueva Oferta",
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
        ofertas = sesion.query(MODELO_OFERTA).all()
        sesion.close()

        if not ofertas:
            self._LISTA.controls.append(
                ft.Container(
                    content=ft.Text(
                        "No hay ofertas registradas",
                        size=TAMANOS.TEXTO_LG,
                        color=COLORES.TEXTO_SECUNDARIO,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    alignment=ft.Alignment(0, 0),
                    padding=TAMANOS.PADDING_2XL,
                )
            )
        else:
            for of in ofertas:
                self._LISTA.controls.append(self._CREAR_CARD(of))

        if hasattr(self, "update"):
            self.update()

    def _CREAR_CARD(self, OFERTA):
        fecha_inicio = OFERTA.FECHA_INICIO if OFERTA.FECHA_INICIO else "N/A"
        fecha_fin = OFERTA.FECHA_FIN if OFERTA.FECHA_FIN else "N/A"
        
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.icons.Icons.LOCAL_OFFER,
                        size=TAMANOS.ICONO_XL,
                        color=COLORES.ADVERTENCIA
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(
                                OFERTA.NOMBRE,
                                size=TAMANOS.TEXTO_LG,
                                weight=ft.FontWeight.BOLD,
                                color=COLORES.TEXTO
                            ),
                            ft.Text(
                                OFERTA.DESCRIPCION or "",
                                size=TAMANOS.TEXTO_SM,
                                color=COLORES.TEXTO_SECUNDARIO
                            ),
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        f"Descuento: {OFERTA.DESCUENTO}%",
                                        size=TAMANOS.TEXTO_SM,
                                        color=COLORES.ADVERTENCIA,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        f"Desde: {fecha_inicio}",
                                        size=TAMANOS.TEXTO_XS,
                                        color=COLORES.TEXTO_SECUNDARIO,
                                    ),
                                    ft.Text(
                                        f"Hasta: {fecha_fin}",
                                        size=TAMANOS.TEXTO_XS,
                                        color=COLORES.TEXTO_SECUNDARIO,
                                    ),
                                    ft.Container(
                                        content=ft.Text(
                                            "ACTIVA" if OFERTA.ACTIVA else "INACTIVA",
                                            size=TAMANOS.TEXTO_XS,
                                            color=COLORES.TEXTO_BLANCO,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        bgcolor=COLORES.EXITO if OFERTA.ACTIVA else COLORES.PELIGRO,
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
                                on_click=lambda e, of=OFERTA: self._EDITAR(of),
                            ),
                            ft.IconButton(
                                icon=ICONOS.ELIMINAR,
                                icon_color=COLORES.PELIGRO,
                                tooltip="Eliminar",
                                on_click=lambda e, of=OFERTA: self._ELIMINAR(of),
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

    def _EDITAR(self, OFERTA):
        self._ABRIR_FORMULARIO(OFERTA)

    def _ABRIR_FORMULARIO(self, OFERTA):
        ES_EDICION = OFERTA is not None

        CAMPO_NOMBRE = ft.TextField(
            label="Nombre",
            value=OFERTA.NOMBRE if ES_EDICION else "",
            width=TAMANOS.ANCHO_INPUT,
        )
        
        CAMPO_DESCRIPCION = ft.TextField(
            label="Descripción",
            value=OFERTA.DESCRIPCION if ES_EDICION else "",
            width=TAMANOS.ANCHO_INPUT,
            multiline=True,
            max_lines=3,
        )
        
        CAMPO_DESCUENTO = ft.Dropdown(
            label="Descuento",
            value=str(OFERTA.DESCUENTO) if ES_EDICION else "10",
            width=TAMANOS.ANCHO_INPUT,
            options=[
                ft.dropdown.Option("5", "5%"),
                ft.dropdown.Option("10", "10%"),
                ft.dropdown.Option("15", "15%"),
                ft.dropdown.Option("20", "20%"),
                ft.dropdown.Option("25", "25%"),
                ft.dropdown.Option("30", "30%"),
                ft.dropdown.Option("50", "50%"),
            ],
        )
        
        CAMPO_FECHA_INICIO = ft.TextField(
            label="Fecha Inicio (YYYY-MM-DD)",
            value=OFERTA.FECHA_INICIO if ES_EDICION else "",
            width=TAMANOS.ANCHO_INPUT,
        )
        
        CAMPO_FECHA_FIN = ft.TextField(
            label="Fecha Fin (YYYY-MM-DD)",
            value=OFERTA.FECHA_FIN if ES_EDICION else "",
            width=TAMANOS.ANCHO_INPUT,
        )
        
        CAMPO_ACTIVA = ft.Checkbox(
            label="Activa",
            value=OFERTA.ACTIVA if ES_EDICION else True,
        )

        def GUARDAR(e):
            if not CAMPO_NOMBRE.value:
                self._MOSTRAR_ERROR(ERRORES_VALIDACION.CAMPO_REQUERIDO)
                return

            try:
                descuento = int(CAMPO_DESCUENTO.value)
            except ValueError:
                self._MOSTRAR_ERROR("El descuento debe ser un número válido")
                return

            sesion = OBTENER_SESION()
            
            if ES_EDICION:
                oferta = sesion.query(MODELO_OFERTA).filter_by(ID=OFERTA.ID).first()
                oferta.NOMBRE = CAMPO_NOMBRE.value
                oferta.DESCRIPCION = CAMPO_DESCRIPCION.value
                oferta.DESCUENTO = descuento
                oferta.FECHA_INICIO = CAMPO_FECHA_INICIO.value
                oferta.FECHA_FIN = CAMPO_FECHA_FIN.value
                oferta.ACTIVA = CAMPO_ACTIVA.value
            else:
                nueva = MODELO_OFERTA(
                    NOMBRE=CAMPO_NOMBRE.value,
                    DESCRIPCION=CAMPO_DESCRIPCION.value,
                    DESCUENTO=descuento,
                    FECHA_INICIO=CAMPO_FECHA_INICIO.value,
                    FECHA_FIN=CAMPO_FECHA_FIN.value,
                    ACTIVA=CAMPO_ACTIVA.value,
                )
                sesion.add(nueva)

            sesion.commit()
            sesion.close()
            
            self._CERRAR_DIALOGO()
            self._CARGAR_DATOS()
            self._MOSTRAR_EXITO(MENSAJES_EXITO.GUARDADO_EXITOSO)

        DLG = ft.AlertDialog(
            title=ft.Text(
                "Editar Oferta" if ES_EDICION else "Nueva Oferta",
                color=COLORES.TEXTO
            ),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        CAMPO_NOMBRE,
                        CAMPO_DESCRIPCION,
                        CAMPO_DESCUENTO,
                        CAMPO_FECHA_INICIO,
                        CAMPO_FECHA_FIN,
                        CAMPO_ACTIVA,
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

    def _ELIMINAR(self, OFERTA):
        def CONFIRMAR(e):
            sesion = OBTENER_SESION()
            oferta = sesion.query(MODELO_OFERTA).filter_by(ID=OFERTA.ID).first()
            
            if oferta:
                sesion.delete(oferta)
                sesion.commit()
            
            sesion.close()
            self._CERRAR_DIALOGO()
            self._CARGAR_DATOS()
            self._MOSTRAR_EXITO(MENSAJES_EXITO.ELIMINADO_EXITOSO)

        DLG = ft.AlertDialog(
            title=ft.Text("Confirmar Eliminación", color=COLORES.PELIGRO),
            content=ft.Text(
                f"¿Estás seguro que deseas eliminar la oferta '{OFERTA.NOMBRE}'?",
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
