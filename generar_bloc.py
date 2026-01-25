#!/usr/bin/env python3
"""
Script para generar BLoCs automáticamente
Uso: python generar_bloc.py <entidad>
Ejemplo: python generar_bloc.py Extras
"""

import sys
import os
from pathlib import Path


TEMPLATE_BLOC = '''"""
BLoC para Gestión de {entidad_plural}
Presentation Layer - Clean Architecture
"""

import asyncio
from typing import Callable, List, Optional
from dataclasses import dataclass

from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_{modelo}


# ============================================================================
# Estados
# ============================================================================

@dataclass
class {entidad}Estado:
    """Estado base"""
    pass


@dataclass
class {entidad}Inicial({entidad}Estado):
    """Estado inicial"""
    pass


@dataclass
class {entidad}Cargando({entidad}Estado):
    """Cargando datos"""
    pass


@dataclass
class {entidad_plural}Cargados({entidad}Estado):
    """{entidad_plural} cargados"""
    {entidad_lower}s: List
    total: int


@dataclass
class {entidad}Error({entidad}Estado):
    """Error en operación"""
    mensaje: str


@dataclass
class {entidad}Guardado({entidad}Estado):
    """{entidad} guardado exitosamente"""
    mensaje: str


@dataclass
class {entidad}Eliminado({entidad}Estado):
    """{entidad} eliminado"""
    mensaje: str


# ============================================================================
# Eventos
# ============================================================================

@dataclass
class {entidad}Evento:
    """Evento base"""
    pass


@dataclass
class Cargar{entidad_plural}({entidad}Evento):
    """Cargar lista de {entidad_lower}s"""
    filtro: Optional[str] = None


@dataclass
class Guardar{entidad}({entidad}Evento):
    """Guardar {entidad_lower}"""
    datos: dict


@dataclass
class Eliminar{entidad}({entidad}Evento):
    """Eliminar {entidad_lower}"""
    {entidad_lower}_id: int


# ============================================================================
# BLoC
# ============================================================================

class {entidad}Bloc:
    """
    BLoC para gestión de {entidad_lower}s
    """
    
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
        """Procesa eventos"""
        if isinstance(evento, Cargar{entidad_plural}):
            asyncio.create_task(self._CARGAR(evento.filtro))
        elif isinstance(evento, Guardar{entidad}):
            asyncio.create_task(self._GUARDAR(evento))
        elif isinstance(evento, Eliminar{entidad}):
            asyncio.create_task(self._ELIMINAR(evento))
    
    async def _CARGAR(self, filtro: Optional[str]):
        """Carga {entidad_lower}s de la BD"""
        self._CAMBIAR_ESTADO({entidad}Cargando())
        
        try:
            sesion = OBTENER_SESION()
            query = sesion.query(MODELO_{modelo})
            
            if filtro:
                # TODO: Ajustar filtro según campos del modelo
                query = query.filter(MODELO_{modelo}.NOMBRE.contains(filtro))
            
            datos = query.all()
            total = len(datos)
            
            sesion.close()
            
            self._CAMBIAR_ESTADO({entidad_plural}Cargados({entidad_lower}s=datos, total=total))
        
        except Exception as e:
            self._CAMBIAR_ESTADO({entidad}Error(mensaje=f"Error cargando: {{str(e)}}"))
    
    async def _GUARDAR(self, evento: Guardar{entidad}):
        """Guarda {entidad_lower}"""
        self._CAMBIAR_ESTADO({entidad}Cargando())
        
        try:
            sesion = OBTENER_SESION()
            
            # TODO: Implementar lógica de guardado
            # Si es nuevo: crear
            # Si existe: actualizar
            
            sesion.commit()
            sesion.close()
            
            self._CAMBIAR_ESTADO({entidad}Guardado(mensaje="{entidad} guardado exitosamente"))
            # Recargar lista
            await self._CARGAR(None)
        
        except Exception as e:
            self._CAMBIAR_ESTADO({entidad}Error(mensaje=f"Error guardando: {{str(e)}}"))
    
    async def _ELIMINAR(self, evento: Eliminar{entidad}):
        """Elimina {entidad_lower}"""
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


# Instancia global
{CONSTANTE}_BLOC = {entidad}Bloc()
'''


def pluralizar(palabra):
    """Pluraliza palabra en español"""
    if palabra.endswith('s'):
        return palabra + 'es'
    elif palabra.endswith('z'):
        return palabra[:-1] + 'ces'
    else:
        return palabra + 's'


def generar_bloc(entidad):
    """Genera archivo BLoC"""
    entidad_plural = pluralizar(entidad)
    entidad_lower = entidad.lower()
    modelo = entidad.upper()
    constante = entidad.upper()
    
    contenido = TEMPLATE_BLOC.format(
        entidad=entidad,
        entidad_plural=entidad_plural,
        entidad_lower=entidad_lower,
        modelo=modelo,
        CONSTANTE=constante
    )
    
    # Determinar ruta
    ruta_bloc = Path(__file__).parent / "features" / "admin" / "presentation" / "bloc" / f"{entidad}Bloc.py"
    
    # Crear archivo
    with open(ruta_bloc, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print(f"✅ BLoC creado: {ruta_bloc}")
    print(f"\n📝 Próximos pasos:")
    print(f"1. Revisar MODELO_{modelo} en ConfiguracionBD.py")
    print(f"2. Ajustar filtros en método _CARGAR")
    print(f"3. Implementar lógica de guardado en _GUARDAR")
    print(f"4. Importar en página: from features.admin.presentation.bloc.{entidad}Bloc import {constante}_BLOC")


def main():
    if len(sys.argv) < 2:
        print("❌ Uso: python generar_bloc.py <Entidad>")
        print("Ejemplo: python generar_bloc.py Extras")
        sys.exit(1)
    
    entidad = sys.argv[1].capitalize()
    
    print(f"🚀 Generando BLoC para {entidad}...")
    generar_bloc(entidad)


if __name__ == "__main__":
    main()
