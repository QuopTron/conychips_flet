from typing import Dict, Optional
import bcrypt
from datetime import datetime
from features.autenticacion.domain.RepositorioAutenticacion import (
    RepositorioAutenticacion,
)
from features.autenticacion.domain.entities.Usuario import Usuario
from core.seguridad.ManejadorJWT import ManejadorJWT
from core.seguridad.GeneradorHuella import GeneradorHuella
from core.cache.GestorRedis import GestorRedis


class IniciarSesion:

    def __init__(self, REPOSITORIO: RepositorioAutenticacion):

        self._REPOSITORIO = REPOSITORIO
        self._MANEJADOR_JWT = ManejadorJWT()
        self._REDIS = GestorRedis()

    async def EJECUTAR(self, EMAIL: str, CONTRASENA: str, APP_TOKEN: str = None) -> Dict:
        """
        Inicia sesión de usuario con sistema de tokens de dos capas
        
        Args:
            EMAIL: Email del usuario
            CONTRASENA: Contraseña del usuario
            APP_TOKEN: Token de aplicación (opcional, se verifica si se proporciona)
        
        Returns:
            Dict con usuario, access_token, refresh_token
        """

        print(f"Iniciando sesión para: {EMAIL}")

        try:
            USUARIO_BD = await self._REPOSITORIO.OBTENER_POR_EMAIL(EMAIL)

            if not USUARIO_BD:
                print(f"Usuario no encontrado: {EMAIL}")
                return {
                    "EXITO": False,
                    "ERROR": "Credenciales inválidas",
                    "CODIGO": 401,
                }

            if not USUARIO_BD.ACTIVO:
                print(f"Usuario inactivo: {EMAIL}")
                return {
                    "EXITO": False,
                    "ERROR": "Usuario inactivo. Contacta al administrador.",
                    "CODIGO": 403,
                }

            CONTRASENA_VALIDA = bcrypt.checkpw(
                CONTRASENA.encode("utf-8"), USUARIO_BD.CONTRASENA_HASH.encode("utf-8")
            )

            if not CONTRASENA_VALIDA:
                print(f"Contraseña inválida para: {EMAIL}")
                return {
                    "EXITO": False,
                    "ERROR": "Credenciales inválidas",
                    "CODIGO": 401,
                }

            USUARIO_DOMINIO = self._MAPEAR_A_DOMINIO(USUARIO_BD)

            ROLES = [ROL.NOMBRE for ROL in USUARIO_BD.ROLES]

            if not ROLES:
                # Si no tiene roles, no permitir login (excepto super admin)
                print(f"Usuario sin roles asignados: {EMAIL}")
                return {
                    "EXITO": False,
                    "ERROR": "Usuario sin roles asignados. Contacta al administrador.",
                    "CODIGO": 403,
                }
            
            # Obtener permisos de todos los roles
            PERMISOS = []
            for ROL in USUARIO_BD.ROLES:
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
            
            # Verificar o generar App Token
            APP_TOKEN_ID = None
            if APP_TOKEN:
                # Verificar app token existente
                PAYLOAD_APP = self._MANEJADOR_JWT.VERIFICAR_TOKEN(APP_TOKEN)
                if PAYLOAD_APP and PAYLOAD_APP.get("tipo") == "app":
                    APP_TOKEN_ID = PAYLOAD_APP.get("jti")
                    print(f"✓ App Token válido: {APP_TOKEN_ID[:16]}...")
                else:
                    print("⚠ App Token inválido, se generará uno nuevo")
            
            if not APP_TOKEN_ID:
                # Generar nuevo App Token
                HUELLA_DISPOSITIVO = GeneradorHuella.OBTENER_HUELLA()
                APP_TOKEN = self._MANEJADOR_JWT.GENERAR_APP_TOKEN(
                    DISPOSITIVO_ID=HUELLA_DISPOSITIVO,
                    METADATA={
                        "plataforma": "desktop",
                        "version": "1.0.0"
                    }
                )
                PAYLOAD_APP = self._MANEJADOR_JWT.VERIFICAR_TOKEN(APP_TOKEN)
                APP_TOKEN_ID = PAYLOAD_APP.get("jti")
                print(f"✓ Nuevo App Token generado: {APP_TOKEN_ID[:16]}...")

            # Generar tokens de usuario
            ACCESS_TOKEN = self._MANEJADOR_JWT.GENERAR_ACCESS_TOKEN(
                USUARIO_ID=USUARIO_BD.ID,
                EMAIL=USUARIO_BD.EMAIL,
                ROLES=ROLES,
                PERMISOS=PERMISOS,
                APP_TOKEN_ID=APP_TOKEN_ID
            )

            REFRESH_TOKEN = self._MANEJADOR_JWT.GENERAR_REFRESH_TOKEN(
                USUARIO_ID=USUARIO_BD.ID,
                APP_TOKEN_ID=APP_TOKEN_ID
            )

            # Crear sesión en BD
            await self._REPOSITORIO.CREAR_SESION(
                USUARIO_ID=USUARIO_BD.ID,
                REFRESH_TOKEN=REFRESH_TOKEN,
                HUELLA_DISPOSITIVO=APP_TOKEN_ID,
            )
            
            # Guardar sesión en Redis
            SESION_DATA = {
                "usuario_id": USUARIO_BD.ID,
                "email": USUARIO_BD.EMAIL,
                "roles": ROLES,
                "permisos": PERMISOS,
                "app_token_id": APP_TOKEN_ID
            }
            
            ACCESS_PAYLOAD = self._MANEJADOR_JWT.VERIFICAR_TOKEN(ACCESS_TOKEN)
            if ACCESS_PAYLOAD:
                self._REDIS.GUARDAR_SESION(
                    USUARIO_ID=USUARIO_BD.ID,
                    TOKEN=ACCESS_PAYLOAD.get("jti"),
                    DATOS=SESION_DATA,
                    TTL_SECONDS=604800  # 7 días
                )

            await self._REPOSITORIO.ACTUALIZAR_ULTIMA_CONEXION(USUARIO_BD.ID)

            print(f"✓ Login exitoso para: {EMAIL}")

            return {
                "EXITO": True,
                "USUARIO": USUARIO_DOMINIO,
                "ACCESS_TOKEN": ACCESS_TOKEN,
                "REFRESH_TOKEN": REFRESH_TOKEN,
                "APP_TOKEN": APP_TOKEN,  # Devolver app token también
                "CODIGO": 200,
            }

        except Exception as ERROR:
            print(f"✗ Error al iniciar sesión: {ERROR}")
            import traceback
            traceback.print_exc()
            return {
                "EXITO": False,
                "ERROR": "Error interno del servidor",
                "CODIGO": 500,
            }

    def _MAPEAR_A_DOMINIO(self, USUARIO_BD) -> Usuario:

        return Usuario(
            ID=USUARIO_BD.ID,
            EMAIL=USUARIO_BD.EMAIL,
            NOMBRE_USUARIO=USUARIO_BD.NOMBRE_USUARIO,
            ROLES=[ROL.NOMBRE for ROL in USUARIO_BD.ROLES],
            ACTIVO=USUARIO_BD.ACTIVO,
            VERIFICADO=USUARIO_BD.VERIFICADO,
            FECHA_CREACION=USUARIO_BD.FECHA_CREACION,
            ULTIMA_CONEXION=USUARIO_BD.ULTIMA_CONEXION,
        )
