#conychips/features/autentitacion/presentation/pages/PaginaDashboard.py
import flet as ft
from features.autenticacion.domain.entities.Usuario import Usuario
from features.autenticacion.presentation.bloc.AutenticacionBloc import AutenticacionBloc
from features.autenticacion.presentation.bloc.AutenticacionEvento import EventoCerrarSesion


class PaginaDashboard(ft.Column):
    """
    Dashboard principal con:
    - Información del usuario
    - Gestión de permisos según rol
    - Navegación a módulos
    - Sesiones activas
    """
    
    def __init__(self, PAGINA: ft.Page, USUARIO: Usuario, BLOC: AutenticacionBloc):
        """
        Inicializa el dashboard
        
        Args:
            PAGINA: Instancia de la página
            USUARIO: Usuario autenticado
            BLOC: BLoC de autenticación
        """
        super().__init__()
        self._PAGINA = PAGINA
        self._USUARIO = USUARIO
        self._BLOC = BLOC
        
        # Construir automáticamente
        self._CONSTRUIR()
    
    def _CONSTRUIR(self):
        """Construye la UI del dashboard"""
        
        # Sidebar
        SIDEBAR = self._CREAR_SIDEBAR()
        
        # Contenido principal
        CONTENIDO_PRINCIPAL = self._CREAR_CONTENIDO_PRINCIPAL()
        
        # Layout principal
        LAYOUT = ft.Row(
            controls=[
                SIDEBAR,
                ft.VerticalDivider(width=1, color=ft.Colors.GREY_300),
                CONTENIDO_PRINCIPAL
            ],
            expand=True,
            spacing=0
        )
        
        # Agregar al Column padre
        self.controls = [LAYOUT]
        self.expand = True
    
    def _CREAR_SIDEBAR(self) -> ft.Container:
        """Crea el sidebar de navegación"""
        
        # Info del usuario
        INFO_USUARIO = ft.Container(
            content=ft.Column(
                controls=[
                    ft.CircleAvatar(
                        content=ft.Text(
                            value=self._USUARIO.NOMBRE_USUARIO[0].upper(),
                            size=32,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE
                        ),
                        bgcolor=ft.Colors.BLUE_600,
                        radius=40
                    ),
                    ft.Text(
                        value=self._USUARIO.NOMBRE_USUARIO,
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        value=self._USUARIO.EMAIL,
                        size=12,
                        color=ft.Colors.GREY_600,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.VERIFIED_USER, size=16, color=ft.Colors.GREEN_600),
                                ft.Text(
                                    value=f"Rol: {', '.join(self._USUARIO.ROLES)}",
                                    size=12,
                                    weight=ft.FontWeight.W_500,
                                    color=ft.Colors.GREEN_600
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=5
                        ),
                        padding=8,
                        bgcolor=ft.Colors.GREEN_50,
                        border_radius=8
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            padding=20
        )
        
        # Menú de navegación
        MENU_ITEMS = [
            {
                "icono": ft.Icons.DASHBOARD_ROUNDED,
                "texto": "Dashboard",
                "permiso": None
            },
            {
                "icono": ft.Icons.PEOPLE_ROUNDED,
                "texto": "Usuarios",
                "permiso": "usuarios.ver"
            },
            {
                "icono": ft.Icons.SETTINGS_ROUNDED,
                "texto": "Configuración",
                "permiso": None
            },
            {
                "icono": ft.Icons.ANALYTICS_ROUNDED,
                "texto": "Reportes",
                "permiso": "contenido.moderar"
            }
        ]
        
        CONTROLES_MENU = []
        for ITEM in MENU_ITEMS:
            # Verificar permiso si existe
            if ITEM["permiso"] and not self._USUARIO.TIENE_PERMISO(ITEM["permiso"]):
                continue
            
            CONTROLES_MENU.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ITEM["icono"], size=20),
                            ft.Text(ITEM["texto"], size=14)
                        ],
                        spacing=15
                    ),
                    padding=15,
                    border_radius=8,
                    ink=True,
                    on_click=lambda e, texto=ITEM["texto"]: self._NAVEGAR_A(texto)
                )
            )
        
        MENU = ft.Column(
            controls=CONTROLES_MENU,
            spacing=5
        )
        
        # Botón de cerrar sesión
        BOTON_LOGOUT = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.LOGOUT_ROUNDED, size=20, color=ft.Colors.RED_600),
                    ft.Text("Cerrar Sesión", size=14, color=ft.Colors.RED_600)
                ],
                spacing=15
            ),
            padding=15,
            border_radius=8,
            ink=True,
            on_click=self._CERRAR_SESION
        )
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    INFO_USUARIO,
                    ft.Divider(height=1),
                    MENU,
                    ft.Container(expand=True),
                    BOTON_LOGOUT
                ],
                spacing=10
            ),
            width=280,
            bgcolor=ft.Colors.WHITE,
            padding=ft.padding.only(bottom=20)
        )
    
    def _CREAR_CONTENIDO_PRINCIPAL(self) -> ft.Container:
        """Crea el contenido principal del dashboard"""
        
        # Header
        HEADER = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(
                        value="Dashboard Principal",
                        size=28,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(expand=True),
                    ft.Icon(ft.Icons.NOTIFICATIONS_OUTLINED, size=24)
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_300))
        )
        
        # Cards de estadísticas
        STATS = ft.Row(
            controls=[
                self._CREAR_CARD_STAT("Sesiones Activas", "1", ft.Icons.PHONE_ANDROID, ft.Colors.BLUE_600),
                self._CREAR_CARD_STAT("Permisos", str(len(self._USUARIO.OBTENER_PERMISOS())), ft.Icons.SECURITY, ft.Colors.GREEN_600),
                self._CREAR_CARD_STAT("Roles", str(len(self._USUARIO.ROLES)), ft.Icons.ADMIN_PANEL_SETTINGS, ft.Colors.PURPLE_600),
            ],
            spacing=20,
            wrap=True
        )
        
        # Información detallada
        INFO_DETALLADA = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Información de la Cuenta", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=1),
                    self._CREAR_FILA_INFO("Usuario ID", str(self._USUARIO.ID)),
                    self._CREAR_FILA_INFO("Email", self._USUARIO.EMAIL),
                    self._CREAR_FILA_INFO("Nombre de Usuario", self._USUARIO.NOMBRE_USUARIO),
                    self._CREAR_FILA_INFO("Estado", "Activo ✓" if self._USUARIO.ACTIVO else "Inactivo"),
                    self._CREAR_FILA_INFO("Verificado", "Sí ✓" if self._USUARIO.VERIFICADO else "No ✗"),
                    self._CREAR_FILA_INFO("Fecha de Registro", 
                                         self._USUARIO.FECHA_CREACION.strftime("%d/%m/%Y %H:%M") if self._USUARIO.FECHA_CREACION else "N/A"),
                    self._CREAR_FILA_INFO("Última Conexión", 
                                         self._USUARIO.ULTIMA_CONEXION.strftime("%d/%m/%Y %H:%M") if self._USUARIO.ULTIMA_CONEXION else "Primera vez"),
                ],
                spacing=15
            ),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300)
        )
        
        # Permisos del usuario
        LISTA_PERMISOS = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Tus Permisos", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=1),
                    ft.Column(
                        controls=[
                            ft.Row([
                                ft.Icon(ft.Icons.CHECK_CIRCLE, size=16, color=ft.Colors.GREEN_600),
                                ft.Text(PERMISO, size=13)
                            ], spacing=8)
                            for PERMISO in self._USUARIO.OBTENER_PERMISOS()[:10]
                        ],
                        spacing=8
                    )
                ],
                spacing=15
            ),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300)
        )
        
        # Contenido scrolleable
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
                                    wrap=True
                                )
                            ],
                            scroll=ft.ScrollMode.AUTO
                        ),
                        padding=20,
                        expand=True
                    )
                ],
                spacing=0
            ),
            expand=True,
            bgcolor=ft.Colors.GREY_50
        )
        
        return CONTENIDO
    
    def _CREAR_CARD_STAT(self, TITULO: str, VALOR: str, ICONO, COLOR) -> ft.Container:
        """Crea una card de estadística"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ICONO, size=32, color=COLOR),
                            ft.Container(expand=True),
                            ft.Text(VALOR, size=32, weight=ft.FontWeight.BOLD, color=COLOR)
                        ]
                    ),
                    ft.Text(TITULO, size=14, color=ft.Colors.GREY_600)
                ],
                spacing=10
            ),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
            width=200
        )
    
    def _CREAR_FILA_INFO(self, ETIQUETA: str, VALOR: str) -> ft.Row:
        """Crea una fila de información"""
        return ft.Row(
            controls=[
                ft.Text(f"{ETIQUETA}:", size=14, weight=ft.FontWeight.W_600, width=180),
                ft.Text(VALOR, size=14, color=ft.Colors.GREY_700)
            ],
            spacing=10
        )
    
    def _NAVEGAR_A(self, SECCION: str):
        """Navega a una sección"""
        print(f"Navegando a: {SECCION}")
        # Aquí implementarías la navegación a diferentes módulos
    
    async def _CERRAR_SESION(self, e):
        """Cierra la sesión del usuario"""
        # Enviar evento de cerrar sesión
        await self._BLOC.AGREGAR_EVENTO(EventoCerrarSesion())
        
        # Volver al login
        from features.autenticacion.presentation.pages.PaginaLogin import PaginaLogin
        
        self._PAGINA.controls.clear()
        self._PAGINA.controls.append(PaginaLogin(self._PAGINA))
        await self._PAGINA.update()