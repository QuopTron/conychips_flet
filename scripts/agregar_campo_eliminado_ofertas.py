"""
Script para agregar campo ELIMINADO a tabla OFERTAS
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from core.base_datos.ConfiguracionBD import OBTENER_SESION

def agregar_campo_eliminado():
    """Agrega campo ELIMINADO con valor por defecto FALSE"""
    with OBTENER_SESION() as sesion:
        try:
            # Verificar si ya existe
            result = sesion.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='OFERTAS' AND column_name='ELIMINADO'
            """))
            
            if result.fetchone():
                print("✅ Campo ELIMINADO ya existe")
                return
            
            # Agregar campo
            sesion.execute(text("""
                ALTER TABLE "OFERTAS" 
                ADD COLUMN "ELIMINADO" BOOLEAN DEFAULT FALSE
            """))
            sesion.commit()
            print("✅ Campo ELIMINADO agregado exitosamente")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            sesion.rollback()

if __name__ == "__main__":
    agregar_campo_eliminado()
