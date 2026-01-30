
import asyncio
from typing import Callable, List, Optional
from dataclasses import dataclass

from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_RESENAS

@dataclass
class ResenasEstado:
    pass

@dataclass
class ResenasInicial(ResenasEstado):
    pass

@dataclass
class ResenasCargando(ResenasEstado):
    pass

@dataclass
class ResenasesCargados(ResenasEstado):
    resenass: List
    total: int

@dataclass
class ResenasError(ResenasEstado):
    mensaje: str

@dataclass
class ResenasGuardado(ResenasEstado):
    mensaje: str

@dataclass
class ResenasEliminado(ResenasEstado):
    mensaje: str

@dataclass
class ResenasEvento:
    pass

@dataclass
class CargarResenases(ResenasEvento):
    filtro: Optional[str] = None

@dataclass
class GuardarResenas(ResenasEvento):
    datos: dict

@dataclass
class EliminarResenas(ResenasEvento):
    resenas_id: int

class ResenasBloc:
    
    def __init__(self):
        self._estado: ResenasEstado = ResenasInicial()
        self._listeners: List[Callable] = []
    
    @property
    def ESTADO(self) -> ResenasEstado:
        return self._estado
    
    def AGREGAR_LISTENER(self, listener: Callable):
        if listener not in self._listeners:
            self._listeners.append(listener)
    
    def REMOVER_LISTENER(self, listener: Callable):
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def _CAMBIAR_ESTADO(self, nuevo_estado: ResenasEstado):
        self._estado = nuevo_estado
        for listener in self._listeners:
            try:
                listener(self._estado)
            except Exception as e:
                print(f"Error en listener: {e}")
    
    def AGREGAR_EVENTO(self, evento: ResenasEvento):
        if isinstance(evento, CargarResenases):
            asyncio.create_task(self._CARGAR(evento.filtro))
        elif isinstance(evento, GuardarResenas):
            asyncio.create_task(self._GUARDAR(evento))
        elif isinstance(evento, EliminarResenas):
            asyncio.create_task(self._ELIMINAR(evento))
    
    async def _CARGAR(self, filtro: Optional[str]):
        self._CAMBIAR_ESTADO(ResenasCargando())
        
        try:
            sesion = OBTENER_SESION()
            query = sesion.query(MODELO_RESENAS)
            
            if filtro:
                query = query.filter(MODELO_RESENAS.NOMBRE.contains(filtro))
            
            datos = query.all()
            total = len(datos)
            
            sesion.close()
            
            self._CAMBIAR_ESTADO(ResenasesCargados(resenass=datos, total=total))
        
        except Exception as e:
            self._CAMBIAR_ESTADO(ResenasError(mensaje=f"Error cargando: {str(e)}"))
    
    async def _GUARDAR(self, evento: GuardarResenas):
        self._CAMBIAR_ESTADO(ResenasCargando())
        
        try:
            sesion = OBTENER_SESION()
            
            
            sesion.commit()
            sesion.close()
            
            self._CAMBIAR_ESTADO(ResenasGuardado(mensaje="Resenas guardado exitosamente"))
            await self._CARGAR(None)
        
        except Exception as e:
            self._CAMBIAR_ESTADO(ResenasError(mensaje=f"Error guardando: {str(e)}"))
    
    async def _ELIMINAR(self, evento: EliminarResenas):
        self._CAMBIAR_ESTADO(ResenasCargando())
        
        try:
            sesion = OBTENER_SESION()
            resenas = sesion.query(MODELO_RESENAS).filter_by(ID=evento.resenas_id).first()
            
            if resenas:
                sesion.delete(resenas)
                sesion.commit()
                sesion.close()
                
                self._CAMBIAR_ESTADO(ResenasEliminado(mensaje="Resenas eliminado"))
                await self._CARGAR(None)
            else:
                sesion.close()
                self._CAMBIAR_ESTADO(ResenasError(mensaje="Resenas no encontrado"))
        
        except Exception as e:
            self._CAMBIAR_ESTADO(ResenasError(mensaje=f"Error eliminando: {str(e)}"))

RESENAS_BLOC = ResenasBloc()
