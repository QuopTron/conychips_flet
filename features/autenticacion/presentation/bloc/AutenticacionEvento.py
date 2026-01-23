#conychips/features/autentitacion/presentation/bloc/AutenticacionEvento.py
from dataclasses import dataclass
from typing import Optional


@dataclass
class EventoAutenticacion:
    """Clase base para todos los eventos de autenticación"""
    pass


@dataclass
class EventoIniciarSesion(EventoAutenticacion):
    """Evento: Usuario intenta iniciar sesión"""
    EMAIL: str
    CONTRASENA: str


@dataclass
class EventoRegistrarse(EventoAutenticacion):
    """Evento: Usuario intenta registrarse"""
    EMAIL: str
    NOMBRE_USUARIO: str
    CONTRASENA: str


@dataclass
class EventoCerrarSesion(EventoAutenticacion):
    """Evento: Usuario cierra sesión"""
    pass


@dataclass
class EventoVerificarSesion(EventoAutenticacion):
    """Evento: Verificar si hay sesión activa válida"""
    pass


@dataclass
class EventoRefrescarToken(EventoAutenticacion):
    """Evento: Refrescar access token usando refresh token"""
    REFRESH_TOKEN: str


@dataclass
class EventoActualizarPerfil(EventoAutenticacion):
    """Evento: Actualizar información del perfil"""
    NOMBRE_USUARIO: Optional[str] = None
    EMAIL: Optional[str] = None


@dataclass
class EventoCambiarContrasena(EventoAutenticacion):
    """Evento: Cambiar contraseña del usuario"""
    CONTRASENA_ACTUAL: str
    CONTRASENA_NUEVA: str


@dataclass
class EventoVerificarSegundoFactor(EventoAutenticacion):
    """Evento: Verificar código de segundo factor (2FA)"""
    CODIGO: str
    USUARIO_ID: int


@dataclass
class EventoSolicitarRecuperacion(EventoAutenticacion):
    """Evento: Solicitar recuperación de contraseña"""
    EMAIL: str


@dataclass
class EventoRestablecerContrasena(EventoAutenticacion):
    """Evento: Restablecer contraseña con token"""
    TOKEN_RECUPERACION: str
    CONTRASENA_NUEVA: str