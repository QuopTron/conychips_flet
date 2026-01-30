import asyncio
import websockets
import threading
import json
from typing import Any

async def _handler(websocket: websockets.WebSocketServerProtocol):
    # websockets library may call handler with single 'websocket' argument
    path = getattr(websocket, 'path', '')
    try:
        async for message in websocket:
            # Intentar parsear y responder con ack
            try:
                data = json.loads(message)
                tipo = data.get("tipo", "desconocido")
            except Exception:
                tipo = "raw"

            resp = {"tipo": "ack", "original": tipo, "path": path}
            await websocket.send(json.dumps(resp))
    except websockets.exceptions.ConnectionClosed:
        return

def iniciar_servidor_local(host: str = "localhost", port: int = 8765):
    """Inicia un servidor WebSocket simple en un hilo separado (solo para desarrollo)."""

    async def _start():
        async with websockets.serve(_handler, host, port):
            print(f"Servidor WebSocket local en ws://{host}:{port}")
            await asyncio.Future()  # run forever

    def _run_loop():
        try:
            asyncio.run(_start())
        except Exception as e:
            print(f"Error iniciando servidor WebSocket local: {e}")

    t = threading.Thread(target=_run_loop, daemon=True, name="WS-Server-Local")
    t.start()
    return t
