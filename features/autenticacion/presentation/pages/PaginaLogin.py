import flet as ft
from features.autenticacion.presentation.widgets.CampoTextoSeguro import CampoTextoSeguro
from features.autenticacion.presentation.widgets.BotonPrimario import BotonPrimario
from features.autenticacion.presentation.bloc.AutenticacionBloc import AutenticacionBloc
from features.autenticacion.presentation.bloc.AutenticacionEvento import EventoIniciarSesion, EventoRegistrarse
from features.autenticacion.presentation.bloc.AutenticacionEstado import *
from features.autenticacion.domain.usecases.IniciarSesion import IniciarSesion
from features.autenticacion.domain.usecases.RegistrarUsuario import RegistrarUsuario
from features.autenticacion.domain.usecases.RefrescarToken import RefrescarToken
from features.autenticacion.domain.usecases.VerificarPermisos import VerificarPermisos
from core.Constantes import ROLES
from features.autenticacion.data.RepositorioAutenticacionImpl import RepositorioAutenticacionImpl
import re
from typing import Optional

class PaginaLogin(ft.Column):
    
    
    def __init__(self, PAGINA: ft.Page):
        super().__init__()
        self._PAGINA = PAGINA
        
        REPOSITORIO = RepositorioAutenticacionImpl()
        self._BLOC = AutenticacionBloc(
            INICIAR_SESION_UC=IniciarSesion(REPOSITORIO),
            REGISTRAR_USUARIO_UC=RegistrarUsuario(REPOSITORIO),
            REFRESCAR_TOKEN_UC=RefrescarToken(REPOSITORIO),
            VERIFICAR_PERMISOS_UC=VerificarPermisos(REPOSITORIO)
        )
        
        self._BLOC.AGREGAR_LISTENER(self._MANEJAR_CAMBIO_ESTADO)
        
        self._CAMPO_EMAIL: Optional[CampoTextoSeguro] = None
        self._CAMPO_CONTRASENA: Optional[CampoTextoSeguro] = None
        self._BOTON_LOGIN: Optional[BotonPrimario] = None
        self._TEXTO_ERROR: Optional[ft.Text] = None
        self._CONTENEDOR_PRINCIPAL: Optional[ft.Container] = None
        self._LINK_REGISTRO: Optional[ft.TextButton] = None
        
        self._MODO_REGISTRO = False
        
        self._CONSTRUIR()
    
    def _CONSTRUIR(self):
        
        
        LOGO = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(
                        ft.Icons.LOCK_OUTLINED,
                        size=80,
                        color=ft.Colors.BLUE_600
                    ),
                    ft.Text(
                        value="Cony Chips",
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_600,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        value="Autenticación de doble capa",
                        size=14,
                        color=ft.Colors.GREY_600,
                        text_align=ft.TextAlign.CENTER
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            margin=ft.margin.only(bottom=30)
        )
        
        self._CAMPO_EMAIL = CampoTextoSeguro(
            ETIQUETA="Email",
            ICONO=ft.Icons.EMAIL_OUTLINED,
            TIPO_TECLADO=ft.KeyboardType.EMAIL,
            VALIDADOR=self._VALIDAR_EMAIL,
            TEXTO_AYUDA="ejemplo@correo.com",
            ANCHO=400
        )
        
        self._CAMPO_CONTRASENA = CampoTextoSeguro(
            ETIQUETA="Contraseña",
            ICONO=ft.Icons.LOCK_OUTLINED,
            ES_CONTRASENA=True,
            VALIDADOR=self._VALIDAR_CONTRASENA,
            TEXTO_AYUDA="Mínimo 8 caracteres",
            ANCHO=400
        )
        
        self._TEXTO_ERROR = ft.Text(
            value="",
            color=ft.Colors.RED_400,
            size=14,
            visible=False,
            text_align=ft.TextAlign.CENTER,
            weight=ft.FontWeight.W_500
        )
        
        self._BOTON_LOGIN = BotonPrimario(
            TEXTO="Iniciar Sesión",
            ICONO=ft.Icons.LOGIN_ROUNDED,
            AL_HACER_CLIC=self._MANEJAR_LOGIN,
            ANCHO=400,
            ALTURA=55,
            COLOR_FONDO=ft.Colors.BLUE_600
        )
        
        self._LINK_REGISTRO = ft.TextButton(
            "¿No tienes cuenta? Regístrate",
            on_click=self._CAMBIAR_MODO,
            style=ft.ButtonStyle(
                color=ft.Colors.BLUE_600
            )
        )
        
        FORMULARIO = ft.Container(
            content=ft.Column(
                controls=[
                    LOGO,
                    self._CAMPO_EMAIL,
                    self._CAMPO_CONTRASENA,
                    self._TEXTO_ERROR,
                    ft.Container(height=10),
                    self._BOTON_LOGIN,
                    ft.Container(height=10),
                    self._LINK_REGISTRO
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15
            ),
            padding=40,
            bgcolor=ft.Colors.WHITE,
            border_radius=15,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 5)
            ),
            width=500
        )
        
        self._CONTENEDOR_PRINCIPAL = ft.Container(
            content=ft.Column(
                controls=[FORMULARIO],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER
            ),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[ft.Colors.BLUE_50, ft.Colors.PURPLE_50]
            ),
            expand=True,
            alignment=ft.Alignment(0, 0)
        )
        
        self.controls = [self._CONTENEDOR_PRINCIPAL]
        self.expand = True
    
    def _VALIDAR_EMAIL(self, EMAIL: str) -> Optional[str]:
        
        if not EMAIL:
            return "El email es requerido"
        
        PATRON = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(PATRON, EMAIL):
            return "Formato de email inválido"
        
        return None
    
    def _VALIDAR_CONTRASENA(self, CONTRASENA: str) -> Optional[str]:
        
        if not CONTRASENA:
            return "La contraseña es requerida"
        
        if len(CONTRASENA) < 8:
            return "Mínimo 8 caracteres"
        
        if self._MODO_REGISTRO:
            if not re.search(r'[A-Z]', CONTRASENA):
                return "Debe contener al menos una mayúscula"
            
            if not re.search(r'\d', CONTRASENA):
                return "Debe contener al menos un número"
        
        return None
    
    async def _MANEJAR_LOGIN(self, e):
        

        EMAIL_VALIDO = self._CAMPO_EMAIL.VALIDAR()
        CONTRASENA_VALIDA = self._CAMPO_CONTRASENA.VALIDAR()
        
        if not EMAIL_VALIDO or not CONTRASENA_VALIDA:
            return
        
        EMAIL = self._CAMPO_EMAIL.OBTENER_VALOR()
        CONTRASENA = self._CAMPO_CONTRASENA.OBTENER_VALOR()

        self._OCULTAR_ERROR()
        
        if self._MODO_REGISTRO:
            EVENTO = EventoRegistrarse(
                EMAIL=EMAIL,
                NOMBRE_USUARIO=EMAIL.split('@')[0],
                CONTRASENA=CONTRASENA
            )
        else:
            EVENTO = EventoIniciarSesion(
                EMAIL=EMAIL,
                CONTRASENA=CONTRASENA
            )
        
        await self._BLOC.AGREGAR_EVENTO(EVENTO)
    
    def _CAMBIAR_MODO(self, e):
        
        self._MODO_REGISTRO = not self._MODO_REGISTRO
        
        if self._MODO_REGISTRO:
            self._BOTON_LOGIN.CAMBIAR_TEXTO("Registrarse")
            self._LINK_REGISTRO.text = "¿Ya tienes cuenta? Inicia sesión"
        else:
            self._BOTON_LOGIN.CAMBIAR_TEXTO("Iniciar Sesión")
            self._LINK_REGISTRO.text = "¿No tienes cuenta? Regístrate"
        
        self._OCULTAR_ERROR()
        if getattr(self, 'page', None):
            self.update()
    
    def _MANEJAR_CAMBIO_ESTADO(self, ESTADO: EstadoAutenticacion):
        
        print(f"📱 UI recibe estado: {type(ESTADO).__name__}")
        
        if isinstance(ESTADO, EstadoCargando):
            pass
        
        elif isinstance(ESTADO, EstadoAutenticado):
            self._MOSTRAR_EXITO("¡Bienvenido!")
            # Configurar servidor WebSocket y crear conexión para este usuario
            try:
                from core.websocket.ManejadorConexion import ManejadorConexion
                from config.ConfiguracionApp import CONFIGURACION_APP

                manejador = ManejadorConexion()
                manejador.CONFIGURAR_SERVIDOR(CONFIGURACION_APP.WEBSOCKET_URL)

                async def _crear_conn():
                    try:
                        await manejador.CREAR_CONEXION(ESTADO.USUARIO.ID, ESTADO.ACCESS_TOKEN)
                    except Exception:
                        pass

                import asyncio
                asyncio.create_task(_crear_conn())
            except Exception:
                pass
            # Si el usuario es cliente, navegar directamente a productos
            try:
                if ESTADO.USUARIO.TIENE_ROL(ROLES.CLIENTE):
                    from features.productos.presentation.pages.PaginaProductos import PaginaProductos

                    self._PAGINA.controls.clear()
                    self._PAGINA.controls.append(PaginaProductos(self._PAGINA, ESTADO.USUARIO.ID))
                    self._PAGINA.update()
                    return
            except Exception:
                pass

            self._NAVEGAR_A_DASHBOARD(ESTADO.USUARIO)
        
        elif isinstance(ESTADO, EstadoRegistroExitoso):
            self._MOSTRAR_EXITO("¡Registro exitoso! Ahora puedes iniciar sesión.")
            self._MODO_REGISTRO = False
            self._BOTON_LOGIN.CAMBIAR_TEXTO("Iniciar Sesión")
            self._CAMPO_EMAIL.LIMPIAR()
            self._CAMPO_CONTRASENA.LIMPIAR()
        
        elif isinstance(ESTADO, EstadoError):
            self._MOSTRAR_ERROR(ESTADO.ERROR)
        
        elif isinstance(ESTADO, EstadoRequiereSegundoFactor):
            self._MOSTRAR_ERROR("Se requiere segundo factor de autenticación")
    
    def _MOSTRAR_ERROR(self, MENSAJE: str):
        
        if self._TEXTO_ERROR:
            self._TEXTO_ERROR.value = f"{MENSAJE}"
            self._TEXTO_ERROR.visible = True
            if getattr(self, 'page', None):
                self.update()
    
    def _OCULTAR_ERROR(self):
        
        if self._TEXTO_ERROR:
            self._TEXTO_ERROR.visible = False
            if getattr(self, 'page', None):
                self.update()
    
    def _MOSTRAR_EXITO(self, MENSAJE: str):
        
        if self._TEXTO_ERROR:
            self._TEXTO_ERROR.value = f"{MENSAJE}"
            self._TEXTO_ERROR.color = ft.Colors.GREEN_600
            self._TEXTO_ERROR.visible = True
            if getattr(self, 'page', None):
                self.update()
    
    def _NAVEGAR_A_DASHBOARD(self, USUARIO):
        from core.Constantes import ROLES
        
        self._PAGINA.controls.clear()
        
        if USUARIO.TIENE_ROL(ROLES.CLIENTE):
            from features.productos.presentation.pages.PaginaProductos import PaginaProductos
            pagina = PaginaProductos(self._PAGINA, USUARIO.ID)
        elif USUARIO.TIENE_ROL(ROLES.ATENCION):
            from features.atencion.presentation.pages.PaginaAtencion import PaginaAtencion
            pagina = PaginaAtencion(self._PAGINA, USUARIO.ID)
        elif USUARIO.TIENE_ROL(ROLES.COCINERO):
            from features.cocina.presentation.pages.PaginaCocina import PaginaCocina
            pagina = PaginaCocina(self._PAGINA, USUARIO.ID)
        elif USUARIO.TIENE_ROL(ROLES.LIMPIEZA):
            from features.limpieza.presentation.pages.PaginaLimpieza import PaginaLimpieza
            pagina = PaginaLimpieza(self._PAGINA, USUARIO.ID)
        elif USUARIO.TIENE_ROL(ROLES.ADMIN) or USUARIO.TIENE_ROL(ROLES.SUPER_ADMIN):
            from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
            pagina = PaginaAdmin(self._PAGINA, USUARIO.ID)
        else:
            from features.autenticacion.presentation.pages.PaginaDashboard import PaginaDashboard
            pagina = PaginaDashboard(self._PAGINA, USUARIO, self._BLOC)
        
        self._PAGINA.controls.append(pagina)
        self._PAGINA.update()
