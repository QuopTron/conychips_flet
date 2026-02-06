"""
Migración: Agregar campos de estado a SUCURSALES
"""
from core.base_datos.ConfiguracionBD import MOTOR
from sqlalchemy import text

print("🔄 Migrando tabla SUCURSALES...")

with MOTOR.connect() as conn:
    try:
        # Agregar columna ESTADO si no existe
        conn.execute(text("""
            ALTER TABLE "SUCURSALES" 
            ADD COLUMN IF NOT EXISTS "ESTADO" VARCHAR(50) DEFAULT 'ACTIVA'
        """))
        conn.commit()
        print("✅ Columna ESTADO agregada")
    except Exception as e:
        print(f"⚠️  ESTADO: {e}")
    
    try:
        # Agregar columna TELEFONO si no existe
        conn.execute(text("""
            ALTER TABLE "SUCURSALES" 
            ADD COLUMN IF NOT EXISTS "TELEFONO" VARCHAR(20)
        """))
        conn.commit()
        print("✅ Columna TELEFONO agregada")
    except Exception as e:
        print(f"⚠️  TELEFONO: {e}")
    
    try:
        # Agregar columna HORARIO si no existe
        conn.execute(text("""
            ALTER TABLE "SUCURSALES" 
            ADD COLUMN IF NOT EXISTS "HORARIO" VARCHAR(100)
        """))
        conn.commit()
        print("✅ Columna HORARIO agregada")
    except Exception as e:
        print(f"⚠️  HORARIO: {e}")
    
    try:
        # Agregar columna FECHA_ULTIMA_MODIFICACION si no existe
        conn.execute(text("""
            ALTER TABLE "SUCURSALES" 
            ADD COLUMN IF NOT EXISTS "FECHA_ULTIMA_MODIFICACION" TIMESTAMP DEFAULT NOW()
        """))
        conn.commit()
        print("✅ Columna FECHA_ULTIMA_MODIFICACION agregada")
    except Exception as e:
        print(f"⚠️  FECHA_ULTIMA_MODIFICACION: {e}")
    
    # Actualizar sucursales existentes
    try:
        conn.execute(text("""
            UPDATE "SUCURSALES" 
            SET "ESTADO" = 'ACTIVA' 
            WHERE "ESTADO" IS NULL
        """))
        conn.commit()
        print("✅ Sucursales existentes actualizadas")
    except Exception as e:
        print(f"⚠️  Actualización: {e}")

print("✅ Migración completada")
