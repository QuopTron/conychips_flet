"""
MANEJADOR DE CONEXIÓN WEBSOCKET
================================
Gestiona múltiples conexiones y estados
"""

from typing import Dict, Optional
from core.websocket.ClienteWebSocket import ClienteWebSocket


class ManejadorConexion:
    """Singleton que gestiona conexiones WebSocket activas"""
    
    _INSTANCIA: Optional['ManejadorConexion'] = None
    
    def __new__(cls):
        if cls._INSTANCIA is None:
            cls._INSTANCIA = super().__new__(cls)
            cls._INSTANCIA._INICIALIZAR()
        return cls._INSTANCIA
    
    def _INICIALIZAR(self):
        """Inicializa el manejador"""
        self._CONEXIONES: Dict[str, ClienteWebSocket] = {}
        self._URL_SERVIDOR: Optional[str] = None
    
    def CONFIGURAR_SERVIDOR(self, URL: str):
        """Configura URL del servidor WebSocket"""
        self._URL_SERVIDOR = URL
        print(f"🔧 Servidor WebSocket configurado: {URL}")
    
    async def CREAR_CONEXION(self, USUARIO_ID: int, TOKEN: str) -> Optional[ClienteWebSocket]:
        """
        Crea nueva conexión WebSocket para un usuario
        
        Args:
            USUARIO_ID: ID del usuario
            TOKEN: Token JWT del usuario
            
        Returns:
            Cliente WebSocket o None si falla
        """
        if not self._URL_SERVIDOR:
            print("❌ Servidor WebSocket no configurado")
            return None
        
        CLAVE_CONEXION = f"usuario_{USUARIO_ID}"
        
        # Si ya existe, cerrar la anterior
        if CLAVE_CONEXION in self._CONEXIONES:
            await self.CERRAR_CONEXION(USUARIO_ID)
        
        # Crear nuevo cliente
        CLIENTE = ClienteWebSocket(self._URL_SERVIDOR, TOKEN)
        
        if await CLIENTE.CONECTAR():
            self._CONEXIONES[CLAVE_CONEXION] = CLIENTE
            print(f"✅ Conexión creada para usuario {USUARIO_ID}")
            return CLIENTE
        
        return None
    
    def OBTENER_CONEXION(self, USUARIO_ID: int) -> Optional[ClienteWebSocket]:
        """Obtiene conexión existente de un usuario"""
        CLAVE_CONEXION = f"usuario_{USUARIO_ID}"
        return self._CONEXIONES.get(CLAVE_CONEXION)
    
    async def CERRAR_CONEXION(self, USUARIO_ID: int):
        """Cierra conexión de un usuario"""
        CLAVE_CONEXION = f"usuario_{USUARIO_ID}"
        
        if CLAVE_CONEXION in self._CONEXIONES:
            await self._CONEXIONES[CLAVE_CONEXION].DESCONECTAR()
            del self._CONEXIONES[CLAVE_CONEXION]
            print(f"✅ Conexión cerrada para usuario {USUARIO_ID}")
    
    async def CERRAR_TODAS(self):
        """Cierra todas las conexiones activas"""
        print("🔌 Cerrando todas las conexiones WebSocket...")
        
        for CLIENTE in self._CONEXIONES.values():
            await CLIENTE.DESCONECTAR()
        
        self._CONEXIONES.clear()
        print("✅ Todas las conexiones cerradas")
    
    def CANTIDAD_CONEXIONES(self) -> int:
        """Retorna cantidad de conexiones activas"""
        return len(self._CONEXIONES)