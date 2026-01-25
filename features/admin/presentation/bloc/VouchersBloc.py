"""
BLoC para Gestión de Voucherses
Presentation Layer - Clean Architecture
"""

import asyncio
from typing import Callable, List, Optional
from dataclasses import dataclass

from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_VOUCHERS


# ============================================================================
# Estados
# ============================================================================

@dataclass
class VouchersEstado:
    """Estado base"""
    pass


@dataclass
class VouchersInicial(VouchersEstado):
    """Estado inicial"""
    pass


@dataclass
class VouchersCargando(VouchersEstado):
    """Cargando datos"""
    pass


@dataclass
class VouchersesCargados(VouchersEstado):
    """Voucherses cargados"""
    voucherss: List
    total: int


@dataclass
class VouchersError(VouchersEstado):
    """Error en operación"""
    mensaje: str


@dataclass
class VouchersGuardado(VouchersEstado):
    """Vouchers guardado exitosamente"""
    mensaje: str


@dataclass
class VouchersEliminado(VouchersEstado):
    """Vouchers eliminado"""
    mensaje: str


# ============================================================================
# Eventos
# ============================================================================

@dataclass
class VouchersEvento:
    """Evento base"""
    pass


@dataclass
class CargarVoucherses(VouchersEvento):
    """Cargar lista de voucherss"""
    filtro: Optional[str] = None


@dataclass
class GuardarVouchers(VouchersEvento):
    """Guardar vouchers"""
    datos: dict


@dataclass
class EliminarVouchers(VouchersEvento):
    """Eliminar vouchers"""
    vouchers_id: int


# ============================================================================
# BLoC
# ============================================================================

class VouchersBloc:
    """
    BLoC para gestión de voucherss
    """
    
    def __init__(self):
        self._estado: VouchersEstado = VouchersInicial()
        self._listeners: List[Callable] = []
    
    @property
    def ESTADO(self) -> VouchersEstado:
        return self._estado
    
    def AGREGAR_LISTENER(self, listener: Callable):
        if listener not in self._listeners:
            self._listeners.append(listener)
    
    def REMOVER_LISTENER(self, listener: Callable):
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def _CAMBIAR_ESTADO(self, nuevo_estado: VouchersEstado):
        self._estado = nuevo_estado
        for listener in self._listeners:
            try:
                listener(self._estado)
            except Exception as e:
                print(f"Error en listener: {e}")
    
    def AGREGAR_EVENTO(self, evento: VouchersEvento):
        """Procesa eventos"""
        if isinstance(evento, CargarVoucherses):
            asyncio.create_task(self._CARGAR(evento.filtro))
        elif isinstance(evento, GuardarVouchers):
            asyncio.create_task(self._GUARDAR(evento))
        elif isinstance(evento, EliminarVouchers):
            asyncio.create_task(self._ELIMINAR(evento))
    
    async def _CARGAR(self, filtro: Optional[str]):
        """Carga voucherss de la BD"""
        self._CAMBIAR_ESTADO(VouchersCargando())
        
        try:
            sesion = OBTENER_SESION()
            query = sesion.query(MODELO_VOUCHERS)
            
            if filtro:
                # TODO: Ajustar filtro según campos del modelo
                query = query.filter(MODELO_VOUCHERS.NOMBRE.contains(filtro))
            
            datos = query.all()
            total = len(datos)
            
            sesion.close()
            
            self._CAMBIAR_ESTADO(VouchersesCargados(voucherss=datos, total=total))
        
        except Exception as e:
            self._CAMBIAR_ESTADO(VouchersError(mensaje=f"Error cargando: {str(e)}"))
    
    async def _GUARDAR(self, evento: GuardarVouchers):
        """Guarda vouchers"""
        self._CAMBIAR_ESTADO(VouchersCargando())
        
        try:
            sesion = OBTENER_SESION()
            
            # TODO: Implementar lógica de guardado
            # Si es nuevo: crear
            # Si existe: actualizar
            
            sesion.commit()
            sesion.close()
            
            self._CAMBIAR_ESTADO(VouchersGuardado(mensaje="Vouchers guardado exitosamente"))
            # Recargar lista
            await self._CARGAR(None)
        
        except Exception as e:
            self._CAMBIAR_ESTADO(VouchersError(mensaje=f"Error guardando: {str(e)}"))
    
    async def _ELIMINAR(self, evento: EliminarVouchers):
        """Elimina vouchers"""
        self._CAMBIAR_ESTADO(VouchersCargando())
        
        try:
            sesion = OBTENER_SESION()
            vouchers = sesion.query(MODELO_VOUCHERS).filter_by(ID=evento.vouchers_id).first()
            
            if vouchers:
                sesion.delete(vouchers)
                sesion.commit()
                sesion.close()
                
                self._CAMBIAR_ESTADO(VouchersEliminado(mensaje="Vouchers eliminado"))
                await self._CARGAR(None)
            else:
                sesion.close()
                self._CAMBIAR_ESTADO(VouchersError(mensaje="Vouchers no encontrado"))
        
        except Exception as e:
            self._CAMBIAR_ESTADO(VouchersError(mensaje=f"Error eliminando: {str(e)}"))


# Instancia global
VOUCHERS_BLOC = VouchersBloc()
