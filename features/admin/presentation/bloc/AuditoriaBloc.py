
import asyncio
from typing import Callable, List, Optional
from dataclasses import dataclass

from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_AUDITORIA

@dataclass
class AuditoriaEstado:
    pass

@dataclass
class AuditoriaInicial(AuditoriaEstado):
    pass

@dataclass
class AuditoriaCargando(AuditoriaEstado):
    pass

@dataclass
class AuditoriasCargados(AuditoriaEstado):
    auditorias: List
    total: int

@dataclass
class AuditoriaError(AuditoriaEstado):
    mensaje: str

@dataclass
class AuditoriaGuardado(AuditoriaEstado):
    mensaje: str

@dataclass
class AuditoriaEliminado(AuditoriaEstado):
    mensaje: str

@dataclass
class AuditoriaEvento:
    pass

@dataclass
class CargarAuditorias(AuditoriaEvento):
    filtro: Optional[str] = None

@dataclass
class GuardarAuditoria(AuditoriaEvento):
    datos: dict

@dataclass
class EliminarAuditoria(AuditoriaEvento):
    auditoria_id: int

class AuditoriaBloc:
    
    def __init__(self):
        self._estado: AuditoriaEstado = AuditoriaInicial()
        self._listeners: List[Callable] = []
    
    @property
    def ESTADO(self) -> AuditoriaEstado:
        return self._estado
    
    def AGREGAR_LISTENER(self, listener: Callable):
        if listener not in self._listeners:
            self._listeners.append(listener)
    
    def REMOVER_LISTENER(self, listener: Callable):
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def _CAMBIAR_ESTADO(self, nuevo_estado: AuditoriaEstado):
        self._estado = nuevo_estado
        for listener in self._listeners:
            try:
                listener(self._estado)
            except Exception as e:
                print(f"Error en listener: {e}")
    
    def AGREGAR_EVENTO(self, evento: AuditoriaEvento):
        if isinstance(evento, CargarAuditorias):
            asyncio.create_task(self._CARGAR(evento.filtro))
        elif isinstance(evento, GuardarAuditoria):
            asyncio.create_task(self._GUARDAR(evento))
        elif isinstance(evento, EliminarAuditoria):
            asyncio.create_task(self._ELIMINAR(evento))
    
    async def _CARGAR(self, filtro: Optional[str]):
        self._CAMBIAR_ESTADO(AuditoriaCargando())
        
        try:
            sesion = OBTENER_SESION()
            query = sesion.query(MODELO_AUDITORIA)
            
            if filtro:
                query = query.filter(MODELO_AUDITORIA.NOMBRE.contains(filtro))
            
            datos = query.all()
            total = len(datos)
            
            sesion.close()
            
            self._CAMBIAR_ESTADO(AuditoriasCargados(auditorias=datos, total=total))
        
        except Exception as e:
            self._CAMBIAR_ESTADO(AuditoriaError(mensaje=f"Error cargando: {str(e)}"))
    
    async def _GUARDAR(self, evento: GuardarAuditoria):
        self._CAMBIAR_ESTADO(AuditoriaCargando())
        
        try:
            sesion = OBTENER_SESION()
            
            
            sesion.commit()
            sesion.close()
            
            self._CAMBIAR_ESTADO(AuditoriaGuardado(mensaje="Auditoria guardado exitosamente"))
            await self._CARGAR(None)
        
        except Exception as e:
            self._CAMBIAR_ESTADO(AuditoriaError(mensaje=f"Error guardando: {str(e)}"))
    
    async def _ELIMINAR(self, evento: EliminarAuditoria):
        self._CAMBIAR_ESTADO(AuditoriaCargando())
        
        try:
            sesion = OBTENER_SESION()
            auditoria = sesion.query(MODELO_AUDITORIA).filter_by(ID=evento.auditoria_id).first()
            
            if auditoria:
                sesion.delete(auditoria)
                sesion.commit()
                sesion.close()
                
                self._CAMBIAR_ESTADO(AuditoriaEliminado(mensaje="Auditoria eliminado"))
                await self._CARGAR(None)
            else:
                sesion.close()
                self._CAMBIAR_ESTADO(AuditoriaError(mensaje="Auditoria no encontrado"))
        
        except Exception as e:
            self._CAMBIAR_ESTADO(AuditoriaError(mensaje=f"Error eliminando: {str(e)}"))

AUDITORIA_BLOC = AuditoriaBloc()
