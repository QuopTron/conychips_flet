#conychips/features/autentitacion/presentation/bloc/AutenticacionEstado.py
from dataclasses import dataclass
from typing import Optional
from features.autenticacion.domain.entities.Usuario import Usuario


@dataclass
class EstadoAutenticacion:
    """Clase base para todos los estados de autenticación"""
    pass


@dataclass
class EstadoInicial(EstadoAutenticacion):
    """Estado inicial - sin autenticación"""
    pass


@dataclass
class EstadoCargando(EstadoAutenticacion):
    """Estado: Procesando operación de autenticación"""
    MENSAJE: str = "Procesando..."


@dataclass
class EstadoAutenticado(EstadoAutenticacion):
    """Estado: Usuario autenticado exitosamente"""
    USUARIO: Usuario
    ACCESS_TOKEN: str
    REFRESH_TOKEN: str
    MENSAJE: str = "Sesión iniciada exitosamente"


@dataclass
class EstadoNoAutenticado(EstadoAutenticacion):
    """Estado: Usuario no autenticado"""
    MENSAJE: Optional[str] = None


@dataclass
class EstadoError(EstadoAutenticacion):
    """Estado: Error en operación de autenticación"""
    ERROR: str
    CODIGO: int = 500


@dataclass
class EstadoRegistroExitoso(EstadoAutenticacion):
    """Estado: Registro completado, pendiente verificación"""
    EMAIL: str
    MENSAJE: str = "Registro exitoso. Verifica tu email."


@dataclass
class EstadoSesionExpirada(EstadoAutenticacion):
    """Estado: Sesión expirada, requiere nuevo login"""
    MENSAJE: str = "Tu sesión ha expirado. Por favor inicia sesión nuevamente."


@dataclass
class EstadoRequiereSegundoFactor(EstadoAutenticacion):
    """Estado: Requiere verificación de segundo factor"""
    USUARIO_ID: int
    METODO: str  # 'sms', 'email', 'authenticator'
    MENSAJE: str = "Se requiere verificación de segundo factor"


@dataclass
class EstadoActualizando(EstadoAutenticacion):
    """Estado: Actualizando información del usuario"""
    MENSAJE: str = "Actualizando información..."


@dataclass
class EstadoPerfilActualizado(EstadoAutenticacion):
    """Estado: Perfil actualizado exitosamente"""
    USUARIO: Usuario
    MENSAJE: str = "Perfil actualizado exitosamente"


@dataclass
class EstadoRecuperacionEnviada(EstadoAutenticacion):
    """Estado: Email de recuperación enviado"""
    EMAIL: str
    MENSAJE: str = "Se ha enviado un email con instrucciones de recuperación"


@dataclass
class EstadoContrasenaRestablecida(EstadoAutenticacion):
    """Estado: Contraseña restablecida exitosamente"""
    MENSAJE: str = "Contraseña restablecida. Ahora puedes iniciar sesión."