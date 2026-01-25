"""
BLoC para Gestión de Ofertases
Presentation Layer - Clean Architecture
"""

import asyncio
from typing import Callable, List, Optional
from dataclasses import dataclass

from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_OFERTAS


# ============================================================================
# Estados
# ============================================================================

@dataclass
class OfertasEstado:
    """Estado base"""
    pass


@dataclass
class OfertasInicial(OfertasEstado):
    """Estado inicial"""
    pass


@dataclass
class OfertasCargando(OfertasEstado):
    """Cargando datos"""
    pass


@dataclass
class OfertasesCargados(OfertasEstado):
    """Ofertases cargados"""
    ofertass: List
    total: int


@dataclass
class OfertasError(OfertasEstado):
    """Error en operación"""
    mensaje: str


@dataclass
class OfertasGuardado(OfertasEstado):
    """Ofertas guardado exitosamente"""
    mensaje: str


@dataclass
class OfertasEliminado(OfertasEstado):
    """Ofertas eliminado"""
    mensaje: str


# ============================================================================
# Eventos
# ============================================================================

@dataclass
class OfertasEvento:
    """Evento base"""
    pass


@dataclass
class CargarOfertases(OfertasEvento):
    """Cargar lista de ofertass"""
    filtro: Optional[str] = None


@dataclass
class GuardarOfertas(OfertasEvento):
    """Guardar ofertas"""
    datos: dict


@dataclass
class EliminarOfertas(OfertasEvento):
    """Eliminar ofertas"""
    ofertas_id: int


# ============================================================================
# BLoC
# ============================================================================

class OfertasBloc:
    """
    BLoC para gestión de ofertass
    """
    
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
        """Procesa eventos"""
        if isinstance(evento, CargarOfertases):
            asyncio.create_task(self._CARGAR(evento.filtro))
        elif isinstance(evento, GuardarOfertas):
            asyncio.create_task(self._GUARDAR(evento))
        elif isinstance(evento, EliminarOfertas):
            asyncio.create_task(self._ELIMINAR(evento))
    
    async def _CARGAR(self, filtro: Optional[str]):
        """Carga ofertass de la BD"""
        self._CAMBIAR_ESTADO(OfertasCargando())
        
        try:
            sesion = OBTENER_SESION()
            query = sesion.query(MODELO_OFERTAS)
            
            if filtro:
                # TODO: Ajustar filtro según campos del modelo
                query = query.filter(MODELO_OFERTAS.NOMBRE.contains(filtro))
            
            datos = query.all()
            total = len(datos)
            
            sesion.close()
            
            self._CAMBIAR_ESTADO(OfertasesCargados(ofertass=datos, total=total))
        
        except Exception as e:
            self._CAMBIAR_ESTADO(OfertasError(mensaje=f"Error cargando: {str(e)}"))
    
    async def _GUARDAR(self, evento: GuardarOfertas):
        """Guarda ofertas"""
        self._CAMBIAR_ESTADO(OfertasCargando())
        
        try:
            sesion = OBTENER_SESION()
            
            # TODO: Implementar lógica de guardado
            # Si es nuevo: crear
            # Si existe: actualizar
            
            sesion.commit()
            sesion.close()
            
            self._CAMBIAR_ESTADO(OfertasGuardado(mensaje="Ofertas guardado exitosamente"))
            # Recargar lista
            await self._CARGAR(None)
        
        except Exception as e:
            self._CAMBIAR_ESTADO(OfertasError(mensaje=f"Error guardando: {str(e)}"))
    
    async def _ELIMINAR(self, evento: EliminarOfertas):
        """Elimina ofertas"""
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


# Instancia global
OFERTAS_BLOC = OfertasBloc()
