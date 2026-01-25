"""
Caso de uso: Registrar Dispositivo
Genera un App Token para identificar la instalación/dispositivo
"""
from typing import Dict
from core.seguridad.ManejadorJWT import ManejadorJWT
from core.seguridad.GeneradorHuella import GeneradorHuella
from core.cache.GestorRedis import GestorRedis


class RegistrarDispositivo:
    
    def __init__(self):
        self._MANEJADOR_JWT = ManejadorJWT()
        self._REDIS = GestorRedis()
    
    async def EJECUTAR(self, METADATA: Dict = None) -> Dict:
        """
        Registra un nuevo dispositivo y genera App Token
        
        Args:
            METADATA: Información del dispositivo (plataforma, version, etc)
        
        Returns:
            Dict con app_token y dispositivo_id
        """
        try:
            # Generar huella única del dispositivo
            DISPOSITIVO_ID = GeneradorHuella.OBTENER_HUELLA()
            
            # Metadata por defecto
            if METADATA is None:
                METADATA = {
                    "plataforma": "desktop",
                    "version_app": "1.0.0"
                }
            
            # Generar App Token (30 días)
            APP_TOKEN = self._MANEJADOR_JWT.GENERAR_APP_TOKEN(
                DISPOSITIVO_ID=DISPOSITIVO_ID,
                METADATA=METADATA
            )
            
            # Guardar metadata en Redis
            await self._REDIS.GUARDAR_CACHE(
                f"dispositivo:{DISPOSITIVO_ID}",
                {
                    "metadata": METADATA,
                    "registrado": True
                },
                TTL=2592000  # 30 días
            )
            
            print(f"✓ Dispositivo registrado: {DISPOSITIVO_ID[:16]}...")
            
            return {
                "EXITO": True,
                "APP_TOKEN": APP_TOKEN,
                "DISPOSITIVO_ID": DISPOSITIVO_ID,
                "CODIGO": 200
            }
            
        except Exception as ERROR:
            print(f"✗ Error registrando dispositivo: {ERROR}")
            import traceback
            traceback.print_exc()
            
            return {
                "EXITO": False,
                "ERROR": f"Error al registrar dispositivo: {str(ERROR)}",
                "CODIGO": 500
            }
