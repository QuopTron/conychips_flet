"""Test de configuración del tiempo de bloqueo de vouchers"""
from datetime import datetime, timedelta, timezone
from core.configuracion.ServicioConfiguracion import ServicioConfiguracion
from features.admin.presentation.pages.vistas.vouchers.VoucherCardBuilder import VoucherCardBuilder
from features.vouchers.domain.entities.Voucher import Voucher

print("🧪 Test de Tiempo de Bloqueo Configurable\n")
print("=" * 60)

# 1. Verificar valor por defecto
print("\n1️⃣ Verificar configuración por defecto:")
tiempo_actual = ServicioConfiguracion.obtener_valor("vouchers.tiempo_bloqueo_minutos")
print(f"   Tiempo de bloqueo: {tiempo_actual} minutos")
assert tiempo_actual == 5, "Debe ser 5 minutos por defecto"
print("   ✅ Valor por defecto correcto")

# 2. Crear voucher de prueba
print("\n2️⃣ Crear voucher de prueba:")
voucher_test = Voucher(
    id=999,
    usuario_id=1,
    monto=100,
    metodo_pago="Pago móvil",
    banco_emisor="Banco Test",
    referencia="REF123",
    imagen_url="https://test.com/img.jpg",
    estado="validado",
    fecha_validacion=datetime.now(timezone.utc) - timedelta(minutes=3),  # Hace 3 min
)
print(f"   Voucher #{voucher_test.id} validado hace 3 minutos")

# 3. Calcular bloqueo con 5 minutos
print("\n3️⃣ Calcular bloqueo (config: 5 min, transcurrido: 3 min):")
bloqueado, tiempo_restante = VoucherCardBuilder._calcular_bloqueo(voucher_test)
print(f"   Bloqueado: {bloqueado}")
print(f"   Tiempo restante: {tiempo_restante}")
assert not bloqueado, "No debe estar bloqueado (3 < 5)"
assert tiempo_restante is not None, "Debe tener tiempo restante"
print("   ✅ Voucher NO bloqueado (correcto)")

# 4. Cambiar configuración a 2 minutos
print("\n4️⃣ Cambiar tiempo de bloqueo a 2 minutos:")
ServicioConfiguracion.actualizar_valor("vouchers.tiempo_bloqueo_minutos", 2)
ServicioConfiguracion.limpiar_cache()
nuevo_tiempo = ServicioConfiguracion.obtener_valor("vouchers.tiempo_bloqueo_minutos")
print(f"   Nuevo tiempo: {nuevo_tiempo} minutos")
assert nuevo_tiempo == 2, "Debe ser 2 minutos"
print("   ✅ Configuración actualizada")

# 5. Re-calcular bloqueo con 2 minutos
print("\n5️⃣ Re-calcular bloqueo (config: 2 min, transcurrido: 3 min):")
bloqueado, tiempo_restante = VoucherCardBuilder._calcular_bloqueo(voucher_test)
print(f"   Bloqueado: {bloqueado}")
print(f"   Tiempo restante: {tiempo_restante}")
assert bloqueado, "DEBE estar bloqueado (3 > 2)"
assert tiempo_restante is None, "No debe tener tiempo restante"
print("   ✅ Voucher BLOQUEADO (correcto)")

# 6. Cambiar a 10 minutos
print("\n6️⃣ Cambiar tiempo de bloqueo a 10 minutos:")
ServicioConfiguracion.actualizar_valor("vouchers.tiempo_bloqueo_minutos", 10)
ServicioConfiguracion.limpiar_cache()
nuevo_tiempo = ServicioConfiguracion.obtener_valor("vouchers.tiempo_bloqueo_minutos")
print(f"   Nuevo tiempo: {nuevo_tiempo} minutos")

# 7. Re-calcular con 10 minutos
print("\n7️⃣ Re-calcular bloqueo (config: 10 min, transcurrido: 3 min):")
bloqueado, tiempo_restante = VoucherCardBuilder._calcular_bloqueo(voucher_test)
print(f"   Bloqueado: {bloqueado}")
print(f"   Tiempo restante: {tiempo_restante}")
assert not bloqueado, "No debe estar bloqueado (3 < 10)"
print("   ✅ Voucher NO bloqueado (correcto)")

# 8. Restaurar valor por defecto
print("\n8️⃣ Restaurar valor por defecto (5 minutos):")
ServicioConfiguracion.actualizar_valor("vouchers.tiempo_bloqueo_minutos", 5)
ServicioConfiguracion.limpiar_cache()
final = ServicioConfiguracion.obtener_valor("vouchers.tiempo_bloqueo_minutos")
print(f"   Tiempo final: {final} minutos")
assert final == 5, "Debe volver a 5 minutos"
print("   ✅ Configuración restaurada")

print("\n" + "=" * 60)
print("✅ TODOS LOS TESTS PASARON")
print("=" * 60)
print("\n📊 Resumen:")
print("   • Configuración dinámica desde BD: ✅")
print("   • Cache funcionando: ✅")
print("   • Cálculo de bloqueo adaptativo: ✅")
print("   • Persistencia en BD: ✅")
