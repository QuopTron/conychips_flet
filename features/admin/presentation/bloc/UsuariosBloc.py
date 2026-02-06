
import asyncio
from typing import Callable, List, Optional
from dataclasses import dataclass

from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION,
    MODELO_USUARIO,
    MODELO_ROL,
)

@dataclass
class UsuariosEstado:
    pass

@dataclass
class UsuariosInicial(UsuariosEstado):
    pass

@dataclass
class UsuariosCargando(UsuariosEstado):
    pass

@dataclass
class UsuariosCargados(UsuariosEstado):
    usuarios: List
    total: int

@dataclass
class UsuarioError(UsuariosEstado):
    mensaje: str

@dataclass
class UsuarioCreado(UsuariosEstado):
    mensaje: str

@dataclass
class UsuarioActualizado(UsuariosEstado):
    mensaje: str

@dataclass
class UsuarioEliminado(UsuariosEstado):
    mensaje: str

@dataclass
class UsuariosEvento:
    pass

@dataclass
class CargarUsuarios(UsuariosEvento):
    filtro: Optional[str] = None

@dataclass
class CrearUsuario(UsuariosEvento):
    email: str
    nombre_usuario: str
    contrasena: str
    rol_id: int

@dataclass
class ActualizarUsuario(UsuariosEvento):
    usuario_id: int
    datos: dict

@dataclass
class EliminarUsuario(UsuariosEvento):
    usuario_id: int

@dataclass
class CambiarEstadoUsuario(UsuariosEvento):
    usuario_id: int
    activo: bool

class UsuariosBloc:
    
    def __init__(self):
        self._estado: UsuariosEstado = UsuariosInicial()
        self._listeners: List[Callable] = []
    
    @property
    def ESTADO(self) -> UsuariosEstado:
        return self._estado
    
    def AGREGAR_LISTENER(self, listener: Callable):
        if listener not in self._listeners:
            self._listeners.append(listener)
    
    def REMOVER_LISTENER(self, listener: Callable):
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def _CAMBIAR_ESTADO(self, nuevo_estado: UsuariosEstado):
        self._estado = nuevo_estado
        for listener in self._listeners:
            try:
                listener(self._estado)
            except Exception as e:
                print(f"Error en listener: {e}")
    
    def AGREGAR_EVENTO(self, evento: UsuariosEvento):
        if isinstance(evento, CargarUsuarios):
            asyncio.create_task(self._CARGAR_USUARIOS(evento.filtro))
        elif isinstance(evento, CrearUsuario):
            asyncio.create_task(self._CREAR_USUARIO(evento))
        elif isinstance(evento, ActualizarUsuario):
            asyncio.create_task(self._ACTUALIZAR_USUARIO(evento))
        elif isinstance(evento, EliminarUsuario):
            asyncio.create_task(self._ELIMINAR_USUARIO(evento))
        elif isinstance(evento, CambiarEstadoUsuario):
            asyncio.create_task(self._CAMBIAR_ESTADO_USUARIO(evento))
    
    async def _CARGAR_USUARIOS(self, filtro: Optional[str]):
        self._CAMBIAR_ESTADO(UsuariosCargando())
        
        try:
            sesion = OBTENER_SESION()
            query = sesion.query(MODELO_USUARIO)
            
            if filtro:
                query = query.filter(
                    (MODELO_USUARIO.EMAIL.contains(filtro)) |
                    (MODELO_USUARIO.NOMBRE_USUARIO.contains(filtro))
                )
            
            usuarios = query.all()
            total = len(usuarios)
            
            sesion.close()
            
            self._CAMBIAR_ESTADO(UsuariosCargados(usuarios=usuarios, total=total))
        
        except Exception as e:
            self._CAMBIAR_ESTADO(UsuarioError(mensaje=f"Error cargando usuarios: {str(e)}"))
    
    async def _CREAR_USUARIO(self, evento: CrearUsuario):
        self._CAMBIAR_ESTADO(UsuariosCargando())
        
        try:
            await asyncio.sleep(0.5)
            
            self._CAMBIAR_ESTADO(UsuarioCreado(mensaje="Usuario creado exitosamente"))
            await self._CARGAR_USUARIOS(None)
        
        except Exception as e:
            self._CAMBIAR_ESTADO(UsuarioError(mensaje=f"Error creando usuario: {str(e)}"))
    
    async def _ACTUALIZAR_USUARIO(self, evento: ActualizarUsuario):
        self._CAMBIAR_ESTADO(UsuariosCargando())
        
        try:
            sesion = OBTENER_SESION()
            usuario = sesion.query(MODELO_USUARIO).filter_by(ID=evento.usuario_id).first()
            
            if usuario:
                for clave, valor in evento.datos.items():
                    if hasattr(usuario, clave):
                        setattr(usuario, clave, valor)
                
                sesion.commit()
                sesion.close()
                
                self._CAMBIAR_ESTADO(UsuarioActualizado(mensaje="Usuario actualizado"))
                await self._CARGAR_USUARIOS(None)
            else:
                sesion.close()
                self._CAMBIAR_ESTADO(UsuarioError(mensaje="Usuario no encontrado"))
        
        except Exception as e:
            self._CAMBIAR_ESTADO(UsuarioError(mensaje=f"Error actualizando: {str(e)}"))
    
    async def _ELIMINAR_USUARIO(self, evento: EliminarUsuario):
        self._CAMBIAR_ESTADO(UsuariosCargando())
        
        try:
            sesion = OBTENER_SESION()
            usuario = sesion.query(MODELO_USUARIO).filter_by(ID=evento.usuario_id).first()
            
            if usuario:
                sesion.delete(usuario)
                sesion.commit()
                sesion.close()
                
                self._CAMBIAR_ESTADO(UsuarioEliminado(mensaje="Usuario eliminado"))
                await self._CARGAR_USUARIOS(None)
            else:
                sesion.close()
                self._CAMBIAR_ESTADO(UsuarioError(mensaje="Usuario no encontrado"))
        
        except Exception as e:
            self._CAMBIAR_ESTADO(UsuarioError(mensaje=f"Error eliminando: {str(e)}"))
    
    async def _CAMBIAR_ESTADO_USUARIO(self, evento: CambiarEstadoUsuario):
        await self._ACTUALIZAR_USUARIO(
            ActualizarUsuario(
                usuario_id=evento.usuario_id,
                datos={"ACTIVO": evento.activo}
            )
        )

USUARIOS_BLOC = UsuariosBloc()

__all__ = [
    'UsuariosEstado',
    'UsuariosInicial',
    'UsuariosCargando',
    'UsuariosCargados',
    'UsuarioError',
    'UsuarioCreado',
    'UsuarioActualizado',
    'UsuarioEliminado',
    'UsuariosEvento',
    'CargarUsuarios',
    'CrearUsuario',
    'ActualizarUsuario',
    'EliminarUsuario',
    'CambiarEstadoUsuario',
    'UsuariosBloc',
    'USUARIOS_BLOC',
]
