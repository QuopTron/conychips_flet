"""
BLoC para Gestión de Extrases
Presentation Layer - Clean Architecture
"""

import asyncio
from typing import Callable, List, Optional
from dataclasses import dataclass

from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_EXTRAS


# ============================================================================
# Estados
# ============================================================================

@dataclass
class ExtrasEstado:
    """Estado base"""
    pass


@dataclass
class ExtrasInicial(ExtrasEstado):
    """Estado inicial"""
    pass


@dataclass
class ExtrasCargando(ExtrasEstado):
    """Cargando datos"""
    pass


@dataclass
class ExtrasesCargados(ExtrasEstado):
    """Extrases cargados"""
    extrass: List
    total: int


@dataclass
class ExtrasError(ExtrasEstado):
    """Error en operación"""
    mensaje: str


@dataclass
class ExtrasGuardado(ExtrasEstado):
    """Extras guardado exitosamente"""
    mensaje: str


@dataclass
class ExtrasEliminado(ExtrasEstado):
    """Extras eliminado"""
    mensaje: str


# ============================================================================
# Eventos
# ============================================================================

@dataclass
class ExtrasEvento:
    """Evento base"""
    pass


@dataclass
class CargarExtrases(ExtrasEvento):
    """Cargar lista de extrass"""
    filtro: Optional[str] = None


@dataclass
class GuardarExtras(ExtrasEvento):
    """Guardar extras"""
    datos: dict


@dataclass
class EliminarExtras(ExtrasEvento):
    """Eliminar extras"""
    extras_id: int


# ============================================================================
# BLoC
# ============================================================================

class ExtrasBloc:
    """
    BLoC para gestión de extrass
    """
    
    def __init__(self):
        self._estado: ExtrasEstado = ExtrasInicial()
        self._listeners: List[Callable] = []
    
    @property
    def ESTADO(self) -> ExtrasEstado:
        return self._estado
    
    def AGREGAR_LISTENER(self, listener: Callable):
        if listener not in self._listeners:
            self._listeners.append(listener)
    
    def REMOVER_LISTENER(self, listener: Callable):
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def _CAMBIAR_ESTADO(self, nuevo_estado: ExtrasEstado):
        self._estado = nuevo_estado
        for listener in self._listeners:
            try:
                listener(self._estado)
            except Exception as e:
                print(f"Error en listener: {e}")
    
    def AGREGAR_EVENTO(self, evento: ExtrasEvento):
        """Procesa eventos"""
        if isinstance(evento, CargarExtrases):
            asyncio.create_task(self._CARGAR(evento.filtro))
        elif isinstance(evento, GuardarExtras):
            asyncio.create_task(self._GUARDAR(evento))
        elif isinstance(evento, EliminarExtras):
            asyncio.create_task(self._ELIMINAR(evento))
    
    async def _CARGAR(self, filtro: Optional[str]):
        """Carga extrass de la BD"""
        self._CAMBIAR_ESTADO(ExtrasCargando())
        
        try:
            sesion = OBTENER_SESION()
            query = sesion.query(MODELO_EXTRAS)
            
            if filtro:
                # TODO: Ajustar filtro según campos del modelo
                query = query.filter(MODELO_EXTRAS.NOMBRE.contains(filtro))
            
            datos = query.all()
            total = len(datos)
            
            sesion.close()
            
            self._CAMBIAR_ESTADO(ExtrasesCargados(extrass=datos, total=total))
        
        except Exception as e:
            self._CAMBIAR_ESTADO(ExtrasError(mensaje=f"Error cargando: {str(e)}"))
    
    async def _GUARDAR(self, evento: GuardarExtras):
        """Guarda extras"""
        self._CAMBIAR_ESTADO(ExtrasCargando())
        
        try:
            sesion = OBTENER_SESION()
            
            # TODO: Implementar lógica de guardado
            # Si es nuevo: crear
            # Si existe: actualizar
            
            sesion.commit()
            sesion.close()
            
            self._CAMBIAR_ESTADO(ExtrasGuardado(mensaje="Extras guardado exitosamente"))
            # Recargar lista
            await self._CARGAR(None)
        
        except Exception as e:
            self._CAMBIAR_ESTADO(ExtrasError(mensaje=f"Error guardando: {str(e)}"))
    
    async def _ELIMINAR(self, evento: EliminarExtras):
        """Elimina extras"""
        self._CAMBIAR_ESTADO(ExtrasCargando())
        
        try:
            sesion = OBTENER_SESION()
            extras = sesion.query(MODELO_EXTRAS).filter_by(ID=evento.extras_id).first()
            
            if extras:
                sesion.delete(extras)
                sesion.commit()
                sesion.close()
                
                self._CAMBIAR_ESTADO(ExtrasEliminado(mensaje="Extras eliminado"))
                await self._CARGAR(None)
            else:
                sesion.close()
                self._CAMBIAR_ESTADO(ExtrasError(mensaje="Extras no encontrado"))
        
        except Exception as e:
            self._CAMBIAR_ESTADO(ExtrasError(mensaje=f"Error eliminando: {str(e)}"))


# Instancia global
EXTRAS_BLOC = ExtrasBloc()
