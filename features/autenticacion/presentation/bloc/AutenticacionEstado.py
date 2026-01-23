from dataclasses import dataclass
from typing import Optional
from features.autenticacion.domain.entities.Usuario import Usuario


@dataclass
class EstadoAutenticacion:

    pass


@dataclass
class EstadoInicial(EstadoAutenticacion):

    pass


@dataclass
class EstadoCargando(EstadoAutenticacion):

    MENSAJE: str = "Procesando..."


@dataclass
class EstadoAutenticado(EstadoAutenticacion):

    USUARIO: Usuario
    ACCESS_TOKEN: str
    REFRESH_TOKEN: str
    MENSAJE: str = "Sesión iniciada exitosamente"


@dataclass
class EstadoNoAutenticado(EstadoAutenticacion):

    MENSAJE: Optional[str] = None


@dataclass
class EstadoError(EstadoAutenticacion):

    ERROR: str
    CODIGO: int = 500


@dataclass
class EstadoRegistroExitoso(EstadoAutenticacion):

    EMAIL: str
    MENSAJE: str = "Registro exitoso. Verifica tu email."


@dataclass
class EstadoSesionExpirada(EstadoAutenticacion):

    MENSAJE: str = "Tu sesión ha expirado. Por favor inicia sesión nuevamente."


@dataclass
class EstadoRequiereSegundoFactor(EstadoAutenticacion):

    USUARIO_ID: int
    METODO: str  # 'sms', 'email', 'authenticator'
    MENSAJE: str = "Se requiere verificación de segundo factor"


@dataclass
class EstadoActualizando(EstadoAutenticacion):

    MENSAJE: str = "Actualizando información..."


@dataclass
class EstadoPerfilActualizado(EstadoAutenticacion):

    USUARIO: Usuario
    MENSAJE: str = "Perfil actualizado exitosamente"


@dataclass
class EstadoRecuperacionEnviada(EstadoAutenticacion):

    EMAIL: str
    MENSAJE: str = "Se ha enviado un email con instrucciones de recuperación"


@dataclass
class EstadoContrasenaRestablecida(EstadoAutenticacion):

    MENSAJE: str = "Contraseña restablecida. Ahora puedes iniciar sesión."
