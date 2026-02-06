import traceback
import sys

print("=" * 60)
print("TEST: Navegación a VouchersPage")
print("=" * 60)

try:
    print("\n1. Importando módulos base...")
    from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_USUARIO
    print("   ✓ Módulos base importados")
    
    print("\n2. Obteniendo usuario admin de prueba...")
    sesion = OBTENER_SESION()
    usuario_admin = sesion.query(MODELO_USUARIO).filter(
        MODELO_USUARIO.NOMBRE_USUARIO == "superadmin"
    ).first()
    sesion.close()
    
    if not usuario_admin:
        print("   ✗ No se encontró usuario admin")
        sys.exit(1)
    print(f"   ✓ Usuario encontrado: {usuario_admin.NOMBRE_USUARIO} (ID: {usuario_admin.ID})")
    
    print("\n3. Intentando importar VouchersPage...")
    from features.admin.presentation.pages.vistas.VouchersPage import VouchersPage
    print("   ✓ VouchersPage importada correctamente")
    
    print("\n4. Verificando constructor de VouchersPage...")
    import inspect
    sig = inspect.signature(VouchersPage.__init__)
    print(f"   Parámetros: {list(sig.parameters.keys())}")
    
    print("\n5. Intentando crear instancia de VouchersPage (sin Flet)...")
    print("   NOTA: Esto fallará porque no hay ft.Page, pero veremos el error exacto")
    
    class MockPage:
        def __init__(self):
            self.controls = []
            self.dialog = None
            
        def update(self):
            pass
    
    mock_page = MockPage()
    
    try:
        vouchers_page = VouchersPage(
            PAGINA=mock_page,
            USUARIO=usuario_admin,
            ON_MENU=None,
            ON_LOGOUT=None
        )
        print("   ✓ Instancia creada (parcialmente)")
        print(f"   Tipo: {type(vouchers_page)}")
        print(f"   Controles: {len(vouchers_page.controls) if hasattr(vouchers_page, 'controls') else 'N/A'}")
        
    except Exception as e:
        print(f"   ✗ Error al crear instancia:")
        print(f"   {type(e).__name__}: {e}")
        print("\n   Traceback completo:")
        traceback.print_exc()
    
    print("\n6. Verificando imports de VouchersPage...")
    import features.admin.presentation.pages.vistas.VouchersPage as vouchers_module
    
    required_imports = [
        'ft', 'COLORES', 'TAMANOS', 'ICONOS', 'ROLES',
        'REQUIERE_ROL', 'OBTENER_SESION', 'MODELO_VOUCHER',
        'HeaderAdmin', 'ContenedorPagina', 'Notificador'
    ]
    
    for imp in required_imports:
        if hasattr(vouchers_module, imp):
            print(f"   ✓ {imp} disponible")
        else:
            print(f"   ✗ {imp} NO disponible")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETADO")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ ERROR CRÍTICO:")
    print(f"   {type(e).__name__}: {e}")
    print("\nTraceback completo:")
    traceback.print_exc()
    sys.exit(1)
