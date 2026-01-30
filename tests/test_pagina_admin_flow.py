"""
Test de flujo completo de PaginaAdmin
"""
import sys
import os

# Agregar path del proyecto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_imports():
    """Test 1: Verificar que todos los imports funcionan"""
    print("✓ Test 1: Verificando imports...")
    
    try:
        from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
        print("  ✓ PaginaAdmin importada")
    except Exception as e:
        print(f"  ✗ Error al importar PaginaAdmin: {e}")
        return False
    
    try:
        from features.admin.presentation.widgets.LayoutBase import LayoutBase
        print("  ✓ LayoutBase importada")
    except Exception as e:
        print(f"  ✗ Error al importar LayoutBase: {e}")
        return False
    
    try:
        from features.admin.presentation.widgets.NavbarGlobal import NavbarGlobal
        print("  ✓ NavbarGlobal importada")
    except Exception as e:
        print(f"  ✗ Error al importar NavbarGlobal: {e}")
        return False
    
    return True


def test_layout_base_structure():
    """Test 2: Verificar estructura de LayoutBase"""
    print("\n✓ Test 2: Verificando estructura de LayoutBase...")
    
    try:
        from features.admin.presentation.widgets.LayoutBase import LayoutBase
        import inspect
        
        # Verificar métodos clave
        metodos_requeridos = [
            'construir',
            '_manejar_cambio_sucursales',
            '_on_sucursales_change',
            '_crear_header_vista',
            '_cerrar_sesion'
        ]
        
        for metodo in metodos_requeridos:
            if hasattr(LayoutBase, metodo):
                print(f"  ✓ Método {metodo} existe")
            else:
                print(f"  ✗ Método {metodo} NO EXISTE")
                return False
        
        # Verificar firma de _manejar_cambio_sucursales
        sig = inspect.signature(LayoutBase._manejar_cambio_sucursales)
        print(f"  ✓ Firma _manejar_cambio_sucursales: {sig}")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pagina_admin_structure():
    """Test 3: Verificar estructura de PaginaAdmin"""
    print("\n✓ Test 3: Verificando estructura de PaginaAdmin...")
    
    try:
        from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
        import inspect
        
        # Verificar que hereda de LayoutBase
        from features.admin.presentation.widgets.LayoutBase import LayoutBase
        if issubclass(PaginaAdmin, LayoutBase):
            print("  ✓ PaginaAdmin hereda de LayoutBase")
        else:
            print("  ✗ PaginaAdmin NO hereda de LayoutBase")
            return False
        
        # Verificar métodos override
        metodos_override = [
            '_on_sucursales_change',
            '_CONSTRUIR_CONTENIDO'
        ]
        
        for metodo in metodos_override:
            if hasattr(PaginaAdmin, metodo):
                print(f"  ✓ Método {metodo} existe")
            else:
                print(f"  ✗ Método {metodo} NO EXISTE")
                return False
        
        # Verificar firma de _on_sucursales_change
        sig = inspect.signature(PaginaAdmin._on_sucursales_change)
        print(f"  ✓ Firma _on_sucursales_change: {sig}")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mock_construccion():
    """Test 4: Simular construcción de PaginaAdmin con mocks"""
    print("\n✓ Test 4: Simulando construcción de PaginaAdmin...")
    
    try:
        from unittest.mock import MagicMock, Mock
        from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
        
        # Mock de Page
        mock_page = MagicMock()
        mock_page.controls = []
        mock_page.update = MagicMock()
        
        # Mock de Usuario
        mock_usuario = MagicMock()
        mock_usuario.ID = 1
        mock_usuario.NOMBRE_USUARIO = "test_user"
        mock_usuario.NOMBRE_COMPLETO = "Test User"
        mock_usuario.ROL = "SUPERADMIN"
        mock_usuario.SUCURSAL_ID = 1
        
        print("  ✓ Mocks creados")
        
        # Intentar crear instancia
        print("  → Creando instancia de PaginaAdmin...")
        try:
            pagina = PaginaAdmin(PAGINA=mock_page, USUARIO=mock_usuario)
            print("  ✓ Instancia creada exitosamente")
            
            # Verificar atributos
            if hasattr(pagina, '_navbar'):
                print(f"  ✓ Atributo _navbar existe: {type(pagina._navbar)}")
            else:
                print("  ✗ Atributo _navbar NO EXISTE")
                return False
            
            if hasattr(pagina, '_on_sucursales_change'):
                print("  ✓ Método _on_sucursales_change existe")
            else:
                print("  ✗ Método _on_sucursales_change NO EXISTE")
                return False
            
            # Intentar llamar al callback
            print("  → Probando callback _on_sucursales_change...")
            try:
                pagina._on_sucursales_change([1, 2])
                print("  ✓ Callback ejecutado sin errores")
            except Exception as e:
                print(f"  ✗ Error al ejecutar callback: {e}")
                import traceback
                traceback.print_exc()
                return False
            
            return True
            
        except Exception as e:
            print(f"  ✗ Error al crear instancia: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f"  ✗ Error general: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_navbar_callback_flow():
    """Test 5: Verificar flujo de callback de NavbarGlobal"""
    print("\n✓ Test 5: Verificando flujo de callback NavbarGlobal...")
    
    try:
        from unittest.mock import MagicMock
        from features.admin.presentation.widgets.NavbarGlobal import NavbarGlobal
        
        # Mock de Page
        mock_page = MagicMock()
        mock_page.update = MagicMock()
        
        # Mock de Usuario
        mock_usuario = MagicMock()
        mock_usuario.ID = 1
        mock_usuario.NOMBRE_USUARIO = "test_user"
        mock_usuario.ROL = "SUPERADMIN"
        
        # Callback mock
        callback_llamado = {'count': 0, 'args': None}
        
        def mock_callback(sucursales_ids):
            callback_llamado['count'] += 1
            callback_llamado['args'] = sucursales_ids
            print(f"  → Callback llamado con: {sucursales_ids}")
        
        print("  → Creando NavbarGlobal con callback...")
        navbar = NavbarGlobal(
            pagina=mock_page,
            usuario=mock_usuario,
            on_cambio_sucursales=mock_callback,
            on_cerrar_sesion=lambda: None
        )
        
        print("  ✓ NavbarGlobal creado")
        
        # Verificar que el callback está guardado
        if hasattr(navbar, '_on_cambio_sucursales'):
            print("  ✓ Atributo _on_cambio_sucursales existe")
            print(f"  → Tipo: {type(navbar._on_cambio_sucursales)}")
            print(f"  → Callable: {callable(navbar._on_cambio_sucursales)}")
        else:
            print("  ✗ Atributo _on_cambio_sucursales NO EXISTE")
            return False
        
        # Simular cambio de sucursales
        print("  → Simulando cambio de sucursales...")
        try:
            if navbar._on_cambio_sucursales:
                navbar._on_cambio_sucursales([1, 2, 3])
                print(f"  ✓ Callback ejecutado {callback_llamado['count']} veces")
                print(f"  ✓ Argumentos recibidos: {callback_llamado['args']}")
                return True
            else:
                print("  ✗ Callback es None")
                return False
        except Exception as e:
            print(f"  ✗ Error al ejecutar callback: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("TESTS DE FLUJO DE PAGINA ADMIN")
    print("=" * 60)
    
    resultados = []
    
    # Ejecutar tests
    resultados.append(("Imports", test_imports()))
    resultados.append(("LayoutBase Structure", test_layout_base_structure()))
    resultados.append(("PaginaAdmin Structure", test_pagina_admin_structure()))
    resultados.append(("Mock Construction", test_mock_construccion()))
    resultados.append(("Navbar Callback Flow", test_navbar_callback_flow()))
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE TESTS")
    print("=" * 60)
    
    for nombre, resultado in resultados:
        estado = "✓ PASS" if resultado else "✗ FAIL"
        print(f"{estado} - {nombre}")
    
    total = len(resultados)
    exitosos = sum(1 for _, r in resultados if r)
    
    print(f"\nTotal: {exitosos}/{total} tests exitosos")
    
    if exitosos == total:
        print("\n🎉 TODOS LOS TESTS PASARON")
        sys.exit(0)
    else:
        print(f"\n❌ {total - exitosos} tests fallaron")
        sys.exit(1)
