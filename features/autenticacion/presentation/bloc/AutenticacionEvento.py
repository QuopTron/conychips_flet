from dataclasses import dataclass
from typing import Optional

@dataclass
class EventoAutenticacion:
    
    pass

@dataclass
class EventoIniciarSesion(EventoAutenticacion):
    
    EMAIL: str
    CONTRASENA: str

@dataclass
class EventoRegistrarse(EventoAutenticacion):
    
    EMAIL: str
    NOMBRE_USUARIO: str
    CONTRASENA: str

@dataclass
class EventoCerrarSesion(EventoAutenticacion):
    
    pass

@dataclass
class EventoVerificarSesion(EventoAutenticacion):
    
    pass

@dataclass
class EventoRefrescarToken(EventoAutenticacion):
    
    REFRESH_TOKEN: str

@dataclass
class EventoActualizarPerfil(EventoAutenticacion):
    
    NOMBRE_USUARIO: Optional[str] = None
    EMAIL: Optional[str] = None

@dataclass
class EventoCambiarContrasena(EventoAutenticacion):
    
    CONTRASENA_ACTUAL: str
    CONTRASENA_NUEVA: str

@dataclass
class EventoVerificarSegundoFactor(EventoAutenticacion):
    
    CODIGO: str
    USUARIO_ID: int

@dataclass
class EventoSolicitarRecuperacion(EventoAutenticacion):
    
    EMAIL: str

@dataclass
class EventoRestablecerContrasena(EventoAutenticacion):
    
    TOKEN_RECUPERACION: str
    CONTRASENA_NUEVA: str
