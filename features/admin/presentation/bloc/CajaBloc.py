
import asyncio
from typing import Callable, List, Optional
from dataclasses import dataclass

from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_CAJA

@dataclass
class CajaEstado:
    pass

@dataclass
class CajaInicial(CajaEstado):
    pass

@dataclass
class CajaCargando(CajaEstado):
    pass

@dataclass
class CajasCargados(CajaEstado):
    cajas: List
    total: int

@dataclass
class CajaError(CajaEstado):
    mensaje: str

@dataclass
class CajaGuardado(CajaEstado):
    mensaje: str

@dataclass
class CajaEliminado(CajaEstado):
    mensaje: str

@dataclass
class CajaEvento:
    pass

@dataclass
class CargarCajas(CajaEvento):
    filtro: Optional[str] = None

@dataclass
class GuardarCaja(CajaEvento):
    datos: dict

@dataclass
class EliminarCaja(CajaEvento):
    caja_id: int

class CajaBloc:
    
    def __init__(self):
        self._estado: CajaEstado = CajaInicial()
        self._listeners: List[Callable] = []
    
    @property
    def ESTADO(self) -> CajaEstado:
        return self._estado
    
    def AGREGAR_LISTENER(self, listener: Callable):
        if listener not in self._listeners:
            self._listeners.append(listener)
    
    def REMOVER_LISTENER(self, listener: Callable):
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def _CAMBIAR_ESTADO(self, nuevo_estado: CajaEstado):
        self._estado = nuevo_estado
        for listener in self._listeners:
            try:
                listener(self._estado)
            except Exception as e:
                print(f"Error en listener: {e}")
    
    def AGREGAR_EVENTO(self, evento: CajaEvento):
        if isinstance(evento, CargarCajas):
            asyncio.create_task(self._CARGAR(evento.filtro))
        elif isinstance(evento, GuardarCaja):
            asyncio.create_task(self._GUARDAR(evento))
        elif isinstance(evento, EliminarCaja):
            asyncio.create_task(self._ELIMINAR(evento))
    
    async def _CARGAR(self, filtro: Optional[str]):
        self._CAMBIAR_ESTADO(CajaCargando())
        
        try:
            sesion = OBTENER_SESION()
            query = sesion.query(MODELO_CAJA)
            
            if filtro:
                query = query.filter(MODELO_CAJA.NOMBRE.contains(filtro))
            
            datos = query.all()
            total = len(datos)
            
            sesion.close()
            
            self._CAMBIAR_ESTADO(CajasCargados(cajas=datos, total=total))
        
        except Exception as e:
            self._CAMBIAR_ESTADO(CajaError(mensaje=f"Error cargando: {str(e)}"))
    
    async def _GUARDAR(self, evento: GuardarCaja):
        self._CAMBIAR_ESTADO(CajaCargando())
        
        try:
            sesion = OBTENER_SESION()
            
            
            sesion.commit()
            sesion.close()
            
            self._CAMBIAR_ESTADO(CajaGuardado(mensaje="Caja guardado exitosamente"))
            await self._CARGAR(None)
        
        except Exception as e:
            self._CAMBIAR_ESTADO(CajaError(mensaje=f"Error guardando: {str(e)}"))
    
    async def _ELIMINAR(self, evento: EliminarCaja):
        self._CAMBIAR_ESTADO(CajaCargando())
        
        try:
            sesion = OBTENER_SESION()
            caja = sesion.query(MODELO_CAJA).filter_by(ID=evento.caja_id).first()
            
            if caja:
                sesion.delete(caja)
                sesion.commit()
                sesion.close()
                
                self._CAMBIAR_ESTADO(CajaEliminado(mensaje="Caja eliminado"))
                await self._CARGAR(None)
            else:
                sesion.close()
                self._CAMBIAR_ESTADO(CajaError(mensaje="Caja no encontrado"))
        
        except Exception as e:
            self._CAMBIAR_ESTADO(CajaError(mensaje=f"Error eliminando: {str(e)}"))

CAJA_BLOC = CajaBloc()
