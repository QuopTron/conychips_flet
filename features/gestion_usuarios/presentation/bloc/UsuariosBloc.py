"""BLoC para la gestión de usuarios - Patrón similar a Vouchers/Finanzas"""
import threading
from typing import Callable, List
from .UsuariosEstado import *
from .UsuariosEvento import *


class UsuariosBloc:
    """
    BLoC para gestionar el estado de usuarios.
    Sin uso de streams - usa listeners directos como AdminBloc.
    """
    
    def __init__(self, repositorio):
        self._repositorio = repositorio
        self._estado: UsuariosEstado = UsuariosInicial()
        self._listeners: List[Callable[[UsuariosEstado], None]] = []
        self._lock = threading.Lock()
    
    @property
    def ESTADO(self) -> UsuariosEstado:
        """Obtiene el estado actual"""
        with self._lock:
            return self._estado
    
    def AGREGAR_LISTENER(self, listener: Callable[[UsuariosEstado], None]):
        """Registra un listener para cambios de estado"""
        with self._lock:
            if listener not in self._listeners:
                self._listeners.append(listener)
    
    def REMOVER_LISTENER(self, listener: Callable[[UsuariosEstado], None]):
        """Remueve un listener"""
        with self._lock:
            if listener in self._listeners:
                self._listeners.remove(listener)
    
    def _CAMBIAR_ESTADO(self, nuevo_estado: UsuariosEstado):
        """Cambia el estado y notifica a los listeners"""
        with self._lock:
            self._estado = nuevo_estado
            listeners = self._listeners.copy()
        
        # Notificar fuera del lock
        for listener in listeners:
            try:
                listener(nuevo_estado)
            except Exception as e:
                print(f"❌ Error en listener de UsuariosBloc: {e}")
    
    def AGREGAR_EVENTO(self, evento: UsuariosEvento):
        """Procesa un evento en un thread separado"""
        thread = threading.Thread(
            target=self._PROCESAR_EVENTO,
            args=(evento,),
            daemon=True
        )
        thread.start()
    
    def _PROCESAR_EVENTO(self, evento: UsuariosEvento):
        """Procesa el evento según su tipo"""
        try:
            if isinstance(evento, CargarUsuarios):
                self._MANEJAR_CARGAR_USUARIOS(evento)
            elif isinstance(evento, CrearUsuario):
                self._MANEJAR_CREAR_USUARIO(evento)
            elif isinstance(evento, ActualizarUsuario):
                self._MANEJAR_ACTUALIZAR_USUARIO(evento)
            elif isinstance(evento, EliminarUsuario):
                self._MANEJAR_ELIMINAR_USUARIO(evento)
            elif isinstance(evento, CambiarEstadoUsuario):
                self._MANEJAR_CAMBIAR_ESTADO(evento)
            elif isinstance(evento, CambiarRolUsuario):
                self._MANEJAR_CAMBIAR_ROL(evento)
            elif isinstance(evento, ResetearContrasena):
                self._MANEJAR_RESETEAR_CONTRASENA(evento)
        except Exception as e:
            self._CAMBIAR_ESTADO(UsuarioError(
                mensaje=f"Error procesando evento: {str(e)}",
                detalles=str(type(e).__name__)
            ))
    
    def _MANEJAR_CARGAR_USUARIOS(self, evento: CargarUsuarios):
        """Carga la lista de usuarios con filtros opcionales"""
        self._CAMBIAR_ESTADO(UsuariosCargando())
        
        try:
            usuarios = self._repositorio.OBTENER_USUARIOS(
                rol_filtro=evento.rol_filtro,
                estado_filtro=evento.estado_filtro,
                sucursal_id=evento.sucursal_id
            )
            
            self._CAMBIAR_ESTADO(UsuariosCargados(
                usuarios=usuarios,
                total=len(usuarios),
                mensaje=f"Se cargaron {len(usuarios)} usuarios"
            ))
        except Exception as e:
            self._CAMBIAR_ESTADO(UsuarioError(
                mensaje=f"Error cargando usuarios: {str(e)}"
            ))
    
    def _MANEJAR_CREAR_USUARIO(self, evento: CrearUsuario):
        """Crea un nuevo usuario"""
        self._CAMBIAR_ESTADO(UsuariosCargando())
        
        try:
            usuario_id = self._repositorio.CREAR_USUARIO(
                nombre_usuario=evento.nombre_usuario,
                email=evento.email,
                contrasena=evento.contrasena,
                nombre_completo=evento.nombre_completo,
                rol=evento.rol,
                sucursal_id=evento.sucursal_id,
                activo=evento.activo
            )
            
            self._CAMBIAR_ESTADO(UsuarioCreado(
                mensaje=f"Usuario '{evento.nombre_usuario}' creado exitosamente",
                usuario_id=usuario_id
            ))
        except Exception as e:
            self._CAMBIAR_ESTADO(UsuarioError(
                mensaje=f"Error creando usuario: {str(e)}"
            ))
    
    def _MANEJAR_ACTUALIZAR_USUARIO(self, evento: ActualizarUsuario):
        """Actualiza un usuario existente"""
        self._CAMBIAR_ESTADO(UsuariosCargando())
        
        try:
            self._repositorio.ACTUALIZAR_USUARIO(
                usuario_id=evento.usuario_id,
                datos=evento.datos
            )
            
            self._CAMBIAR_ESTADO(UsuarioActualizado(
                mensaje="Usuario actualizado exitosamente",
                usuario_id=evento.usuario_id
            ))
        except Exception as e:
            self._CAMBIAR_ESTADO(UsuarioError(
                mensaje=f"Error actualizando usuario: {str(e)}"
            ))
    
    def _MANEJAR_ELIMINAR_USUARIO(self, evento: EliminarUsuario):
        """Elimina un usuario (soft delete - marca como inactivo)"""
        self._CAMBIAR_ESTADO(UsuariosCargando())
        
        try:
            self._repositorio.ELIMINAR_USUARIO(evento.usuario_id)
            
            self._CAMBIAR_ESTADO(UsuarioEliminado(
                mensaje="Usuario eliminado exitosamente",
                usuario_id=evento.usuario_id
            ))
        except Exception as e:
            self._CAMBIAR_ESTADO(UsuarioError(
                mensaje=f"Error eliminando usuario: {str(e)}"
            ))
    
    def _MANEJAR_CAMBIAR_ESTADO(self, evento: CambiarEstadoUsuario):
        """Activa o desactiva un usuario"""
        self._CAMBIAR_ESTADO(UsuariosCargando())
        
        try:
            self._repositorio.CAMBIAR_ESTADO_USUARIO(
                usuario_id=evento.usuario_id,
                activo=evento.activo
            )
            
            estado_texto = "activado" if evento.activo else "desactivado"
            self._CAMBIAR_ESTADO(UsuarioActualizado(
                mensaje=f"Usuario {estado_texto} exitosamente",
                usuario_id=evento.usuario_id
            ))
        except Exception as e:
            self._CAMBIAR_ESTADO(UsuarioError(
                mensaje=f"Error cambiando estado: {str(e)}"
            ))
    
    def _MANEJAR_CAMBIAR_ROL(self, evento: CambiarRolUsuario):
        """Cambia el rol de un usuario"""
        self._CAMBIAR_ESTADO(UsuariosCargando())
        
        try:
            self._repositorio.CAMBIAR_ROL_USUARIO(
                usuario_id=evento.usuario_id,
                nuevo_rol=evento.nuevo_rol
            )
            
            self._CAMBIAR_ESTADO(UsuarioActualizado(
                mensaje=f"Rol cambiado a '{evento.nuevo_rol}' exitosamente",
                usuario_id=evento.usuario_id
            ))
        except Exception as e:
            self._CAMBIAR_ESTADO(UsuarioError(
                mensaje=f"Error cambiando rol: {str(e)}"
            ))
    
    def _MANEJAR_RESETEAR_CONTRASENA(self, evento: ResetearContrasena):
        """Resetea la contraseña de un usuario"""
        self._CAMBIAR_ESTADO(UsuariosCargando())
        
        try:
            self._repositorio.RESETEAR_CONTRASENA(
                usuario_id=evento.usuario_id,
                nueva_contrasena=evento.nueva_contrasena
            )
            
            self._CAMBIAR_ESTADO(UsuarioActualizado(
                mensaje="Contraseña reseteada exitosamente",
                usuario_id=evento.usuario_id
            ))
        except Exception as e:
            self._CAMBIAR_ESTADO(UsuarioError(
                mensaje=f"Error reseteando contraseña: {str(e)}"
            ))
    
    def DISPOSE(self):
        """Limpia recursos del BLoC"""
        with self._lock:
            self._listeners.clear()
