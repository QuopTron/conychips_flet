"""
Test simple de flujo completo del sistema
"""
import sys
sys.path.insert(0, '/mnt/flox/conychips')

def test_imports():
    """Verifica que todos los imports funcionan"""
    try:
        from features.admin.presentation.widgets.LayoutBase import LayoutBase
        from features.admin.presentation.widgets.NavbarGlobal import NavbarGlobal
        from features.admin.presentation.widgets.BottomNavigation import BottomNavigation
        from features.autenticacion.domain.entities.Usuario import Usuario
        import flet as ft
        print("✓ Todos los imports funcionan correctamente")
        return True
    except Exception as e:
        print(f"✗ Error en imports: {e}")
        return False

def test_usuario_entity():
    """Verifica que Usuario funciona sin NOMBRE_COMPLETO"""
    from features.autenticacion.domain.entities.Usuario import Usuario
    
    usuario = Usuario(
        ID=1,
        EMAIL="test@test.com",
        NOMBRE_USUARIO="test_user",
        ROLES=["ADMIN"]
    )
    
    # Verificar que getattr funciona
    nombre = getattr(usuario, 'NOMBRE_COMPLETO', None) or getattr(usuario, 'NOMBRE_USUARIO', 'Usuario')
    assert nombre == "test_user"
    print(f"✓ Usuario sin NOMBRE_COMPLETO funciona: {nombre}")
    return True

def test_layout_base_creation():
    """Verifica que LayoutBase se puede crear"""
    import flet as ft
    from features.admin.presentation.widgets.LayoutBase import LayoutBase
    from features.autenticacion.domain.entities.Usuario import Usuario
    
    page = ft.Page()
    usuario = Usuario(ID=1, EMAIL="test@test.com", NOMBRE_USUARIO="test", ROLES=["ADMIN"])
    
    try:
        layout = LayoutBase(
            pagina=page,
            usuario=usuario,
            titulo_vista="Test"
        )
        print("✓ LayoutBase creado correctamente")
        return True
    except Exception as e:
        print(f"✗ Error creando LayoutBase: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_navbar_global_creation():
    """Verifica que NavbarGlobal se puede crear"""
    import flet as ft
    from features.admin.presentation.widgets.NavbarGlobal import NavbarGlobal
    from features.autenticacion.domain.entities.Usuario import Usuario
    
    page = ft.Page()
    usuario = Usuario(ID=1, EMAIL="test@test.com", NOMBRE_USUARIO="test", ROLES=["ADMIN"])
    
    try:
        navbar = NavbarGlobal(
            pagina=page,
            usuario=usuario,
            on_cambio_sucursales=None,
            on_cerrar_sesion=None
        )
        print("✓ NavbarGlobal creado correctamente")
        return True
    except Exception as e:
        print(f"✗ Error creando NavbarGlobal: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 PRUEBAS RÁPIDAS DE FLUJO")
    print("="*60 + "\n")
    
    tests = [
        ("Imports", test_imports),
        ("Usuario Entity", test_usuario_entity),
        ("LayoutBase Creation", test_layout_base_creation),
        ("NavbarGlobal Creation", test_navbar_global_creation),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        print(f"\n📋 Test: {name}")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*60)
    print(f"✓ Pasados: {passed}/{len(tests)}")
    print(f"✗ Fallidos: {failed}/{len(tests)}")
    print("="*60 + "\n")
    
    sys.exit(0 if failed == 0 else 1)
