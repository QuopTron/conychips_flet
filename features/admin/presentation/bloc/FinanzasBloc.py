"""
BLoC para Gestión Financiera
Presentation Layer - Clean Architecture
"""

import asyncio
from typing import Callable, List, Optional
from dataclasses import dataclass
from datetime import datetime, date

from core.base_datos.ConfiguracionBD import OBTENER_SESION


@dataclass
class FinanzasEstado:
    pass


@dataclass
class FinanzasInicial(FinanzasEstado):
    pass


@dataclass
class FinanzasCargando(FinanzasEstado):
    pass


@dataclass
class FinanzasCargadas(FinanzasEstado):
    total_ingresos: float
    total_egresos: float
    balance: float
    transacciones: List


@dataclass
class FinanzasError(FinanzasEstado):
    mensaje: str


@dataclass
class FinanzasEvento:
    pass


@dataclass
class CargarFinanzas(FinanzasEvento):
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None


@dataclass
class RegistrarIngreso(FinanzasEvento):
    monto: float
    descripcion: str


@dataclass
class RegistrarEgreso(FinanzasEvento):
    monto: float
    descripcion: str


class FinanzasBloc:
    def __init__(self):
        self._estado: FinanzasEstado = FinanzasInicial()
        self._listeners: List[Callable] = []
    
    @property
    def ESTADO(self) -> FinanzasEstado:
        return self._estado
    
    def AGREGAR_LISTENER(self, listener: Callable):
        if listener not in self._listeners:
            self._listeners.append(listener)
    
    def REMOVER_LISTENER(self, listener: Callable):
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def _CAMBIAR_ESTADO(self, nuevo_estado: FinanzasEstado):
        self._estado = nuevo_estado
        for listener in self._listeners:
            try:
                listener(self._estado)
            except:
                pass
    
    def AGREGAR_EVENTO(self, evento: FinanzasEvento):
        if isinstance(evento, CargarFinanzas):
            asyncio.create_task(self._CARGAR(evento))
        elif isinstance(evento, RegistrarIngreso):
            asyncio.create_task(self._REGISTRAR_INGRESO(evento))
        elif isinstance(evento, RegistrarEgreso):
            asyncio.create_task(self._REGISTRAR_EGRESO(evento))
    
    async def _CARGAR(self, evento):
        self._CAMBIAR_ESTADO(FinanzasCargando())
        try:
            # Simulación de carga de datos financieros
            await asyncio.sleep(0.5)
            
            ingresos = 15000.0
            egresos = 8500.0
            balance = ingresos - egresos
            transacciones = []
            
            self._CAMBIAR_ESTADO(
                FinanzasCargadas(
                    total_ingresos=ingresos,
                    total_egresos=egresos,
                    balance=balance,
                    transacciones=transacciones
                )
            )
        except Exception as e:
            self._CAMBIAR_ESTADO(FinanzasError(mensaje=str(e)))
    
    async def _REGISTRAR_INGRESO(self, evento):
        self._CAMBIAR_ESTADO(FinanzasCargando())
        try:
            await asyncio.sleep(0.3)
            await self._CARGAR(CargarFinanzas())
        except Exception as e:
            self._CAMBIAR_ESTADO(FinanzasError(mensaje=str(e)))
    
    async def _REGISTRAR_EGRESO(self, evento):
        self._CAMBIAR_ESTADO(FinanzasCargando())
        try:
            await asyncio.sleep(0.3)
            await self._CARGAR(CargarFinanzas())
        except Exception as e:
            self._CAMBIAR_ESTADO(FinanzasError(mensaje=str(e)))


FINANZAS_BLOC = FinanzasBloc()
