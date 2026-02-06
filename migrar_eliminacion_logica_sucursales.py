#!/usr/bin/env python3
"""
Script de migración para agregar campos de eliminación lógica a la tabla SUCURSALES
"""
from sqlalchemy import text
from core.base_datos.ConfiguracionBD import MOTOR, OBTENER_SESION

def migrar_eliminacion_logica():
    """Agrega campos ELIMINADA, FECHA_ELIMINACION y USUARIO_ELIMINO_ID a SUCURSALES"""
    
    print("🔧 Iniciando migración: Eliminación lógica de sucursales...")
    
    with MOTOR.connect() as conexion:
        # Verificar si las columnas ya existen (PostgreSQL)
        resultado = conexion.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'SUCURSALES'
        """))
        columnas_existentes = [fila[0] for fila in resultado]
        
        print(f"📋 Columnas actuales: {columnas_existentes}")
        
        # Agregar ELIMINADA si no existe
        if 'ELIMINADA' not in columnas_existentes and 'eliminada' not in columnas_existentes:
            print("➕ Agregando columna ELIMINADA...")
            conexion.execute(text("""
                ALTER TABLE "SUCURSALES" 
                ADD COLUMN "ELIMINADA" BOOLEAN DEFAULT FALSE
            """))
            conexion.commit()
            print("✅ Columna ELIMINADA agregada")
        else:
            print("⚠️  Columna ELIMINADA ya existe")
        
        # Agregar FECHA_ELIMINACION si no existe
        if 'FECHA_ELIMINACION' not in columnas_existentes and 'fecha_eliminacion' not in columnas_existentes:
            print("➕ Agregando columna FECHA_ELIMINACION...")
            conexion.execute(text("""
                ALTER TABLE "SUCURSALES" 
                ADD COLUMN "FECHA_ELIMINACION" TIMESTAMP
            """))
            conexion.commit()
            print("✅ Columna FECHA_ELIMINACION agregada")
        else:
            print("⚠️  Columna FECHA_ELIMINACION ya existe")
        
        # Agregar USUARIO_ELIMINO_ID si no existe
        if 'USUARIO_ELIMINO_ID' not in columnas_existentes and 'usuario_elimino_id' not in columnas_existentes:
            print("➕ Agregando columna USUARIO_ELIMINO_ID...")
            conexion.execute(text("""
                ALTER TABLE "SUCURSALES" 
                ADD COLUMN "USUARIO_ELIMINO_ID" INTEGER
            """))
            conexion.commit()
            print("✅ Columna USUARIO_ELIMINO_ID agregada")
        else:
            print("⚠️  Columna USUARIO_ELIMINO_ID ya existe")
        
        # Inicializar valores para sucursales existentes
        print("🔄 Inicializando valores para sucursales existentes...")
        conexion.execute(text("""
            UPDATE "SUCURSALES" 
            SET "ELIMINADA" = FALSE 
            WHERE "ELIMINADA" IS NULL
        """))
        conexion.commit()
        
        print("✅ Migración completada exitosamente!")
        
        # Verificar resultado
        resultado = conexion.execute(text('SELECT COUNT(*) FROM "SUCURSALES"'))
        total = resultado.fetchone()[0]
        print(f"📊 Total de sucursales en BD: {total}")
        
        resultado = conexion.execute(text('SELECT COUNT(*) FROM "SUCURSALES" WHERE "ELIMINADA" = FALSE'))
        activas = resultado.fetchone()[0]
        print(f"✅ Sucursales activas (no eliminadas): {activas}")
        
        resultado = conexion.execute(text('SELECT COUNT(*) FROM "SUCURSALES" WHERE "ELIMINADA" = TRUE'))
        eliminadas = resultado.fetchone()[0]
        print(f"🗑️  Sucursales eliminadas: {eliminadas}")

if __name__ == "__main__":
    try:
        migrar_eliminacion_logica()
        print("\n✅ Migración completada con éxito!")
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        import traceback
        traceback.print_exc()
