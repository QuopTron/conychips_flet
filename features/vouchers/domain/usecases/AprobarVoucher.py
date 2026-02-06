
from ..RepositorioVouchers import RepositorioVouchers

class AprobarVoucher:
    
    def __init__(self, repositorio: RepositorioVouchers):
        self._repositorio = repositorio
    
    def ejecutar(self, voucher_id: int, validador_id: int) -> dict:
        try:
            voucher = self._repositorio.obtener_por_id(voucher_id)
            
            if not voucher:
                return {"exito": False, "mensaje": "Voucher no encontrado"}
            
            exito = self._repositorio.aprobar_voucher(voucher_id, validador_id)
            
            if exito:
                estado_anterior = voucher.estado
                mensaje = "Voucher aprobado correctamente"
                if estado_anterior == "RECHAZADO":
                    mensaje = "Voucher aprobado (revertido desde rechazado)"
                
                # Emitir evento WebSocket para notificar aprobación en tiempo real
                try:
                    from core.realtime.broker_notify import notify
                    from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_EVENTO_REALTIME
                    import json
                    from datetime import datetime, timezone
                    
                    payload = {
                        "tipo": "voucher_aprobado",
                        "voucher_id": voucher_id,
                        "validador_id": validador_id,
                        "pedido_id": voucher.pedido_id,
                        "usuario_id": voucher.usuario_id,
                        "fecha": datetime.now(timezone.utc).isoformat()
                    }
                    
                    # Guardar evento en BD para auditoría
                    sesion = OBTENER_SESION()
                    evento_rt = MODELO_EVENTO_REALTIME(
                        TIPO="voucher_aprobado",
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
                return {"exito": False, "mensaje": "Error al aprobar voucher"}
                
        except Exception as e:
            return {"exito": False, "mensaje": f"Error: {str(e)}"}
