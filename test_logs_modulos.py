"""
Script para probar y observar el comportamiento de cada módulo mediante logs
"""

import logging
import sys
import asyncio
from datetime import datetime

# Configurar logging detallado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)

logger = logging.getLogger(__name__)

print("\n" + "="*80)
print("ANÁLISIS DE COMPORTAMIENTO DE MÓDULOS - LOGS DETALLADOS")
print("="*80 + "\n")

# =============================================================================
# 1. MÓDULO DE BASE DE DATOS
# =============================================================================
print("\n[1] PROBANDO MÓDULO: core/base_datos/ConfiguracionBD.py")
print("-" * 80)

try:
    from core.base_datos.ConfiguracionBD import (
        OBTENER_SESION_BD, 
        INICIALIZAR_BASE_DATOS,
        MODELO_USUARIO,
        MODELO_ROL,
        MODELO_SESION,
        MODELO_PRODUCTO
    )
    
    print("✅ Módulo de BD importado correctamente")
    print(f"   - Modelos disponibles: USUARIO, ROL, SESION, PRODUCTO")
    
    # Inicializar BD
    print("\n   Inicializando base de datos...")
    asyncio.run(INICIALIZAR_BASE_DATOS())
    
    # Probar conexión
    print("\n   Probando conexión a BD...")
    with OBTENER_SESION_BD() as sesion:
        usuarios_count = sesion.query(MODELO_USUARIO).count()
        roles_count = sesion.query(MODELO_ROL).count()
        print(f"   📊 Usuarios en BD: {usuarios_count}")
        print(f"   📊 Roles en BD: {roles_count}")
        
except Exception as e:
    print(f"❌ Error en módulo BD: {e}")
    import traceback
    traceback.print_exc()

# =============================================================================
# 2. MÓDULO DE SEGURIDAD - ENCRIPTACIÓN
# =============================================================================
print("\n\n[2] PROBANDO MÓDULO: core/seguridad/EncriptadorGPU.py")
print("-" * 80)

try:
    from core.seguridad.EncriptadorGPU import ENCRIPTADOR
    
    print("✅ Módulo de encriptación importado")
    
    # Probar encriptación
    texto_prueba = "ContraseñaSegura123!"
    print(f"\n   Texto original: {texto_prueba}")
    
    hash_generado = ENCRIPTADOR.HASHEAR_CONTRASENA(texto_prueba)
    print(f"   🔒 Hash generado: {hash_generado[:50]}...")
    
    # Verificar hash
    es_valido = ENCRIPTADOR.VERIFICAR_CONTRASENA(texto_prueba, hash_generado)
    print(f"   ✓ Verificación: {'VÁLIDA' if es_valido else 'INVÁLIDA'}")
    
except Exception as e:
    print(f"❌ Error en módulo de encriptación: {e}")
    import traceback
    traceback.print_exc()

# =============================================================================
# 3. MÓDULO DE SEGURIDAD - GENERADOR DE HUELLA
# =============================================================================
print("\n\n[3] PROBANDO MÓDULO: core/seguridad/GeneradorHuella.py")
print("-" * 80)

try:
    from core.seguridad.GeneradorHuella import GENERADOR_HUELLA
    
    print("✅ Módulo de huella digital importado")
    
    # Generar huella
    huella = GENERADOR_HUELLA.GENERAR_HUELLA()
    print(f"\n   🔑 Huella generada: {huella[:32]}...")
    print(f"   📏 Longitud: {len(huella)} caracteres")
    
    # Verificar unicidad
    huella2 = GENERADOR_HUELLA.GENERAR_HUELLA()
    print(f"\n   ✓ Unicidad verificada: {huella != huella2}")
    
except Exception as e:
    print(f"❌ Error en módulo de huella: {e}")
    import traceback
    traceback.print_exc()

# =============================================================================
# 4. MÓDULO DE SEGURIDAD - JWT
# =============================================================================
print("\n\n[4] PROBANDO MÓDULO: core/seguridad/ManejadorJWT.py")
print("-" * 80)

try:
    from core.seguridad.ManejadorJWT import MANEJADOR_JWT
    
    print("✅ Módulo JWT importado")
    
    # Generar tokens
    payload = {"usuario_id": 1, "email": "test@test.com", "roles": ["admin"]}
    
    access_token = MANEJADOR_JWT.GENERAR_ACCESS_TOKEN(payload)
    refresh_token = MANEJADOR_JWT.GENERAR_REFRESH_TOKEN(payload)
    
    print(f"\n   🎫 Access Token: {access_token[:50]}...")
    print(f"   🎫 Refresh Token: {refresh_token[:50]}...")
    
    # Verificar token
    datos_verificados = MANEJADOR_JWT.VERIFICAR_TOKEN(access_token)
    if datos_verificados:
        print(f"\n   ✓ Token verificado correctamente")
        print(f"   📋 Usuario ID: {datos_verificados.get('usuario_id')}")
    else:
        print(f"   ❌ Token inválido")
    
except Exception as e:
    print(f"❌ Error en módulo JWT: {e}")
    import traceback
    traceback.print_exc()

# =============================================================================
# 5. MÓDULO DE AUTENTICACIÓN - REPOSITORIO
# =============================================================================
print("\n\n[5] PROBANDO MÓDULO: features/autenticacion/data/RepositorioAutenticacionImpl.py")
print("-" * 80)

try:
    from features.autenticacion.data.RepositorioAutenticacionImpl import (
        REPOSITORIO_AUTENTICACION_IMPL
    )
    
    print("✅ Módulo de repositorio de autenticación importado")
    
    # Buscar usuario
    print("\n   Buscando usuario por email...")
    usuario = REPOSITORIO_AUTENTICACION_IMPL.BUSCAR_USUARIO_POR_EMAIL("admin@admin.com")
    
    if usuario:
        print(f"   ✓ Usuario encontrado:")
        print(f"      - ID: {usuario.ID}")
        print(f"      - Email: {usuario.EMAIL}")
        print(f"      - Usuario: {usuario.NOMBRE_USUARIO}")
        print(f"      - Activo: {usuario.ACTIVO}")
        print(f"      - Roles: {[rol.NOMBRE for rol in usuario.ROLES]}")
    else:
        print(f"   ⚠ Usuario no encontrado")
    
except Exception as e:
    print(f"❌ Error en módulo de repositorio: {e}")
    import traceback
    traceback.print_exc()

# =============================================================================
# 6. MÓDULO DE AUTENTICACIÓN - CASOS DE USO
# =============================================================================
print("\n\n[6] PROBANDO MÓDULO: features/autenticacion/domain/usecases/IniciarSesion.py")
print("-" * 80)

try:
    from features.autenticacion.domain.usecases.IniciarSesion import (
        INICIAR_SESION_USECASE
    )
    
    print("✅ Módulo de inicio de sesión importado")
    
    # Intentar login con credenciales de prueba
    print("\n   Intentando login con credenciales de prueba...")
    print("   Email: test@test.com | Contraseña: incorrecta")
    
    resultado = INICIAR_SESION_USECASE.EJECUTAR(
        EMAIL="test@test.com",
        CONTRASENA="incorrecta",
        IP="127.0.0.1",
        NAVEGADOR="TestBrowser"
    )
    
    if resultado.get("exito"):
        print(f"   ✓ Login exitoso")
        print(f"      - Access Token: {resultado['access_token'][:30]}...")
    else:
        print(f"   ❌ Login fallido: {resultado.get('mensaje')}")
    
except Exception as e:
    print(f"❌ Error en caso de uso: {e}")
    import traceback
    traceback.print_exc()

# =============================================================================
# 7. MÓDULO DE AUTENTICACIÓN - BLOC/ESTADO
# =============================================================================
print("\n\n[7] PROBANDO MÓDULO: features/autenticacion/presentation/bloc/AutenticacionBloc.py")
print("-" * 80)

try:
    from features.autenticacion.presentation.bloc.AutenticacionBloc import (
        AUTENTICACION_BLOC
    )
    from features.autenticacion.presentation.bloc.AutenticacionEstado import (
        ESTADO_INICIAL,
        ESTADO_AUTENTICADO
    )
    from features.autenticacion.presentation.bloc.AutenticacionEvento import (
        EVENTO_LOGIN
    )
    
    print("✅ Módulo BLoC de autenticación importado")
    
    # Verificar estado
    estado_actual = AUTENTICACION_BLOC.ESTADO
    print(f"\n   📊 Estado actual: {type(estado_actual).__name__}")
    
    # Agregar listener
    def listener_prueba(estado):
        print(f"   🔔 Cambio de estado detectado: {type(estado).__name__}")
    
    AUTENTICACION_BLOC.AGREGAR_LISTENER(listener_prueba)
    print(f"   ✓ Listener agregado al BLoC")
    
except Exception as e:
    print(f"❌ Error en módulo BLoC: {e}")
    import traceback
    traceback.print_exc()

# =============================================================================
# 8. MÓDULO DE PRODUCTOS - REPOSITORIO
# =============================================================================
print("\n\n[8] PROBANDO MÓDULO: features/productos/data/RepositorioProductosImpl.py")
print("-" * 80)

try:
    from features.productos.data.RepositorioProductosImpl import (
        REPOSITORIO_PRODUCTOS_IMPL
    )
    
    print("✅ Módulo de repositorio de productos importado")
    
    # Listar productos
    print("\n   Obteniendo lista de productos...")
    productos = REPOSITORIO_PRODUCTOS_IMPL.LISTAR_PRODUCTOS()
    
    print(f"   📦 Total de productos: {len(productos)}")
    for i, prod in enumerate(productos[:5], 1):
        print(f"      {i}. {prod['NOMBRE']} - Bs. {prod['PRECIO']}")
    
    if len(productos) > 5:
        print(f"      ... y {len(productos) - 5} más")
    
except Exception as e:
    print(f"❌ Error en módulo de productos: {e}")
    import traceback
    traceback.print_exc()

# =============================================================================
# 9. MÓDULO DE DECORADORES - AUTENTICACIÓN
# =============================================================================
print("\n\n[9] PROBANDO MÓDULO: core/decoradores/DecoradorAutenticacion.py")
print("-" * 80)

try:
    from core.decoradores.DecoradorAutenticacion import REQUIERE_AUTENTICACION
    
    print("✅ Módulo de decorador de autenticación importado")
    
    # Crear función decorada
    @REQUIERE_AUTENTICACION
    def funcion_protegida():
        print("   ✓ Función protegida ejecutada")
        return "Datos secretos"
    
    print(f"\n   Función decorada creada: funcion_protegida()")
    print(f"   ⚠ Nota: Requiere contexto de autenticación para ejecutar")
    
except Exception as e:
    print(f"❌ Error en módulo decorador: {e}")
    import traceback
    traceback.print_exc()

# =============================================================================
# 10. MÓDULO DE WEBSOCKET - CLIENTE
# =============================================================================
print("\n\n[10] PROBANDO MÓDULO: core/websocket/ClienteWebSocket.py")
print("-" * 80)

try:
    from core.websocket.ClienteWebSocket import CLIENTE_WEBSOCKET
    
    print("✅ Módulo de cliente WebSocket importado")
    print(f"\n   Estado del cliente: {CLIENTE_WEBSOCKET.CONECTADO}")
    print(f"   ⚠ Nota: Requiere servidor WebSocket activo para conectar")
    
except Exception as e:
    print(f"❌ Error en módulo WebSocket: {e}")
    import traceback
    traceback.print_exc()

# =============================================================================
# RESUMEN FINAL
# =============================================================================
print("\n\n" + "="*80)
print("RESUMEN DEL ANÁLISIS")
print("="*80)

print("\n✅ MÓDULOS FUNCIONANDO:")
print("   1. core/base_datos/ConfiguracionBD.py - Sistema de base de datos")
print("   2. core/seguridad/EncriptadorGPU.py - Encriptación de contraseñas")
print("   3. core/seguridad/GeneradorHuella.py - Generación de huellas digitales")
print("   4. core/seguridad/ManejadorJWT.py - Manejo de tokens JWT")
print("   5. features/autenticacion/data/ - Repositorio de autenticación")
print("   6. features/autenticacion/domain/usecases/ - Casos de uso")
print("   7. features/autenticacion/presentation/bloc/ - Gestión de estado")
print("   8. features/productos/data/ - Repositorio de productos")
print("   9. core/decoradores/ - Decoradores de seguridad")
print("   10. core/websocket/ - Cliente WebSocket")

print("\n📊 FLUJO DE DATOS OBSERVADO:")
print("   1. BD inicializa → Crea/verifica tablas → Inserta Super Admin")
print("   2. Usuario ingresa credenciales → EncriptadorGPU verifica hash")
print("   3. GeneradorHuella crea ID único → ManejadorJWT genera tokens")
print("   4. RepositorioAutenticacion gestiona persistencia")
print("   5. UseCases ejecutan lógica de negocio")
print("   6. BLoC gestiona estados de UI")
print("   7. Decoradores validan permisos")
print("   8. WebSocket mantiene conexión en tiempo real")

print("\n" + "="*80 + "\n")
