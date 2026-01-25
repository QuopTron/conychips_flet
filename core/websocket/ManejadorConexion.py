from typing import Dict, Optional
from core.websocket.ClienteWebSocket import ClienteWebSocket


class ManejadorConexion:

    _INSTANCIA: Optional["ManejadorConexion"] = None

    def __new__(cls):
        if cls._INSTANCIA is None:
            cls._INSTANCIA = super().__new__(cls)
            cls._INSTANCIA._INICIALIZAR()
        return cls._INSTANCIA

    def _INICIALIZAR(self):

        self._CONEXIONES: Dict[str, ClienteWebSocket] = {}
        self._URL_SERVIDOR: Optional[str] = None

    def CONFIGURAR_SERVIDOR(self, URL: str):

        self._URL_SERVIDOR = URL
        print(f" Servidor WebSocket configurado: {URL}")

    async def CREAR_CONEXION(
        self, USUARIO_ID: int, TOKEN: str
    ) -> Optional[ClienteWebSocket]:

        if not self._URL_SERVIDOR:
            print(" Servidor WebSocket no configurado")
            return None

        CLAVE_CONEXION = f"usuario_{USUARIO_ID}"

        if CLAVE_CONEXION in self._CONEXIONES:
            await self.CERRAR_CONEXION(USUARIO_ID)

        CLIENTE = ClienteWebSocket(self._URL_SERVIDOR, TOKEN)

        if await CLIENTE.CONECTAR():
            self._CONEXIONES[CLAVE_CONEXION] = CLIENTE
            print(f" Conexión creada para usuario {USUARIO_ID}")
            return CLIENTE

        return None

    def OBTENER_CONEXION(self, USUARIO_ID: int) -> Optional[ClienteWebSocket]:

        CLAVE_CONEXION = f"usuario_{USUARIO_ID}"
        return self._CONEXIONES.get(CLAVE_CONEXION)

    async def CERRAR_CONEXION(self, USUARIO_ID: int):

        CLAVE_CONEXION = f"usuario_{USUARIO_ID}"

        if CLAVE_CONEXION in self._CONEXIONES:
            await self._CONEXIONES[CLAVE_CONEXION].DESCONECTAR()
            del self._CONEXIONES[CLAVE_CONEXION]
            print(f" Conexión cerrada para usuario {USUARIO_ID}")

    async def CERRAR_TODAS(self):

        print(" Cerrando todas las conexiones WebSocket...")

        for CLIENTE in self._CONEXIONES.values():
            await CLIENTE.DESCONECTAR()

        self._CONEXIONES.clear()
        print(" Todas las conexiones cerradas")

    def CANTIDAD_CONEXIONES(self) -> int:

        return len(self._CONEXIONES)

    async def BROADCAST(self, MENSAJE: dict):

        for CLIENTE in list(self._CONEXIONES.values()):
            try:
                await CLIENTE.ENVIAR(MENSAJE)
            except Exception:
                continue
