import asyncio
from features.autenticacion.domain.usecases.IniciarSesion import IniciarSesion
from features.autenticacion.data.RepositorioAutenticacionImpl import RepositorioAutenticacionImpl

async def test_login():
    print("="*60)
    print("TEST DE LOGIN")
    print("="*60)
    
    repo = RepositorioAutenticacionImpl()
    login = IniciarSesion(repo)
    
    print("\nIntentando login...")
    print("  Email: superadmin@conychips.com")
    print("  Password: SuperAdmin123.")
    
    resultado = await login.EJECUTAR(
        EMAIL='superadmin@conychips.com',
        CONTRASENA='SuperAdmin123.',
        APP_TOKEN=None
    )
    
    print("\nResultado:")
    print(f"  EXITO: {resultado['EXITO']}")
    
    if resultado['EXITO']:
        print(f"  ✓ Usuario: {resultado['USUARIO'].EMAIL}")
        print(f"  ✓ Access Token: {'ACCESS_TOKEN' in resultado}")
        print(f"  ✓ Refresh Token: {'REFRESH_TOKEN' in resultado}")
        print(f"  ✓ App Token: {'APP_TOKEN' in resultado}")
        
        if 'ACCESS_TOKEN' in resultado:
            token = resultado['ACCESS_TOKEN']
            print(f"\n  Access Token: {token[:50]}...")
    else:
        print(f"  ✗ ERROR: {resultado.get('ERROR')}")
        print(f"  ✗ CODIGO: {resultado.get('CODIGO')}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    asyncio.run(test_login())
