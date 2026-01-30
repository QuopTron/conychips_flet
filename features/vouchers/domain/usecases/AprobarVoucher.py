
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
                return {"exito": True, "mensaje": mensaje}
            else:
                return {"exito": False, "mensaje": "Error al aprobar voucher"}
                
        except Exception as e:
            return {"exito": False, "mensaje": f"Error: {str(e)}"}
