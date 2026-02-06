from typing import Dict
from datetime import datetime, timedelta, timezone
import secrets
import bcrypt
import smtplib
from email.mime.text import MIMEText
from features.autenticacion.domain.RepositorioAutenticacion import (
    RepositorioAutenticacion,
)
from core.decoradores.DecoradorValidacion import (
    VALIDAR_EMAIL,
    VALIDAR_CONTRASENA_FUERTE,
    VALIDAR_CAMPOS_REQUERIDOS,
)
from config.ConfiguracionApp import CONFIGURACION_APP

class SolicitarResetContrasena:
    def __init__(self, REPO: RepositorioAutenticacion):
        self._REPO = REPO

    @VALIDAR_CAMPOS_REQUERIDOS("EMAIL")
    @VALIDAR_EMAIL
    async def EJECUTAR(self, EMAIL: str) -> Dict:
        usuario = await self._REPO.OBTENER_POR_EMAIL(EMAIL)
        if not usuario:
            return {"EXITO": False, "ERROR": "Email no encontrado", "CODIGO": 404}

        if not usuario.ACTIVO:
            return {"EXITO": False, "ERROR": "Usuario inactivo", "CODIGO": 403}

        token = secrets.token_urlsafe(32)
        expira = datetime.now(timezone.utc) + timedelta(hours=1)

        await self._REPO.ACTUALIZAR_TOKEN_RESET(usuario.ID, token, expira)

        self._ENVIAR_EMAIL_RESET(EMAIL, token)

        return {"EXITO": True, "CODIGO": 200}

    def _ENVIAR_EMAIL_RESET(self, EMAIL: str, TOKEN: str):
        if not CONFIGURACION_APP.SMTP_HOST:
            print(f"Email enviado a {EMAIL}: Token de reset: {TOKEN}")
            return

        cuerpo = f"Tu token para restablecer contraseña es: {TOKEN}"
        mensaje = MIMEText(cuerpo)
        mensaje["Subject"] = "Restablecer contraseña"
        mensaje["From"] = CONFIGURACION_APP.EMAIL_FROM
        mensaje["To"] = EMAIL

        servidor = smtplib.SMTP(CONFIGURACION_APP.SMTP_HOST, CONFIGURACION_APP.SMTP_PORT)
        servidor.starttls()
        servidor.login(CONFIGURACION_APP.SMTP_USER, CONFIGURACION_APP.SMTP_PASSWORD)
        servidor.sendmail(CONFIGURACION_APP.EMAIL_FROM, [EMAIL], mensaje.as_string())
        servidor.quit()

class ResetearContrasena:
    def __init__(self, REPO: RepositorioAutenticacion):
        self._REPO = REPO

    @VALIDAR_CAMPOS_REQUERIDOS("TOKEN", "NUEVA_CONTRASENA")
    @VALIDAR_CONTRASENA_FUERTE
    async def EJECUTAR(self, TOKEN: str, NUEVA_CONTRASENA: str) -> Dict:
        usuario = await self._REPO.OBTENER_USUARIO_POR_TOKEN_RESET(TOKEN)
        if not usuario:
            return {"EXITO": False, "ERROR": "Token inválido o expirado", "CODIGO": 400}

        if not usuario.TOKEN_RESET_EXPIRA or datetime.now(timezone.utc) > usuario.TOKEN_RESET_EXPIRA:
            return {"EXITO": False, "ERROR": "Token expirado", "CODIGO": 400}

        sal = bcrypt.gensalt(rounds=12)
        contrasena_hash = bcrypt.hashpw(NUEVA_CONTRASENA.encode("utf-8"), sal).decode("utf-8")

        await self._REPO.ACTUALIZAR_CONTRASENA(usuario.ID, contrasena_hash)
        await self._REPO.LIMPIAR_TOKEN_RESET(usuario.ID)

        return {"EXITO": True, "CODIGO": 200}
