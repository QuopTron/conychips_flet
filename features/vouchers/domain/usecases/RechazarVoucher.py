
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
                return {"exito": True, "mensaje": mensaje}
            else:
                return {"exito": False, "mensaje": "Error al rechazar voucher"}
                
        except Exception as e:
            return {"exito": False, "mensaje": f"Error: {str(e)}"}
