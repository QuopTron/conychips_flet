import flet as ft
import asyncio
from features.autenticacion.domain.entities.Usuario import Usuario
from features.autenticacion.presentation.bloc.AutenticacionBloc import AutenticacionBloc
from features.autenticacion.presentation.bloc.AutenticacionEvento import (
    EventoCerrarSesion,
)
from core.Constantes import (
    COLORES,
    TAMANOS,
    ICONOS,
    ERRORES_AUTENTICACION,
    ERRORES_VALIDACION,
    MENSAJES_EXITO,
    MENSAJES_CONFIRMACION,
)

class PaginaDashboard(ft.Column):

    def __init__(self, PAGINA: ft.Page, USUARIO: Usuario, BLOC: AutenticacionBloc):

        super().__init__()
        self._PAGINA = PAGINA
        self._USUARIO = USUARIO
        self._BLOC = BLOC

        self._CONSTRUIR()

    def _CONSTRUIR(self):
        self._SECCIONES = [
            "Dashboard",
            "Perfil",
            "Productos",
            "Pedidos",
            "Admin",
        ]

        self._CONTENIDO = ft.Container(
            content=self._CREAR_CONTENIDO_PRINCIPAL(),
            expand=True,
        )

        self._NAVBAR = ft.NavigationBar(
            selected_index=0,
            destinations=[
                ft.NavigationBarDestination(icon=ICONOS.DASHBOARD, label="Inicio"),
                ft.NavigationBarDestination(icon=ICONOS.USUARIO, label="Perfil"),
                ft.NavigationBarDestination(icon=ICONOS.PRODUCTOS, label="Productos"),
                ft.NavigationBarDestination(icon=ICONOS.PEDIDOS, label="Pedidos"),
                ft.NavigationBarDestination(icon=ICONOS.ADMIN, label="Admin"),
            ],
            on_change=self._AL_CAMBIAR_NAV,
            bgcolor=COLORES.FONDO_BLANCO,
            indicator_color=ft.Colors.BLUE_50,
        )

        self.controls = [
            ft.Column(
                controls=[self._CONTENIDO, self._NAVBAR],
                spacing=0,
                expand=True,
            )
        ]
        self.expand = True

    def _AL_CAMBIAR_NAV(self, e):
        indice = e.control.selected_index
        seccion = self._SECCIONES[indice]

        if seccion == "Dashboard":
            self._CONTENIDO.content = self._CREAR_CONTENIDO_PRINCIPAL()
            self.update()
            return

        if seccion == "Perfil":
            from features.autenticacion.presentation.pages.PaginaPerfil import (
                PaginaPerfil,
            )

            self._CONTENIDO.content = PaginaPerfil(self._PAGINA, self._USUARIO)
            self.update()
            return

        self._NAVEGAR_A(seccion)

    def _CREAR_SIDEBAR(self) -> ft.Container:

        INFO_USUARIO = ft.Container(
            content=ft.Column(
                controls=[
                    ft.CircleAvatar(
                        content=ft.Text(
                            value=self._USUARIO.NOMBRE_USUARIO[0].upper(),
                            size=TAMANOS.TEXTO_4XL,
                            weight=ft.FontWeight.BOLD,
                            color=COLORES.TEXTO_BLANCO,
                        ),
                        bgcolor=COLORES.PRIMARIO,
                        radius=40,
                    ),
                    ft.Text(
                        value=self._USUARIO.NOMBRE_USUARIO,
                        size=TAMANOS.TEXTO_XL,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        value=self._USUARIO.EMAIL,
                        size=TAMANOS.TEXTO_SM,
                        color=COLORES.TEXTO_SECUNDARIO,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.icons.Icons.VERIFIED_USER,
                                    size=TAMANOS.ICONO_XS,
                                    color=COLORES.EXITO,
                                ),
                                ft.Text(
                                    value=f"Rol: {', '.join(self._USUARIO.ROLES)}",
                                    size=TAMANOS.TEXTO_SM,
                                    weight=ft.FontWeight.W_500,
                                    color=COLORES.EXITO,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=5,
                        ),
                        padding=8,
                        bgcolor=ft.Colors.GREEN_50,
                        border_radius=8,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=TAMANOS.ESPACIADO_MD,
            ),
            padding=TAMANOS.PADDING_XL,
        )

        MENU_ITEMS = []

        MENU_ITEMS.append(
            {"icono": ICONOS.DASHBOARD, "texto": "Dashboard", "permiso": None}
        )
        MENU_ITEMS.append(
            {"icono": ICONOS.USUARIO, "texto": "Perfil", "permiso": None}
        )

        if self._USUARIO.TIENE_PERMISO("usuarios.ver"):
            MENU_ITEMS.append(
                {"icono": ICONOS.USUARIOS, "texto": "Usuarios", "permiso": "usuarios.ver"}
            )

        if self._USUARIO.TIENE_PERMISO("productos.ver"):
            MENU_ITEMS.append(
                {"icono": ICONOS.PRODUCTOS, "texto": "Productos", "permiso": "productos.ver"}
            )

        if self._USUARIO.TIENE_PERMISO("pedidos.ver"):
            MENU_ITEMS.append(
                {"icono": ICONOS.PEDIDOS, "texto": "Pedidos", "permiso": "pedidos.ver"}
            )

        if self._USUARIO.TIENE_PERMISO("reportes.ver"):
            MENU_ITEMS.append(
                {"icono": ft.icons.Icons.ANALYTICS_ROUNDED, "texto": "Reportes", "permiso": "reportes.ver"}
            )

        from core.Constantes import ROLES

        if self._USUARIO.TIENE_ROL(ROLES.COCINERO):
            MENU_ITEMS.append(
                {"icono": ICONOS.COCINA, "texto": "Cocina", "permiso": None}
            )

        if self._USUARIO.TIENE_ROL(ROLES.ATENCION):
            MENU_ITEMS.append(
                {"icono": ICONOS.ATENCION, "texto": "Atención", "permiso": None}
            )

        if self._USUARIO.TIENE_ROL(ROLES.LIMPIEZA):
            MENU_ITEMS.append(
                {"icono": ICONOS.LIMPIEZA, "texto": "Limpieza", "permiso": None}
            )

        if self._USUARIO.TIENE_ROL(ROLES.ADMIN) or self._USUARIO.TIENE_ROL(ROLES.SUPERADMIN):
            MENU_ITEMS.append(
                {"icono": ICONOS.ADMIN, "texto": "Admin", "permiso": None}
            )

        MENU_ITEMS.append(
            {"icono": ft.icons.Icons.HISTORY_ROUNDED, "texto": "Historial", "permiso": None}
        )
        MENU_ITEMS.append(
            {"icono": ICONOS.CONFIGURACION, "texto": "Configuración", "permiso": None}
        )

        CONTROLES_MENU = []
        for ITEM in MENU_ITEMS:
            CONTROLES_MENU.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ITEM["icono"], size=TAMANOS.ICONO_SM),
                            ft.Text(ITEM["texto"], size=TAMANOS.TEXTO_MD),
                        ],
                        spacing=15,
                    ),
                    padding=15,
                    border_radius=8,
                    ink=True,
                    on_click=lambda e, texto=ITEM["texto"]: self._NAVEGAR_A(texto),
                )
            )

        MENU = ft.Column(controls=CONTROLES_MENU, spacing=5)

        BOTON_LOGOUT = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ICONOS.CERRAR_SESION, size=TAMANOS.ICONO_SM, color=COLORES.PELIGRO),
                    ft.Text("Cerrar Sesión", size=TAMANOS.TEXTO_MD, color=COLORES.PELIGRO),
                ],
                spacing=15,
            ),
            padding=15,
            border_radius=8,
            ink=True,
            on_click=self._CERRAR_SESION,
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    INFO_USUARIO,
                    ft.Divider(height=1),
                    MENU,
                    ft.Container(expand=True),
                    BOTON_LOGOUT,
                ],
                spacing=TAMANOS.ESPACIADO_MD,
            ),
            width=280,
            bgcolor=COLORES.FONDO_BLANCO,
            padding=ft.Padding.only(bottom=TAMANOS.PADDING_XL),
        )

    def _CREAR_CONTENIDO_PRINCIPAL(self) -> ft.Container:

        HEADER = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(
                        value="Dashboard Principal", size=28, weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(expand=True),
                    ft.Icon(ft.icons.Icons.NOTIFICATIONS_OUTLINED, size=TAMANOS.ICONO_MD),
                    ft.IconButton(
                        icon=ICONOS.CERRAR_SESION,
                        icon_color=COLORES.PELIGRO,
                        on_click=lambda e: asyncio.create_task(self._CERRAR_SESION(e)),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=TAMANOS.PADDING_XL,
            bgcolor=COLORES.FONDO_BLANCO,
            border=ft.border.only(bottom=ft.BorderSide(1, COLORES.BORDE)),
        )

        STATS = ft.Row(
            controls=[
                self._CREAR_CARD_STAT(
                    "Sesiones Activas", "1", ft.icons.Icons.PHONE_ANDROID, COLORES.PRIMARIO
                ),
                self._CREAR_CARD_STAT(
                    "Permisos",
                    str(len(self._USUARIO.OBTENER_PERMISOS())),
                    ft.icons.Icons.SECURITY,
                    COLORES.EXITO,
                ),
                self._CREAR_CARD_STAT(
                    "Roles",
                    str(len(self._USUARIO.ROLES)),
                    ICONOS.ADMIN,
                    COLORES.SECUNDARIO,
                ),
            ],
            spacing=TAMANOS.ESPACIADO_XL,
            wrap=True,
        )

        INFO_DETALLADA = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Información de la Cuenta", size=20, weight=ft.FontWeight.BOLD
                    ),
                    ft.Divider(height=1),
                    self._CREAR_FILA_INFO("Usuario ID", str(self._USUARIO.ID)),
                    self._CREAR_FILA_INFO("Email", self._USUARIO.EMAIL),
                    self._CREAR_FILA_INFO(
                        "Nombre de Usuario", self._USUARIO.NOMBRE_USUARIO
                    ),
                    self._CREAR_FILA_INFO(
                        "Estado", "Activo " if self._USUARIO.ACTIVO else "Inactivo"
                    ),
                    self._CREAR_FILA_INFO(
                        "Verificado", "Sí " if self._USUARIO.VERIFICADO else "No "
                    ),
                    self._CREAR_FILA_INFO(
                        "Fecha de Registro",
                        (
                            self._USUARIO.FECHA_CREACION.strftime("%d/%m/%Y %H:%M")
                            if self._USUARIO.FECHA_CREACION
                            else "N/A"
                        ),
                    ),
                    self._CREAR_FILA_INFO(
                        "Última Conexión",
                        (
                            self._USUARIO.ULTIMA_CONEXION.strftime("%d/%m/%Y %H:%M")
                            if self._USUARIO.ULTIMA_CONEXION
                            else "Primera vez"
                        ),
                    ),
                ],
                spacing=15,
            ),
            padding=TAMANOS.PADDING_XL,
            bgcolor=COLORES.FONDO_BLANCO,
            border_radius=TAMANOS.RADIO_MD,
            border=ft.Border.all(1, COLORES.BORDE),
        )

        LISTA_PERMISOS = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Tus Permisos", size=TAMANOS.TEXTO_2XL, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=1),
                    ft.Column(
                        controls=[
                            ft.Row(
                                [
                                    ft.Icon(ICONOS.EXITO,
                                        size=TAMANOS.ICONO_XS,
                                        color=COLORES.EXITO,
                                    ),
                                    ft.Text(PERMISO, size=13),
                                ],
                                spacing=8,
                            )
                            for PERMISO in self._USUARIO.OBTENER_PERMISOS()[:10]
                        ],
                        spacing=8,
                    ),
                ],
                spacing=15,
            ),
            padding=TAMANOS.PADDING_XL,
            bgcolor=COLORES.FONDO_BLANCO,
            border_radius=TAMANOS.RADIO_MD,
            border=ft.Border.all(1, COLORES.BORDE),
        )

        CONTENIDO = ft.Container(
            content=ft.Column(
                controls=[
                    HEADER,
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                STATS,
                                ft.Container(height=20),
                                ft.Row(
                                    controls=[INFO_DETALLADA, LISTA_PERMISOS],
                                    spacing=20,
                                    alignment=ft.MainAxisAlignment.START,
                                    vertical_alignment=ft.CrossAxisAlignment.START,
                                    wrap=True,
                                ),
                            ],
                            scroll=ft.ScrollMode.AUTO,
                        ),
                padding=TAMANOS.PADDING_XL,
                expand=True,
            ),
        ],
        spacing=0,
    ),
    expand=True,
    bgcolor=COLORES.FONDO,

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ICONO, size=TAMANOS.ICONO_LG, color=COLOR),
                            ft.Container(expand=True),
                            ft.Text(
                                VALOR, size=TAMANOS.TEXTO_4XL, weight=ft.FontWeight.BOLD, color=COLOR
                            ),
                        ]
                    ),
                    ft.Text(TITULO, size=TAMANOS.TEXTO_MD, color=COLORES.TEXTO_SECUNDARIO),
                ],
                spacing=TAMANOS.ESPACIADO_MD,
            ),
            padding=TAMANOS.PADDING_XL,
            bgcolor=COLORES.FONDO_BLANCO,
            border_radius=TAMANOS.RADIO_MD,
            border=ft.Border.all(1, COLORES.BORDE),
            width=200,
        )

    def _CREAR_FILA_INFO(self, ETIQUETA: str, VALOR: str) -> ft.Row:

        return ft.Row(
            controls=[
                ft.Text(f"{ETIQUETA}:", size=TAMANOS.TEXTO_MD, weight=ft.FontWeight.W_600, width=180),
                ft.Text(VALOR, size=TAMANOS.TEXTO_MD, color=ft.Colors.GREY_700),
            ],
            spacing=TAMANOS.ESPACIADO_MD,
        )

    def _NAVEGAR_A(self, SECCION: str):

        if not self._PUEDE_ACCEDER(SECCION):
            self._MOSTRAR_ERROR("No tienes permisos para acceder")
            return

        if SECCION == "Productos":
            from core.Constantes import ROLES

            if self._USUARIO.TIENE_ROL(ROLES.ADMIN) or self._USUARIO.TIENE_ROL(ROLES.SUPERADMIN):
                from features.admin.presentation.pages.PaginaProductosAdmin import (
                    PaginaProductosAdmin,
                )

                self._PAGINA.controls.clear()
                self._PAGINA.controls.append(PaginaProductosAdmin(self._PAGINA, self._USUARIO))
                self._PAGINA.update()
                return

            from features.productos.presentation.pages.PaginaProductos import (
                PaginaProductos,
            )

            self._PAGINA.controls.clear()
            self._PAGINA.controls.append(
                PaginaProductos(self._PAGINA, self._USUARIO.ID)
            )
            self._PAGINA.update()
            return
        if SECCION == "Historial":
            from features.productos.presentation.pages.PaginaHistorialPedidos import (
                PaginaHistorialPedidos,
            )

            self._PAGINA.controls.clear()
            self._PAGINA.controls.append(
                PaginaHistorialPedidos(self._PAGINA, self._USUARIO.ID)
            )
            self._PAGINA.update()
            return
        if SECCION == "Limpieza":
            from features.limpieza.presentation.pages.PaginaLimpieza import (
                PaginaLimpieza,
            )

            self._PAGINA.controls.clear()
            self._PAGINA.controls.append(PaginaLimpieza(self._PAGINA, self._USUARIO.ID))
            self._PAGINA.update()
            return
        if SECCION == "Perfil":
            from features.autenticacion.presentation.pages.PaginaPerfil import (
                PaginaPerfil,
            )

            self._PAGINA.controls.clear()
            self._PAGINA.controls.append(PaginaPerfil(self._PAGINA, self._USUARIO))
            self._PAGINA.update()
            return

        if SECCION == "Cocina":
            from features.cocina.presentation.pages.PaginaCocina import PaginaCocina

            self._PAGINA.controls.clear()
            self._PAGINA.controls.append(PaginaCocina(self._PAGINA, self._USUARIO.ID))
            self._PAGINA.update()
            return

        if SECCION == "Atención":
            from features.atencion.presentation.pages.PaginaAtencion import (
                PaginaAtencion,
            )

            self._PAGINA.controls.clear()
            self._PAGINA.controls.append(PaginaAtencion(self._PAGINA, self._USUARIO.ID))
            self._PAGINA.update()
            return

        if SECCION == "Admin":
            from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin

            self._PAGINA.controls.clear()
            self._PAGINA.controls.append(PaginaAdmin(self._PAGINA, self._USUARIO))
            self._PAGINA.update()
            return

    def _PUEDE_ACCEDER(self, SECCION: str) -> bool:
        from core.Constantes import ROLES

        if SECCION in ["Dashboard", "Perfil", "Historial", "Configuración"]:
            return True

        if SECCION == "Productos":
            return self._USUARIO.TIENE_PERMISO("productos.ver") or self._USUARIO.TIENE_ROL(ROLES.CLIENTE)

        if SECCION == "Pedidos":
            return self._USUARIO.TIENE_PERMISO("pedidos.ver")

        if SECCION == "Reportes":
            return self._USUARIO.TIENE_PERMISO("reportes.ver")

        if SECCION == "Usuarios":
            return self._USUARIO.TIENE_PERMISO("usuarios.ver")

        if SECCION == "Cocina":
            return self._USUARIO.TIENE_ROL(ROLES.COCINERO)

        if SECCION == "Atención":
            return self._USUARIO.TIENE_ROL(ROLES.ATENCION)

        if SECCION == "Admin":
            return self._USUARIO.TIENE_ROL(ROLES.ADMIN) or self._USUARIO.TIENE_ROL(ROLES.SUPERADMIN)

        if SECCION == "Limpieza":
            return self._USUARIO.TIENE_ROL(ROLES.LIMPIEZA)

        return False

    def _MOSTRAR_ERROR(self, MENSAJE: str):
        snackbar = ft.SnackBar(
            content=ft.Text(MENSAJE, color=COLORES.TEXTO_BLANCO),
            bgcolor=COLORES.PELIGRO,
        )
        self._PAGINA.overlay.append(snackbar)
        snackbar.open = True
        self._PAGINA.update()

    async def _CERRAR_SESION(self, e):

        await self._BLOC.AGREGAR_EVENTO(EventoCerrarSesion())

        from features.autenticacion.presentation.pages.PaginaLogin import PaginaLogin

        self._PAGINA.controls.clear()
        self._PAGINA.controls.append(PaginaLogin(self._PAGINA))
        await self._PAGINA.update()
