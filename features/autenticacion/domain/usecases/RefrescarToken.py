from typing import Dict
from features.autenticacion.domain.RepositorioAutenticacion import (
    RepositorioAutenticacion,
)
from core.seguridad.ManejadorJWT import ManejadorJWT
from core.seguridad.ValidadorDispositivo import ValidadorDispositivo


class RefrescarToken:

    def __init__(self, REPOSITORIO: RepositorioAutenticacion):

        self._REPOSITORIO = REPOSITORIO
        self._MANEJADOR_JWT = ManejadorJWT()

    async def EJECUTAR(self, REFRESH_TOKEN: str) -> Dict:

        print("🔄 Refrescando access token...")

        try:
            PAYLOAD = self._MANEJADOR_JWT.VERIFICAR_TOKEN(REFRESH_TOKEN, "refresh")

            if not PAYLOAD:
                print("❌ Refresh token inválido o expirado")
                return {
                    "EXITO": False,
                    "ERROR": "Refresh token inválido",
                    "CODIGO": 401,
                }

            USUARIO_ID = PAYLOAD["USUARIO_ID"]
            HUELLA_JWT = PAYLOAD["HUELLA_DISPOSITIVO"]

            if not ValidadorDispositivo.VALIDAR_HUELLA(HUELLA_JWT):
                print("❌ Huella de dispositivo no coincide")
                return {
                    "EXITO": False,
                    "ERROR": "Dispositivo no autorizado",
                    "CODIGO": 403,
                }

            SESION_VALIDA = await self._REPOSITORIO.VERIFICAR_SESION(
                USUARIO_ID=USUARIO_ID, REFRESH_TOKEN=REFRESH_TOKEN
            )

            if not SESION_VALIDA:
                print("❌ Sesión no encontrada o inactiva")
                return {"EXITO": False, "ERROR": "Sesión inválida", "CODIGO": 401}

            USUARIO = await self._REPOSITORIO.OBTENER_POR_ID(USUARIO_ID)

            if not USUARIO or not USUARIO.ACTIVO:
                print("❌ Usuario no encontrado o inactivo")
                return {"EXITO": False, "ERROR": "Usuario no autorizado", "CODIGO": 403}

            ROLES = [ROL.NOMBRE for ROL in USUARIO.ROLES]

            NUEVO_ACCESS_TOKEN = self._MANEJADOR_JWT.CREAR_ACCESS_TOKEN(
                USUARIO_ID=USUARIO_ID,
                EMAIL=USUARIO.EMAIL,
                ROLES=ROLES,
                HUELLA_DISPOSITIVO=HUELLA_JWT,
            )

            print(f"✅ Access token refrescado para usuario {USUARIO_ID}")

            return {"EXITO": True, "ACCESS_TOKEN": NUEVO_ACCESS_TOKEN, "CODIGO": 200}

        except Exception as ERROR:
            print(f"❌ Error al refrescar token: {ERROR}")
            return {
                "EXITO": False,
                "ERROR": "Error interno del servidor",
                "CODIGO": 500,
            }
