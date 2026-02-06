
import asyncio
from typing import Callable, List, Optional
from dataclasses import dataclass

from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_INSUMOS

@dataclass
class InsumosEstado:
    pass

@dataclass
class InsumosInicial(InsumosEstado):
    pass

@dataclass
class InsumosCargando(InsumosEstado):
    pass

@dataclass
class InsumosesCargados(InsumosEstado):
    insumoss: List
    total: int

@dataclass
class InsumosError(InsumosEstado):
    mensaje: str

@dataclass
class InsumosGuardado(InsumosEstado):
    mensaje: str

@dataclass
class InsumosEliminado(InsumosEstado):
    mensaje: str

@dataclass
class InsumosEvento:
    pass

@dataclass
class CargarInsumoses(InsumosEvento):
    filtro: Optional[str] = None

@dataclass
class GuardarInsumos(InsumosEvento):
    datos: dict

@dataclass
class EliminarInsumos(InsumosEvento):
    insumos_id: int

class InsumosBloc:
    
    def __init__(self):
        self._estado: InsumosEstado = InsumosInicial()
        self._listeners: List[Callable] = []
    
    @property
    def ESTADO(self) -> InsumosEstado:
        return self._estado
    
    def AGREGAR_LISTENER(self, listener: Callable):
        if listener not in self._listeners:
            self._listeners.append(listener)
    
    def REMOVER_LISTENER(self, listener: Callable):
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def _CAMBIAR_ESTADO(self, nuevo_estado: InsumosEstado):
        self._estado = nuevo_estado
        for listener in self._listeners:
            try:
                listener(self._estado)
            except Exception as e:
                print(f"Error en listener: {e}")
    
    def AGREGAR_EVENTO(self, evento: InsumosEvento):
        if isinstance(evento, CargarInsumoses):
            asyncio.create_task(self._CARGAR(evento.filtro))
        elif isinstance(evento, GuardarInsumos):
            asyncio.create_task(self._GUARDAR(evento))
        elif isinstance(evento, EliminarInsumos):
            asyncio.create_task(self._ELIMINAR(evento))
    
    async def _CARGAR(self, filtro: Optional[str]):
        self._CAMBIAR_ESTADO(InsumosCargando())
        
        try:
            sesion = OBTENER_SESION()
            query = sesion.query(MODELO_INSUMOS)
            
            if filtro:
                query = query.filter(MODELO_INSUMOS.NOMBRE.contains(filtro))
            
            datos = query.all()
            total = len(datos)
            
            sesion.close()
            
            self._CAMBIAR_ESTADO(InsumosesCargados(insumoss=datos, total=total))
        
        except Exception as e:
            self._CAMBIAR_ESTADO(InsumosError(mensaje=f"Error cargando: {str(e)}"))
    
    async def _GUARDAR(self, evento: GuardarInsumos):
        self._CAMBIAR_ESTADO(InsumosCargando())
        
        try:
            sesion = OBTENER_SESION()
            
            
            sesion.commit()
            sesion.close()
            
            self._CAMBIAR_ESTADO(InsumosGuardado(mensaje="Insumos guardado exitosamente"))
            await self._CARGAR(None)
        
        except Exception as e:
            self._CAMBIAR_ESTADO(InsumosError(mensaje=f"Error guardando: {str(e)}"))
    
    async def _ELIMINAR(self, evento: EliminarInsumos):
        self._CAMBIAR_ESTADO(InsumosCargando())
        
        try:
            sesion = OBTENER_SESION()
            insumos = sesion.query(MODELO_INSUMOS).filter_by(ID=evento.insumos_id).first()
            
            if insumos:
                sesion.delete(insumos)
                sesion.commit()
                sesion.close()
                
                self._CAMBIAR_ESTADO(InsumosEliminado(mensaje="Insumos eliminado"))
                await self._CARGAR(None)
            else:
                sesion.close()
                self._CAMBIAR_ESTADO(InsumosError(mensaje="Insumos no encontrado"))
        
        except Exception as e:
            self._CAMBIAR_ESTADO(InsumosError(mensaje=f"Error eliminando: {str(e)}"))

INSUMOS_BLOC = InsumosBloc()
