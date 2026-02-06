"""
Migración para PostgreSQL - Actualiza tabla OFERTAS y crea OFERTA_SUCURSAL
"""
from sqlalchemy import text
from core.base_datos.ConfiguracionBD import MOTOR, OBTENER_SESION

def migrar():
    print("🔄 Iniciando migración de ofertas (PostgreSQL)...")
    
    with MOTOR.begin() as conn:
        # 1. Agregar columna NOMBRE
        try:
            conn.execute(text('ALTER TABLE "OFERTAS" ADD COLUMN "NOMBRE" VARCHAR(100)'))
            print("✅ Columna NOMBRE agregada")
        except Exception as e:
            print(f"⚠️ NOMBRE: {e}")
        
        # 2. Agregar columna TIPO
        try:
            conn.execute(text('ALTER TABLE "OFERTAS" ADD COLUMN "TIPO" VARCHAR(50) DEFAULT \'DESCUENTO\''))
            print("✅ Columna TIPO agregada")
        except Exception as e:
            print(f"⚠️ TIPO: {e}")
        
        # 3. Agregar columna APLICAR_TODAS_SUCURSALES
        try:
            conn.execute(text('ALTER TABLE "OFERTAS" ADD COLUMN "APLICAR_TODAS_SUCURSALES" BOOLEAN DEFAULT TRUE'))
            print("✅ Columna APLICAR_TODAS_SUCURSALES agregada")
        except Exception as e:
            print(f"⚠️ APLICAR_TODAS_SUCURSALES: {e}")
        
        # 4. Crear tabla OFERTA_SUCURSAL
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS "OFERTA_SUCURSAL" (
                    "ID" SERIAL PRIMARY KEY,
                    "OFERTA_ID" INTEGER NOT NULL REFERENCES "OFERTAS"("ID") ON DELETE CASCADE,
                    "SUCURSAL_ID" INTEGER NOT NULL REFERENCES "SUCURSALES"("ID"),
                    "FECHA_FIN_ESPECIFICA" TIMESTAMP,
                    "ACTIVA" BOOLEAN DEFAULT TRUE
                )
            """))
            print("✅ Tabla OFERTA_SUCURSAL creada")
        except Exception as e:
            print(f"⚠️ OFERTA_SUCURSAL: {e}")
    
    # 5. Actualizar datos existentes
    try:
        with OBTENER_SESION() as sesion:
            from core.base_datos.ConfiguracionBD import MODELO_OFERTA
            
            # Actualizar ofertas sin nombre
            ofertas = sesion.query(MODELO_OFERTA).all()
            for oferta in ofertas:
                if not oferta.NOMBRE or oferta.NOMBRE == '':
                    oferta.NOMBRE = f"Oferta {oferta.DESCUENTO_PORCENTAJE}% - {oferta.PRODUCTO.NOMBRE}"
                    print(f"📝 Actualizado: {oferta.NOMBRE}")
            
            sesion.commit()
            print(f"✅ {len(ofertas)} ofertas actualizadas")
    except Exception as e:
        print(f"⚠️ Error actualizando datos: {e}")
    
    print("✅ Migración completada")

if __name__ == "__main__":
    migrar()
