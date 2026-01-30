import asyncio
import websockets
import json
import os
from typing import Optional, Callable, List
from core.Constantes import WS_INTENTOS_RECONEXION, WS_TIMEOUT

class ClienteWebSocket:

    def __init__(self, URL: str, TOKEN_ACCESS: str):

        self._URL = URL
        self._TOKEN = TOKEN_ACCESS
        self._WEBSOCKET: Optional[websockets.WebSocketClientProtocol] = None
        self._CONECTADO = False
        self._INTENTOS_RECONEXION = 0
        self._CALLBACK_MENSAJE: Optional[Callable] = None
        self._CALLBACK_ERROR: Optional[Callable] = None
        self._TAREA_ESCUCHA: Optional[asyncio.Task] = None
        self._COLA_PENDIENTE: List[dict] = []
        self._RUTA_CACHE = self._OBTENER_RUTA_CACHE()
        self._CARGAR_CACHE()

    async def CONECTAR(self) -> bool:

        try:
            print(f" Conectando a WebSocket: {self._URL}")

            HEADERS_EXTRA = {"Authorization": f"Bearer {self._TOKEN}"}
            try:
                self._WEBSOCKET = await asyncio.wait_for(
                    websockets.connect(
                        self._URL,
                        extra_headers=HEADERS_EXTRA,
                        ping_interval=20,
                        ping_timeout=10,
                    ),
                    timeout=WS_TIMEOUT,
                )
            except TypeError as te:
                try:
                    url_con_token = f"{self._URL.rstrip('/')}?token={self._TOKEN}"
                    self._WEBSOCKET = await asyncio.wait_for(
                        websockets.connect(
                            url_con_token, ping_interval=20, ping_timeout=10
                        ),
                        timeout=WS_TIMEOUT,
                    )
                except Exception as e:
                    raise e

            self._CONECTADO = True
            self._INTENTOS_RECONEXION = 0

            print(" WebSocket conectado exitosamente")

            self._TAREA_ESCUCHA = asyncio.create_task(self._ESCUCHAR_MENSAJES())
            await self._ENVIAR_PENDIENTES()

            return True

        except asyncio.TimeoutError:
            print(" Timeout al conectar WebSocket")
            return False
        except Exception as ERROR:
            print(f" Error al conectar WebSocket: {ERROR}")
            return False

    async def _ESCUCHAR_MENSAJES(self):

        try:
            while self._CONECTADO and self._WEBSOCKET:
                try:
                    MENSAJE_RAW = await asyncio.wait_for(
                        self._WEBSOCKET.recv(), timeout=WS_TIMEOUT
                    )

                    MENSAJE = json.loads(MENSAJE_RAW)

                    print(f" Mensaje recibido: {MENSAJE.get('tipo', 'desconocido')}")

                    if self._CALLBACK_MENSAJE:
                        await self._CALLBACK_MENSAJE(MENSAJE)

                except asyncio.TimeoutError:
                    continue
                except websockets.exceptions.ConnectionClosed:
                    print(" Conexión WebSocket cerrada")
                    await self._INTENTAR_RECONECTAR()
                    break
                except json.JSONDecodeError:
                    print("Error al decodificar mensaje JSON")
                except Exception as ERROR:
                    print(f"Error al recibir mensaje: {ERROR}")

        except Exception as ERROR:
            print(f"Error en tarea de escucha: {ERROR}")
            if self._CALLBACK_ERROR:
                await self._CALLBACK_ERROR(ERROR)

    async def _INTENTAR_RECONECTAR(self):

        while self._INTENTOS_RECONEXION < WS_INTENTOS_RECONEXION:
            self._INTENTOS_RECONEXION += 1
            ESPERA = min(2**self._INTENTOS_RECONEXION, 60)

            print(
                f"Reintentando conexión ({self._INTENTOS_RECONEXION}/{WS_INTENTOS_RECONEXION}) en {ESPERA}s..."
            )

            await asyncio.sleep(ESPERA)

            if await self.CONECTAR():
                return

        print("No se pudo reconectar después de múltiples intentos")
        self._CONECTADO = False

    async def ENVIAR(self, MENSAJE: dict) -> bool:

        if not self._CONECTADO or not self._WEBSOCKET:
            self._COLA_PENDIENTE.append(MENSAJE)
            self._GUARDAR_CACHE()
            return False

        try:
            MENSAJE_JSON = json.dumps(MENSAJE)
            await self._WEBSOCKET.send(MENSAJE_JSON)
            print(f"Mensaje enviado: {MENSAJE.get('tipo', 'desconocido')}")
            return True

        except Exception as ERROR:
            print(f"Error al enviar mensaje: {ERROR}")
            return False

    async def _ENVIAR_PENDIENTES(self):
        if not self._COLA_PENDIENTE:
            return

        pendientes = list(self._COLA_PENDIENTE)
        self._COLA_PENDIENTE.clear()
        self._GUARDAR_CACHE()

        for mensaje in pendientes:
            await self.ENVIAR(mensaje)

    def _OBTENER_RUTA_CACHE(self) -> str:
        base = os.path.expanduser("~/.app_segura")
        os.makedirs(base, exist_ok=True)
        return os.path.join(base, "ws_cache.json")

    def _CARGAR_CACHE(self):
        if not os.path.exists(self._RUTA_CACHE):
            return
        try:
            with open(self._RUTA_CACHE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    self._COLA_PENDIENTE.extend(data)
        except Exception:
            self._COLA_PENDIENTE = []

    def _GUARDAR_CACHE(self):
        try:
            with open(self._RUTA_CACHE, "w", encoding="utf-8") as f:
                json.dump(self._COLA_PENDIENTE, f)
        except Exception:
            pass

    def REGISTRAR_CALLBACK_MENSAJE(self, CALLBACK: Callable):

        self._CALLBACK_MENSAJE = CALLBACK

    def REGISTRAR_CALLBACK_ERROR(self, CALLBACK: Callable):

        self._CALLBACK_ERROR = CALLBACK

    async def DESCONECTAR(self):

        print(" Desconectando WebSocket...")

        self._CONECTADO = False

        if self._TAREA_ESCUCHA:
            self._TAREA_ESCUCHA.cancel()

        if self._WEBSOCKET:
            await self._WEBSOCKET.close()
            self._WEBSOCKET = None

        print("WebSocket desconectado")

    @property
    def ESTA_CONECTADO(self) -> bool:

        return self._CONECTADO
