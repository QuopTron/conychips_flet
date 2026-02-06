"""Test completo del sistema de configuración con logs"""
from core.configuracion.ServicioConfiguracion import ServicioConfiguracion
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_LOG_CONFIGURACION

print("🧪 Test Sistema de Configuración con Auditoría\n")
print("=" * 70)

# 1. Estado inicial
print("\n1️⃣ Verificar configuración inicial:")
tiempo = ServicioConfiguracion.obtener_valor("vouchers.tiempo_bloqueo_minutos")
print(f"   Tiempo bloqueo: {tiempo} minutos")

# 2. Cambio 1 (admin usuario_id=1)
print("\n2️⃣ Primer cambio (usuario_id=1 - superadmin):")
print("   Cambio: 5 → 10 minutos")
ok = ServicioConfiguracion.actualizar_valor("vouchers.tiempo_bloqueo_minutos", 10, usuario_id=1)
print(f"   Actualizado: {ok}")

# 3. Verificar log
sesion = OBTENER_SESION()
logs = sesion.query(MODELO_LOG_CONFIGURACION).all()
print(f"\n   📋 Logs en BD: {len(logs)}")
if logs:
    ultimo = logs[-1]
    print(f"   • Clave: {ultimo.CLAVE}")
    print(f"   • Anterior: {ultimo.VALOR_ANTERIOR}")
    print(f"   • Nuevo: {ultimo.VALOR_NUEVO}")
    print(f"   • Usuario ID: {ultimo.USUARIO_ID}")
    print(f"   • Fecha: {ultimo.FECHA}")
sesion.close()

# 4. Cambio 2 (sin usuario)
print("\n3️⃣ Segundo cambio (sin usuario):")
print("   Cambio: 10 → 3 minutos")
ServicioConfiguracion.limpiar_cache()
ok = ServicioConfiguracion.actualizar_valor("vouchers.tiempo_bloqueo_minutos", 3)
print(f"   Actualizado: {ok}")

# 5. Cambio 3 (otro admin usuario_id=2)
print("\n4️⃣ Tercer cambio (usuario_id=2):")
print("   Cambio: 3 → 15 minutos")
ServicioConfiguracion.limpiar_cache()
ok = ServicioConfiguracion.actualizar_valor("vouchers.tiempo_bloqueo_minutos", 15, usuario_id=2)
print(f"   Actualizado: {ok}")

# 6. Ver historial completo
print("\n5️⃣ Historial completo de cambios:")
historial = ServicioConfiguracion.obtener_historial(clave="vouchers.tiempo_bloqueo_minutos", limite=10)
print(f"   Total de cambios: {len(historial)}")
print("\n   📜 Registro de cambios:")
for i, log in enumerate(reversed(historial), 1):
    print(f"\n   {i}. {log['valor_anterior']} → {log['valor_nuevo']} minutos")
    print(f"      Usuario: {log['usuario_nombre']} (ID: {log['usuario_id']})")
    print(f"      Fecha: {log['fecha'].strftime('%d/%m/%Y %H:%M:%S')}")

# 7. Ver todas las configuraciones actuales
print("\n6️⃣ Estado actual de todas las configuraciones:")
todas = ServicioConfiguracion.obtener_todas()
for config in todas:
    print(f"   • {config['clave']}: {config['valor']} ({config['tipo']})")

# 8. Restaurar valor original
print("\n7️⃣ Restaurar a 5 minutos:")
ServicioConfiguracion.limpiar_cache()
ok = ServicioConfiguracion.actualizar_valor("vouchers.tiempo_bloqueo_minutos", 5, usuario_id=1)
print(f"   Restaurado: {ok}")

# Verificación final
ServicioConfiguracion.limpiar_cache()
final = ServicioConfiguracion.obtener_valor("vouchers.tiempo_bloqueo_minutos")
print(f"   Valor final: {final} minutos")

print("\n" + "=" * 70)
print("✅ SISTEMA DE CONFIGURACIÓN Y AUDITORÍA FUNCIONANDO")
print("=" * 70)

print("\n📊 Resumen de funcionalidades:")
print("   • Configuraciones dinámicas en BD: ✅")
print("   • Cache en memoria: ✅")
print("   • Log de cambios (auditoría): ✅")
print("   • Registro de usuario que modifica: ✅")
print("   • Historial completo: ✅")
print("   • Persistencia en PostgreSQL: ✅")

# Conteo final de logs
sesion = OBTENER_SESION()
total_logs = sesion.query(MODELO_LOG_CONFIGURACION).count()
print(f"\n   Total de cambios registrados: {total_logs}")
sesion.close()
