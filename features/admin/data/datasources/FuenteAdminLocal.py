"""
Fuente de Datos Local para Admin
Data Layer - Clean Architecture
Acceso directo a la base de datos
"""

from datetime import datetime, timedelta
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


class FuenteAdminLocal:
    """
    Fuente de datos local para operaciones de administración
    Accede a la base de datos PostgreSQL
    """

    def OBTENER_TOTAL_USUARIOS(self) -> int:
        """Cuenta total de usuarios en el sistema"""
        sesion = OBTENER_SESION()
        try:
            return sesion.query(MODELO_USUARIO).count()
        finally:
            sesion.close()

    def OBTENER_TOTAL_PRODUCTOS(self) -> int:
        """Cuenta total de productos"""
        sesion = OBTENER_SESION()
        try:
            return sesion.query(MODELO_PRODUCTO).count()
        finally:
            sesion.close()

    def OBTENER_PEDIDOS_HOY(self) -> int:
        """Cuenta pedidos de hoy"""
        sesion = OBTENER_SESION()
        try:
            hoy = datetime.utcnow().date()
            return (
                sesion.query(MODELO_PEDIDO)
                .filter(MODELO_PEDIDO.FECHA_CREACION >= hoy)
                .count()
            )
        finally:
            sesion.close()

    def OBTENER_GANANCIAS_HOY(self) -> float:
        """Calcula ganancias del día"""
        sesion = OBTENER_SESION()
        try:
            hoy = datetime.utcnow().date()
            cajas_hoy = (
                sesion.query(MODELO_CAJA)
                .filter(MODELO_CAJA.FECHA_APERTURA >= hoy)
                .all()
            )
            return sum(c.GANANCIAS or 0 for c in cajas_hoy)
        finally:
            sesion.close()

    def OBTENER_ROLES_CON_USUARIOS(self) -> List:
        """Obtiene roles con sus usuarios"""
        sesion = OBTENER_SESION()
        try:
            return sesion.query(MODELO_ROL).all()
        finally:
            sesion.close()

    def OBTENER_SUCURSALES_CON_PEDIDOS(self) -> List:
        """Obtiene sucursales con conteo de pedidos"""
        sesion = OBTENER_SESION()
        try:
            return sesion.query(MODELO_SUCURSAL).all()
        finally:
            sesion.close()

    def CONTAR_PEDIDOS_POR_SUCURSAL(self, sucursal_id: int) -> int:
        """Cuenta pedidos de una sucursal"""
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
        """Cuenta pedidos de un día específico"""
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
        """Cuenta total de insumos"""
        sesion = OBTENER_SESION()
        try:
            return sesion.query(MODELO_INSUMO).count()
        finally:
            sesion.close()

    def OBTENER_TOTAL_PROVEEDORES(self) -> int:
        """Cuenta total de proveedores"""
        sesion = OBTENER_SESION()
        try:
            return sesion.query(MODELO_PROVEEDOR).count()
        finally:
            sesion.close()

    def OBTENER_OFERTAS_ACTIVAS(self) -> int:
        """Cuenta ofertas activas"""
        sesion = OBTENER_SESION()
        try:
            return sesion.query(MODELO_OFERTA).filter_by(ACTIVA=True).count()
        finally:
            sesion.close()

    def OBTENER_TOTAL_EXTRAS(self) -> int:
        """Cuenta total de extras"""
        sesion = OBTENER_SESION()
        try:
            return sesion.query(MODELO_EXTRA).count()
        finally:
            sesion.close()

    def ACTUALIZAR_ROL_USUARIO(self, usuario_id: int, nombre_rol: str) -> bool:
        """Actualiza el rol de un usuario"""
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
        """Obtiene todos los roles"""
        sesion = OBTENER_SESION()
        try:
            return sesion.query(MODELO_ROL).all()
        finally:
            sesion.close()
