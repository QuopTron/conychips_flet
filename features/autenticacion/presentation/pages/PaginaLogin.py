import flet as ft
from features.autenticacion.presentation.widgets.CampoTextoSeguro import (
    CampoTextoSeguro,
)
from features.autenticacion.presentation.widgets.BotonPrimario import BotonPrimario
from features.autenticacion.presentation.bloc.AutenticacionBloc import AutenticacionBloc
from features.autenticacion.presentation.bloc.AutenticacionEvento import (
    EventoIniciarSesion,
    EventoRegistrarse,
)
from features.autenticacion.presentation.bloc.AutenticacionEstado import *
from features.autenticacion.domain.usecases.IniciarSesion import IniciarSesion
from features.autenticacion.domain.usecases.RegistrarUsuario import RegistrarUsuario
from features.autenticacion.domain.usecases.RefrescarToken import RefrescarToken
from features.autenticacion.domain.usecases.VerificarPermisos import VerificarPermisos
from core.Constantes import (
    COLORES,
    TAMANOS,
    ICONOS,
    ERRORES_AUTENTICACION,
    ERRORES_VALIDACION,
    MENSAJES_EXITO,
    MENSAJES_CONFIRMACION,
    ROLES,
)
from features.autenticacion.data.RepositorioAutenticacionImpl import (
    RepositorioAutenticacionImpl,
)
from core.ui.fondo_animado import FondoAnimadoLogin
from core.ui.colores import (
    PRIMARIO,
    SECUNDARIO,
    obtener_gradiente_primario,
    obtener_sombra_elevada,
)
from core.ui.animaciones import animar_hover
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
            VERIFICAR_PERMISOS_UC=VerificarPermisos(REPOSITORIO),
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
        # Crear fondo animado con emojis cayendo
        ancho_ventana = self._PAGINA.width or 1200
        alto_ventana = self._PAGINA.height or 800
        
        self._FONDO_ANIMADO = FondoAnimadoLogin(ancho_ventana, alto_ventana)
        
        # Iniciar animación de emojis
        self._PAGINA.run_task(self._FONDO_ANIMADO.iniciar_animacion, self._PAGINA)

        LOGO = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.icons.Icons.RESTAURANT_MENU,
                        size=60,
                        color=ft.Colors.ORANGE,
                    ),
                    ft.Text(
                        value="Cony Chips",
                        size=TAMANOS.TEXTO_4XL,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        value="Autenticación de doble capa",
                        size=TAMANOS.TEXTO_MD,
                        color=ft.Colors.with_opacity(0.9, ft.Colors.WHITE),
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=TAMANOS.ESPACIADO_MD,
            ),
            gradient=obtener_gradiente_primario(),
            padding=30,
            border_radius=15,
            margin=ft.margin.only(bottom=30),
        )

        self._CAMPO_EMAIL = CampoTextoSeguro(
            ETIQUETA="Email",
            ICONO=ICONOS.EMAIL,
            TIPO_TECLADO=ft.KeyboardType.EMAIL,
            VALIDADOR=self._VALIDAR_EMAIL,
            TEXTO_AYUDA="ejemplo@correo.com",
            ANCHO=400,
        )
        self._CAMPO_EMAIL.bgcolor = ft.Colors.with_opacity(0.05, ft.Colors.BLACK)
        self._CAMPO_EMAIL.focused_border_color = SECUNDARIO
        self._CAMPO_EMAIL.border_color = PRIMARIO

        self._CAMPO_CONTRASENA = CampoTextoSeguro(
            ETIQUETA="Contraseña",
            ICONO=ICONOS.CONTRASENA,
            ES_CONTRASENA=True,
            VALIDADOR=self._VALIDAR_CONTRASENA,
            TEXTO_AYUDA="Mínimo 8 caracteres",
            ANCHO=400,
        )
        self._CAMPO_CONTRASENA.bgcolor = ft.Colors.with_opacity(0.05, ft.Colors.BLACK)
        self._CAMPO_CONTRASENA.focused_border_color = SECUNDARIO
        self._CAMPO_CONTRASENA.border_color = PRIMARIO

        self._TEXTO_ERROR = ft.Text(
            value="",
            color=COLORES.PELIGRO_CLARO,
            size=TAMANOS.TEXTO_MD,
            visible=False,
            text_align=ft.TextAlign.CENTER,
            weight=ft.FontWeight.W_500,
        )

        self._BOTON_LOGIN = BotonPrimario(
            TEXTO="Iniciar Sesión",
            ICONO=ICONOS.INICIAR_SESION,
            AL_HACER_CLIC=self._MANEJAR_LOGIN,
            ANCHO=400,
            ALTURA=55,
            COLOR_FONDO=PRIMARIO,
        )
        # Agregar efecto hover al botón
        animar_hover(
            self._BOTON_LOGIN,
            PRIMARIO,
            ft.Colors.with_opacity(0.9, PRIMARIO)
        )

        self._LINK_REGISTRO = ft.TextButton(
            "¿No tienes cuenta? Regístrate",
            on_click=self._CAMBIAR_MODO,
            style=ft.ButtonStyle(color=COLORES.PRIMARIO),
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
                    self._LINK_REGISTRO,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
            ),
            padding=40,
            bgcolor=ft.Colors.WHITE,
        )

        # Centrar formulario sobre el fondo animado
        self._FONDO_ANIMADO.controls.append(
            ft.Container(
                content=FORMULARIO,
                alignment=ft.Alignment(0, 0),
                expand=True,
            )
        )

        self.controls = [self._FONDO_ANIMADO]
        self.expand = True

    def _VALIDAR_EMAIL(self, EMAIL: str) -> Optional[str]:

        if not EMAIL:
            return "El email es requerido"

        PATRON = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(PATRON, EMAIL):
            return "Formato de email inválido"

        return None

    def _VALIDAR_CONTRASENA(self, CONTRASENA: str) -> Optional[str]:

        if not CONTRASENA:
            return "La contraseña es requerida"

        if len(CONTRASENA) < 8:
            return "Mínimo 8 caracteres"

        if self._MODO_REGISTRO:
            if not re.search(r"[A-Z]", CONTRASENA):
                return "Debe contener al menos una mayúscula"

            if not re.search(r"\d", CONTRASENA):
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
                EMAIL=EMAIL, NOMBRE_USUARIO=EMAIL.split("@")[0], CONTRASENA=CONTRASENA
            )
        else:
            EVENTO = EventoIniciarSesion(EMAIL=EMAIL, CONTRASENA=CONTRASENA)

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
        if getattr(self, "page", None):
            self.update()

    def _MANEJAR_CAMBIO_ESTADO(self, ESTADO: EstadoAutenticacion):

        print(f" UI recibe estado: {type(ESTADO).__name__}")

        if isinstance(ESTADO, EstadoCargando):
            pass

        elif isinstance(ESTADO, EstadoAutenticado):
            self._MOSTRAR_EXITO(MENSAJES_EXITO.SESION_INICIADA)
            try:
                from core.websocket.ManejadorConexion import ManejadorConexion
                from config.ConfiguracionApp import CONFIGURACION_APP

                manejador = ManejadorConexion()
                manejador.CONFIGURAR_SERVIDOR(CONFIGURACION_APP.WEBSOCKET_URL)

                async def _crear_conn():
                    try:
                        await manejador.CREAR_CONEXION(
                            ESTADO.USUARIO.ID, ESTADO.ACCESS_TOKEN
                        )
                    except Exception:
                        pass

                import asyncio

                asyncio.create_task(_crear_conn())
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
            if getattr(self, "page", None):
                self.update()

    def _OCULTAR_ERROR(self):

        if self._TEXTO_ERROR:
            self._TEXTO_ERROR.visible = False
            if getattr(self, "page", None):
                self.update()

    def _MOSTRAR_EXITO(self, MENSAJE: str):

        if self._TEXTO_ERROR:
            self._TEXTO_ERROR.value = f"{MENSAJE}"
            self._TEXTO_ERROR.color = COLORES.EXITO
            self._TEXTO_ERROR.visible = True
            if getattr(self, "page", None):
                self.update()

    def _NAVEGAR_A_DASHBOARD(self, USUARIO):
        from core.Constantes import ROLES

        print(f"🔴 _NAVEGAR_A_DASHBOARD - Usuario: {USUARIO.NOMBRE_USUARIO}, Roles: {[r.NOMBRE if hasattr(r, 'NOMBRE') else r for r in USUARIO.ROLES]}")
        print("🔴 Limpiando page.controls")
        self._PAGINA.controls.clear()
        # Default: permitir que Superadmin (y en general) tenga selección global de sucursal (Todas)
        try:
            # Añadir atributo de selección de sucursal en el objeto usuario
            if not hasattr(USUARIO, 'SUCURSAL_SELECCIONADA'):
                USUARIO.SUCURSAL_SELECCIONADA = None  # None = Todas
        except Exception:
            pass

        if USUARIO.TIENE_ROL(ROLES.SUPERADMIN):
            print("🔴 Usuario es SUPERADMIN - Creando PaginaAdmin")
            from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin

            pagina = PaginaAdmin(self._PAGINA, USUARIO)
            print(f"🔴 PaginaAdmin creada. Tipo: {type(pagina).__name__}, controls: {len(pagina.controls)}")
        elif USUARIO.TIENE_ROL(ROLES.ADMIN):
            print("🔴 Usuario es ADMIN - Creando PaginaAdmin")
            from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin

            pagina = PaginaAdmin(self._PAGINA, USUARIO)
            print(f"🔴 PaginaAdmin creada. Tipo: {type(pagina).__name__}, controls: {len(pagina.controls)}")
        elif USUARIO.TIENE_ROL(ROLES.ATENCION):
            from features.atencion.presentation.pages.PaginaDashboardAtencion import (
                PaginaDashboardAtencion,
            )

            pagina = PaginaDashboardAtencion(self._PAGINA, USUARIO.ID)
        elif USUARIO.TIENE_ROL(ROLES.COCINERO):
            from features.cocina.presentation.pages.PaginaDashboardCocina import PaginaDashboardCocina

            pagina = PaginaDashboardCocina(self._PAGINA, USUARIO.ID)
        elif USUARIO.TIENE_ROL(ROLES.LIMPIEZA):
            from features.limpieza.presentation.pages.PaginaDashboardLimpieza import (
                PaginaDashboardLimpieza,
            )

            pagina = PaginaDashboardLimpieza(self._PAGINA, USUARIO.ID)
        elif USUARIO.TIENE_ROL(ROLES.MOTORIZADO):
            from features.motorizado.presentation.pages.PaginaDashboardMotorizado import (
                PaginaDashboardMotorizado,
            )

            pagina = PaginaDashboardMotorizado(self._PAGINA, USUARIO.ID)
        elif USUARIO.TIENE_ROL(ROLES.CLIENTE):
            from features.cliente.presentation.pages.PaginaDashboardCliente import (
                PaginaDashboardCliente,
            )

            pagina = PaginaDashboardCliente(self._PAGINA, USUARIO.ID)
        else:
            from features.autenticacion.presentation.pages.PaginaDashboard import (
                PaginaDashboard,
            )

            pagina = PaginaDashboard(self._PAGINA, USUARIO, self._BLOC)

        print(f"🔴 Agregando página a page.controls. Página tiene {len(pagina.controls)} controls")
        self._PAGINA.controls.append(pagina)
        print(f"🔴 page.controls ahora tiene {len(self._PAGINA.controls)} items")
        print("🔴 Llamando page.update()")
        self._PAGINA.update()
        print("🔴 page.update() completado")
