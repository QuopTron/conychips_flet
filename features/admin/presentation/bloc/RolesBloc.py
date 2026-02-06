
import asyncio
from typing import Callable, List
from dataclasses import dataclass

from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_ROL

@dataclass
class RolesEstado:
    pass

@dataclass
class RolesInicial(RolesEstado):
    pass

@dataclass
class RolesCargando(RolesEstado):
    pass

@dataclass
class RolesCargados(RolesEstado):
    roles: List
    permisos: List

@dataclass
class RolError(RolesEstado):
    mensaje: str

@dataclass
class RolGuardado(RolesEstado):
    mensaje: str

@dataclass
class RolesEvento:
    pass

@dataclass
class CargarRoles(RolesEvento):
    pass

@dataclass
class CrearRol(RolesEvento):
    nombre: str
    descripcion: str
    permisos_ids: List[int]

@dataclass
class ActualizarPermisos(RolesEvento):
    rol_id: int
    permisos_ids: List[int]

class RolesBloc:
    def __init__(self):
        self._estado: RolesEstado = RolesInicial()
        self._listeners: List[Callable] = []
    
    @property
    def ESTADO(self) -> RolesEstado:
        return self._estado
    
    def AGREGAR_LISTENER(self, listener: Callable):
        if listener not in self._listeners:
            self._listeners.append(listener)
    
    def REMOVER_LISTENER(self, listener: Callable):
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def _CAMBIAR_ESTADO(self, nuevo_estado: RolesEstado):
        self._estado = nuevo_estado
        for listener in self._listeners:
            try:
                listener(self._estado)
            except:
                pass
    
    def AGREGAR_EVENTO(self, evento: RolesEvento):
        if isinstance(evento, CargarRoles):
            asyncio.create_task(self._CARGAR())
        elif isinstance(evento, CrearRol):
            asyncio.create_task(self._CREAR(evento))
        elif isinstance(evento, ActualizarPermisos):
            asyncio.create_task(self._ACTUALIZAR_PERMISOS(evento))
    
    async def _CARGAR(self):
        self._CAMBIAR_ESTADO(RolesCargando())
        try:
            sesion = OBTENER_SESION()
            roles = sesion.query(MODELO_ROL).all()
            sesion.close()
            self._CAMBIAR_ESTADO(RolesCargados(roles=roles, permisos=[]))
        except Exception as e:
            self._CAMBIAR_ESTADO(RolError(mensaje=str(e)))
    
    async def _CREAR(self, evento):
        self._CAMBIAR_ESTADO(RolesCargando())
        try:
            await asyncio.sleep(0.3)
            self._CAMBIAR_ESTADO(RolGuardado(mensaje="Rol creado"))
            await self._CARGAR()
        except Exception as e:
            self._CAMBIAR_ESTADO(RolError(mensaje=str(e)))
    
    async def _ACTUALIZAR_PERMISOS(self, evento):
        self._CAMBIAR_ESTADO(RolesCargando())
        try:
            await asyncio.sleep(0.3)
            self._CAMBIAR_ESTADO(RolGuardado(mensaje="Permisos actualizados"))
            await self._CARGAR()
        except Exception as e:
            self._CAMBIAR_ESTADO(RolError(mensaje=str(e)))

ROLES_BLOC = RolesBloc()

__all__ = [
    'RolesEstado',
    'RolesInicial',
    'RolesCargando',
    'RolesCargados',
    'RolError',
    'RolGuardado',
    'RolesEvento',
    'CargarRoles',
    'CrearRol',
    'ActualizarPermisos',
    'RolesBloc',
    'ROLES_BLOC',
]
