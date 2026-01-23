"""
ENCRIPTADOR GPU - CAPA DE SEGURIDAD NIVEL 1
============================================
Utiliza aceleración por hardware (GPU/CPU) para encriptar datos sensibles.
Implementa AES-256-GCM con derivación de claves PBKDF2.
"""

import hashlib
import os
from typing import Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64


class EncriptadorGPU:
    """
    Encriptador que utiliza aceleración por hardware cuando está disponible.
    Flujo: Datos → Derivación de Clave → AES-GCM → Base64
    """
    
    LONGITUD_SAL = 32  # 256 bits
    LONGITUD_CLAVE = 32  # 256 bits para AES-256
    ITERACIONES = 100000  # Iteraciones PBKDF2HMAC
    
    def __init__(self, HUELLA_DISPOSITIVO: str):
        """
        Inicializa el encriptador con la huella única del dispositivo.
        
        Args:
            HUELLA_DISPOSITIVO: Identificador único del dispositivo
        """
        self._HUELLA = HUELLA_DISPOSITIVO.encode()
        self._BACKEND = default_backend()
    
    def _GENERAR_CLAVE(self, SAL: bytes) -> bytes:
        """
        Genera una clave derivada usando PBKPBKDF2HMACDF2-SHA256.
        
        Flujo: Huella + Sal → PBKDF2HMAC (100k iter) → Clave AES-256
        
        Args:
            SAL: Sal criptográfica aleatoria
            
        Returns:
            Clave derivada de 32 bytes
        """
        KDF = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.LONGITUD_CLAVE,
            salt=SAL,
            iterations=self.ITERACIONES,
            backend=self._BACKEND
        )
        return kdf.derive(self._HUELLA)
    
    def ENCRIPTAR(self, DATOS_PLANOS: str) -> str:
        """
        Encripta datos usando AES-256-GCM con autenticación.
        
        Flujo de Encriptación:
        1. Genera sal aleatoria (32 bytes)
        2. Deriva clave desde huella + sal
        3. Genera nonce aleatorio (12 bytes)
        4. Encripta con AES-GCM (incluye tag de autenticación)
        5. Combina: sal + nonce + datos_encriptados
        6. Codifica en Base64
        
        Args:
            DATOS_PLANOS: Texto a encriptar
            
        Returns:
            Cadena Base64 con formato: sal(32) + nonce(12) + cifrado + tag(16)
        """
        SAL = os.urandom(self.LONGITUD_SAL)
        CLAVE = self._GENERAR_CLAVE(SAL)
        AESGCM_CIFRADOR = AESGCM(CLAVE)
        NONCE = os.urandom(12)
        
        DATOS_CIFRADOS = AESGCM_CIFRADOR.encrypt(
            NONCE,
            DATOS_PLANOS.encode('utf-8'),
            None
        )
        
        PAQUETE_COMPLETO = SAL + NONCE + DATOS_CIFRADOS
        return base64.b64encode(PAQUETE_COMPLETO).decode('utf-8')
    
    def DESENCRIPTAR(self, DATOS_ENCRIPTADOS: str) -> Optional[str]:
        """
        Desencripta datos previamente encriptados.
        
        Args:
            DATOS_ENCRIPTADOS: Cadena Base64 encriptada
            
        Returns:
            Texto desencriptado o None si falla
        """
        try:
            PAQUETE_COMPLETO = base64.b64decode(DATOS_ENCRIPTADOS)
            SAL = PAQUETE_COMPLETO[:self.LONGITUD_SAL]
            NONCE = PAQUETE_COMPLETO[self.LONGITUD_SAL:self.LONGITUD_SAL + 12]
            DATOS_CIFRADOS = PAQUETE_COMPLETO[self.LONGITUD_SAL + 12:]
            
            CLAVE = self._GENERAR_CLAVE(SAL)
            AESGCM_CIFRADOR = AESGCM(CLAVE)
            DATOS_PLANOS = AESGCM_CIFRADOR.decrypt(NONCE, DATOS_CIFRADOS, None)
            
            return DATOS_PLANOS.decode('utf-8')
            
        except Exception as ERROR:
            print(f"❌ Error de desencriptación: {ERROR}")
            return None
    
    def GENERAR_HASH(self, DATOS: str) -> str:
        """Genera un hash SHA-256 de los datos"""
        return hashlib.sha256(DATOS.encode()).hexdigest()