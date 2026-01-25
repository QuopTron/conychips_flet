"""
BLoC para Gestión de Horarioses
Presentation Layer - Clean Architecture
"""

import asyncio
from typing import Callable, List, Optional
from dataclasses import dataclass

from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_HORARIOS


# ============================================================================
# Estados
# ============================================================================

@dataclass
class HorariosEstado:
    """Estado base"""
    pass


@dataclass
class HorariosInicial(HorariosEstado):
    """Estado inicial"""
    pass


@dataclass
class HorariosCargando(HorariosEstado):
    """Cargando datos"""
    pass


@dataclass
class HorariosesCargados(HorariosEstado):
    """Horarioses cargados"""
    horarioss: List
    total: int


@dataclass
class HorariosError(HorariosEstado):
    """Error en operación"""
    mensaje: str


@dataclass
class HorariosGuardado(HorariosEstado):
    """Horarios guardado exitosamente"""
    mensaje: str


@dataclass
class HorariosEliminado(HorariosEstado):
    """Horarios eliminado"""
    mensaje: str


# ============================================================================
# Eventos
# ============================================================================

@dataclass
class HorariosEvento:
    """Evento base"""
    pass


@dataclass
class CargarHorarioses(HorariosEvento):
    """Cargar lista de horarioss"""
    filtro: Optional[str] = None


@dataclass
class GuardarHorarios(HorariosEvento):
    """Guardar horarios"""
    datos: dict


@dataclass
class EliminarHorarios(HorariosEvento):
    """Eliminar horarios"""
    horarios_id: int


# ============================================================================
# BLoC
# ============================================================================

class HorariosBloc:
    """
    BLoC para gestión de horarioss
    """
    
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
        """Procesa eventos"""
        if isinstance(evento, CargarHorarioses):
            asyncio.create_task(self._CARGAR(evento.filtro))
        elif isinstance(evento, GuardarHorarios):
            asyncio.create_task(self._GUARDAR(evento))
        elif isinstance(evento, EliminarHorarios):
            asyncio.create_task(self._ELIMINAR(evento))
    
    async def _CARGAR(self, filtro: Optional[str]):
        """Carga horarioss de la BD"""
        self._CAMBIAR_ESTADO(HorariosCargando())
        
        try:
            sesion = OBTENER_SESION()
            query = sesion.query(MODELO_HORARIOS)
            
            if filtro:
                # TODO: Ajustar filtro según campos del modelo
                query = query.filter(MODELO_HORARIOS.NOMBRE.contains(filtro))
            
            datos = query.all()
            total = len(datos)
            
            sesion.close()
            
            self._CAMBIAR_ESTADO(HorariosesCargados(horarioss=datos, total=total))
        
        except Exception as e:
            self._CAMBIAR_ESTADO(HorariosError(mensaje=f"Error cargando: {str(e)}"))
    
    async def _GUARDAR(self, evento: GuardarHorarios):
        """Guarda horarios"""
        self._CAMBIAR_ESTADO(HorariosCargando())
        
        try:
            sesion = OBTENER_SESION()
            
            # TODO: Implementar lógica de guardado
            # Si es nuevo: crear
            # Si existe: actualizar
            
            sesion.commit()
            sesion.close()
            
            self._CAMBIAR_ESTADO(HorariosGuardado(mensaje="Horarios guardado exitosamente"))
            # Recargar lista
            await self._CARGAR(None)
        
        except Exception as e:
            self._CAMBIAR_ESTADO(HorariosError(mensaje=f"Error guardando: {str(e)}"))
    
    async def _ELIMINAR(self, evento: EliminarHorarios):
        """Elimina horarios"""
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


# Instancia global
HORARIOS_BLOC = HorariosBloc()
