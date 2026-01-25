import flet as ft
from features.autenticacion.presentation.widgets.CampoTextoSeguro import (
    CampoTextoSeguro,
)
from features.autenticacion.presentation.widgets.BotonPrimario import BotonPrimario
from features.autenticacion.presentation.bloc.AutenticacionBloc import AutenticacionBloc
from features.autenticacion.presentation.bloc.AutenticacionEvento import (
    EventoRegistrarse,
)
from features.autenticacion.presentation.bloc.AutenticacionEstado import *
from core.Constantes import (
    COLORES,
    TAMANOS,
    ICONOS,
    ERRORES_AUTENTICACION,
    ERRORES_VALIDACION,
    MENSAJES_EXITO,
    MENSAJES_CONFIRMACION,
)
import re
import asyncio
from typing import Optional


class PaginaRegistro(ft.Column):

    def __init__(self, PAGINA: ft.Page, BLOC: AutenticacionBloc):

        super().__init__()
        self._PAGINA = PAGINA
        self._BLOC = BLOC

        self._BLOC.AGREGAR_LISTENER(self._MANEJAR_ESTADO)

        self._CAMPO_EMAIL: Optional[CampoTextoSeguro] = None
        self._CAMPO_NOMBRE_USUARIO: Optional[CampoTextoSeguro] = None
        self._CAMPO_CONTRASENA: Optional[CampoTextoSeguro] = None
        self._CAMPO_CONFIRMAR_CONTRASENA: Optional[CampoTextoSeguro] = None
        self._BOTON_REGISTRAR: Optional[BotonPrimario] = None
        self._TEXTO_ERROR: Optional[ft.Text] = None
        self._CHECKBOX_TERMINOS: Optional[ft.Checkbox] = None

        self._CONSTRUIR()

    def _CONSTRUIR(self):

        HEADER = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(
                        ft.Icons.PERSON_ADD_ROUNDED, size=70, color=COLORES.SECUNDARIO
                    ),
                    ft.Text(
                        value="Crear Cuenta",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=COLORES.SECUNDARIO,
                    ),
                    ft.Text(
                        value="Completa el formulario para registrarte",
                        size=TAMANOS.TEXTO_MD,
                        color=COLORES.TEXTO_SECUNDARIO,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            margin=ft.Margin.only(bottom=25),
        )

        self._CAMPO_EMAIL = CampoTextoSeguro(
            ETIQUETA="Email",
            ICONO=ICONOS.EMAIL,
            TIPO_TECLADO=ft.KeyboardType.EMAIL,
            VALIDADOR=self._VALIDAR_EMAIL,
            ANCHO=400,
        )

        self._CAMPO_NOMBRE_USUARIO = CampoTextoSeguro(
            ETIQUETA="Nombre de Usuario",
            ICONO=ICONOS.USUARIO,
            VALIDADOR=self._VALIDAR_NOMBRE_USUARIO,
            TEXTO_AYUDA="Solo letras, números y guiones bajos",
            ANCHO=400,
        )

        self._CAMPO_CONTRASENA = CampoTextoSeguro(
            ETIQUETA="Contraseña",
            ICONO=ICONOS.CONTRASENA,
            ES_CONTRASENA=True,
            VALIDADOR=self._VALIDAR_CONTRASENA,
            ANCHO=400,
        )

        self._CAMPO_CONFIRMAR_CONTRASENA = CampoTextoSeguro(
            ETIQUETA="Confirmar Contraseña",
            ICONO=ICONOS.CONTRASENA,
            ES_CONTRASENA=True,
            VALIDADOR=self._VALIDAR_CONFIRMAR_CONTRASENA,
            ANCHO=400,
        )

        INDICADOR_FORTALEZA = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Requisitos de contraseña:", size=TAMANOS.TEXTO_SM, weight=ft.FontWeight.W_500
                    ),
                    ft.Row(
                        [
                            ft.Icon(
                                ICONOS.EXITO,
                                size=TAMANOS.ICONO_XS,
                                color=COLORES.EXITO,
                            ),
                            ft.Text("Mínimo 8 caracteres", size=11),
                        ],
                        spacing=5,
                    ),
                    ft.Row(
                        [
                            ft.Icon(
                                ICONOS.EXITO,
                                size=TAMANOS.ICONO_XS,
                                color=COLORES.EXITO,
                            ),
                            ft.Text("Al menos una mayúscula", size=11),
                        ],
                        spacing=5,
                    ),
                    ft.Row(
                        [
                            ft.Icon(
                                ICONOS.EXITO,
                                size=TAMANOS.ICONO_XS,
                                color=COLORES.EXITO,
                            ),
                            ft.Text("Al menos un número", size=11),
                        ],
                        spacing=5,
                    ),
                    ft.Row(
                        [
                            ft.Icon(
                                ICONOS.EXITO,
                                size=TAMANOS.ICONO_XS,
                                color=COLORES.EXITO,
                            ),
                            ft.Text("Al menos un carácter especial", size=11),
                        ],
                        spacing=5,
                    ),
                ],
                spacing=3,
            ),
            padding=TAMANOS.PADDING_MD,
            bgcolor=ft.Colors.GREY_100,
            border_radius=8,
            width=400,
        )

        self._CHECKBOX_TERMINOS = ft.Checkbox(
            label="Acepto los términos y condiciones", value=False
        )

        self._TEXTO_ERROR = ft.Text(
            value="",
            color=COLORES.PELIGRO_CLARO,
            size=TAMANOS.TEXTO_MD,
            visible=False,
            text_align=ft.TextAlign.CENTER,
        )

        self._BOTON_REGISTRAR = BotonPrimario(
            TEXTO="Crear Cuenta",
            ICONO=ft.Icons.CHECK_ROUNDED,
            AL_HACER_CLIC=self._MANEJAR_REGISTRO,
            ANCHO=400,
            ALTURA=55,
            COLOR_FONDO=COLORES.SECUNDARIO,
        )

        LINK_LOGIN = ft.TextButton(
            "¿Ya tienes cuenta? Inicia sesión",
            on_click=self._VOLVER_LOGIN,
            style=ft.ButtonStyle(color=COLORES.SECUNDARIO),
        )

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
                    LINK_LOGIN,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=40,
            bgcolor=COLORES.FONDO_BLANCO,
            border_radius=15,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 5),
            ),
            width=500,
        )

        CONTENEDOR_PRINCIPAL = ft.Container(
            content=ft.Column(
                controls=[FORMULARIO],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO,
            ),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[COLORES.SECUNDARIO_CLARO, ft.Colors.PINK_50],
            ),
            expand=True,
            alignment=ft.Alignment(0, 0),
        )

        self.controls = [CONTENEDOR_PRINCIPAL]
        self.expand = True

    def _VALIDAR_EMAIL(self, EMAIL: str) -> Optional[str]:

        if not EMAIL:
            return "El email es requerido"

        PATRON = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(PATRON, EMAIL):
            return "Formato de email inválido"

        return None

    def _VALIDAR_NOMBRE_USUARIO(self, NOMBRE: str) -> Optional[str]:

        if not NOMBRE:
            return "El nombre de usuario es requerido"

        if len(NOMBRE) < 3:
            return "Mínimo 3 caracteres"

        if not re.match(r"^[a-zA-Z0-9_]+$", NOMBRE):
            return "Solo letras, números y guiones bajos"

        return None

    def _VALIDAR_CONTRASENA(self, CONTRASENA: str) -> Optional[str]:

        if not CONTRASENA:
            return "La contraseña es requerida"

        if len(CONTRASENA) < 8:
            return "Mínimo 8 caracteres"

        if not re.search(r"[A-Z]", CONTRASENA):
            return "Debe contener al menos una mayúscula"

        if not re.search(r"[a-z]", CONTRASENA):
            return "Debe contener al menos una minúscula"

        if not re.search(r"\d", CONTRASENA):
            return "Debe contener al menos un número"

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', CONTRASENA):
            return "Debe contener al menos un carácter especial"

        return None

    def _VALIDAR_CONFIRMAR_CONTRASENA(self, CONFIRMAR: str) -> Optional[str]:

        CONTRASENA = (
            self._CAMPO_CONTRASENA.OBTENER_VALOR() if self._CAMPO_CONTRASENA else ""
        )

        if not CONFIRMAR:
            return "Debes confirmar la contraseña"

        if CONFIRMAR != CONTRASENA:
            return "Las contraseñas no coinciden"

        return None

    async def _MANEJAR_REGISTRO(self, e):

        EMAIL_VALIDO = self._CAMPO_EMAIL.VALIDAR()
        NOMBRE_VALIDO = self._CAMPO_NOMBRE_USUARIO.VALIDAR()
        CONTRASENA_VALIDA = self._CAMPO_CONTRASENA.VALIDAR()
        CONFIRMAR_VALIDA = self._CAMPO_CONFIRMAR_CONTRASENA.VALIDAR()

        if not all([EMAIL_VALIDO, NOMBRE_VALIDO, CONTRASENA_VALIDA, CONFIRMAR_VALIDA]):
            return

        if not self._CHECKBOX_TERMINOS.value:
            self._MOSTRAR_ERROR("Debes aceptar los términos y condiciones")
            return

        EMAIL = self._CAMPO_EMAIL.OBTENER_VALOR()
        NOMBRE_USUARIO = self._CAMPO_NOMBRE_USUARIO.OBTENER_VALOR()
        CONTRASENA = self._CAMPO_CONTRASENA.OBTENER_VALOR()

        self._OCULTAR_ERROR()

        EVENTO = EventoRegistrarse(
            EMAIL=EMAIL, NOMBRE_USUARIO=NOMBRE_USUARIO, CONTRASENA=CONTRASENA
        )

        await self._BLOC.AGREGAR_EVENTO(EVENTO)

    def _MANEJAR_ESTADO(self, ESTADO: EstadoAutenticacion):

        if isinstance(ESTADO, EstadoRegistroExitoso):
            self._MOSTRAR_EXITO("¡Registro exitoso! Redirigiendo al login...")
            asyncio.create_task(self._ESPERAR_Y_VOLVER_LOGIN())

        elif isinstance(ESTADO, EstadoError):
            self._MOSTRAR_ERROR(ESTADO.ERROR)

    async def _ESPERAR_Y_VOLVER_LOGIN(self):

        await asyncio.sleep(2)
        self._VOLVER_LOGIN(None)

    def _VOLVER_LOGIN(self, e):

        from features.autenticacion.presentation.pages.PaginaLogin import PaginaLogin

        self._PAGINA.controls.clear()
        self._PAGINA.controls.append(PaginaLogin(self._PAGINA))
        self._PAGINA.update()

    def _MOSTRAR_ERROR(self, MENSAJE: str):

        if self._TEXTO_ERROR:
            self._TEXTO_ERROR.value = f"{MENSAJE}"
            self._TEXTO_ERROR.color = COLORES.PELIGRO_CLARO
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
