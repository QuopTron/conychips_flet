from typing import Dict, List
import asyncio
from features.pedidos.domain.RepositorioPedidos import RepositorioPedidos
from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION,
    MODELO_PEDIDO,
    MODELO_PRODUCTO,
    MODELO_USUARIO,
)
from core.websocket.ManejadorConexion import ManejadorConexion

class RepositorioPedidosImpl(RepositorioPedidos):
    def __init__(self):
        self._MANJADOR = ManejadorConexion()

    async def CREAR_PEDIDO(
        self,
        CLIENTE_ID: int,
        PRODUCTO_ID: int,
        CANTIDAD: int,
        SUCURSAL_ID: int = None,
        EXTRAS: List[str] = None,
    ) -> Dict:
        sesion = OBTENER_SESION()
        producto = (
            sesion.query(MODELO_PRODUCTO)
            .filter_by(ID=PRODUCTO_ID, DISPONIBLE=True)
            .first()
        )
        if not producto:
            return {"EXITO": False, "ERROR": "Producto no disponible"}

        from core.base_datos.ConfiguracionBD import MODELO_DETALLE_PEDIDO

        pedido = MODELO_PEDIDO(
            CLIENTE_ID=CLIENTE_ID,
            SUCURSAL_ID=SUCURSAL_ID,
            TIPO="delivery",
            ESTADO="pendiente",
            MONTO_TOTAL=producto.PRECIO * CANTIDAD,
        )
        sesion.add(pedido)
        sesion.commit()

        # Fire-and-forget: notify local websocket clients immediately (low-latency)
        try:
            asyncio.create_task(
                self._MANJADOR.BROADCAST(
                    {
                        "tipo": "nuevo_pedido:created",
                        "pedido_id": pedido.ID,
                        "estado": pedido.ESTADO,
                        "paso": "pedido_creado",
                    }
                )
            )
        except Exception:
            # best-effort: don't block the flow if broadcasting fails
            pass

        detalle = MODELO_DETALLE_PEDIDO(
            PEDIDO_ID=pedido.ID,
            PRODUCTO_ID=PRODUCTO_ID,
            CANTIDAD=CANTIDAD,
            PRECIO_UNITARIO=producto.PRECIO,
            EXTRAS_SELECCIONADOS=",".join(EXTRAS) if EXTRAS else None,
        )
        sesion.add(detalle)
        sesion.commit()

        # Broadcast a progress update (detalle agregado) without awaiting
        try:
            asyncio.create_task(
                self._MANJADOR.BROADCAST(
                    {
                        "tipo": "nuevo_pedido:detalle_agregado",
                        "pedido_id": pedido.ID,
                        "detalle_id": getattr(detalle, 'ID', None),
                        "producto": getattr(producto, 'NOMBRE', None),
                        "cantidad": CANTIDAD,
                        "estado": pedido.ESTADO,
                        "paso": "detalle_agregado",
                    }
                )
            )
        except Exception:
            pass

        # Notify external realtime broker in executor to avoid blocking
        try:
            from core.realtime.broker_notify import notify

            payload = {
                'type': 'pedido_creado',
                'pedido_id': pedido.ID,
                'cliente_id': CLIENTE_ID,
                'sucursal_id': SUCURSAL_ID,
                'nuevo_estado': pedido.ESTADO,
                'progreso': '100%',
            }

            loop = asyncio.get_running_loop()
            loop.run_in_executor(None, notify, payload)
        except Exception:
            pass

        return {"EXITO": True, "PEDIDO_ID": pedido.ID}

    async def OBTENER_PEDIDOS_POR_CLIENTE(self, CLIENTE_ID: int) -> List[Dict]:
        sesion = OBTENER_SESION()
        pedidos = (
            sesion.query(MODELO_PEDIDO)
            .filter_by(CLIENTE_ID=CLIENTE_ID)
            .order_by(MODELO_PEDIDO.FECHA_CREACION.desc())
            .all()
        )
        salida = []
        for p in pedidos:
            salida.append(
                {
                    "ID": p.ID,
                    "PRODUCTO_ID": p.PRODUCTO_ID,
                    "CANTIDAD": p.CANTIDAD,
                    "ESTADO": p.ESTADO,
                    "MONTO_PAGADO": p.MONTO_PAGADO,
                    "QR_PAGO": p.QR_PAGO,
                    "FECHA_CREACION": p.FECHA_CREACION,
                }
            )
        return salida

    async def CONFIRMAR_PAGO_QR(self, PEDIDO_ID: int, MONTO: int, QR: str) -> bool:
        sesion = OBTENER_SESION()
        pedido = sesion.query(MODELO_PEDIDO).filter_by(ID=PEDIDO_ID).first()
        if not pedido:
            return False
        pedido.MONTO_PAGADO = MONTO
        pedido.QR_PAGO = QR
        pedido.ESTADO = "pagado"
        sesion.commit()

        # Broadcast payment event quickly (do not block)
        try:
            asyncio.create_task(
                self._MANJADOR.BROADCAST(
                    {"tipo": "pedido_pagado", "pedido_id": PEDIDO_ID, "monto": MONTO, "paso": "pagado"}
                )
            )
        except Exception:
            pass

        # External notify in executor (best-effort, non-blocking)
        try:
            from core.realtime.broker_notify import notify

            payload = {
                'type': 'pedido_actualizado',
                'pedido_id': PEDIDO_ID,
                'nuevo_estado': pedido.ESTADO,
                'monto': MONTO,
                'sucursal_id': getattr(pedido, 'SUCURSAL_ID', None),
                'paso': 'pagado',
            }
            loop = asyncio.get_running_loop()
            loop.run_in_executor(None, notify, payload)
        except Exception:
            pass

        return True
