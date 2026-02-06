
import asyncio
from typing import Callable, List, Optional
from dataclasses import dataclass

from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_SUCURSAL

@dataclass
class SucursalesEstado:
    pass

@dataclass
class SucursalesInicial(SucursalesEstado):
    pass

@dataclass
class SucursalesCargando(SucursalesEstado):
    pass

@dataclass
class SucursalesCargadas(SucursalesEstado):
    sucursales: List
    total: int

@dataclass
class SucursalError(SucursalesEstado):
    mensaje: str

@dataclass
class SucursalGuardada(SucursalesEstado):
    mensaje: str

@dataclass
class SucursalesEvento:
    pass

@dataclass
class CargarSucursales(SucursalesEvento):
    pass

@dataclass
class GuardarSucursal(SucursalesEvento):
    datos: dict

@dataclass
class EliminarSucursal(SucursalesEvento):
    sucursal_id: int

class SucursalesBloc:
    def __init__(self):
        self._estado: SucursalesEstado = SucursalesInicial()
        self._listeners: List[Callable] = []
    
    @property
    def ESTADO(self) -> SucursalesEstado:
        return self._estado
    
    def AGREGAR_LISTENER(self, listener: Callable):
        if listener not in self._listeners:
            self._listeners.append(listener)
    
    def REMOVER_LISTENER(self, listener: Callable):
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def _CAMBIAR_ESTADO(self, nuevo_estado: SucursalesEstado):
        self._estado = nuevo_estado
        for listener in self._listeners:
            try:
                listener(self._estado)
            except Exception as e:
                print(f"Error: {e}")
    
    def AGREGAR_EVENTO(self, evento: SucursalesEvento):
        if isinstance(evento, CargarSucursales):
            asyncio.create_task(self._CARGAR())
        elif isinstance(evento, GuardarSucursal):
            asyncio.create_task(self._GUARDAR(evento))
        elif isinstance(evento, EliminarSucursal):
            asyncio.create_task(self._ELIMINAR(evento))
    
    async def _CARGAR(self):
        self._CAMBIAR_ESTADO(SucursalesCargando())
        try:
            sesion = OBTENER_SESION()
            sucursales = sesion.query(MODELO_SUCURSAL).all()
            sesion.close()
            self._CAMBIAR_ESTADO(SucursalesCargadas(sucursales=sucursales, total=len(sucursales)))
        except Exception as e:
            self._CAMBIAR_ESTADO(SucursalError(mensaje=str(e)))
    
    async def _GUARDAR(self, evento):
        self._CAMBIAR_ESTADO(SucursalesCargando())
        try:
            await asyncio.sleep(0.3)
            self._CAMBIAR_ESTADO(SucursalGuardada(mensaje="Sucursal guardada"))
            await self._CARGAR()
        except Exception as e:
            self._CAMBIAR_ESTADO(SucursalError(mensaje=str(e)))
    
    async def _ELIMINAR(self, evento):
        self._CAMBIAR_ESTADO(SucursalesCargando())
        try:
            sesion = OBTENER_SESION()
            sucursal = sesion.query(MODELO_SUCURSAL).filter_by(ID=evento.sucursal_id).first()
            if sucursal:
                sesion.delete(sucursal)
                sesion.commit()
            sesion.close()
            self._CAMBIAR_ESTADO(SucursalGuardada(mensaje="Eliminada"))
            await self._CARGAR()
        except Exception as e:
            self._CAMBIAR_ESTADO(SucursalError(mensaje=str(e)))

SUCURSALES_BLOC = SucursalesBloc()
