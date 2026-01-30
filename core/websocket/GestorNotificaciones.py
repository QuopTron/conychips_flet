import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Callable

from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION,
    MODELO_NOTIFICACION,
    MODELO_MENSAJE_CHAT,
    MODELO_UBICACION_MOTORIZADO,
)

class GestorNotificaciones:
    
    _INSTANCIA = None
    _CONEXIONES: Dict[int, List[Callable]] = {}
    _CALLBACKS_TIPO: Dict[str, List[Callable]] = {}
    
    
    def __new__(cls):
        if cls._INSTANCIA is None:
            cls._INSTANCIA = super().__new__(cls)
            cls._INSTANCIA._INICIALIZADO = False
        return cls._INSTANCIA
    
    
    def __init__(self):
        if self._INICIALIZADO:
            return
        
        self._CONEXIONES = {}
        self._CALLBACKS_TIPO = {
            "pedido": [],
            "pago": [],
            "entrega": [],
            "chat": [],
            "gps": [],
            "refill": [],
            "sistema": [],
        }
        self._INICIALIZADO = True
    
    
    def REGISTRAR_CONEXION(self, USUARIO_ID: int, CALLBACK: Callable):
        if USUARIO_ID not in self._CONEXIONES:
            self._CONEXIONES[USUARIO_ID] = []
        
        if CALLBACK not in self._CONEXIONES[USUARIO_ID]:
            self._CONEXIONES[USUARIO_ID].append(CALLBACK)
    
    
    def DESREGISTRAR_CONEXION(self, USUARIO_ID: int, CALLBACK: Callable):
        if USUARIO_ID in self._CONEXIONES:
            if CALLBACK in self._CONEXIONES[USUARIO_ID]:
                self._CONEXIONES[USUARIO_ID].remove(CALLBACK)
            
            if not self._CONEXIONES[USUARIO_ID]:
                del self._CONEXIONES[USUARIO_ID]
    
    
    def SUSCRIBIR_TIPO(self, TIPO: str, CALLBACK: Callable):
        if TIPO in self._CALLBACKS_TIPO:
            if CALLBACK not in self._CALLBACKS_TIPO[TIPO]:
                self._CALLBACKS_TIPO[TIPO].append(CALLBACK)
    
    
    async def ENVIAR_NOTIFICACION(
        self,
        USUARIO_ID: int,
        TITULO: str,
        MENSAJE: str,
        TIPO: str = "sistema",
        DATOS_EXTRA: Optional[dict] = None
    ):
        sesion = OBTENER_SESION()
        
        notificacion = MODELO_NOTIFICACION(
            USUARIO_ID=USUARIO_ID,
            TITULO=TITULO,
            MENSAJE=MENSAJE,
            TIPO=TIPO,
            DATOS_EXTRA=json.dumps(DATOS_EXTRA) if DATOS_EXTRA else None,
        )
        
        sesion.add(notificacion)
        sesion.commit()
        
        PAYLOAD = {
            "tipo": "notificacion",
            "subtipo": TIPO,
            "id": notificacion.ID,
            "usuario_id": USUARIO_ID,
            "titulo": TITULO,
            "mensaje": MENSAJE,
            "datos": DATOS_EXTRA,
            "fecha": datetime.now(timezone.utc).isoformat(),
        }
        
        sesion.close()
        
        # Broadcast to external WS broker (best-effort)
        try:
            from core.realtime.broker_notify import notify
            notify({'type': 'notificacion', 'notificacion_id': notificacion.ID, 'usuario_id': USUARIO_ID, 'titulo': TITULO, 'mensaje': MENSAJE, 'subtipo': TIPO})
        except Exception:
            pass

        await self._ENVIAR_A_USUARIO(USUARIO_ID, PAYLOAD)
        await self._EJECUTAR_CALLBACKS_TIPO(TIPO, PAYLOAD)
    
    
    async def ENVIAR_MENSAJE_CHAT(
        self,
        PEDIDO_ID: int,
        USUARIO_ID: int,
        MENSAJE: str,
        TIPO: str = "texto"
    ):
        sesion = OBTENER_SESION()
        
        mensaje_obj = MODELO_MENSAJE_CHAT(
            PEDIDO_ID=PEDIDO_ID,
            USUARIO_ID=USUARIO_ID,
            MENSAJE=MENSAJE,
            TIPO=TIPO,
        )
        
        sesion.add(mensaje_obj)
        sesion.commit()
        
        PAYLOAD = {
            "tipo": "chat",
            "id": mensaje_obj.ID,
            "pedido_id": PEDIDO_ID,
            "usuario_id": USUARIO_ID,
            "mensaje": MENSAJE,
            "tipo_mensaje": TIPO,
            "fecha": datetime.now(timezone.utc).isoformat(),
        }
        
        sesion.close()
        # Broadcast chat message to external broker
        try:
            from core.realtime.broker_notify import notify
            notify({'type': 'chat', 'mensaje_id': mensaje_obj.ID, 'pedido_id': PEDIDO_ID, 'usuario_id': USUARIO_ID, 'mensaje': MENSAJE})
        except Exception:
            pass

        await self._BROADCAST_PEDIDO(PEDIDO_ID, PAYLOAD)
    
    
    async def ACTUALIZAR_GPS(
        self,
        USUARIO_ID: int,
        PEDIDO_ID: int,
        LATITUD: str,
        LONGITUD: str,
        ESTADO: str
    ):
        sesion = OBTENER_SESION()
        
        ubicacion = MODELO_UBICACION_MOTORIZADO(
            USUARIO_ID=USUARIO_ID,
            PEDIDO_ID=PEDIDO_ID,
            LATITUD=LATITUD,
            LONGITUD=LONGITUD,
            ESTADO=ESTADO,
        )
        
        sesion.add(ubicacion)
        sesion.commit()
        
        PAYLOAD = {
            "tipo": "gps",
            "usuario_id": USUARIO_ID,
            "pedido_id": PEDIDO_ID,
            "latitud": LATITUD,
            "longitud": LONGITUD,
            "estado": ESTADO,
            "fecha": datetime.now(timezone.utc).isoformat(),
        }
        
        sesion.close()
        try:
            from core.realtime.broker_notify import notify
            notify({'type': 'gps', 'usuario_id': USUARIO_ID, 'pedido_id': PEDIDO_ID, 'latitud': LATITUD, 'longitud': LONGITUD, 'estado': ESTADO})
        except Exception:
            pass

        await self._BROADCAST_PEDIDO(PEDIDO_ID, PAYLOAD)
    
    
    async def NOTIFICAR_CAMBIO_ESTADO_PEDIDO(
        self,
        PEDIDO_ID: int,
        NUEVO_ESTADO: str,
        USUARIO_AFECTADO: int
    ):
        MENSAJES_ESTADO = {
            "pendiente": "Tu pedido está pendiente de confirmación",
            "confirmado": "¡Tu pedido ha sido confirmado!",
            "en_preparacion": "Tu pedido está siendo preparado",
            "listo": "¡Tu pedido está listo!",
            "en_camino": "Tu pedido está en camino",
            "entregado": "Tu pedido ha sido entregado",
            "cancelado": "Tu pedido ha sido cancelado",
        }
        
        await self.ENVIAR_NOTIFICACION(
            USUARIO_ID=USUARIO_AFECTADO,
            TITULO="Estado de Pedido",
            MENSAJE=MENSAJES_ESTADO.get(NUEVO_ESTADO, f"Estado actualizado: {NUEVO_ESTADO}"),
            TIPO="pedido",
            DATOS_EXTRA={"pedido_id": PEDIDO_ID, "estado": NUEVO_ESTADO}
        )
    
    
    async def NOTIFICAR_REFILL_SOLICITADO(
        self,
        INSUMO_NOMBRE: str,
        CANTIDAD: int,
        USUARIOS_ADMIN: List[int]
    ):
        for USUARIO_ID in USUARIOS_ADMIN:
            await self.ENVIAR_NOTIFICACION(
                USUARIO_ID=USUARIO_ID,
                TITULO="Solicitud de Refill",
                MENSAJE=f"Se solicitó refill de {INSUMO_NOMBRE} ({CANTIDAD} unidades)",
                TIPO="refill",
                DATOS_EXTRA={"insumo": INSUMO_NOMBRE, "cantidad": CANTIDAD}
            )
    
    
    async def _ENVIAR_A_USUARIO(self, USUARIO_ID: int, PAYLOAD: dict):
        if USUARIO_ID in self._CONEXIONES:
            for callback in self._CONEXIONES[USUARIO_ID]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(PAYLOAD)
                    else:
                        callback(PAYLOAD)
                except Exception as e:
                    print(f"Error enviando a usuario {USUARIO_ID}: {e}")
    
    
    async def _BROADCAST_PEDIDO(self, PEDIDO_ID: int, PAYLOAD: dict):
        from core.base_datos.ConfiguracionBD import MODELO_PEDIDO
        
        sesion = OBTENER_SESION()
        pedido = sesion.query(MODELO_PEDIDO).filter_by(ID=PEDIDO_ID).first()
        
        if pedido:
            USUARIOS_NOTIFICAR = [pedido.CLIENTE_ID]
            
            if hasattr(pedido, 'MOTORIZADO_ID') and pedido.MOTORIZADO_ID:
                USUARIOS_NOTIFICAR.append(pedido.MOTORIZADO_ID)
        
        sesion.close()
        
        for USUARIO_ID in USUARIOS_NOTIFICAR:
            await self._ENVIAR_A_USUARIO(USUARIO_ID, PAYLOAD)
    
    
    async def _EJECUTAR_CALLBACKS_TIPO(self, TIPO: str, PAYLOAD: dict):
        if TIPO in self._CALLBACKS_TIPO:
            for callback in self._CALLBACKS_TIPO[TIPO]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(PAYLOAD)
                    else:
                        callback(PAYLOAD)
                except Exception as e:
                    print(f"Error ejecutando callback tipo {TIPO}: {e}")
    
    
    def OBTENER_NOTIFICACIONES_NO_LEIDAS(self, USUARIO_ID: int) -> List[dict]:
        sesion = OBTENER_SESION()
        
        notificaciones = (
            sesion.query(MODELO_NOTIFICACION)
            .filter_by(USUARIO_ID=USUARIO_ID, LEIDA=False)
            .order_by(MODELO_NOTIFICACION.FECHA.desc())
            .all()
        )
        
        resultado = []
        for n in notificaciones:
            resultado.append({
                "id": n.ID,
                "titulo": n.TITULO,
                "mensaje": n.MENSAJE,
                "tipo": n.TIPO,
                "datos": json.loads(n.DATOS_EXTRA) if n.DATOS_EXTRA else None,
                "fecha": n.FECHA.isoformat(),
            })
        
        sesion.close()
        return resultado
    
    
    def MARCAR_LEIDA(self, NOTIFICACION_ID: int):
        sesion = OBTENER_SESION()
        
        notificacion = sesion.query(MODELO_NOTIFICACION).filter_by(ID=NOTIFICACION_ID).first()
        if notificacion:
            notificacion.LEIDA = True
            sesion.commit()
        
        sesion.close()
