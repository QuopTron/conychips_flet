#!/usr/bin/env python
"""
Script de configuración inicial del sistema
Configura PostgreSQL, Redis, y genera claves JWT
"""
import os
import sys
import subprocess


def EJECUTAR_COMANDO(comando, descripcion):
    print(f"\n{descripcion}...")
    try:
        resultado = subprocess.run(
            comando,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✓ {descripcion} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error en {descripcion}")
        print(f"  {e.stderr}")
        return False


def VERIFICAR_POSTGRESQL():
    print("\n" + "="*60)
    print("1. VERIFICANDO POSTGRESQL")
    print("="*60)
    
    try:
        resultado = subprocess.run(
            ["psql", "--version"],
            capture_output=True,
            text=True
        )
        print(f"✓ PostgreSQL instalado: {resultado.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("✗ PostgreSQL no está instalado")
        print("\nPara instalar PostgreSQL:")
        print("  Ubuntu/Debian: sudo apt install postgresql postgresql-contrib")
        print("  Arch Linux:    sudo pacman -S postgresql")
        print("  macOS:         brew install postgresql")
        return False


def CONFIGURAR_BASE_DATOS():
    print("\n" + "="*60)
    print("2. CONFIGURANDO BASE DE DATOS")
    print("="*60)
    
    print("\nCreando usuario y base de datos...")
    print("Comandos SQL a ejecutar manualmente:")
    print()
    print("sudo -u postgres psql")
    print("CREATE USER conychips_user WITH PASSWORD 'ConyCh1ps2026!';")
    print("CREATE DATABASE conychips_db OWNER conychips_user;")
    print("GRANT ALL PRIVILEGES ON DATABASE conychips_db TO conychips_user;")
    print("\\q")
    print()
    
    respuesta = input("¿Ya ejecutaste estos comandos? (s/N): ")
    return respuesta.lower() == 's'


def VERIFICAR_REDIS():
    print("\n" + "="*60)
    print("3. VERIFICANDO REDIS")
    print("="*60)
    
    try:
        resultado = subprocess.run(
            ["redis-cli", "--version"],
            capture_output=True,
            text=True
        )
        print(f"✓ Redis instalado: {resultado.stdout.strip()}")
        
        resultado_server = subprocess.run(
            ["redis-cli", "ping"],
            capture_output=True,
            text=True
        )
        
        if "PONG" in resultado_server.stdout:
            print("✓ Redis server está corriendo")
            return True
        else:
            print("⚠ Redis instalado pero server no está corriendo")
            print("\nPara iniciar Redis:")
            print("  sudo systemctl start redis")
            print("  O: redis-server &")
            return False
            
    except FileNotFoundError:
        print("✗ Redis no está instalado")
        print("\nPara instalar Redis:")
        print("  Ubuntu/Debian: sudo apt install redis-server")
        print("  Arch Linux:    sudo pacman -S redis")
        print("  macOS:         brew install redis")
        return False


def INSTALAR_DEPENDENCIAS():
    print("\n" + "="*60)
    print("4. INSTALANDO DEPENDENCIAS PYTHON")
    print("="*60)
    
    if not os.path.exists("venv"):
        print("✗ Entorno virtual no encontrado")
        print("Creando entorno virtual...")
        EJECUTAR_COMANDO(
            "python -m venv venv",
            "Creación de entorno virtual"
        )
    
    return EJECUTAR_COMANDO(
        "source venv/bin/activate && pip install -r requirements.txt",
        "Instalación de dependencias"
    )


def GENERAR_CLAVES_JWT():
    print("\n" + "="*60)
    print("5. GENERANDO CLAVES JWT RSA")
    print("="*60)
    
    if os.path.exists("config/keys/jwt_private.pem"):
        respuesta = input("\n⚠ Las claves ya existen. ¿Regenerar? (s/N): ")
        if respuesta.lower() != 's':
            print("✓ Usando claves existentes")
            return True
    
    return EJECUTAR_COMANDO(
        "source venv/bin/activate && python generar_claves_jwt.py",
        "Generación de claves RSA"
    )


def MIGRAR_BASE_DATOS():
    print("\n" + "="*60)
    print("6. MIGRANDO BASE DE DATOS")
    print("="*60)
    
    return EJECUTAR_COMANDO(
        "source venv/bin/activate && python migrar_nuevas_tablas.py",
        "Migración de tablas"
    )


def CREAR_GITIGNORE():
    print("\n" + "="*60)
    print("7. CONFIGURANDO .gitignore")
    print("="*60)
    
    CONTENIDO_GITIGNORE = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Base de datos
*.db
*.db-journal
*.sqlite
*.sqlite3

# Claves privadas
config/keys/
*.pem
*.key

# Configuración
.env
.env.local

# Logs
*.log
app_logs.txt

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Backups
*.backup.*
*.old
"""
    
    try:
        with open(".gitignore", "w") as f:
            f.write(CONTENIDO_GITIGNORE)
        print("✓ .gitignore creado/actualizado")
        return True
    except Exception as e:
        print(f"✗ Error creando .gitignore: {e}")
        return False


def MAIN():
    print("="*60)
    print("CONFIGURACIÓN INICIAL DEL SISTEMA CONY CHIPS")
    print("="*60)
    
    PASOS_EXITOSOS = []
    PASOS_FALLIDOS = []
    
    if VERIFICAR_POSTGRESQL():
        PASOS_EXITOSOS.append("PostgreSQL verificado")
    else:
        PASOS_FALLIDOS.append("PostgreSQL no disponible")
    
    if CONFIGURAR_BASE_DATOS():
        PASOS_EXITOSOS.append("Base de datos configurada")
    else:
        PASOS_FALLIDOS.append("Base de datos no configurada")
    
    if VERIFICAR_REDIS():
        PASOS_EXITOSOS.append("Redis verificado")
    else:
        PASOS_FALLIDOS.append("Redis no disponible (opcional pero recomendado)")
    
    if INSTALAR_DEPENDENCIAS():
        PASOS_EXITOSOS.append("Dependencias instaladas")
    else:
        PASOS_FALLIDOS.append("Error instalando dependencias")
    
    if GENERAR_CLAVES_JWT():
        PASOS_EXITOSOS.append("Claves JWT generadas")
    else:
        PASOS_FALLIDOS.append("Error generando claves JWT")
    
    if MIGRAR_BASE_DATOS():
        PASOS_EXITOSOS.append("Base de datos migrada")
    else:
        PASOS_FALLIDOS.append("Error en migración")
    
    if CREAR_GITIGNORE():
        PASOS_EXITOSOS.append(".gitignore configurado")
    else:
        PASOS_FALLIDOS.append("Error configurando .gitignore")
    
    print("\n" + "="*60)
    print("RESUMEN DE CONFIGURACIÓN")
    print("="*60)
    
    print(f"\n✓ Pasos exitosos ({len(PASOS_EXITOSOS)}):")
    for paso in PASOS_EXITOSOS:
        print(f"  - {paso}")
    
    if PASOS_FALLIDOS:
        print(f"\n✗ Pasos fallidos ({len(PASOS_FALLIDOS)}):")
        for paso in PASOS_FALLIDOS:
            print(f"  - {paso}")
    
    print("\n" + "="*60)
    if not PASOS_FALLIDOS:
        print("✓ CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
        print("\nPuedes ejecutar:")
        print("  source venv/bin/activate && python main.py")
    else:
        print("⚠ CONFIGURACIÓN COMPLETADA CON ADVERTENCIAS")
        print("\nRevisa los pasos fallidos arriba")
    print("="*60)
    print()


if __name__ == "__main__":
    try:
        MAIN()
    except KeyboardInterrupt:
        print("\n\n✗ Configuración cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
