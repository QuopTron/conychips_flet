import asyncio
import sys
from datetime import datetime

async def VERIFICAR_POSTGRESQL():
    print("\n" + "="*60)
    print("1. VERIFICANDO POSTGRESQL")
    print("="*60)
    
    try:
        from core.base_datos.ConfiguracionBD import OBTENER_SESION, MOTOR
        from sqlalchemy import text
        
        SESION = OBTENER_SESION()
        
        resultado = SESION.execute(text("SELECT version();")).fetchone()
        print(f"✓ PostgreSQL conectado")
        print(f"  Versión: {resultado[0].split(',')[0]}")
        
        print(f"  Pool size: {MOTOR.pool.size()}")
        
        SESION.close()
        return True
        
    except Exception as e:
        print(f"✗ Error conectando a PostgreSQL: {e}")
        return False

async def VERIFICAR_REDIS():
    print("\n" + "="*60)
    print("2. VERIFICANDO REDIS")
    print("="*60)
    
    try:
        from core.cache.GestorRedis import GestorRedis
        
        redis = GestorRedis()
        
        if redis.CONEXION.ping():
            print("✓ Redis conectado")
            
            info = redis.CONEXION.info()
            print(f"  Versión: {info.get('redis_version', 'N/A')}")
            print(f"  Memoria usada: {info.get('used_memory_human', 'N/A')}")
            
            redis.GUARDAR_CACHE("test:verificacion", {"estado": "ok"}, 10)
            valor = redis.OBTENER_CACHE("test:verificacion")
            
            if valor and valor.get("estado") == "ok":
                print("✓ Test de cache exitoso")
            
            return True
        else:
            print("✗ Redis no responde a ping")
            return False
            
    except Exception as e:
        print(f"✗ Error conectando a Redis: {e}")
        return False

async def VERIFICAR_JWT():
    print("\n" + "="*60)
    print("3. VERIFICANDO SISTEMA JWT")
    print("="*60)
    
    try:
        from core.seguridad.ManejadorJWT import ManejadorJWT
        
        jwt = ManejadorJWT()
        
        app_token = jwt.GENERAR_APP_TOKEN(
            DISPOSITIVO_ID="test-device-123",
            METADATA={"plataforma": "test"}
        )
        
        payload_app = jwt.VERIFICAR_TOKEN(app_token)
        
        if payload_app and payload_app.get("tipo") == "app":
            print("✓ App Token RS256: OK")
            print(f"  JTI: {payload_app.get('jti')[:16]}...")
        else:
            print("✗ Error verificando App Token")
            return False
        
        access_token = jwt.GENERAR_ACCESS_TOKEN(
            USUARIO_ID=1,
            EMAIL="test@ejemplo.com",
            ROLES=["admin"],
            PERMISOS=["ver_todo"],
            APP_TOKEN_ID=payload_app.get("jti")
        )
        
        payload_access = jwt.VERIFICAR_TOKEN(access_token)
        
        if payload_access and payload_access.get("tipo") == "access":
            print("✓ Access Token RS256: OK")
        else:
            print("✗ Error verificando Access Token")
            return False
        
        refresh_token = jwt.GENERAR_REFRESH_TOKEN(
            USUARIO_ID=1,
            APP_TOKEN_ID=payload_app.get("jti")
        )
        
        payload_refresh = jwt.VERIFICAR_TOKEN(refresh_token)
        
        if payload_refresh and payload_refresh.get("tipo") == "refresh":
            print("✓ Refresh Token RS256: OK")
        else:
            print("✗ Error verificando Refresh Token")
            return False
        
        jwt.REVOCAR_TOKEN(refresh_token)
        
        payload_revocado = jwt.VERIFICAR_TOKEN(refresh_token)
        
        if not payload_revocado:
            print("✓ Revocación de tokens: OK")
        else:
            print("✗ Token revocado sigue siendo válido")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error en sistema JWT: {e}")
        import traceback
        traceback.print_exc()
        return False

async def MAIN():
    print("="*60)
    print("VERIFICACIÓN DEL SISTEMA CONY CHIPS")
    print("="*60)
    
    RESULTADOS = {}
    
    RESULTADOS["postgresql"] = await VERIFICAR_POSTGRESQL()
    RESULTADOS["redis"] = await VERIFICAR_REDIS()
    RESULTADOS["jwt"] = await VERIFICAR_JWT()
    
    print("\n" + "="*60)
    print("RESUMEN")
    print("="*60)
    
    EXITOSOS = sum(1 for v in RESULTADOS.values() if v)
    TOTAL = len(RESULTADOS)
    
    for nombre, resultado in RESULTADOS.items():
        simbolo = "✓" if resultado else "✗"
        print(f"{simbolo} {nombre.upper()}")
    
    print(f"\n{EXITOSOS}/{TOTAL} verificaciones exitosas")
    print("="*60)
    
    return EXITOSOS == TOTAL

if __name__ == "__main__":
    try:
        resultado = asyncio.run(MAIN())
        sys.exit(0 if resultado else 1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
