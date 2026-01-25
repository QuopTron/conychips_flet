import hashlib
import os
from typing import Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64


class EncriptadorGPU:

    LONGITUD_SAL = 32  # 256 bits
    LONGITUD_CLAVE = 32  # 256 bits para AES-256
    ITERACIONES = 100000  # Iteraciones PBKDF2HMAC

    def __init__(self, HUELLA_DISPOSITIVO: str):

        self._HUELLA = HUELLA_DISPOSITIVO.encode()
        self._BACKEND = default_backend()

    def _GENERAR_CLAVE(self, SAL: bytes) -> bytes:

        KDF = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.LONGITUD_CLAVE,
            salt=SAL,
            iterations=self.ITERACIONES,
            backend=self._BACKEND,
        )
        return kdf.derive(self._HUELLA)

    def ENCRIPTAR(self, DATOS_PLANOS: str) -> str:

        SAL = os.urandom(self.LONGITUD_SAL)
        CLAVE = self._GENERAR_CLAVE(SAL)
        AESGCM_CIFRADOR = AESGCM(CLAVE)
        NONCE = os.urandom(12)

        DATOS_CIFRADOS = AESGCM_CIFRADOR.encrypt(
            NONCE, DATOS_PLANOS.encode("utf-8"), None
        )

        PAQUETE_COMPLETO = SAL + NONCE + DATOS_CIFRADOS
        return base64.b64encode(PAQUETE_COMPLETO).decode("utf-8")

    def DESENCRIPTAR(self, DATOS_ENCRIPTADOS: str) -> Optional[str]:

        try:
            PAQUETE_COMPLETO = base64.b64decode(DATOS_ENCRIPTADOS)
            SAL = PAQUETE_COMPLETO[: self.LONGITUD_SAL]
            NONCE = PAQUETE_COMPLETO[self.LONGITUD_SAL : self.LONGITUD_SAL + 12]
            DATOS_CIFRADOS = PAQUETE_COMPLETO[self.LONGITUD_SAL + 12 :]

            CLAVE = self._GENERAR_CLAVE(SAL)
            AESGCM_CIFRADOR = AESGCM(CLAVE)
            DATOS_PLANOS = AESGCM_CIFRADOR.decrypt(NONCE, DATOS_CIFRADOS, None)

            return DATOS_PLANOS.decode("utf-8")

        except Exception as ERROR:
            print(f" Error de desencriptación: {ERROR}")
            return None

    def GENERAR_HASH(self, DATOS: str) -> str:

        return hashlib.sha256(DATOS.encode()).hexdigest()
