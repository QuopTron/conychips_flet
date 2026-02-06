
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION,
    MODELO_USUARIO,
    MODELO_ROL,
    MODELO_PEDIDO,
    MODELO_CAJA,
    MODELO_SUCURSAL,
    MODELO_PRODUCTO,
    MODELO_INSUMO,
    MODELO_PROVEEDOR,
    MODELO_OFERTA,
    MODELO_EXTRA,
)

from sqlalchemy import func
from ...domain.entities.EstadisticasDashboard import (
    EstadisticasGenerales,
    EstadisticaRol,
    EstadisticaSucursal,
    EstadisticaDiaria,
    EstadisticaInventario,
    DashboardCompleto,
)

class FuenteAdminLocal:

    def OBTENER_TOTAL_USUARIOS(self) -> int:
        sesion = OBTENER_SESION()
        try:
            return sesion.query(MODELO_USUARIO).count()
        finally:
            sesion.close()

    def OBTENER_TOTAL_PRODUCTOS(self) -> int:
        sesion = OBTENER_SESION()
        try:
            return sesion.query(MODELO_PRODUCTO).count()
        finally:
            sesion.close()

    def OBTENER_PEDIDOS_HOY(self) -> int:
        sesion = OBTENER_SESION()
        try:
            hoy = datetime.now(timezone.utc).date()
            return (
                sesion.query(MODELO_PEDIDO)
                .filter(MODELO_PEDIDO.FECHA_CREACION >= hoy)
                .count()
            )
        finally:
            sesion.close()

    def OBTENER_GANANCIAS_HOY(self) -> float:
        sesion = OBTENER_SESION()
        try:
            hoy = datetime.now(timezone.utc).date()
            cajas_hoy = (
                sesion.query(MODELO_CAJA)
                .filter(MODELO_CAJA.FECHA_APERTURA >= hoy)
                .all()
            )
            return sum(c.GANANCIAS or 0 for c in cajas_hoy)
        finally:
            sesion.close()

    def OBTENER_ROLES_CON_USUARIOS(self) -> List:
        from sqlalchemy.orm import joinedload
        sesion = OBTENER_SESION()
        try:
            roles = sesion.query(MODELO_ROL).options(joinedload(MODELO_ROL.USUARIOS)).all()
            for rol in roles:
                _ = rol.USUARIOS
            return roles
        finally:
            sesion.close()

    def OBTENER_SUCURSALES_CON_PEDIDOS(self) -> List:
        sesion = OBTENER_SESION()
        try:
            return sesion.query(MODELO_SUCURSAL).all()
        finally:
            sesion.close()

    def CONTAR_PEDIDOS_POR_SUCURSAL(self, sucursal_id: int) -> int:
        sesion = OBTENER_SESION()
        try:
            return (
                sesion.query(MODELO_PEDIDO)
                .filter_by(SUCURSAL_ID=sucursal_id)
                .count()
            )
        finally:
            sesion.close()

    def OBTENER_PEDIDOS_POR_DIA(self, fecha: datetime.date) -> int:
        sesion = OBTENER_SESION()
        try:
            return (
                sesion.query(MODELO_PEDIDO)
                .filter(
                    MODELO_PEDIDO.FECHA_CREACION >= fecha,
                    MODELO_PEDIDO.FECHA_CREACION < fecha + timedelta(days=1)
                )
                .count()
            )
        finally:
            sesion.close()

    def OBTENER_TOTAL_INSUMOS(self) -> int:
        sesion = OBTENER_SESION()
        try:
            return sesion.query(MODELO_INSUMO).count()
        finally:
            sesion.close()

    def OBTENER_TOTAL_PROVEEDORES(self) -> int:
        sesion = OBTENER_SESION()
        try:
            return sesion.query(MODELO_PROVEEDOR).count()
        finally:
            sesion.close()

    def OBTENER_OFERTAS_ACTIVAS(self) -> int:
        sesion = OBTENER_SESION()
        try:
            return sesion.query(MODELO_OFERTA).filter_by(ACTIVA=True).count()
        finally:
            sesion.close()

    def OBTENER_TOTAL_EXTRAS(self) -> int:
        sesion = OBTENER_SESION()
        try:
            return sesion.query(MODELO_EXTRA).count()
        finally:
            sesion.close()

    def OBTENER_DASHBOARD_COMPLETO(self, sucursal_id: Optional[int] = None) -> DashboardCompleto:
        sesion = OBTENER_SESION()
        try:
            hoy = datetime.now(timezone.utc).date()

            total_usuarios = sesion.query(func.count(MODELO_USUARIO.ID)).scalar() or 0

            total_productos = sesion.query(func.count(MODELO_PRODUCTO.ID)).scalar() or 0

            # Filtrar pedidos por sucursal si se especifica
            query_pedidos_hoy = sesion.query(func.count(MODELO_PEDIDO.ID)).filter(MODELO_PEDIDO.FECHA_CREACION >= hoy)
            if sucursal_id is not None:
                query_pedidos_hoy = query_pedidos_hoy.filter(MODELO_PEDIDO.SUCURSAL_ID == sucursal_id)
            pedidos_hoy = query_pedidos_hoy.scalar() or 0

            # Filtrar ganancias por sucursal si se especifica
            query_ganancias = sesion.query(func.coalesce(func.sum(MODELO_CAJA.GANANCIAS), 0)).filter(MODELO_CAJA.FECHA_APERTURA >= hoy)
            if sucursal_id is not None:
                query_ganancias = query_ganancias.filter(MODELO_CAJA.SUCURSAL_ID == sucursal_id)
            ganancias_hoy = query_ganancias.scalar() or 0

            generales = EstadisticasGenerales(
                total_usuarios=total_usuarios,
                total_pedidos_hoy=pedidos_hoy,
                ganancias_hoy=ganancias_hoy,
                total_productos=total_productos,
            )

            from sqlalchemy.orm import joinedload
            roles_model = sesion.query(MODELO_ROL).options(joinedload(MODELO_ROL.USUARIOS)).all()
            estadisticas_roles = []
            for rol in roles_model:
                cantidad = len(rol.USUARIOS) if getattr(rol, 'USUARIOS', None) is not None else 0
                porcentaje = (cantidad / total_usuarios * 100) if total_usuarios > 0 else 0
                estadisticas_roles.append(EstadisticaRol(
                    nombre_rol=rol.NOMBRE,
                    cantidad_usuarios=cantidad,
                    porcentaje=porcentaje,
                ))

            sucursales_model = sesion.query(MODELO_SUCURSAL).all()
            estadisticas_sucursales = []
            for suc in sucursales_model:
                total_pedidos = (
                    sesion.query(func.count(MODELO_PEDIDO.ID)).filter_by(SUCURSAL_ID=suc.ID).scalar()
                ) or 0
                estadisticas_sucursales.append(EstadisticaSucursal(
                    id=suc.ID,
                    nombre=suc.NOMBRE,
                    total_pedidos=total_pedidos,
                ))

            estadisticas_semanales = []
            nombres_dias = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
            for i in range(7):
                dia = hoy - timedelta(days=6 - i)
                query_dia = sesion.query(func.count(MODELO_PEDIDO.ID)).filter(
                    MODELO_PEDIDO.FECHA_CREACION >= dia
                ).filter(
                    MODELO_PEDIDO.FECHA_CREACION < dia + timedelta(days=1)
                )
                if sucursal_id is not None:
                    query_dia = query_dia.filter(MODELO_PEDIDO.SUCURSAL_ID == sucursal_id)
                pedidos_dia = query_dia.scalar() or 0
                estadisticas_semanales.append(EstadisticaDiaria(
                    fecha=dia,
                    nombre_dia=nombres_dias[dia.weekday()],
                    total_pedidos=pedidos_dia,
                ))

            total_insumos = sesion.query(func.count(MODELO_INSUMO.ID)).scalar() or 0
            total_proveedores = sesion.query(func.count(MODELO_PROVEEDOR.ID)).scalar() or 0
            ofertas_activas = sesion.query(func.count(MODELO_OFERTA.ID)).filter(MODELO_OFERTA.ACTIVA == True).scalar() or 0
            total_extras = sesion.query(func.count(MODELO_EXTRA.ID)).scalar() or 0

            inventario = EstadisticaInventario(
                total_insumos=total_insumos,
                total_proveedores=total_proveedores,
                ofertas_activas=ofertas_activas,
                total_extras=total_extras,
            )

            dashboard = DashboardCompleto(
                estadisticas_generales=generales,
                estadisticas_roles=estadisticas_roles,
                estadisticas_sucursales=estadisticas_sucursales,
                estadisticas_semanales=estadisticas_semanales,
                estadisticas_inventario=inventario,
            )

            return dashboard
        finally:
            sesion.close()

    def ACTUALIZAR_ROL_USUARIO(self, usuario_id: int, nombre_rol: str) -> bool:
        sesion = OBTENER_SESION()
        try:
            usuario = sesion.query(MODELO_USUARIO).filter_by(ID=usuario_id).first()
            rol = sesion.query(MODELO_ROL).filter_by(NOMBRE=nombre_rol).first()

            if usuario and rol:
                usuario.ROLES.clear()
                usuario.ROLES.append(rol)
                sesion.commit()
                return True
            return False
        except Exception as error:
            sesion.rollback()
            print(f"Error actualizando rol: {error}")
            return False
        finally:
            sesion.close()

    def OBTENER_ROLES(self) -> List:
        sesion = OBTENER_SESION()
        try:
            return sesion.query(MODELO_ROL).all()
        finally:
            sesion.close()
