"""
BLoC para Gestión de Productos
Presentation Layer - Clean Architecture
"""

import asyncio
from typing import Callable, List, Optional
from dataclasses import dataclass

from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_PRODUCTO


# Estados
@dataclass
class ProductosEstado:
    pass


@dataclass
class ProductosInicial(ProductosEstado):
    pass


@dataclass
class ProductosCargando(ProductosEstado):
    pass


@dataclass
class ProductosCargados(ProductosEstado):
    productos: List
    total: int


@dataclass
class ProductoError(ProductosEstado):
    mensaje: str


@dataclass
class ProductoGuardado(ProductosEstado):
    mensaje: str


# Eventos
@dataclass
class ProductosEvento:
    pass


@dataclass
class CargarProductos(ProductosEvento):
    filtro: Optional[str] = None


@dataclass
class GuardarProducto(ProductosEvento):
    datos: dict


@dataclass
class EliminarProducto(ProductosEvento):
    producto_id: int


# BLoC
class ProductosBloc:
    def __init__(self):
        self._estado: ProductosEstado = ProductosInicial()
        self._listeners: List[Callable] = []
    
    @property
    def ESTADO(self) -> ProductosEstado:
        return self._estado
    
    def AGREGAR_LISTENER(self, listener: Callable):
        if listener not in self._listeners:
            self._listeners.append(listener)
    
    def REMOVER_LISTENER(self, listener: Callable):
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def _CAMBIAR_ESTADO(self, nuevo_estado: ProductosEstado):
        self._estado = nuevo_estado
        for listener in self._listeners:
            try:
                listener(self._estado)
            except Exception as e:
                print(f"Error en listener: {e}")
    
    def AGREGAR_EVENTO(self, evento: ProductosEvento):
        if isinstance(evento, CargarProductos):
            asyncio.create_task(self._CARGAR_PRODUCTOS(evento.filtro))
        elif isinstance(evento, GuardarProducto):
            asyncio.create_task(self._GUARDAR_PRODUCTO(evento))
        elif isinstance(evento, EliminarProducto):
            asyncio.create_task(self._ELIMINAR_PRODUCTO(evento))
    
    async def _CARGAR_PRODUCTOS(self, filtro: Optional[str]):
        self._CAMBIAR_ESTADO(ProductosCargando())
        
        try:
            sesion = OBTENER_SESION()
            query = sesion.query(MODELO_PRODUCTO)
            
            if filtro:
                query = query.filter(MODELO_PRODUCTO.NOMBRE.contains(filtro))
            
            productos = query.all()
            sesion.close()
            
            self._CAMBIAR_ESTADO(ProductosCargados(productos=productos, total=len(productos)))
        except Exception as e:
            self._CAMBIAR_ESTADO(ProductoError(mensaje=f"Error: {str(e)}"))
    
    async def _GUARDAR_PRODUCTO(self, evento: GuardarProducto):
        self._CAMBIAR_ESTADO(ProductosCargando())
        try:
            # Lógica de guardado
            await asyncio.sleep(0.3)
            self._CAMBIAR_ESTADO(ProductoGuardado(mensaje="Producto guardado"))
            await self._CARGAR_PRODUCTOS(None)
        except Exception as e:
            self._CAMBIAR_ESTADO(ProductoError(mensaje=f"Error: {str(e)}"))
    
    async def _ELIMINAR_PRODUCTO(self, evento: EliminarProducto):
        self._CAMBIAR_ESTADO(ProductosCargando())
        try:
            sesion = OBTENER_SESION()
            producto = sesion.query(MODELO_PRODUCTO).filter_by(ID=evento.producto_id).first()
            if producto:
                sesion.delete(producto)
                sesion.commit()
            sesion.close()
            
            self._CAMBIAR_ESTADO(ProductoGuardado(mensaje="Producto eliminado"))
            await self._CARGAR_PRODUCTOS(None)
        except Exception as e:
            self._CAMBIAR_ESTADO(ProductoError(mensaje=f"Error: {str(e)}"))


PRODUCTOS_BLOC = ProductosBloc()
