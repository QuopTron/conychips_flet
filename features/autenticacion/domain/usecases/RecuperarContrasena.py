from typing import Dict
from features.autenticacion.domain.RepositorioAutenticacion import (
    RepositorioAutenticacion,
)
import secrets
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText


class SolicitarResetContrasena:
    def __init__(self, REPO: RepositorioAutenticacion):
        self._REPO = REPO

    async def EJECUTAR(self, EMAIL: str) -> Dict:
        usuario = await self._REPO.OBTENER_USUARIO_POR_EMAIL(EMAIL)
        if not usuario:
            return {"EXITO": False, "ERROR": "Email no encontrado"}

        token = secrets.token_urlsafe(32)
        expira = datetime.utcnow() + timedelta(hours=1)

        await self._REPO.ACTUALIZAR_TOKEN_RESET(usuario["ID"], token, expira)

        self._ENVIAR_EMAIL_RESET(EMAIL, token)

        return {"EXITO": True}

    def _ENVIAR_EMAIL_RESET(self, EMAIL: str, TOKEN: str):
        print(f"Email enviado a {EMAIL}: Token de reset: {TOKEN}")


class ResetearContrasena:
    def __init__(self, REPO: RepositorioAutenticacion):
        self._REPO = REPO

    async def EJECUTAR(self, TOKEN: str, NUEVA_CONTRASENA: str) -> Dict:
        usuario = await self._REPO.OBTENER_USUARIO_POR_TOKEN_RESET(TOKEN)
        if not usuario:
            return {"EXITO": False, "ERROR": "Token inválido o expirado"}

        if datetime.utcnow() > usuario["TOKEN_RESET_EXPIRA"]:
            return {"EXITO": False, "ERROR": "Token expirado"}

        await self._REPO.ACTUALIZAR_CONTRASENA(usuario["ID"], NUEVA_CONTRASENA)
        await self._REPO.LIMPIAR_TOKEN_RESET(usuario["ID"])

        return {"EXITO": True}


class ConfirmarEmail:
    def __init__(self, REPO: RepositorioAutenticacion):
        self._REPO = REPO

    async def EJECUTAR(self, TOKEN: str) -> Dict:
        usuario = await self._REPO.OBTENER_USUARIO_POR_TOKEN_VERIFICACION(TOKEN)
        if not usuario:
            return {"EXITO": False, "ERROR": "Token inválido"}

        await self._REPO.VERIFICAR_EMAIL(usuario["ID"])

        return {"EXITO": True}
