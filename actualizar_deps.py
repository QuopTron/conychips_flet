#!/usr/bin/env python3
"""
Script para actualizar dependencias a versiones compatibles con Flet 0.80.3
"""

import subprocess
import sys

def actualizar_dependencias():
    """Actualiza las dependencias del proyecto"""
    
    print("=" * 60)
    print("ACTUALIZACIÓN DE DEPENDENCIAS")
    print("=" * 60)
    print()
    
    print("📦 Instalando dependencias optimizadas para Flet 0.80.3...")
    print()
    
    try:
        # Actualizar pip
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
            check=True
        )
        
        # Instalar desde requirements.txt
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True
        )
        
        print()
        print("=" * 60)
        print("✅ DEPENDENCIAS ACTUALIZADAS EXITOSAMENTE")
        print("=" * 60)
        print()
        print("📋 Versiones instaladas:")
        print()
        
        # Mostrar versiones instaladas
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list"],
            capture_output=True,
            text=True
        )
        
        packages = ["flet", "sqlalchemy", "bcrypt", "pyjwt", "cryptography", "websockets"]
        for line in result.stdout.split('\n'):
            for pkg in packages:
                if line.lower().startswith(pkg.lower()):
                    print(f"  • {line}")
        
        print()
        print("🚀 Todo listo! Ejecuta: python main.py")
        print()
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al instalar dependencias: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    actualizar_dependencias()
