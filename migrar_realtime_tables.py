"""
Migración: Añadir tablas para sistema realtime
- ALERTAS_COCINA: Alertas enviadas desde atención a cocina
- EVENTOS_REALTIME: Registro de todos los eventos realtime para auditoría
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text
from core.base_datos.ConfiguracionBD import (
    MOTOR,
    BASE,
    MODELO_ALERTA_COCINA,
    MODELO_EVENTO_REALTIME,
    OBTENER_SESION
)

def migrar():
    print("=" * 60)
    print("🔄 Migración: Añadir tablas sistema realtime")
    print("=" * 60)
    
    try:
        # Crear tablas nuevas
        print("\n📦 Creando nuevas tablas...")
        BASE.metadata.create_all(MOTOR, tables=[
            MODELO_ALERTA_COCINA.__table__,
            MODELO_EVENTO_REALTIME.__table__
        ])
        print("✅ Tablas creadas: ALERTAS_COCINA, EVENTOS_REALTIME")
        
        # Verificar columnas
        sesion = OBTENER_SESION()
        
        # Verificar ALERTAS_COCINA
        result = sesion.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'ALERTAS_COCINA'
        """))
        columnas_alertas = [row[0] for row in result.fetchall()]
        print(f"\n✅ ALERTAS_COCINA columnas: {len(columnas_alertas)}")
        print(f"   {', '.join(columnas_alertas)}")
        
        # Verificar EVENTOS_REALTIME
        result = sesion.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'EVENTOS_REALTIME'
        """))
        columnas_eventos = [row[0] for row in result.fetchall()]
        print(f"\n✅ EVENTOS_REALTIME columnas: {len(columnas_eventos)}")
        print(f"   {', '.join(columnas_eventos)}")
        
        sesion.close()
        
        print("\n" + "=" * 60)
        print("✅ Migración completada exitosamente")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error en migración: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    migrar()
