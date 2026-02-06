
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def MIGRAR_BD():
    print("=" * 60)
    print("MIGRACIÓN A SISTEMA DE ROLES DINÁMICOS")
    print("=" * 60)
    print()
    
    respuesta = input("⚠️  Esto eliminará la base de datos actual y creará una nueva.\n¿Continuar? (s/n): ")
    
    if respuesta.lower() != 's':
        print("❌ Migración cancelada")
        return
    
    print("\n📦 Importando módulos...")
    from core.base_datos.ConfiguracionBD import RUTA_BD, INICIALIZAR_BASE_DATOS
    import asyncio
    
    if os.path.exists(RUTA_BD):
        print(f"\n🗑️  Eliminando BD antigua: {RUTA_BD}")
        os.remove(RUTA_BD)
        print("✅ BD antigua eliminada")
    else:
        print(f"\n⚠️  No se encontró BD anterior en: {RUTA_BD}")
    
    print("\n🔨 Creando nueva base de datos...")
    asyncio.run(INICIALIZAR_BASE_DATOS())
    
    print("\n" + "=" * 60)
    print("✅ MIGRACIÓN COMPLETADA CON ÉXITO")
    print("=" * 60)
    print()
    print("📋 Resumen de cambios:")
    print("  • Campos de BD optimizados (tamaños reducidos)")
    print("  • Sistema de roles dinámicos activado")
    print("  • Solo rol 'super_admin' predefinido")
    print("  • Usuario super admin creado")
    print()
    print("🔑 Credenciales de Super Admin:")
    print("  Email: superadmin@conychips.com")
    print("  Contraseña: SuperAdmin123.")
    print()
    print("⚠️  IMPORTANTE: Cambia esta contraseña en producción")
    print()
    print("📖 Para más información, revisa README.md")
    print("=" * 60)

if __name__ == "__main__":
    MIGRAR_BD()
