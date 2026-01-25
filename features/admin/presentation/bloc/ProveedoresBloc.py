"""
BLoC para Gestión de Proveedoreses
Presentation Layer - Clean Architecture
"""

import asyncio
from typing import Callable, List, Optional
from dataclasses import dataclass

from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_PROVEEDORES


# ============================================================================
# Estados
# ============================================================================

@dataclass
class ProveedoresEstado:
    """Estado base"""
    pass


@dataclass
class ProveedoresInicial(ProveedoresEstado):
    """Estado inicial"""
    pass


@dataclass
class ProveedoresCargando(ProveedoresEstado):
    """Cargando datos"""
    pass


@dataclass
class ProveedoresesCargados(ProveedoresEstado):
    """Proveedoreses cargados"""
    proveedoress: List
    total: int


@dataclass
class ProveedoresError(ProveedoresEstado):
    """Error en operación"""
    mensaje: str


@dataclass
class ProveedoresGuardado(ProveedoresEstado):
    """Proveedores guardado exitosamente"""
    mensaje: str


@dataclass
class ProveedoresEliminado(ProveedoresEstado):
    """Proveedores eliminado"""
    mensaje: str


# ============================================================================
# Eventos
# ============================================================================

@dataclass
class ProveedoresEvento:
    """Evento base"""
    pass


@dataclass
class CargarProveedoreses(ProveedoresEvento):
    """Cargar lista de proveedoress"""
    filtro: Optional[str] = None


@dataclass
class GuardarProveedores(ProveedoresEvento):
    """Guardar proveedores"""
    datos: dict


@dataclass
class EliminarProveedores(ProveedoresEvento):
    """Eliminar proveedores"""
    proveedores_id: int


# ============================================================================
# BLoC
# ============================================================================

class ProveedoresBloc:
    """
    BLoC para gestión de proveedoress
    """
    
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
        """Procesa eventos"""
        if isinstance(evento, CargarProveedoreses):
            asyncio.create_task(self._CARGAR(evento.filtro))
        elif isinstance(evento, GuardarProveedores):
            asyncio.create_task(self._GUARDAR(evento))
        elif isinstance(evento, EliminarProveedores):
            asyncio.create_task(self._ELIMINAR(evento))
    
    async def _CARGAR(self, filtro: Optional[str]):
        """Carga proveedoress de la BD"""
        self._CAMBIAR_ESTADO(ProveedoresCargando())
        
        try:
            sesion = OBTENER_SESION()
            query = sesion.query(MODELO_PROVEEDORES)
            
            if filtro:
                # TODO: Ajustar filtro según campos del modelo
                query = query.filter(MODELO_PROVEEDORES.NOMBRE.contains(filtro))
            
            datos = query.all()
            total = len(datos)
            
            sesion.close()
            
            self._CAMBIAR_ESTADO(ProveedoresesCargados(proveedoress=datos, total=total))
        
        except Exception as e:
            self._CAMBIAR_ESTADO(ProveedoresError(mensaje=f"Error cargando: {str(e)}"))
    
    async def _GUARDAR(self, evento: GuardarProveedores):
        """Guarda proveedores"""
        self._CAMBIAR_ESTADO(ProveedoresCargando())
        
        try:
            sesion = OBTENER_SESION()
            
            # TODO: Implementar lógica de guardado
            # Si es nuevo: crear
            # Si existe: actualizar
            
            sesion.commit()
            sesion.close()
            
            self._CAMBIAR_ESTADO(ProveedoresGuardado(mensaje="Proveedores guardado exitosamente"))
            # Recargar lista
            await self._CARGAR(None)
        
        except Exception as e:
            self._CAMBIAR_ESTADO(ProveedoresError(mensaje=f"Error guardando: {str(e)}"))
    
    async def _ELIMINAR(self, evento: EliminarProveedores):
        """Elimina proveedores"""
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


# Instancia global
PROVEEDORES_BLOC = ProveedoresBloc()
