from typing import Dict
import bcrypt
from features.autenticacion.domain.RepositorioAutenticacion import (
    RepositorioAutenticacion,
)
from core.seguridad.GeneradorHuella import GeneradorHuella

class RegistrarUsuario:

    def __init__(self, REPOSITORIO: RepositorioAutenticacion):

        self._REPOSITORIO = REPOSITORIO

    async def EJECUTAR(self, EMAIL: str, NOMBRE_USUARIO: str, CONTRASENA: str) -> Dict:

        print(f" Registrando nuevo usuario: {EMAIL}")

        try:
            USUARIO_EXISTENTE = await self._REPOSITORIO.OBTENER_POR_EMAIL(EMAIL)

            if USUARIO_EXISTENTE:
                print(f" Email ya registrado: {EMAIL}")
                return {
                    "EXITO": False,
                    "ERROR": "Este email ya está registrado",
                    "CODIGO": 409,
                }

            USUARIO_EXISTENTE = await self._REPOSITORIO.OBTENER_POR_NOMBRE_USUARIO(
                NOMBRE_USUARIO
            )

            if USUARIO_EXISTENTE:
                print(f" Nombre de usuario ya existe: {NOMBRE_USUARIO}")
                return {
                    "EXITO": False,
                    "ERROR": "Este nombre de usuario ya está en uso",
                    "CODIGO": 409,
                }

            SAL = bcrypt.gensalt(rounds=12)
            CONTRASENA_HASH = bcrypt.hashpw(CONTRASENA.encode("utf-8"), SAL)

            HUELLA_DISPOSITIVO = GeneradorHuella.OBTENER_HUELLA()

            NUEVO_USUARIO = await self._REPOSITORIO.CREAR_USUARIO(
                EMAIL=EMAIL,
                NOMBRE_USUARIO=NOMBRE_USUARIO,
                CONTRASENA_HASH=CONTRASENA_HASH.decode("utf-8"),
                HUELLA_DISPOSITIVO=HUELLA_DISPOSITIVO,
            )

            from core.Constantes import ROLES

            await self._REPOSITORIO.ASIGNAR_ROL(NUEVO_USUARIO.ID, ROLES.CLIENTE)

            print(
                f" Usuario registrado exitosamente: {EMAIL} (ID: {NUEVO_USUARIO.ID})"
            )

            return {
                "EXITO": True,
                "USUARIO_ID": NUEVO_USUARIO.ID,
                "EMAIL": EMAIL,
                "CODIGO": 201,
            }

        except Exception as ERROR:
            print(f" Error al registrar usuario: {ERROR}")
            return {
                "EXITO": False,
                "ERROR": "Error interno del servidor",
                "CODIGO": 500,
            }

    async def _ENVIAR_EMAIL_VERIFICACION(self, EMAIL: str):

        print(f" Email de verificación enviado a: {EMAIL}")
