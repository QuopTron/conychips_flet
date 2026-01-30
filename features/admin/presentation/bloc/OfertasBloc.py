
import asyncio
from typing import Callable, List, Optional
from dataclasses import dataclass

from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_OFERTAS

@dataclass
class OfertasEstado:
    pass

@dataclass
class OfertasInicial(OfertasEstado):
    pass

@dataclass
class OfertasCargando(OfertasEstado):
    pass

@dataclass
class OfertasesCargados(OfertasEstado):
    ofertass: List
    total: int

@dataclass
class OfertasError(OfertasEstado):
    mensaje: str

@dataclass
class OfertasGuardado(OfertasEstado):
    mensaje: str

@dataclass
class OfertasEliminado(OfertasEstado):
    mensaje: str

@dataclass
class OfertasEvento:
    pass

@dataclass
class CargarOfertases(OfertasEvento):
    filtro: Optional[str] = None

@dataclass
class GuardarOfertas(OfertasEvento):
    datos: dict

@dataclass
class EliminarOfertas(OfertasEvento):
    ofertas_id: int

class OfertasBloc:
    
    def __init__(self):
        self._estado: OfertasEstado = OfertasInicial()
        self._listeners: List[Callable] = []
    
    @property
    def ESTADO(self) -> OfertasEstado:
        return self._estado
    
    def AGREGAR_LISTENER(self, listener: Callable):
        if listener not in self._listeners:
            self._listeners.append(listener)
    
    def REMOVER_LISTENER(self, listener: Callable):
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def _CAMBIAR_ESTADO(self, nuevo_estado: OfertasEstado):
        self._estado = nuevo_estado
        for listener in self._listeners:
            try:
                listener(self._estado)
            except Exception as e:
                print(f"Error en listener: {e}")
    
    def AGREGAR_EVENTO(self, evento: OfertasEvento):
        if isinstance(evento, CargarOfertases):
            asyncio.create_task(self._CARGAR(evento.filtro))
        elif isinstance(evento, GuardarOfertas):
            asyncio.create_task(self._GUARDAR(evento))
        elif isinstance(evento, EliminarOfertas):
            asyncio.create_task(self._ELIMINAR(evento))
    
    async def _CARGAR(self, filtro: Optional[str]):
        self._CAMBIAR_ESTADO(OfertasCargando())
        
        try:
            sesion = OBTENER_SESION()
            query = sesion.query(MODELO_OFERTAS)
            
            if filtro:
                query = query.filter(MODELO_OFERTAS.NOMBRE.contains(filtro))
            
            datos = query.all()
            total = len(datos)
            
            sesion.close()
            
            self._CAMBIAR_ESTADO(OfertasesCargados(ofertass=datos, total=total))
        
        except Exception as e:
            self._CAMBIAR_ESTADO(OfertasError(mensaje=f"Error cargando: {str(e)}"))
    
    async def _GUARDAR(self, evento: GuardarOfertas):
        self._CAMBIAR_ESTADO(OfertasCargando())
        
        try:
            sesion = OBTENER_SESION()
            
            
            sesion.commit()
            sesion.close()
            
            self._CAMBIAR_ESTADO(OfertasGuardado(mensaje="Ofertas guardado exitosamente"))
            await self._CARGAR(None)
        
        except Exception as e:
            self._CAMBIAR_ESTADO(OfertasError(mensaje=f"Error guardando: {str(e)}"))
    
    async def _ELIMINAR(self, evento: EliminarOfertas):
        self._CAMBIAR_ESTADO(OfertasCargando())
        
        try:
            sesion = OBTENER_SESION()
            ofertas = sesion.query(MODELO_OFERTAS).filter_by(ID=evento.ofertas_id).first()
            
            if ofertas:
                sesion.delete(ofertas)
                sesion.commit()
                sesion.close()
                
                self._CAMBIAR_ESTADO(OfertasEliminado(mensaje="Ofertas eliminado"))
                await self._CARGAR(None)
            else:
                sesion.close()
                self._CAMBIAR_ESTADO(OfertasError(mensaje="Ofertas no encontrado"))
        
        except Exception as e:
            self._CAMBIAR_ESTADO(OfertasError(mensaje=f"Error eliminando: {str(e)}"))

OFERTAS_BLOC = OfertasBloc()
