
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import func

from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_VOUCHER
from ...domain.entities.Voucher import Voucher

class FuenteVouchersLocal:
    
    def obtener_por_estado(self, estado: str, limite: int = 50, offset: int = 0, sucursal_id: int | None = None) -> List[Voucher]:
        sesion = OBTENER_SESION()
        try:
            # Base de la query según estado
            if estado == "PENDIENTE":
                query = sesion.query(MODELO_VOUCHER).filter(
                    MODELO_VOUCHER.VALIDADO == False,
                    MODELO_VOUCHER.RECHAZADO == False
                )
            elif estado == "APROBADO":
                query = sesion.query(MODELO_VOUCHER).filter(MODELO_VOUCHER.VALIDADO == True)
            elif estado == "RECHAZADO":
                query = sesion.query(MODELO_VOUCHER).filter(MODELO_VOUCHER.RECHAZADO == True)
            else:
                return []

            # Si se especifica sucursal, unir con PEDIDOS y filtrar por SUCURSAL_ID
            if sucursal_id is not None:
                from core.base_datos.ConfiguracionBD import MODELO_PEDIDO
                query = query.join(MODELO_PEDIDO, MODELO_PEDIDO.ID == MODELO_VOUCHER.PEDIDO_ID).filter(
                    MODELO_PEDIDO.SUCURSAL_ID == sucursal_id
                )

            modelos = query.order_by(MODELO_VOUCHER.FECHA_SUBIDA.desc()).limit(limite).offset(offset).all()

            return [self._modelo_a_entidad(m) for m in modelos]
        finally:
            sesion.close()
    
    def obtener_por_id(self, voucher_id: int) -> Optional[Voucher]:
        sesion = OBTENER_SESION()
        try:
            modelo = sesion.query(MODELO_VOUCHER).filter_by(ID=voucher_id).first()
            
            if modelo:
                return self._modelo_a_entidad(modelo)
            return None
        finally:
            sesion.close()
    
    def contar_por_estado(self, estado: str) -> int:
        sesion = OBTENER_SESION()
        try:
            if estado == "PENDIENTE":
                return sesion.query(func.count(MODELO_VOUCHER.ID)).filter(
                    MODELO_VOUCHER.VALIDADO == False,
                    MODELO_VOUCHER.RECHAZADO == False
                ).scalar() or 0
            elif estado == "APROBADO":
                return sesion.query(func.count(MODELO_VOUCHER.ID)).filter(
                    MODELO_VOUCHER.VALIDADO == True
                ).scalar() or 0
            elif estado == "RECHAZADO":
                return sesion.query(func.count(MODELO_VOUCHER.ID)).filter(
                    MODELO_VOUCHER.RECHAZADO == True
                ).scalar() or 0
            else:
                return 0
        finally:
            sesion.close()
    
    def aprobar_voucher(self, voucher_id: int, validador_id: int) -> bool:
        sesion = OBTENER_SESION()
        try:
            modelo = sesion.query(MODELO_VOUCHER).filter_by(ID=voucher_id).first()
            
            if not modelo:
                return False
            
            modelo.VALIDADO = True
            modelo.RECHAZADO = False
            modelo.MOTIVO_RECHAZO = None
            modelo.VALIDADO_POR = validador_id
            modelo.FECHA_VALIDACION = datetime.now(timezone.utc)
            
            sesion.commit()
            # Notify realtime broker (non-blocking, errors ignored)
            try:
                from core.realtime.broker_notify import notify
                # attempt to include sucursal_id if available
                sucursal_id = None
                try:
                    from core.base_datos.ConfiguracionBD import MODELO_PEDIDO
                    pedido = sesion.query(MODELO_PEDIDO).filter_by(ID=modelo.PEDIDO_ID).first()
                    if pedido:
                        sucursal_id = getattr(pedido, 'SUCURSAL_ID', None)
                except Exception:
                    sucursal_id = None

                payload = {
                    'type': 'voucher_actualizado',
                    'voucher_id': voucher_id,
                    'nuevo_estado': 'APROBADO'
                }
                if sucursal_id is not None:
                    payload['sucursal_id'] = sucursal_id

                notify(payload)
            except Exception:
                pass
            return True
        except Exception as e:
            sesion.rollback()
            print(f"Error aprobando voucher: {e}")
            return False
        finally:
            sesion.close()
    
    def rechazar_voucher(self, voucher_id: int, validador_id: int, motivo: str = "") -> bool:
        sesion = OBTENER_SESION()
        try:
            modelo = sesion.query(MODELO_VOUCHER).filter_by(ID=voucher_id).first()
            
            if not modelo:
                return False
            
            modelo.RECHAZADO = True
            modelo.VALIDADO = False
            modelo.MOTIVO_RECHAZO = motivo
            modelo.VALIDADO_POR = validador_id
            modelo.FECHA_VALIDACION = datetime.now(timezone.utc)
            
            sesion.commit()
            # Notify realtime broker (non-blocking, errors ignored)
            try:
                from core.realtime.broker_notify import notify
                sucursal_id = None
                try:
                    from core.base_datos.ConfiguracionBD import MODELO_PEDIDO
                    pedido = sesion.query(MODELO_PEDIDO).filter_by(ID=modelo.PEDIDO_ID).first()
                    if pedido:
                        sucursal_id = getattr(pedido, 'SUCURSAL_ID', None)
                except Exception:
                    sucursal_id = None

                payload = {
                    'type': 'voucher_actualizado',
                    'voucher_id': voucher_id,
                    'nuevo_estado': 'RECHAZADO',
                    'motivo': motivo,
                }
                if sucursal_id is not None:
                    payload['sucursal_id'] = sucursal_id

                notify(payload)
            except Exception:
                pass
            return True
        except Exception as e:
            sesion.rollback()
            print(f"Error rechazando voucher: {e}")
            return False
        finally:
            sesion.close()
    
    def obtener_estadisticas(self) -> dict:
        sesion = OBTENER_SESION()
        try:
            total_pendientes = sesion.query(func.count(MODELO_VOUCHER.ID)).filter(
                MODELO_VOUCHER.VALIDADO == False,
                MODELO_VOUCHER.RECHAZADO == False
            ).scalar() or 0
            
            total_aprobados = sesion.query(func.count(MODELO_VOUCHER.ID)).filter(
                MODELO_VOUCHER.VALIDADO == True
            ).scalar() or 0
            
            total_rechazados = sesion.query(func.count(MODELO_VOUCHER.ID)).filter(
                MODELO_VOUCHER.RECHAZADO == True
            ).scalar() or 0
            
            monto_total_aprobado = sesion.query(func.coalesce(func.sum(MODELO_VOUCHER.MONTO), 0)).filter(
                MODELO_VOUCHER.VALIDADO == True
            ).scalar() or 0
            
            return {
                "pendientes": total_pendientes,
                "aprobados": total_aprobados,
                "rechazados": total_rechazados,
                "monto_total_aprobado": float(monto_total_aprobado),
                "total": total_pendientes + total_aprobados + total_rechazados,
            }
        finally:
            sesion.close()
    
    def _modelo_a_entidad(self, modelo) -> Voucher:
        rechazado = getattr(modelo, 'RECHAZADO', False)
        validado = getattr(modelo, 'VALIDADO', False)
        
        if rechazado:
            estado = "RECHAZADO"
        elif validado:
            estado = "APROBADO"
        else:
            estado = "PENDIENTE"
        
        fecha_subida = modelo.FECHA_SUBIDA
        if fecha_subida and fecha_subida.tzinfo is None:
            fecha_subida = fecha_subida.replace(tzinfo=timezone.utc)
        
        fecha_validacion = getattr(modelo, 'FECHA_VALIDACION', None)
        if fecha_validacion and fecha_validacion.tzinfo is None:
            fecha_validacion = fecha_validacion.replace(tzinfo=timezone.utc)
        
        return Voucher(
            id=modelo.ID,
            pedido_id=modelo.PEDIDO_ID,
            usuario_id=modelo.USUARIO_ID,
            imagen_url=modelo.IMAGEN_URL,
            monto=float(modelo.MONTO),
            metodo_pago=modelo.METODO_PAGO,
            estado=estado,
            fecha_subida=fecha_subida,
            validado=validado,
            rechazado=rechazado,
            motivo_rechazo=getattr(modelo, 'MOTIVO_RECHAZO', None),
            validado_por=getattr(modelo, 'VALIDADO_POR', None),
            fecha_validacion=fecha_validacion,
            codigo_operacion=None,
        )
