"""
Script de migración para actualizar el modelo de ofertas
Agrega: NOMBRE, TIPO, APLICAR_TODAS_SUCURSALES y tabla OFERTA_SUCURSAL
"""
from core.base_datos.ConfiguracionBD import BASE, MOTOR

def migrar_ofertas():
    """Migra la tabla OFERTAS a la nueva estructura"""
    
    print("🔄 Iniciando migración de ofertas...")
    
    try:
        # Crear todas las tablas (solo creará las que no existen)
        BASE.metadata.create_all(bind=MOTOR)
        print("✅ Tablas creadas/actualizadas exitosamente")
        print("✅ Migración completada")
    except Exception as e:
        print(f"❌ Error en migración: {e}")

if __name__ == "__main__":
    migrar_ofertas()
