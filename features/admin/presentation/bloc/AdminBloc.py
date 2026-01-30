import threading
from typing import Callable, List, Optional
import flet as ft

from .AdminEstado import (
    AdminEstado,
    AdminInicial,
    AdminCargando,
    AdminCargado,
    AdminError,
    AdminActualizandoRol,
    AdminRolActualizado,
)
from .AdminEvento import (
    AdminEvento,
    CargarDashboard,
    ActualizarRol,
    RecargarDashboard,
)
from ...domain.usecases.CargarEstadisticasDashboard import CargarEstadisticasDashboard
from ...domain.usecases.ActualizarRolUsuario import ActualizarRolUsuario
from ...data.RepositorioAdminImpl import REPOSITORIO_ADMIN_IMPL

class AdminBloc:
    def __init__(self):
        self._estado: AdminEstado = AdminInicial()
        self._listeners: List[Callable[[AdminEstado], None]] = []
        self._page: Optional[ft.Page] = None
        
        self._cargar_estadisticas = CargarEstadisticasDashboard(REPOSITORIO_ADMIN_IMPL)
        self._actualizar_rol = ActualizarRolUsuario(REPOSITORIO_ADMIN_IMPL)

    def CONFIGURAR_PAGINA(self, page: ft.Page):
        self._page = page

    @property
    def ESTADO(self) -> AdminEstado:
        return self._estado

    def AGREGAR_LISTENER(self, listener: Callable[[AdminEstado], None]):
        if listener not in self._listeners:
            self._listeners.append(listener)

    def REMOVER_LISTENER(self, listener: Callable[[AdminEstado], None]):
        if listener in self._listeners:
            self._listeners.remove(listener)

    def _CAMBIAR_ESTADO(self, nuevo_estado: AdminEstado):
        self._estado = nuevo_estado
        self._NOTIFICAR_LISTENERS()

    def _NOTIFICAR_LISTENERS(self):
        for listener in self._listeners:
            try:
                listener(self._estado)
            except Exception as error:
                pass

    def AGREGAR_EVENTO(self, evento: AdminEvento):
        if isinstance(evento, CargarDashboard):
            self._MANEJAR_CARGAR_DASHBOARD(evento.sucursal_id)
        elif isinstance(evento, ActualizarRol):
            self._MANEJAR_ACTUALIZAR_ROL(evento)
        elif isinstance(evento, RecargarDashboard):
            self._MANEJAR_CARGAR_DASHBOARD(evento.sucursal_id)

    def _MANEJAR_CARGAR_DASHBOARD(self, sucursal_id: Optional[int] = None):
        self._CAMBIAR_ESTADO(AdminCargando())
        
        thread = threading.Thread(
            target=self._CARGAR_DASHBOARD_SYNC, 
            args=(sucursal_id,),
            daemon=True
        )
        thread.start()

    def _CARGAR_DASHBOARD_SYNC(self, sucursal_id: Optional[int] = None):
        try:
            # Intentar obtener de cache primero
            dashboard = self._obtener_dashboard_cache(sucursal_id)
            
            if dashboard is None:
                # Si no está en cache, cargar de BD
                dashboard = self._cargar_estadisticas.EJECUTAR(sucursal_id=sucursal_id)
                
                # Guardar en cache
                self._guardar_dashboard_cache(dashboard, sucursal_id)
            
            if dashboard:
                self._CAMBIAR_ESTADO(AdminCargado(dashboard=dashboard))
            else:
                self._CAMBIAR_ESTADO(AdminError(
                    mensaje="No se pudieron cargar las estadísticas"
                ))
        except Exception as error:
            self._CAMBIAR_ESTADO(AdminError(
                mensaje=f"Error cargando dashboard: {str(error)}"
            ))
    
    def _obtener_dashboard_cache(self, sucursal_id: Optional[int] = None):
        """Obtiene las estadísticas del dashboard desde cache"""
        try:
            from core.cache.GestorRedis import GestorRedis
            redis = GestorRedis()
            
            if sucursal_id is None:
                cache_key = "dashboard:estadisticas"
            else:
                cache_key = f"dashboard:estadisticas:sucursal:{sucursal_id}"
            
            return redis.OBTENER_CACHE(cache_key)
        except Exception:
            return None
    
    def _guardar_dashboard_cache(self, dashboard, sucursal_id: Optional[int] = None):
        """Guarda las estadísticas del dashboard en cache"""
        try:
            from core.cache.GestorRedis import GestorRedis
            redis = GestorRedis()
            
            if sucursal_id is None:
                cache_key = "dashboard:estadisticas"
            else:
                cache_key = f"dashboard:estadisticas:sucursal:{sucursal_id}"
            
            # Cache de 5 minutos para estadísticas
            redis.GUARDAR_CACHE(cache_key, dashboard, TTL_SECONDS=300)
        except Exception as e:
            print(f"[DEBUG] No se pudo guardar dashboard en cache: {e}")

    def _MANEJAR_ACTUALIZAR_ROL(self, evento: ActualizarRol):
        self._CAMBIAR_ESTADO(AdminActualizandoRol(usuario_id=evento.usuario_id))
        
        thread = threading.Thread(
            target=self._ACTUALIZAR_ROL_SYNC,
            args=(evento.usuario_id, evento.nombre_rol),
            daemon=True
        )
        thread.start()

    def _ACTUALIZAR_ROL_SYNC(self, usuario_id: int, nombre_rol: str):
        try:
            resultado = self._actualizar_rol.EJECUTAR(usuario_id, nombre_rol)
            
            if resultado["exito"]:
                dashboard = self._cargar_estadisticas.EJECUTAR()
                self._CAMBIAR_ESTADO(AdminRolActualizado(
                    mensaje=resultado["mensaje"],
                    dashboard=dashboard
                ))
            else:
                self._CAMBIAR_ESTADO(AdminError(mensaje=resultado["mensaje"]))
        except Exception as error:
            self._CAMBIAR_ESTADO(AdminError(
                mensaje=f"Error actualizando rol: {str(error)}"
            ))

    def DISPOSE(self):
        self._listeners.clear()

ADMIN_BLOC = AdminBloc()
