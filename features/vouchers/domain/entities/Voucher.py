
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

@dataclass
class Voucher:
    id: int
    pedido_id: Optional[int] = None
    usuario_id: Optional[int] = None
    imagen_url: Optional[str] = None
    monto: float = 0.0
    metodo_pago: Optional[str] = None
    banco_emisor: Optional[str] = None
    referencia: Optional[str] = None
    estado: str = "PENDIENTE"
    fecha_subida: Optional[datetime] = None
    validado: bool = False
    rechazado: bool = False
    motivo_rechazo: Optional[str] = None
    validado_por: Optional[int] = None
    fecha_validacion: Optional[datetime] = None
    codigo_operacion: Optional[str] = None
    
    def es_pendiente(self) -> bool:
        return self.estado == "PENDIENTE"
    
    def es_aprobado(self) -> bool:
        return self.estado == "APROBADO"
    
    def es_rechazado(self) -> bool:
        return self.estado == "RECHAZADO"
    
    def puede_ser_validado(self) -> bool:
        return True
    
    def aprobar(self, validador_id: int):
        self.estado = "APROBADO"
        self.validado = True
        self.rechazado = False
        self.motivo_rechazo = None
        self.validado_por = validador_id
        self.fecha_validacion = datetime.now(timezone.utc)
    
    def rechazar(self, validador_id: int, motivo: str = ""):
        self.estado = "RECHAZADO"
        self.validado = False
        self.rechazado = True
        self.motivo_rechazo = motivo
        self.validado_por = validador_id
        self.fecha_validacion = datetime.now(timezone.utc)
