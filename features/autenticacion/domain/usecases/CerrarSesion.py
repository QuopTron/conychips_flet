from typing import Dict
from features.autenticacion.domain.RepositorioAutenticacion import RepositorioAutenticacion
from core.seguridad.ManejadorJWT import ManejadorJWT
from core.cache.GestorRedis import GestorRedis

class CerrarSesion:
    
    def __init__(self, REPOSITORIO: RepositorioAutenticacion):
        self._REPOSITORIO = REPOSITORIO
        self._MANEJADOR_JWT = ManejadorJWT()
        self._REDIS = GestorRedis()
    
    async def EJECUTAR(self, ACCESS_TOKEN: str, REFRESH_TOKEN: str = None) -> Dict:
        try:
            PAYLOAD = self._MANEJADOR_JWT.VERIFICAR_TOKEN(ACCESS_TOKEN)
            
            if not PAYLOAD:
                return {
                    "EXITO": False,
                    "ERROR": "Token inválido",
                    "CODIGO": 401
                }
            
            USUARIO_ID = PAYLOAD.get("usuario_id")
            APP_TOKEN_ID = PAYLOAD.get("app_token_id")
            
            self._MANEJADOR_JWT.REVOCAR_TOKEN(ACCESS_TOKEN)
            print(f"✓ Access token revocado para usuario {USUARIO_ID}")
            
            if REFRESH_TOKEN:
                self._MANEJADOR_JWT.REVOCAR_TOKEN(REFRESH_TOKEN)
                print(f"✓ Refresh token revocado para usuario {USUARIO_ID}")
                
                await self._REPOSITORIO.CERRAR_SESION(REFRESH_TOKEN)
            
            TOKEN_ID = PAYLOAD.get("jti")
            self._REDIS.ELIMINAR_SESION(USUARIO_ID, TOKEN_ID)
            print(f"✓ Sesión eliminada de Redis para usuario {USUARIO_ID}")
            
            print(f"ℹ App Token {APP_TOKEN_ID[:16]}... sigue válido")
            
            return {
                "EXITO": True,
                "MENSAJE": "Sesión cerrada exitosamente",
                "CODIGO": 200
            }
            
        except Exception as ERROR:
            print(f"✗ Error al cerrar sesión: {ERROR}")
            import traceback
            traceback.print_exc()
            
            return {
                "EXITO": False,
                "ERROR": f"Error al cerrar sesión: {str(ERROR)}",
                "CODIGO": 500
            }
    
    async def CERRAR_TODAS_LAS_SESIONES(self, USUARIO_ID: int) -> Dict:
        try:
            self._REDIS.ELIMINAR_TODAS_SESIONES_USUARIO(USUARIO_ID)
            
            SESIONES = await self._REPOSITORIO.OBTENER_SESIONES_ACTIVAS(USUARIO_ID)
            
            for SESION in SESIONES:
                self._MANEJADOR_JWT.REVOCAR_TOKEN(SESION.REFRESH_TOKEN)
                await self._REPOSITORIO.CERRAR_SESION(SESION.REFRESH_TOKEN)
            
            print(f"✓ Todas las sesiones cerradas para usuario {USUARIO_ID}")
            
            return {
                "EXITO": True,
                "MENSAJE": f"Se cerraron {len(SESIONES)} sesiones",
                "CODIGO": 200
            }
            
        except Exception as ERROR:
            print(f"✗ Error al cerrar todas las sesiones: {ERROR}")
            import traceback
            traceback.print_exc()
            
            return {
                "EXITO": False,
                "ERROR": f"Error al cerrar sesiones: {str(ERROR)}",
                "CODIGO": 500
            }
