"""
Caso de uso: Refrescar Token
Genera nuevos Access y Refresh Tokens usando un Refresh Token válido
"""
from typing import Dict
from features.autenticacion.domain.RepositorioAutenticacion import RepositorioAutenticacion
from core.seguridad.ManejadorJWT import ManejadorJWT
from core.cache.GestorRedis import GestorRedis


class RefrescarToken:
    
    def __init__(self, REPOSITORIO: RepositorioAutenticacion):
        self._REPOSITORIO = REPOSITORIO
        self._MANEJADOR_JWT = ManejadorJWT()
        self._REDIS = GestorRedis()
    
    async def EJECUTAR(self, REFRESH_TOKEN: str) -> Dict:
        """
        Refresca los tokens de acceso usando un refresh token válido
        
        Args:
            REFRESH_TOKEN: Token de refresco actual
        
        Returns:
            Dict con nuevos access_token y refresh_token
        """
        try:
            # Verificar refresh token
            PAYLOAD = self._MANEJADOR_JWT.VERIFICAR_TOKEN(REFRESH_TOKEN)
            
            if not PAYLOAD or PAYLOAD.get("tipo") != "refresh":
                return {
                    "EXITO": False,
                    "ERROR": "Token de refresco inválido",
                    "CODIGO": 401
                }
            
            USUARIO_ID = PAYLOAD.get("usuario_id")
            APP_TOKEN_ID = PAYLOAD.get("app_token_id")
            
            # Obtener usuario de BD
            USUARIO = await self._REPOSITORIO.OBTENER_POR_ID(USUARIO_ID)
            
            if not USUARIO or not USUARIO.ACTIVO:
                return {
                    "EXITO": False,
                    "ERROR": "Usuario no encontrado o inactivo",
                    "CODIGO": 403
                }
            
            # Obtener roles
            ROLES = [ROL.NOMBRE for ROL in USUARIO.ROLES]
            
            # Obtener permisos
            PERMISOS = []
            for ROL in USUARIO.ROLES:
                # ROL.PERMISOS puede ser un string JSON o lista de objetos
                if hasattr(ROL, 'PERMISOS'):
                    if isinstance(ROL.PERMISOS, str):
                        # Es un JSON string
                        import json
                        try:
                            permisos_lista = json.loads(ROL.PERMISOS) if ROL.PERMISOS else []
                            for p in permisos_lista:
                                if p not in PERMISOS:
                                    PERMISOS.append(p)
                        except:
                            # Si no es JSON válido, asumir que es "*" (superadmin)
                            if ROL.PERMISOS == "*":
                                PERMISOS = ["*"]
                                break
                    elif isinstance(ROL.PERMISOS, list):
                        # Ya es una lista
                        for p in ROL.PERMISOS:
                            # Puede ser string o objeto
                            if isinstance(p, str):
                                if p not in PERMISOS:
                                    PERMISOS.append(p)
                            elif hasattr(p, 'NOMBRE'):
                                if p.NOMBRE not in PERMISOS:
                                    PERMISOS.append(p.NOMBRE)
            
            # Si no hay permisos específicos y es superadmin, dar todos
            if not PERMISOS and "SUPERADMIN" in ROLES:
                PERMISOS = ["*"]
            
            # Revocar tokens anteriores
            self._MANEJADOR_JWT.REVOCAR_TOKEN(REFRESH_TOKEN)
            
            # Generar nuevos tokens
            NUEVO_ACCESS_TOKEN = self._MANEJADOR_JWT.GENERAR_ACCESS_TOKEN(
                USUARIO_ID=USUARIO_ID,
                EMAIL=USUARIO.EMAIL,
                ROLES=ROLES,
                PERMISOS=PERMISOS,
                APP_TOKEN_ID=APP_TOKEN_ID
            )
            
            NUEVO_REFRESH_TOKEN = self._MANEJADOR_JWT.GENERAR_REFRESH_TOKEN(
                USUARIO_ID=USUARIO_ID,
                APP_TOKEN_ID=APP_TOKEN_ID
            )
            
            # Actualizar sesión en BD
            await self._REPOSITORIO.CREAR_SESION(
                USUARIO_ID=USUARIO_ID,
                REFRESH_TOKEN=NUEVO_REFRESH_TOKEN,
                HUELLA_DISPOSITIVO=APP_TOKEN_ID  # Usamos app_token_id como huella
            )
            
            # Guardar sesión en Redis
            SESION_DATA = {
                "usuario_id": USUARIO_ID,
                "email": USUARIO.EMAIL,
                "roles": ROLES,
                "app_token_id": APP_TOKEN_ID
            }
            
            # Extraer JTI del access token para usar como key
            ACCESS_PAYLOAD = self._MANEJADOR_JWT.VERIFICAR_TOKEN(NUEVO_ACCESS_TOKEN)
            if ACCESS_PAYLOAD:
                self._REDIS.GUARDAR_SESION(
                    USUARIO_ID=USUARIO_ID,
                    TOKEN=ACCESS_PAYLOAD.get("jti"),
                    DATOS=SESION_DATA,
                    TTL_SECONDS=604800  # 7 días (duración del refresh token)
                )
            
            print(f"✓ Tokens refrescados para usuario: {USUARIO_ID}")
            
            return {
                "EXITO": True,
                "ACCESS_TOKEN": NUEVO_ACCESS_TOKEN,
                "REFRESH_TOKEN": NUEVO_REFRESH_TOKEN,
                "CODIGO": 200
            }

        except Exception as ERROR:
            print(f"✗ Error al refrescar token: {ERROR}")
            import traceback
            traceback.print_exc()
            
            return {
                "EXITO": False,
                "ERROR": f"Error al refrescar token: {str(ERROR)}",
                "CODIGO": 500,
            }
