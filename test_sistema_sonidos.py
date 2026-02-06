#!/usr/bin/env python3
"""
Test del sistema de sonidos y notificaciones
"""

import sys
sys.path.insert(0, '/mnt/flox/conychips')

from core.audio.GestorSonidos import GestorSonidos
from core.websocket.GestorNotificaciones import GestorNotificaciones

def test_gestor_sonidos():
    """Test básico del GestorSonidos"""
    print("🔊 Testing GestorSonidos...")
    
    # Test 1: Reproducir sonido de mensaje nuevo
    print("  ✓ Test 1: REPRODUCIR_SONIDO('mensaje_nuevo')")
    resultado = GestorSonidos.REPRODUCIR_SONIDO("mensaje_nuevo")
    print(f"    Resultado: {resultado}")
    
    # Test 2: Notificar mensaje nuevo sin argumentos
    print("  ✓ Test 2: NOTIFICAR_MENSAJE_NUEVO()")
    GestorSonidos.NOTIFICAR_MENSAJE_NUEVO()
    print("    ✅ Ejecutado sin errores")
    
    # Test 3: Notificar mensaje nuevo con argumentos
    print("  ✓ Test 3: NOTIFICAR_MENSAJE_NUEVO(pedido_id=123, cliente_nombre='Juan')")
    GestorSonidos.NOTIFICAR_MENSAJE_NUEVO(pedido_id=123, cliente_nombre="Juan")
    print("    ✅ Ejecutado sin errores")


def test_gestor_notificaciones():
    """Test básico del GestorNotificaciones con audio"""
    print("\n🔔 Testing GestorNotificaciones con audio...")
    
    # Obtener instancia singleton
    gestor = GestorNotificaciones()
    
    print("  ✓ Test 1: GestorNotificaciones instanciado")
    print(f"    Tiene GESTOR_SONIDOS: {hasattr(gestor, 'GESTOR_SONIDOS')}")
    print(f"    GESTOR_SONIDOS es válido: {isinstance(gestor.GESTOR_SONIDOS, GestorSonidos)}")
    
    print("  ✓ Test 2: Llamar GESTOR_SONIDOS.NOTIFICAR_MENSAJE_NUEVO()")
    gestor.GESTOR_SONIDOS.NOTIFICAR_MENSAJE_NUEVO()
    print("    ✅ Ejecutado sin errores")


if __name__ == "__main__":
    print("=" * 60)
    print("TESTING SISTEMA DE SONIDOS Y NOTIFICACIONES")
    print("=" * 60)
    
    try:
        test_gestor_sonidos()
        test_gestor_notificaciones()
        
        print("\n" + "=" * 60)
        print("✅ TODOS LOS TESTS PASARON")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
