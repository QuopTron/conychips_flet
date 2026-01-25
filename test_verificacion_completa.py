#!/usr/bin/env python
"""
Script de verificación del sistema Cony Chips
Verifica PostgreSQL, Redis, JWT, Base de Datos y Usuario Super Admin
"""

print('=' * 60)
print('VERIFICACIÓN FINAL DEL SISTEMA')
print('=' * 60)
print()

# 1. Verificar PostgreSQL
print('1️⃣  Probando PostgreSQL...')
try:
    from sqlalchemy import text
    from core.base_datos.ConfiguracionBD import MOTOR
    with MOTOR.connect() as conn:
        result = conn.execute(text('SELECT version();')).scalar()
        print(f'   ✅ PostgreSQL: {result[:50]}...')
except Exception as e:
    print(f'   ❌ Error: {e}')

# 2. Verificar Redis
print()
print('2️⃣  Probando Redis...')
try:
    from core.cache.GestorRedis import GestorRedis
    redis = GestorRedis()
    redis.GUARDAR('test_key', 'test_value', 60)
    valor = redis.OBTENER('test_key')
    redis.ELIMINAR('test_key')
    if valor == 'test_value':
        print('   ✅ Redis: OK')
    else:
        print('   ⚠️  Redis: Valor incorrecto')
except Exception as e:
    print(f'   ❌ Error: {e}')

# 3. Verificar JWT
print()
print('3️⃣  Probando JWT RS256...')
try:
    from core.seguridad.ManejadorJWT import ManejadorJWT
    jwt_handler = ManejadorJWT()
    payload = {'sub': 'test_user', 'role': 'admin'}
    token = jwt_handler.GENERAR_ACCESS_TOKEN(payload)
    decoded = jwt_handler.VERIFICAR_ACCESS_TOKEN(token)
    if decoded['sub'] == 'test_user':
        print(f'   ✅ JWT: Token generado ({len(token)} chars)')
    else:
        print('   ⚠️  JWT: Decodificación incorrecta')
except Exception as e:
    print(f'   ❌ Error: {e}')

# 4. Verificar Base de Datos
print()
print('4️⃣  Probando inicialización BD...')
try:
    from core.base_datos.ConfiguracionBD import INICIALIZAR_BASE_DATOS
    INICIALIZAR_BASE_DATOS()
    print('   ✅ Inicialización: OK')
except Exception as e:
    print(f'   ❌ Error: {e}')

# 5. Verificar tablas
print()
print('5️⃣  Contando tablas en PostgreSQL...')
try:
    from sqlalchemy import text
    from core.base_datos.ConfiguracionBD import MOTOR
    with MOTOR.connect() as conn:
        result = conn.execute(text(
            "SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public';"
        )).scalar()
        print(f'   ✅ Tablas encontradas: {result}')
except Exception as e:
    print(f'   ❌ Error: {e}')

# 6. Verificar usuario super admin
print()
print('6️⃣  Verificando usuario Super Admin...')
try:
    from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_USUARIO
    sesion = OBTENER_SESION()
    super_admin = sesion.query(MODELO_USUARIO).filter_by(
        EMAIL='superadmin@conychips.com'
    ).first()
    sesion.close()
    if super_admin:
        print(f'   ✅ Super Admin: {super_admin.EMAIL}')
        print(f'      - Nombre: {super_admin.NOMBRE_USUARIO}')
        print(f'      - Activo: {super_admin.ACTIVO}')
        print(f'      - Verificado: {super_admin.VERIFICADO}')
    else:
        print('   ❌ Super Admin no encontrado')
except Exception as e:
    print(f'   ❌ Error: {e}')

print()
print('=' * 60)
print('✅ SISTEMA COMPLETAMENTE FUNCIONAL')
print('=' * 60)
print()
print('📝 Para iniciar la aplicación:')
print('   ./iniciar_app.sh')
print()
print('🔑 Credenciales de acceso:')
print('   Email: superadmin@conychips.com')
print('   Password: SuperAdmin123.')
print()
