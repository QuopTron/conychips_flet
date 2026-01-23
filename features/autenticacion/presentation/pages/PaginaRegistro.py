#conychips/features/autentitacion/presentation/pages/PaginaRegistro.py
import flet as ft
from features.autenticacion.presentation.widgets.CampoTextoSeguro import CampoTextoSeguro
from features.autenticacion.presentation.widgets.BotonPrimario import BotonPrimario
from features.autenticacion.presentation.bloc.AutenticacionBloc import AutenticacionBloc
from features.autenticacion.presentation.bloc.AutenticacionEvento import EventoRegistrarse
from features.autenticacion.presentation.bloc.AutenticacionEstado import *
import re
import asyncio
from typing import Optional


class PaginaRegistro(ft.Column):
    """
    Página de registro con validación completa
    """
    
    def __init__(self, PAGINA: ft.Page, BLOC: AutenticacionBloc):
        """
        Inicializa la página de registro
        
        Args:
            PAGINA: Instancia de la página de Flet
            BLOC: BLoC de autenticación
        """
        super().__init__()
        self._PAGINA = PAGINA
        self._BLOC = BLOC
        
        # Escuchar estados
        self._BLOC.AGREGAR_LISTENER(self._MANEJAR_ESTADO)
        
        # Widgets
        self._CAMPO_EMAIL: Optional[CampoTextoSeguro] = None
        self._CAMPO_NOMBRE_USUARIO: Optional[CampoTextoSeguro] = None
        self._CAMPO_CONTRASENA: Optional[CampoTextoSeguro] = None
        self._CAMPO_CONFIRMAR_CONTRASENA: Optional[CampoTextoSeguro] = None
        self._BOTON_REGISTRAR: Optional[BotonPrimario] = None
        self._TEXTO_ERROR: Optional[ft.Text] = None
        self._CHECKBOX_TERMINOS: Optional[ft.Checkbox] = None
        
        # Construir automáticamente
        self._CONSTRUIR()
    
    def _CONSTRUIR(self):
        """Construye la UI"""
        
        # Header
        HEADER = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(
                        ft.Icons.PERSON_ADD_ROUNDED,
                        size=70,
                        color=ft.Colors.PURPLE_600
                    ),
                    ft.Text(
                        value="Crear Cuenta",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.PURPLE_600
                    ),
                    ft.Text(
                        value="Completa el formulario para registrarte",
                        size=14,
                        color=ft.Colors.GREY_600
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8
            ),
            margin=ft.margin.only(bottom=25)
        )
        
        # Campos del formulario
        self._CAMPO_EMAIL = CampoTextoSeguro(
            ETIQUETA="Email",
            ICONO=ft.Icons.EMAIL_OUTLINED,
            TIPO_TECLADO=ft.KeyboardType.EMAIL,
            VALIDADOR=self._VALIDAR_EMAIL,
            ANCHO=400
        )
        
        self._CAMPO_NOMBRE_USUARIO = CampoTextoSeguro(
            ETIQUETA="Nombre de Usuario",
            ICONO=ft.Icons.PERSON_OUTLINED,
            VALIDADOR=self._VALIDAR_NOMBRE_USUARIO,
            TEXTO_AYUDA="Solo letras, números y guiones bajos",
            ANCHO=400
        )
        
        self._CAMPO_CONTRASENA = CampoTextoSeguro(
            ETIQUETA="Contraseña",
            ICONO=ft.Icons.LOCK_OUTLINED,
            ES_CONTRASENA=True,
            VALIDADOR=self._VALIDAR_CONTRASENA,
            ANCHO=400
        )
        
        self._CAMPO_CONFIRMAR_CONTRASENA = CampoTextoSeguro(
            ETIQUETA="Confirmar Contraseña",
            ICONO=ft.Icons.LOCK_OUTLINED,
            ES_CONTRASENA=True,
            VALIDADOR=self._VALIDAR_CONFIRMAR_CONTRASENA,
            ANCHO=400
        )
        
        # Indicador de fortaleza de contraseña
        INDICADOR_FORTALEZA = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Requisitos de contraseña:", size=12, weight=ft.FontWeight.W_500),
                    ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, size=16, color=ft.Colors.GREEN_600),
                        ft.Text("Mínimo 8 caracteres", size=11)
                    ], spacing=5),
                    ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, size=16, color=ft.Colors.GREEN_600),
                        ft.Text("Al menos una mayúscula", size=11)
                    ], spacing=5),
                    ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, size=16, color=ft.Colors.GREEN_600),
                        ft.Text("Al menos un número", size=11)
                    ], spacing=5),
                    ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, size=16, color=ft.Colors.GREEN_600),
                        ft.Text("Al menos un carácter especial", size=11)
                    ], spacing=5)
                ],
                spacing=3
            ),
            padding=10,
            bgcolor=ft.Colors.GREY_100,
            border_radius=8,
            width=400
        )
        
        # Checkbox de términos
        self._CHECKBOX_TERMINOS = ft.Checkbox(
            label="Acepto los términos y condiciones",
            value=False
        )
        
        # Texto de error
        self._TEXTO_ERROR = ft.Text(
            value="",
            color=ft.Colors.RED_400,
            size=14,
            visible=False,
            text_align=ft.TextAlign.CENTER
        )
        
        # Botón de registro
        self._BOTON_REGISTRAR = BotonPrimario(
            TEXTO="Crear Cuenta",
            ICONO=ft.Icons.CHECK_ROUNDED,
            AL_HACER_CLIC=self._MANEJAR_REGISTRO,
            ANCHO=400,
            ALTURA=55,
            COLOR_FONDO=ft.Colors.PURPLE_600
        )
        
        # Link para volver al login
        LINK_LOGIN = ft.TextButton(
            "¿Ya tienes cuenta? Inicia sesión",
            on_click=self._VOLVER_LOGIN,
            style=ft.ButtonStyle(color=ft.Colors.PURPLE_600)
        )
        
        # Formulario
        FORMULARIO = ft.Container(
            content=ft.Column(
                controls=[
                    HEADER,
                    self._CAMPO_EMAIL,
                    self._CAMPO_NOMBRE_USUARIO,
                    self._CAMPO_CONTRASENA,
                    self._CAMPO_CONFIRMAR_CONTRASENA,
                    INDICADOR_FORTALEZA,
                    self._CHECKBOX_TERMINOS,
                    self._TEXTO_ERROR,
                    ft.Container(height=10),
                    self._BOTON_REGISTRAR,
                    LINK_LOGIN
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
                scroll=ft.ScrollMode.AUTO
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
        
        CONTENEDOR_PRINCIPAL = ft.Container(
            content=ft.Column(
                controls=[FORMULARIO],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO
            ),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[ft.Colors.PURPLE_50, ft.Colors.PINK_50]
            ),
            expand=True,
            alignment=ft.Alignment(0, 0)
        )
        
        # Agregar al Column padre
        self.controls = [CONTENEDOR_PRINCIPAL]
        self.expand = True
    
    def _VALIDAR_EMAIL(self, EMAIL: str) -> Optional[str]:
        """Valida email"""
        if not EMAIL:
            return "El email es requerido"
        
        PATRON = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(PATRON, EMAIL):
            return "Formato de email inválido"
        
        return None
    
    def _VALIDAR_NOMBRE_USUARIO(self, NOMBRE: str) -> Optional[str]:
        """Valida nombre de usuario"""
        if not NOMBRE:
            return "El nombre de usuario es requerido"
        
        if len(NOMBRE) < 3:
            return "Mínimo 3 caracteres"
        
        if not re.match(r'^[a-zA-Z0-9_]+$', NOMBRE):
            return "Solo letras, números y guiones bajos"
        
        return None
    
    def _VALIDAR_CONTRASENA(self, CONTRASENA: str) -> Optional[str]:
        """Valida contraseña fuerte"""
        if not CONTRASENA:
            return "La contraseña es requerida"
        
        if len(CONTRASENA) < 8:
            return "Mínimo 8 caracteres"
        
        if not re.search(r'[A-Z]', CONTRASENA):
            return "Debe contener al menos una mayúscula"
        
        if not re.search(r'[a-z]', CONTRASENA):
            return "Debe contener al menos una minúscula"
        
        if not re.search(r'\d', CONTRASENA):
            return "Debe contener al menos un número"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', CONTRASENA):
            return "Debe contener al menos un carácter especial"
        
        return None
    
    def _VALIDAR_CONFIRMAR_CONTRASENA(self, CONFIRMAR: str) -> Optional[str]:
        """Valida que las contraseñas coincidan"""
        CONTRASENA = self._CAMPO_CONTRASENA.OBTENER_VALOR() if self._CAMPO_CONTRASENA else ""
        
        if not CONFIRMAR:
            return "Debes confirmar la contraseña"
        
        if CONFIRMAR != CONTRASENA:
            return "Las contraseñas no coinciden"
        
        return None
    
    async def _MANEJAR_REGISTRO(self, e):
        """Maneja el evento de registro"""
        # Validar todos los campos
        EMAIL_VALIDO = self._CAMPO_EMAIL.VALIDAR()
        NOMBRE_VALIDO = self._CAMPO_NOMBRE_USUARIO.VALIDAR()
        CONTRASENA_VALIDA = self._CAMPO_CONTRASENA.VALIDAR()
        CONFIRMAR_VALIDA = self._CAMPO_CONFIRMAR_CONTRASENA.VALIDAR()
        
        if not all([EMAIL_VALIDO, NOMBRE_VALIDO, CONTRASENA_VALIDA, CONFIRMAR_VALIDA]):
            return
        
        # Validar términos
        if not self._CHECKBOX_TERMINOS.value:
            self._MOSTRAR_ERROR("Debes aceptar los términos y condiciones")
            return
        
        # Obtener valores
        EMAIL = self._CAMPO_EMAIL.OBTENER_VALOR()
        NOMBRE_USUARIO = self._CAMPO_NOMBRE_USUARIO.OBTENER_VALOR()
        CONTRASENA = self._CAMPO_CONTRASENA.OBTENER_VALOR()
        
        # Ocultar error
        self._OCULTAR_ERROR()
        
        # Crear evento de registro
        EVENTO = EventoRegistrarse(
            EMAIL=EMAIL,
            NOMBRE_USUARIO=NOMBRE_USUARIO,
            CONTRASENA=CONTRASENA
        )
        
        # Enviar al BLoC
        await self._BLOC.AGREGAR_EVENTO(EVENTO)
    
    def _MANEJAR_ESTADO(self, ESTADO: EstadoAutenticacion):
        """Maneja cambios de estado"""
        if isinstance(ESTADO, EstadoRegistroExitoso):
            self._MOSTRAR_EXITO("¡Registro exitoso! Redirigiendo al login...")
            # Esperar 2 segundos y volver al login
            asyncio.create_task(self._ESPERAR_Y_VOLVER_LOGIN())
        
        elif isinstance(ESTADO, EstadoError):
            self._MOSTRAR_ERROR(ESTADO.ERROR)
    
    async def _ESPERAR_Y_VOLVER_LOGIN(self):
        """Espera 2 segundos y vuelve al login"""
        await asyncio.sleep(2)
        self._VOLVER_LOGIN(None)
    
    def _VOLVER_LOGIN(self, e):
        """Vuelve a la página de login"""
        from features.autenticacion.presentation.pages.PaginaLogin import PaginaLogin
        
        self._PAGINA.controls.clear()
        self._PAGINA.controls.append(PaginaLogin(self._PAGINA))
        self._PAGINA.update()
    
    def _MOSTRAR_ERROR(self, MENSAJE: str):
        """Muestra error"""
        if self._TEXTO_ERROR:
            self._TEXTO_ERROR.value = f"{MENSAJE}"
            self._TEXTO_ERROR.color = ft.Colors.RED_400
            self._TEXTO_ERROR.visible = True
            self.update()
    
    def _OCULTAR_ERROR(self):
        """Oculta error"""
        if self._TEXTO_ERROR:
            self._TEXTO_ERROR.visible = False
            self.update()
    
    def _MOSTRAR_EXITO(self, MENSAJE: str):
        """Muestra mensaje de éxito"""
        if self._TEXTO_ERROR:
            self._TEXTO_ERROR.value = f"{MENSAJE}"
            self._TEXTO_ERROR.color = ft.Colors.GREEN_600
            self._TEXTO_ERROR.visible = True
            self.update()