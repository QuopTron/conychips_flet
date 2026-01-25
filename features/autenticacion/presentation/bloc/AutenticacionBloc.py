import asyncio
from typing import Callable, Optional
from features.autenticacion.presentation.bloc.AutenticacionEvento import *
from features.autenticacion.presentation.bloc.AutenticacionEstado import *
from features.autenticacion.domain.usecases.IniciarSesion import IniciarSesion
from features.autenticacion.domain.usecases.RegistrarUsuario import RegistrarUsuario
from features.autenticacion.domain.usecases.RefrescarToken import RefrescarToken
from features.autenticacion.domain.usecases.VerificarPermisos import VerificarPermisos


class AutenticacionBloc:

    def __init__(
        self,
        INICIAR_SESION_UC: IniciarSesion,
        REGISTRAR_USUARIO_UC: RegistrarUsuario,
        REFRESCAR_TOKEN_UC: RefrescarToken,
        VERIFICAR_PERMISOS_UC: VerificarPermisos,
    ):

        self._INICIAR_SESION = INICIAR_SESION_UC
        self._REGISTRAR_USUARIO = REGISTRAR_USUARIO_UC
        self._REFRESCAR_TOKEN = REFRESCAR_TOKEN_UC
        self._VERIFICAR_PERMISOS = VERIFICAR_PERMISOS_UC

        self._ESTADO_ACTUAL: EstadoAutenticacion = EstadoInicial()

        self._LISTENERS: list[Callable[[EstadoAutenticacion], None]] = []

        self._ACCESS_TOKEN: Optional[str] = None
        self._REFRESH_TOKEN: Optional[str] = None

    def AGREGAR_LISTENER(self, CALLBACK: Callable[[EstadoAutenticacion], None]):

        self._LISTENERS.append(CALLBACK)

    def REMOVER_LISTENER(self, CALLBACK: Callable[[EstadoAutenticacion], None]):

        if CALLBACK in self._LISTENERS:
            self._LISTENERS.remove(CALLBACK)

    def _EMITIR_ESTADO(self, NUEVO_ESTADO: EstadoAutenticacion):

        self._ESTADO_ACTUAL = NUEVO_ESTADO

        print(f"BLoC emite: {type(NUEVO_ESTADO).__name__}")

        for LISTENER in self._LISTENERS:
            try:
                LISTENER(NUEVO_ESTADO)
            except Exception as ERROR:
                print(f"Error en listener: {ERROR}")

    async def AGREGAR_EVENTO(self, EVENTO: EventoAutenticacion):

        print(f"BLoC recibe evento: {type(EVENTO).__name__}")

        if isinstance(EVENTO, EventoIniciarSesion):
            await self._MANEJAR_INICIAR_SESION(EVENTO)

        elif isinstance(EVENTO, EventoRegistrarse):
            await self._MANEJAR_REGISTRARSE(EVENTO)

        elif isinstance(EVENTO, EventoCerrarSesion):
            await self._MANEJAR_CERRAR_SESION(EVENTO)

        elif isinstance(EVENTO, EventoRefrescarToken):
            await self._MANEJAR_REFRESCAR_TOKEN(EVENTO)

        elif isinstance(EVENTO, EventoVerificarSesion):
            await self._MANEJAR_VERIFICAR_SESION(EVENTO)

        else:
            print(f"Evento no manejado: {type(EVENTO).__name__}")

    async def _MANEJAR_INICIAR_SESION(self, EVENTO: EventoIniciarSesion):

        self._EMITIR_ESTADO(EstadoCargando("Iniciando sesión..."))

        try:
            RESULTADO = await self._INICIAR_SESION.EJECUTAR(
                EMAIL=EVENTO.EMAIL, CONTRASENA=EVENTO.CONTRASENA
            )

            if RESULTADO["EXITO"]:
                self._ACCESS_TOKEN = RESULTADO["ACCESS_TOKEN"]
                self._REFRESH_TOKEN = RESULTADO["REFRESH_TOKEN"]

                if RESULTADO.get("REQUIERE_2FA"):
                    self._EMITIR_ESTADO(
                        EstadoRequiereSegundoFactor(
                            USUARIO_ID=RESULTADO["USUARIO"].ID,
                            METODO=RESULTADO.get("METODO_2FA", "email"),
                        )
                    )
                else:
                    self._EMITIR_ESTADO(
                        EstadoAutenticado(
                            USUARIO=RESULTADO["USUARIO"],
                            ACCESS_TOKEN=self._ACCESS_TOKEN,
                            REFRESH_TOKEN=self._REFRESH_TOKEN,
                        )
                    )
            else:
                self._EMITIR_ESTADO(
                    EstadoError(
                        ERROR=RESULTADO["ERROR"], CODIGO=RESULTADO.get("CODIGO", 401)
                    )
                )

        except Exception as ERROR:
            print(f" Error al iniciar sesión: {ERROR}")
            self._EMITIR_ESTADO(
                EstadoError(ERROR="Error al procesar inicio de sesión", CODIGO=500)
            )

    async def _MANEJAR_REGISTRARSE(self, EVENTO: EventoRegistrarse):

        self._EMITIR_ESTADO(EstadoCargando("Registrando usuario..."))

        try:
            RESULTADO = await self._REGISTRAR_USUARIO.EJECUTAR(
                EMAIL=EVENTO.EMAIL,
                NOMBRE_USUARIO=EVENTO.NOMBRE_USUARIO,
                CONTRASENA=EVENTO.CONTRASENA,
            )

            if RESULTADO["EXITO"]:
                self._EMITIR_ESTADO(EstadoRegistroExitoso(EMAIL=EVENTO.EMAIL))
            else:
                self._EMITIR_ESTADO(
                    EstadoError(
                        ERROR=RESULTADO["ERROR"], CODIGO=RESULTADO.get("CODIGO", 400)
                    )
                )

        except Exception as ERROR:
            print(f" Error al registrar: {ERROR}")
            self._EMITIR_ESTADO(
                EstadoError(ERROR="Error al procesar registro", CODIGO=500)
            )

    async def _MANEJAR_CERRAR_SESION(self, EVENTO: EventoCerrarSesion):

        self._ACCESS_TOKEN = None
        self._REFRESH_TOKEN = None

        self._EMITIR_ESTADO(EstadoNoAutenticado("Sesión cerrada"))

        print("Sesión cerrada exitosamente")

    async def _MANEJAR_REFRESCAR_TOKEN(self, EVENTO: EventoRefrescarToken):

        try:
            RESULTADO = await self._REFRESCAR_TOKEN.EJECUTAR(
                REFRESH_TOKEN=EVENTO.REFRESH_TOKEN
            )

            if RESULTADO["EXITO"]:
                self._ACCESS_TOKEN = RESULTADO["ACCESS_TOKEN"]

                if isinstance(self._ESTADO_ACTUAL, EstadoAutenticado):
                    self._EMITIR_ESTADO(
                        EstadoAutenticado(
                            USUARIO=self._ESTADO_ACTUAL.USUARIO,
                            ACCESS_TOKEN=self._ACCESS_TOKEN,
                            REFRESH_TOKEN=self._REFRESH_TOKEN,
                            MENSAJE="Token refrescado",
                        )
                    )
            else:
                self._EMITIR_ESTADO(EstadoSesionExpirada())

        except Exception as ERROR:
            print(f" Error al refrescar token: {ERROR}")
            self._EMITIR_ESTADO(EstadoSesionExpirada())

    async def _MANEJAR_VERIFICAR_SESION(self, EVENTO: EventoVerificarSesion):

        if self._ACCESS_TOKEN:
            print("Sesión activa encontrada")
        else:
            self._EMITIR_ESTADO(EstadoNoAutenticado())

    @property
    def ESTADO_ACTUAL(self) -> EstadoAutenticacion:

        return self._ESTADO_ACTUAL

    @property
    def ESTA_AUTENTICADO(self) -> bool:

        return isinstance(self._ESTADO_ACTUAL, EstadoAutenticado)

    def OBTENER_USUARIO_ACTUAL(self) -> Optional[Usuario]:

        if isinstance(self._ESTADO_ACTUAL, EstadoAutenticado):
            return self._ESTADO_ACTUAL.USUARIO
        return None
