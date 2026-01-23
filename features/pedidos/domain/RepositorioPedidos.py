from typing import Dict, Optional


class RepositorioPedidos:
    async def CREAR_PEDIDO(
        self, CLIENTE_ID: int, PRODUCTO_ID: int, CANTIDAD: int
    ) -> Dict:
        raise NotImplementedError()

    async def OBTENER_PEDIDOS_POR_CLIENTE(self, CLIENTE_ID: int):
        raise NotImplementedError()

    async def CONFIRMAR_PAGO_QR(self, PEDIDO_ID: int, MONTO: int, QR: str) -> bool:
        raise NotImplementedError()
