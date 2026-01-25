#!/usr/bin/env python
"""
Script para generar claves RSA privada y pública para JWT RS256
"""
import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend


def GENERAR_CLAVES_RSA():
    print("="*60)
    print("GENERADOR DE CLAVES RSA PARA JWT")
    print("="*60)
    print()
    
    DIRECTORIO_CLAVES = "config/keys"
    os.makedirs(DIRECTORIO_CLAVES, exist_ok=True)
    
    RUTA_PRIVADA = os.path.join(DIRECTORIO_CLAVES, "jwt_private.pem")
    RUTA_PUBLICA = os.path.join(DIRECTORIO_CLAVES, "jwt_public.pem")
    
    if os.path.exists(RUTA_PRIVADA) or os.path.exists(RUTA_PUBLICA):
        respuesta = input("\n⚠ Las claves ya existen. ¿Sobrescribir? (s/N): ")
        if respuesta.lower() != 's':
            print("\n✗ Operación cancelada")
            return
    
    print("1. Generando clave privada RSA (4096 bits)...")
    clave_privada = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend()
    )
    
    print("2. Guardando clave privada...")
    with open(RUTA_PRIVADA, 'wb') as f:
        f.write(
            clave_privada.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        )
    
    os.chmod(RUTA_PRIVADA, 0o600)
    
    print("3. Extrayendo clave pública...")
    clave_publica = clave_privada.public_key()
    
    print("4. Guardando clave pública...")
    with open(RUTA_PUBLICA, 'wb') as f:
        f.write(
            clave_publica.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )
    
    os.chmod(RUTA_PUBLICA, 0o644)
    
    print()
    print("="*60)
    print("✓ CLAVES GENERADAS EXITOSAMENTE")
    print("="*60)
    print(f"\nClave privada: {RUTA_PRIVADA}")
    print(f"Clave pública:  {RUTA_PUBLICA}")
    print()
    print("⚠ IMPORTANTE:")
    print("  - NO compartas la clave privada")
    print("  - Agrega config/keys/ a .gitignore")
    print("  - Haz backup seguro de las claves")
    print()


if __name__ == "__main__":
    try:
        GENERAR_CLAVES_RSA()
    except Exception as e:
        print(f"\n✗ Error generando claves: {e}")
        import traceback
        traceback.print_exc()
