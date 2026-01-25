"""
BLoC para Gestión de Insumoses
Presentation Layer - Clean Architecture
"""

import asyncio
from typing import Callable, List, Optional
from dataclasses import dataclass

from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_INSUMOS


# ============================================================================
# Estados
# ============================================================================

@dataclass
class InsumosEstado:
    """Estado base"""
    pass


@dataclass
class InsumosInicial(InsumosEstado):
    """Estado inicial"""
    pass


@dataclass
class InsumosCargando(InsumosEstado):
    """Cargando datos"""
    pass


@dataclass
class InsumosesCargados(InsumosEstado):
    """Insumoses cargados"""
    insumoss: List
    total: int


@dataclass
class InsumosError(InsumosEstado):
    """Error en operación"""
    mensaje: str


@dataclass
class InsumosGuardado(InsumosEstado):
    """Insumos guardado exitosamente"""
    mensaje: str


@dataclass
class InsumosEliminado(InsumosEstado):
    """Insumos eliminado"""
    mensaje: str


# ============================================================================
# Eventos
# ============================================================================

@dataclass
class InsumosEvento:
    """Evento base"""
    pass


@dataclass
class CargarInsumoses(InsumosEvento):
    """Cargar lista de insumoss"""
    filtro: Optional[str] = None


@dataclass
class GuardarInsumos(InsumosEvento):
    """Guardar insumos"""
    datos: dict


@dataclass
class EliminarInsumos(InsumosEvento):
    """Eliminar insumos"""
    insumos_id: int


# ============================================================================
# BLoC
# ============================================================================

class InsumosBloc:
    """
    BLoC para gestión de insumoss
    """
    
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
        """Procesa eventos"""
        if isinstance(evento, CargarInsumoses):
            asyncio.create_task(self._CARGAR(evento.filtro))
        elif isinstance(evento, GuardarInsumos):
            asyncio.create_task(self._GUARDAR(evento))
        elif isinstance(evento, EliminarInsumos):
            asyncio.create_task(self._ELIMINAR(evento))
    
    async def _CARGAR(self, filtro: Optional[str]):
        """Carga insumoss de la BD"""
        self._CAMBIAR_ESTADO(InsumosCargando())
        
        try:
            sesion = OBTENER_SESION()
            query = sesion.query(MODELO_INSUMOS)
            
            if filtro:
                # TODO: Ajustar filtro según campos del modelo
                query = query.filter(MODELO_INSUMOS.NOMBRE.contains(filtro))
            
            datos = query.all()
            total = len(datos)
            
            sesion.close()
            
            self._CAMBIAR_ESTADO(InsumosesCargados(insumoss=datos, total=total))
        
        except Exception as e:
            self._CAMBIAR_ESTADO(InsumosError(mensaje=f"Error cargando: {str(e)}"))
    
    async def _GUARDAR(self, evento: GuardarInsumos):
        """Guarda insumos"""
        self._CAMBIAR_ESTADO(InsumosCargando())
        
        try:
            sesion = OBTENER_SESION()
            
            # TODO: Implementar lógica de guardado
            # Si es nuevo: crear
            # Si existe: actualizar
            
            sesion.commit()
            sesion.close()
            
            self._CAMBIAR_ESTADO(InsumosGuardado(mensaje="Insumos guardado exitosamente"))
            # Recargar lista
            await self._CARGAR(None)
        
        except Exception as e:
            self._CAMBIAR_ESTADO(InsumosError(mensaje=f"Error guardando: {str(e)}"))
    
    async def _ELIMINAR(self, evento: EliminarInsumos):
        """Elimina insumos"""
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


# Instancia global
INSUMOS_BLOC = InsumosBloc()
