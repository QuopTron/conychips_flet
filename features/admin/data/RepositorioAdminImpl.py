
from datetime import datetime, timedelta, timezone
from typing import List, Optional

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
from core.cache.GestorRedis import REDIS_GLOBAL

class RepositorioAdminImpl(RepositorioAdmin):

    def __init__(self):
        self._fuente_local = FuenteAdminLocal()

    def OBTENER_ESTADISTICAS_GENERALES(self) -> EstadisticasGenerales:
        return EstadisticasGenerales(
            total_usuarios=self._fuente_local.OBTENER_TOTAL_USUARIOS(),
            total_pedidos_hoy=self._fuente_local.OBTENER_PEDIDOS_HOY(),
            ganancias_hoy=self._fuente_local.OBTENER_GANANCIAS_HOY(),
            total_productos=self._fuente_local.OBTENER_TOTAL_PRODUCTOS(),
        )

    def OBTENER_ESTADISTICAS_ROLES(self) -> List[EstadisticaRol]:
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
        hoy = datetime.now(timezone.utc).date()
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
        return EstadisticaInventario(
            total_insumos=self._fuente_local.OBTENER_TOTAL_INSUMOS(),
            total_proveedores=self._fuente_local.OBTENER_TOTAL_PROVEEDORES(),
            ofertas_activas=self._fuente_local.OBTENER_OFERTAS_ACTIVAS(),
            total_extras=self._fuente_local.OBTENER_TOTAL_EXTRAS(),
        )

    def OBTENER_DASHBOARD_COMPLETO(self, sucursal_id: Optional[int] = None) -> DashboardCompleto:
        try:
            if sucursal_id is None:
                cache_key = "dashboard:completo"
            else:
                cache_key = f"dashboard:completo:sucursal:{sucursal_id}"
            if REDIS_GLOBAL.ESTA_DISPONIBLE():
                cached = REDIS_GLOBAL.OBTENER_CACHE(cache_key)
                if cached:
                    try:
                        gen = cached.get("estadisticas_generales", {})
                        generales = EstadisticasGenerales(**gen)

                        roles = [EstadisticaRol(**r) for r in cached.get("estadisticas_roles", [])]
                        sucursales = [EstadisticaSucursal(**s) for s in cached.get("estadisticas_sucursales", [])]
                        semanales = [EstadisticaDiaria(**d) for d in cached.get("estadisticas_semanales", [])]
                        inv = EstadisticaInventario(**cached.get("estadisticas_inventario", {}))

                        return DashboardCompleto(
                            estadisticas_generales=generales,
                            estadisticas_roles=roles,
                            estadisticas_sucursales=sucursales,
                            estadisticas_semanales=semanales,
                            estadisticas_inventario=inv,
                        )
                    except Exception:
                        pass

            dashboard = self._fuente_local.OBTENER_DASHBOARD_COMPLETO(sucursal_id=sucursal_id)

            try:
                if REDIS_GLOBAL.ESTA_DISPONIBLE():
                    semanales_serial = []
                    for d in dashboard.estadisticas_semanales:
                        item = d.__dict__.copy()
                        if hasattr(item.get('fecha'), 'isoformat'):
                            item['fecha'] = item['fecha'].isoformat()
                        semanales_serial.append(item)

                    payload = {
                        "estadisticas_generales": dashboard.estadisticas_generales.__dict__,
                        "estadisticas_roles": [r.__dict__ for r in dashboard.estadisticas_roles],
                        "estadisticas_sucursales": [s.__dict__ for s in dashboard.estadisticas_sucursales],
                        "estadisticas_semanales": semanales_serial,
                        "estadisticas_inventario": dashboard.estadisticas_inventario.__dict__,
                    }
                    REDIS_GLOBAL.GUARDAR_CACHE(cache_key, payload, TTL_SECONDS=30)
            except Exception:
                pass

            return dashboard
        except Exception as e:
            print(f"[RepositorioAdmin] Error creando dashboard: {e}")
            import traceback
            traceback.print_exc()
            raise

    def ACTUALIZAR_ROL_USUARIO(self, usuario_id: int, nombre_rol: str) -> bool:
        return self._fuente_local.ACTUALIZAR_ROL_USUARIO(usuario_id, nombre_rol)

    def OBTENER_ROLES_DISPONIBLES(self) -> List:
        return self._fuente_local.OBTENER_ROLES()

REPOSITORIO_ADMIN_IMPL = RepositorioAdminImpl()
