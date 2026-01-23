"""
CLIENTE WEBSOCKET
=================
Gestiona conexión WebSocket segura con reconexión automática
"""

import asyncio
import websockets
import json
from typing import Optional, Callable
from datetime import datetime
from core.Constantes import WS_INTENTOS_RECONEXION, WS_TIMEOUT


class ClienteWebSocket:
    """Cliente WebSocket con autenticación JWT y reconexión automática"""
    
    def __init__(self, URL: str, TOKEN_ACCESS: str):
        """
        Inicializa cliente WebSocket
        
        Args:
            URL: URL del servidor WebSocket (ws:// o wss://)
            TOKEN_ACCESS: Token JWT para autenticación
        """
        self._URL = URL
        self._TOKEN = TOKEN_ACCESS
        self._WEBSOCKET: Optional[websockets.WebSocketClientProtocol] = None
        self._CONECTADO = False
        self._INTENTOS_RECONEXION = 0
        self._CALLBACK_MENSAJE: Optional[Callable] = None
        self._CALLBACK_ERROR: Optional[Callable] = None
        self._TAREA_ESCUCHA: Optional[asyncio.Task] = None
    
    async def CONECTAR(self) -> bool:
        """
        Establece conexión WebSocket con autenticación
        
        Flujo:
        1. Conecta al servidor WebSocket
        2. Envía token JWT para autenticación
        3. Espera confirmación del servidor
        4. Inicia tarea de escucha de mensajes
        
        Returns:
            True si conectó exitosamente, False si no
        """
        try:
            print(f"🔌 Conectando a WebSocket: {self._URL}")
            
            # Headers con token JWT
            HEADERS_EXTRA = {
                "Authorization": f"Bearer {self._TOKEN}"
            }
            
            # Conectar con timeout
            self._WEBSOCKET = await asyncio.wait_for(
                websockets.connect(
                    self._URL,
                    extra_headers=HEADERS_EXTRA,
                    ping_interval=20,
                    ping_timeout=10
                ),
                timeout=WS_TIMEOUT
            )
            
            self._CONECTADO = True
            self._INTENTOS_RECONEXION = 0
            
            print("✅ WebSocket conectado exitosamente")
            
            # Iniciar tarea de escucha
            self._TAREA_ESCUCHA = asyncio.create_task(self._ESCUCHAR_MENSAJES())
            
            return True
            
        except asyncio.TimeoutError:
            print("❌ Timeout al conectar WebSocket")
            return False
        except Exception as ERROR:
            print(f"❌ Error al conectar WebSocket: {ERROR}")
            return False
    
    async def _ESCUCHAR_MENSAJES(self):
        """Tarea que escucha mensajes entrantes del servidor"""
        try:
            while self._CONECTADO and self._WEBSOCKET:
                try:
                    # Recibir mensaje
                    MENSAJE_RAW = await asyncio.wait_for(
                        self._WEBSOCKET.recv(),
                        timeout=WS_TIMEOUT
                    )
                    
                    # Parsear JSON
                    MENSAJE = json.loads(MENSAJE_RAW)
                    
                    print(f"📨 Mensaje recibido: {MENSAJE.get('tipo', 'desconocido')}")
                    
                    # Llamar callback si existe
                    if self._CALLBACK_MENSAJE:
                        await self._CALLBACK_MENSAJE(MENSAJE)
                    
                except asyncio.TimeoutError:
                    continue
                except websockets.exceptions.ConnectionClosed:
                    print("⚠️ Conexión WebSocket cerrada")
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
        """Intenta reconectar con backoff exponencial"""
        while self._INTENTOS_RECONEXION < WS_INTENTOS_RECONEXION:
            self._INTENTOS_RECONEXION += 1
            ESPERA = min(2 ** self._INTENTOS_RECONEXION, 60)
            
            print(f"Reintentando conexión ({self._INTENTOS_RECONEXION}/{WS_INTENTOS_RECONEXION}) en {ESPERA}s...")
            
            await asyncio.sleep(ESPERA)
            
            if await self.CONECTAR():
                return
        
        print("No se pudo reconectar después de múltiples intentos")
        self._CONECTADO = False
    
    async def ENVIAR(self, MENSAJE: dict) -> bool:
        """
        Envía mensaje al servidor
        
        Args:
            MENSAJE: Diccionario a enviar (se convierte a JSON)
            
        Returns:
            True si se envió exitosamente, False si no
        """
        if not self._CONECTADO or not self._WEBSOCKET:
            print("No hay conexión WebSocket activa")
            return False
        
        try:
            MENSAJE_JSON = json.dumps(MENSAJE)
            await self._WEBSOCKET.send(MENSAJE_JSON)
            print(f"Mensaje enviado: {MENSAJE.get('tipo', 'desconocido')}")
            return True
            
        except Exception as ERROR:
            print(f"Error al enviar mensaje: {ERROR}")
            return False
    
    def REGISTRAR_CALLBACK_MENSAJE(self, CALLBACK: Callable):
        """Registra función callback para mensajes entrantes"""
        self._CALLBACK_MENSAJE = CALLBACK
    
    def REGISTRAR_CALLBACK_ERROR(self, CALLBACK: Callable):
        """Registra función callback para errores"""
        self._CALLBACK_ERROR = CALLBACK
    
    async def DESCONECTAR(self):
        """Cierra conexión WebSocket limpiamente"""
        print("🔌 Desconectando WebSocket...")
        
        self._CONECTADO = False
        
        if self._TAREA_ESCUCHA:
            self._TAREA_ESCUCHA.cancel()
        
        if self._WEBSOCKET:
            await self._WEBSOCKET.close()
            self._WEBSOCKET = None
        
        print("WebSocket desconectado")
    
    @property
    def ESTA_CONECTADO(self) -> bool:
        """Indica si el WebSocket está conectado"""
        return self._CONECTADO