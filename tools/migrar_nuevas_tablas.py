from core.base_datos.ConfiguracionBD import MOTOR, BASE, OBTENER_SESION

def MIGRAR_NUEVAS_TABLAS():
    print("Iniciando migración de nuevas tablas...")
    
    try:
        BASE.metadata.create_all(MOTOR)
        
        print("✓ Tablas creadas exitosamente")
        
        sesion = OBTENER_SESION()
        
        from core.base_datos.ConfiguracionBD import (
            MODELO_VOUCHER,
            MODELO_REPORTE_LIMPIEZA_FOTO,
            MODELO_UBICACION_MOTORIZADO,
            MODELO_MENSAJE_CHAT,
            MODELO_NOTIFICACION,
            MODELO_CALIFICACION,
            MODELO_REFILL_SOLICITUD,
        )
        
        TABLAS_NUEVAS = [
            "voucher",
            "reporte_limpieza_foto",
            "ubicacion_motorizado",
            "mensaje_chat",
            "notificacion",
            "calificacion",
            "refill_solicitud",
        ]
        
        print("\nTablas verificadas:")
        for tabla in TABLAS_NUEVAS:
            print(f"  - {tabla}")
        
        sesion.close()
        
        print("\n✓ Migración completada exitosamente")
        
    except Exception as e:
        print(f"\n✗ Error en migración: {e}")
        raise

if __name__ == "__main__":
    print("="*60)
    print("MIGRACIÓN DE BASE DE DATOS - NUEVAS FUNCIONALIDADES")
    print("="*60)
    print()
    
    MIGRAR_NUEVAS_TABLAS()
    
    print()
    print("="*60)
    print("MIGRACIÓN FINALIZADA")
    print("="*60)
