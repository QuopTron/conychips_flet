"""
Admin BLoC - Business Logic Component
Presentation Layer - Clean Architecture
Gestiona el estado del dashboard de administración
"""

import asyncio
from typing import Callable, List

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
    """
    BLoC para gestión de estado del dashboard admin
    Patrón Observer - notifica a los listeners cuando cambia el estado
    """

    def __init__(self):
        self._estado: AdminEstado = AdminInicial()
        self._listeners: List[Callable[[AdminEstado], None]] = []
        
        # Casos de uso
        self._cargar_estadisticas = CargarEstadisticasDashboard(REPOSITORIO_ADMIN_IMPL)
        self._actualizar_rol = ActualizarRolUsuario(REPOSITORIO_ADMIN_IMPL)

    @property
    def ESTADO(self) -> AdminEstado:
        """Obtiene el estado actual"""
        return self._estado

    def AGREGAR_LISTENER(self, listener: Callable[[AdminEstado], None]):
        """Agrega un listener para cambios de estado"""
        if listener not in self._listeners:
            self._listeners.append(listener)

    def REMOVER_LISTENER(self, listener: Callable[[AdminEstado], None]):
        """Remueve un listener"""
        if listener in self._listeners:
            self._listeners.remove(listener)

    def _CAMBIAR_ESTADO(self, nuevo_estado: AdminEstado):
        """Cambia el estado y notifica a los listeners"""
        self._estado = nuevo_estado
        self._NOTIFICAR_LISTENERS()

    def _NOTIFICAR_LISTENERS(self):
        """Notifica a todos los listeners del cambio de estado"""
        for listener in self._listeners:
            try:
                listener(self._estado)
            except Exception as error:
                print(f"Error notificando listener: {error}")

    def AGREGAR_EVENTO(self, evento: AdminEvento):
        """
        Procesa un evento y cambia el estado correspondiente
        Punto de entrada principal del BLoC
        """
        if isinstance(evento, CargarDashboard):
            self._MANEJAR_CARGAR_DASHBOARD()
        elif isinstance(evento, ActualizarRol):
            self._MANEJAR_ACTUALIZAR_ROL(evento)
        elif isinstance(evento, RecargarDashboard):
            self._MANEJAR_CARGAR_DASHBOARD()

    def _MANEJAR_CARGAR_DASHBOARD(self):
        """Maneja el evento de cargar dashboard"""
        self._CAMBIAR_ESTADO(AdminCargando())
        
        # Ejecutar en background
        asyncio.create_task(self._CARGAR_DASHBOARD_ASYNC())

    async def _CARGAR_DASHBOARD_ASYNC(self):
        """Carga las estadísticas de forma asíncrona"""
        try:
            dashboard = self._cargar_estadisticas.EJECUTAR()
            
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

    def _MANEJAR_ACTUALIZAR_ROL(self, evento: ActualizarRol):
        """Maneja el evento de actualizar rol"""
        self._CAMBIAR_ESTADO(AdminActualizandoRol(usuario_id=evento.usuario_id))
        
        # Ejecutar en background
        asyncio.create_task(
            self._ACTUALIZAR_ROL_ASYNC(evento.usuario_id, evento.nombre_rol)
        )

    async def _ACTUALIZAR_ROL_ASYNC(self, usuario_id: int, nombre_rol: str):
        """Actualiza el rol de forma asíncrona"""
        try:
            resultado = self._actualizar_rol.EJECUTAR(usuario_id, nombre_rol)
            
            if resultado["exito"]:
                # Recargar dashboard después de actualizar
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
        """Limpia los recursos del BLoC"""
        self._listeners.clear()


# Instancia única del BLoC (Singleton)
ADMIN_BLOC = AdminBloc()
