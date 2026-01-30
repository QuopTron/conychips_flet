
import sys
import os
from pathlib import Path

import asyncio
from typing import Callable, List, Optional
from dataclasses import dataclass

from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_{modelo}

@dataclass
class {entidad}Estado:
    pass

@dataclass
class {entidad}Inicial({entidad}Estado):
    pass

@dataclass
class {entidad}Cargando({entidad}Estado):
    pass

@dataclass
class {entidad_plural}Cargados({entidad}Estado):
    {entidad_lower}s: List
    total: int

@dataclass
class {entidad}Error({entidad}Estado):
    mensaje: str

@dataclass
class {entidad}Guardado({entidad}Estado):
    mensaje: str

@dataclass
class {entidad}Eliminado({entidad}Estado):
    mensaje: str

@dataclass
class {entidad}Evento:
    pass

@dataclass
class Cargar{entidad_plural}({entidad}Evento):
    filtro: Optional[str] = None

@dataclass
class Guardar{entidad}({entidad}Evento):
    datos: dict

@dataclass
class Eliminar{entidad}({entidad}Evento):
    {entidad_lower}_id: int

class {entidad}Bloc:
    
    def __init__(self):
        self._estado: {entidad}Estado = {entidad}Inicial()
        self._listeners: List[Callable] = []
    
    @property
    def ESTADO(self) -> {entidad}Estado:
        return self._estado
    
    def AGREGAR_LISTENER(self, listener: Callable):
        if listener not in self._listeners:
            self._listeners.append(listener)
    
    def REMOVER_LISTENER(self, listener: Callable):
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def _CAMBIAR_ESTADO(self, nuevo_estado: {entidad}Estado):
        self._estado = nuevo_estado
        for listener in self._listeners:
            try:
                listener(self._estado)
            except Exception as e:
                print(f"Error en listener: {{e}}")
    
    def AGREGAR_EVENTO(self, evento: {entidad}Evento):
        if isinstance(evento, Cargar{entidad_plural}):
            asyncio.create_task(self._CARGAR(evento.filtro))
        elif isinstance(evento, Guardar{entidad}):
            asyncio.create_task(self._GUARDAR(evento))
        elif isinstance(evento, Eliminar{entidad}):
            asyncio.create_task(self._ELIMINAR(evento))
    
    async def _CARGAR(self, filtro: Optional[str]):
        self._CAMBIAR_ESTADO({entidad}Cargando())
        
        try:
            sesion = OBTENER_SESION()
            query = sesion.query(MODELO_{modelo})
            
            if filtro:
                query = query.filter(MODELO_{modelo}.NOMBRE.contains(filtro))
            
            datos = query.all()
            total = len(datos)
            
            sesion.close()
            
            self._CAMBIAR_ESTADO({entidad_plural}Cargados({entidad_lower}s=datos, total=total))
        
        except Exception as e:
            self._CAMBIAR_ESTADO({entidad}Error(mensaje=f"Error cargando: {{str(e)}}"))
    
    async def _GUARDAR(self, evento: Guardar{entidad}):
        self._CAMBIAR_ESTADO({entidad}Cargando())
        
        try:
            sesion = OBTENER_SESION()
            
            
            sesion.commit()
            sesion.close()
            
            self._CAMBIAR_ESTADO({entidad}Guardado(mensaje="{entidad} guardado exitosamente"))
            await self._CARGAR(None)
        
        except Exception as e:
            self._CAMBIAR_ESTADO({entidad}Error(mensaje=f"Error guardando: {{str(e)}}"))
    
    async def _ELIMINAR(self, evento: Eliminar{entidad}):
        self._CAMBIAR_ESTADO({entidad}Cargando())
        
        try:
            sesion = OBTENER_SESION()
            {entidad_lower} = sesion.query(MODELO_{modelo}).filter_by(ID=evento.{entidad_lower}_id).first()
            
            if {entidad_lower}:
                sesion.delete({entidad_lower})
                sesion.commit()
                sesion.close()
                
                self._CAMBIAR_ESTADO({entidad}Eliminado(mensaje="{entidad} eliminado"))
                await self._CARGAR(None)
            else:
                sesion.close()
                self._CAMBIAR_ESTADO({entidad}Error(mensaje="{entidad} no encontrado"))
        
        except Exception as e:
            self._CAMBIAR_ESTADO({entidad}Error(mensaje=f"Error eliminando: {{str(e)}}"))

{CONSTANTE}_BLOC = {entidad}Bloc()