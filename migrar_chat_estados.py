#!/usr/bin/env python3
"""
🔄 Migración: Agregar campos de estado al chat
"""

import sys
sys.path.insert(0, '/mnt/flox/conychips')

from sqlalchemy import text
from core.base_datos.ConfiguracionBD import OBTENER_SESION

def migrar_mensajes_chat():
    """Agrega columnas de estado a MENSAJES_CHAT"""
    print("🔄 Migrando tabla MENSAJES_CHAT...")
    
    sesion = OBTENER_SESION()
    
    try:
        # Agregar columna ESTADO si no existe
        try:
            sesion.execute(text("""
                ALTER TABLE "MENSAJES_CHAT" 
                ADD COLUMN IF NOT EXISTS "ESTADO" VARCHAR(20) DEFAULT 'enviado'
            """))
            print("  ✅ Columna ESTADO agregada")
        except Exception as e:
            print(f"  ⚠️  ESTADO ya existe o error: {e}")
        
        # Agregar columna HASH si no existe
        try:
            sesion.execute(text("""
                ALTER TABLE "MENSAJES_CHAT" 
                ADD COLUMN IF NOT EXISTS "HASH" VARCHAR(64)
            """))
            print("  ✅ Columna HASH agregada")
        except Exception as e:
            print(f"  ⚠️  HASH ya existe o error: {e}")
        
        # Agregar columna FECHA_LECTURA si no existe
        try:
            sesion.execute(text("""
                ALTER TABLE "MENSAJES_CHAT" 
                ADD COLUMN IF NOT EXISTS "FECHA_LECTURA" TIMESTAMP
            """))
            print("  ✅ Columna FECHA_LECTURA agregada")
        except Exception as e:
            print(f"  ⚠️  FECHA_LECTURA ya existe o error: {e}")
        
        sesion.commit()
        print("\n✅ Migración completada exitosamente")
        
    except Exception as e:
        print(f"\n❌ Error en migración: {e}")
        sesion.rollback()
        return False
    finally:
        sesion.close()
    
    return True


if __name__ == "__main__":
    print("="*60)
    print("MIGRACIÓN DE BASE DE DATOS - SISTEMA DE CHAT")
    print("="*60 + "\n")
    
    if migrar_mensajes_chat():
        print("\n" + "="*60)
        print("✅ MIGRACIÓN COMPLETADA CON ÉXITO")
        print("="*60)
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("❌ MIGRACIÓN FALLÓ")
        print("="*60)
        sys.exit(1)
