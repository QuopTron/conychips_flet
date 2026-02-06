
import asyncio
from typing import Callable, List, Optional
from dataclasses import dataclass

from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_HORARIOS

@dataclass
class HorariosEstado:
    pass

@dataclass
class HorariosInicial(HorariosEstado):
    pass

@dataclass
class HorariosCargando(HorariosEstado):
    pass

@dataclass
class HorariosesCargados(HorariosEstado):
    horarioss: List
    total: int

@dataclass
class HorariosError(HorariosEstado):
    mensaje: str

@dataclass
class HorariosGuardado(HorariosEstado):
    mensaje: str

@dataclass
class HorariosEliminado(HorariosEstado):
    mensaje: str

@dataclass
class HorariosEvento:
    pass

@dataclass
class CargarHorarioses(HorariosEvento):
    filtro: Optional[str] = None

@dataclass
class GuardarHorarios(HorariosEvento):
    datos: dict

@dataclass
class EliminarHorarios(HorariosEvento):
    horarios_id: int

class HorariosBloc:
    
    def __init__(self):
        self._estado: HorariosEstado = HorariosInicial()
        self._listeners: List[Callable] = []
    
    @property
    def ESTADO(self) -> HorariosEstado:
        return self._estado
    
    def AGREGAR_LISTENER(self, listener: Callable):
        if listener not in self._listeners:
            self._listeners.append(listener)
    
    def REMOVER_LISTENER(self, listener: Callable):
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def _CAMBIAR_ESTADO(self, nuevo_estado: HorariosEstado):
        self._estado = nuevo_estado
        for listener in self._listeners:
            try:
                listener(self._estado)
            except Exception as e:
                print(f"Error en listener: {e}")
    
    def AGREGAR_EVENTO(self, evento: HorariosEvento):
        if isinstance(evento, CargarHorarioses):
            asyncio.create_task(self._CARGAR(evento.filtro))
        elif isinstance(evento, GuardarHorarios):
            asyncio.create_task(self._GUARDAR(evento))
        elif isinstance(evento, EliminarHorarios):
            asyncio.create_task(self._ELIMINAR(evento))
    
    async def _CARGAR(self, filtro: Optional[str]):
        self._CAMBIAR_ESTADO(HorariosCargando())
        
        try:
            sesion = OBTENER_SESION()
            query = sesion.query(MODELO_HORARIOS)
            
            if filtro:
                query = query.filter(MODELO_HORARIOS.NOMBRE.contains(filtro))
            
            datos = query.all()
            total = len(datos)
            
            sesion.close()
            
            self._CAMBIAR_ESTADO(HorariosesCargados(horarioss=datos, total=total))
        
        except Exception as e:
            self._CAMBIAR_ESTADO(HorariosError(mensaje=f"Error cargando: {str(e)}"))
    
    async def _GUARDAR(self, evento: GuardarHorarios):
        self._CAMBIAR_ESTADO(HorariosCargando())
        
        try:
            sesion = OBTENER_SESION()
            
            
            sesion.commit()
            sesion.close()
            
            self._CAMBIAR_ESTADO(HorariosGuardado(mensaje="Horarios guardado exitosamente"))
            await self._CARGAR(None)
        
        except Exception as e:
            self._CAMBIAR_ESTADO(HorariosError(mensaje=f"Error guardando: {str(e)}"))
    
    async def _ELIMINAR(self, evento: EliminarHorarios):
        self._CAMBIAR_ESTADO(HorariosCargando())
        
        try:
            sesion = OBTENER_SESION()
            horarios = sesion.query(MODELO_HORARIOS).filter_by(ID=evento.horarios_id).first()
            
            if horarios:
                sesion.delete(horarios)
                sesion.commit()
                sesion.close()
                
                self._CAMBIAR_ESTADO(HorariosEliminado(mensaje="Horarios eliminado"))
                await self._CARGAR(None)
            else:
                sesion.close()
                self._CAMBIAR_ESTADO(HorariosError(mensaje="Horarios no encontrado"))
        
        except Exception as e:
            self._CAMBIAR_ESTADO(HorariosError(mensaje=f"Error eliminando: {str(e)}"))

HORARIOS_BLOC = HorariosBloc()
