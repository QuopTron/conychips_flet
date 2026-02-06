
from ..RepositorioVouchers import RepositorioVouchers

class RechazarVoucher:
    
    def __init__(self, repositorio: RepositorioVouchers):
        self._repositorio = repositorio
    
    def ejecutar(self, voucher_id: int, validador_id: int, motivo: str = "") -> dict:
        try:
            if not motivo or len(motivo.strip()) < 10:
                return {"exito": False, "mensaje": "El motivo debe tener al menos 10 caracteres"}
            
            voucher = self._repositorio.obtener_por_id(voucher_id)
            if not voucher:
                return {"exito": False, "mensaje": "Voucher no encontrado"}
            
            exito = self._repositorio.rechazar_voucher(voucher_id, validador_id, motivo)
            
            if exito:
                estado_anterior = voucher.estado
                mensaje = "Voucher rechazado"
                if estado_anterior == "APROBADO":
                    mensaje = "Voucher rechazado (revertido desde aprobado)"
                
                # Emitir evento WebSocket para notificar rechazo en tiempo real
                try:
                    from core.realtime.broker_notify import notify
                    from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_EVENTO_REALTIME
                    import json
                    from datetime import datetime, timezone
                    
                    payload = {
                        "tipo": "voucher_rechazado",
                        "voucher_id": voucher_id,
                        "validador_id": validador_id,
                        "motivo": motivo,
                        "pedido_id": voucher.pedido_id,
                        "usuario_id": voucher.usuario_id,
                        "fecha": datetime.now(timezone.utc).isoformat()
                    }
                    
                    # Guardar evento en BD para auditoría
                    sesion = OBTENER_SESION()
                    evento_rt = MODELO_EVENTO_REALTIME(
                        TIPO="voucher_rechazado",
                        PAYLOAD=json.dumps(payload),
                        USUARIO_ID=validador_id,
                        ENTIDAD_TIPO="VOUCHER",
                        ENTIDAD_ID=voucher_id
                    )
                    sesion.add(evento_rt)
                    sesion.commit()
                    sesion.close()
                    
                    # Broadcast via WebSocket
                    notify(payload)
                except Exception:
                    pass  # No fallar si el broker no está disponible
                
                return {"exito": True, "mensaje": mensaje}
            else:
                return {"exito": False, "mensaje": "Error al rechazar voucher"}
                
        except Exception as e:
            return {"exito": False, "mensaje": f"Error: {str(e)}"}
