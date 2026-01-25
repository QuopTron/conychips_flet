"""
Implementación del Repositorio Admin
Data Layer - Clean Architecture
"""

from datetime import datetime, timedelta
from typing import List

from ..domain.RepositorioAdmin import RepositorioAdmin
from ..domain.entities.EstadisticasDashboard import (
    EstadisticasGenerales,
    EstadisticaRol,
    EstadisticaSucursal,
    EstadisticaDiaria,
    EstadisticaInventario,
    DashboardCompleto,
)
from .datasources.FuenteAdminLocal import FuenteAdminLocal


class RepositorioAdminImpl(RepositorioAdmin):
    """
    Implementación concreta del repositorio admin
    Coordina las fuentes de datos
    """

    def __init__(self):
        self._fuente_local = FuenteAdminLocal()

    def OBTENER_ESTADISTICAS_GENERALES(self) -> EstadisticasGenerales:
        """Obtiene estadísticas generales del sistema"""
        return EstadisticasGenerales(
            total_usuarios=self._fuente_local.OBTENER_TOTAL_USUARIOS(),
            total_pedidos_hoy=self._fuente_local.OBTENER_PEDIDOS_HOY(),
            ganancias_hoy=self._fuente_local.OBTENER_GANANCIAS_HOY(),
            total_productos=self._fuente_local.OBTENER_TOTAL_PRODUCTOS(),
        )

    def OBTENER_ESTADISTICAS_ROLES(self) -> List[EstadisticaRol]:
        """Obtiene distribución de usuarios por rol"""
        roles = self._fuente_local.OBTENER_ROLES_CON_USUARIOS()
        total_usuarios = self._fuente_local.OBTENER_TOTAL_USUARIOS()

        estadisticas = []
        for rol in roles:
            cantidad = len(rol.USUARIOS)
            porcentaje = (cantidad / total_usuarios * 100) if total_usuarios > 0 else 0
            
            estadisticas.append(EstadisticaRol(
                nombre_rol=rol.NOMBRE,
                cantidad_usuarios=cantidad,
                porcentaje=porcentaje,
            ))

        return estadisticas

    def OBTENER_ESTADISTICAS_SUCURSALES(self) -> List[EstadisticaSucursal]:
        """Obtiene pedidos por sucursal"""
        sucursales = self._fuente_local.OBTENER_SUCURSALES_CON_PEDIDOS()
        
        estadisticas = []
        for sucursal in sucursales:
            total_pedidos = self._fuente_local.CONTAR_PEDIDOS_POR_SUCURSAL(sucursal.ID)
            
            estadisticas.append(EstadisticaSucursal(
                id=sucursal.ID,
                nombre=sucursal.NOMBRE,
                total_pedidos=total_pedidos,
            ))

        return estadisticas

    def OBTENER_ESTADISTICAS_SEMANALES(self) -> List[EstadisticaDiaria]:
        """Obtiene pedidos de la última semana"""
        hoy = datetime.utcnow().date()
        estadisticas = []
        
        nombres_dias = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        
        for i in range(7):
            dia = hoy - timedelta(days=6 - i)
            pedidos_dia = self._fuente_local.OBTENER_PEDIDOS_POR_DIA(dia)
            
            estadisticas.append(EstadisticaDiaria(
                fecha=dia,
                nombre_dia=nombres_dias[dia.weekday()],
                total_pedidos=pedidos_dia,
            ))

        return estadisticas

    def OBTENER_ESTADISTICAS_INVENTARIO(self) -> EstadisticaInventario:
        """Obtiene estadísticas de inventario"""
        return EstadisticaInventario(
            total_insumos=self._fuente_local.OBTENER_TOTAL_INSUMOS(),
            total_proveedores=self._fuente_local.OBTENER_TOTAL_PROVEEDORES(),
            ofertas_activas=self._fuente_local.OBTENER_OFERTAS_ACTIVAS(),
            total_extras=self._fuente_local.OBTENER_TOTAL_EXTRAS(),
        )

    def OBTENER_DASHBOARD_COMPLETO(self) -> DashboardCompleto:
        """Obtiene todas las estadísticas del dashboard"""
        return DashboardCompleto(
            estadisticas_generales=self.OBTENER_ESTADISTICAS_GENERALES(),
            estadisticas_roles=self.OBTENER_ESTADISTICAS_ROLES(),
            estadisticas_sucursales=self.OBTENER_ESTADISTICAS_SUCURSALES(),
            estadisticas_semanales=self.OBTENER_ESTADISTICAS_SEMANALES(),
            estadisticas_inventario=self.OBTENER_ESTADISTICAS_INVENTARIO(),
        )

    def ACTUALIZAR_ROL_USUARIO(self, usuario_id: int, nombre_rol: str) -> bool:
        """Actualiza el rol de un usuario"""
        return self._fuente_local.ACTUALIZAR_ROL_USUARIO(usuario_id, nombre_rol)

    def OBTENER_ROLES_DISPONIBLES(self) -> List:
        """Obtiene lista de roles disponibles"""
        return self._fuente_local.OBTENER_ROLES()


# Instancia única del repositorio (Singleton)
REPOSITORIO_ADMIN_IMPL = RepositorioAdminImpl()
