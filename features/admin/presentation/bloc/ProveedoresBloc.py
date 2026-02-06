
import asyncio
from typing import Callable, List, Optional
from dataclasses import dataclass

from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_PROVEEDORES

@dataclass
class ProveedoresEstado:
    pass

@dataclass
class ProveedoresInicial(ProveedoresEstado):
    pass

@dataclass
class ProveedoresCargando(ProveedoresEstado):
    pass

@dataclass
class ProveedoresesCargados(ProveedoresEstado):
    proveedoress: List
    total: int

@dataclass
class ProveedoresError(ProveedoresEstado):
    mensaje: str

@dataclass
class ProveedoresGuardado(ProveedoresEstado):
    mensaje: str

@dataclass
class ProveedoresEliminado(ProveedoresEstado):
    mensaje: str

@dataclass
class ProveedoresEvento:
    pass

@dataclass
class CargarProveedoreses(ProveedoresEvento):
    filtro: Optional[str] = None

@dataclass
class GuardarProveedores(ProveedoresEvento):
    datos: dict

@dataclass
class EliminarProveedores(ProveedoresEvento):
    proveedores_id: int

class ProveedoresBloc:
    
    def __init__(self):
        self._estado: ProveedoresEstado = ProveedoresInicial()
        self._listeners: List[Callable] = []
    
    @property
    def ESTADO(self) -> ProveedoresEstado:
        return self._estado
    
    def AGREGAR_LISTENER(self, listener: Callable):
        if listener not in self._listeners:
            self._listeners.append(listener)
    
    def REMOVER_LISTENER(self, listener: Callable):
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def _CAMBIAR_ESTADO(self, nuevo_estado: ProveedoresEstado):
        self._estado = nuevo_estado
        for listener in self._listeners:
            try:
                listener(self._estado)
            except Exception as e:
                print(f"Error en listener: {e}")
    
    def AGREGAR_EVENTO(self, evento: ProveedoresEvento):
        if isinstance(evento, CargarProveedoreses):
            asyncio.create_task(self._CARGAR(evento.filtro))
        elif isinstance(evento, GuardarProveedores):
            asyncio.create_task(self._GUARDAR(evento))
        elif isinstance(evento, EliminarProveedores):
            asyncio.create_task(self._ELIMINAR(evento))
    
    async def _CARGAR(self, filtro: Optional[str]):
        self._CAMBIAR_ESTADO(ProveedoresCargando())
        
        try:
            sesion = OBTENER_SESION()
            query = sesion.query(MODELO_PROVEEDORES)
            
            if filtro:
                query = query.filter(MODELO_PROVEEDORES.NOMBRE.contains(filtro))
            
            datos = query.all()
            total = len(datos)
            
            sesion.close()
            
            self._CAMBIAR_ESTADO(ProveedoresesCargados(proveedoress=datos, total=total))
        
        except Exception as e:
            self._CAMBIAR_ESTADO(ProveedoresError(mensaje=f"Error cargando: {str(e)}"))
    
    async def _GUARDAR(self, evento: GuardarProveedores):
        self._CAMBIAR_ESTADO(ProveedoresCargando())
        
        try:
            sesion = OBTENER_SESION()
            
            
            sesion.commit()
            sesion.close()
            
            self._CAMBIAR_ESTADO(ProveedoresGuardado(mensaje="Proveedores guardado exitosamente"))
            await self._CARGAR(None)
        
        except Exception as e:
            self._CAMBIAR_ESTADO(ProveedoresError(mensaje=f"Error guardando: {str(e)}"))
    
    async def _ELIMINAR(self, evento: EliminarProveedores):
        self._CAMBIAR_ESTADO(ProveedoresCargando())
        
        try:
            sesion = OBTENER_SESION()
            proveedores = sesion.query(MODELO_PROVEEDORES).filter_by(ID=evento.proveedores_id).first()
            
            if proveedores:
                sesion.delete(proveedores)
                sesion.commit()
                sesion.close()
                
                self._CAMBIAR_ESTADO(ProveedoresEliminado(mensaje="Proveedores eliminado"))
                await self._CARGAR(None)
            else:
                sesion.close()
                self._CAMBIAR_ESTADO(ProveedoresError(mensaje="Proveedores no encontrado"))
        
        except Exception as e:
            self._CAMBIAR_ESTADO(ProveedoresError(mensaje=f"Error eliminando: {str(e)}"))

PROVEEDORES_BLOC = ProveedoresBloc()
