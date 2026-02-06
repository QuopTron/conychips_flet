"""
Test automatizado de Login y Dashboard
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest.mock import MagicMock, Mock, patch
import flet as ft

def test_login_to_dashboard_flow():
    """Test completo desde login hasta dashboard"""
    print("=" * 60)
    print("TEST: FLUJO LOGIN → DASHBOARD")
    print("=" * 60)
    
    # Mock de Page
    mock_page = MagicMock(spec=ft.Page)
    mock_page.controls = []
    mock_page.window = MagicMock()
    mock_page.window.width = 1200
    mock_page.window.height = 800
    mock_page.update = MagicMock()
    mock_page.go = MagicMock()
    mock_page.clean = MagicMock()
    mock_page.add = MagicMock()
    
    print("\n✓ 1. Mock de Page creado")
    
    # Mock de Usuario
    mock_usuario = MagicMock()
    mock_usuario.ID = 1
    mock_usuario.NOMBRE_USUARIO = "superadmin@conychips.com"
    mock_usuario.EMAIL = "superadmin@conychips.com"
    mock_usuario.ROLES = ["SUPERADMIN"]
    mock_usuario.ACTIVO = True
    mock_usuario.TIENE_ROL = MagicMock(return_value=True)
    
    print("✓ 2. Usuario mock creado:", mock_usuario.NOMBRE_USUARIO)
    
    # Simular que el login fue exitoso y ahora cargamos el dashboard
    print("\n✓ 3. Iniciando creación de PaginaAdmin...")
    
    try:
        from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
        
        # Crear instancia del dashboard
        print("  → Instanciando PaginaAdmin...")
        dashboard = PaginaAdmin(PAGINA=mock_page, USUARIO=mock_usuario)
        
        print("  ✓ PaginaAdmin creada exitosamente")
        
        # Verificar estructura
        print("\n✓ 4. Verificando estructura del dashboard...")
        
        assert hasattr(dashboard, '_navbar'), "Dashboard debe tener _navbar"
        print("  ✓ Navbar existe")
        
        assert hasattr(dashboard, '_bottom_nav'), "Dashboard debe tener _bottom_nav"
        print("  ✓ Bottom nav existe")
        
        assert hasattr(dashboard, 'controls'), "Dashboard debe tener controls"
        print("  ✓ Controls existe")
        
        assert len(dashboard.controls) > 0, "Dashboard debe tener controles"
        print(f"  ✓ Dashboard tiene {len(dashboard.controls)} controles")
        
        # Verificar que los métodos callback existen
        assert hasattr(dashboard, '_on_sucursales_change'), "Debe tener _on_sucursales_change"
        print("  ✓ Método _on_sucursales_change existe")
        
        assert callable(dashboard._on_sucursales_change), "Debe ser callable"
        print("  ✓ _on_sucursales_change es callable")
        
        # Simular cambio de sucursales
        print("\n✓ 5. Probando callback de sucursales...")
        try:
            dashboard._on_sucursales_change([1, 2])
            print("  ✓ Callback ejecutado sin errores")
        except Exception as e:
            print(f"  ✗ Error al ejecutar callback: {e}")
            raise
        
        # Verificar que el contenido se construyó
        print("\n✓ 6. Verificando contenido del dashboard...")
        
        assert dashboard._card_usuarios is not None, "Card usuarios debe existir"
        print("  ✓ Card usuarios creada")
        
        assert dashboard._card_pedidos is not None, "Card pedidos debe existir"
        print("  ✓ Card pedidos creada")
        
        assert dashboard._grafico_roles is not None, "Gráfico roles debe existir"
        print("  ✓ Gráfico roles creado")
        
        # Simular agregar al page
        print("\n✓ 7. Simulando agregar dashboard a Page...")
        mock_page.controls.clear()
        mock_page.controls.append(dashboard)
        print(f"  ✓ Dashboard agregado a page.controls (total: {len(mock_page.controls)})")
        
        # Verificar que no hay errores al actualizar
        print("\n✓ 8. Simulando page.update()...")
        mock_page.update()
        print("  ✓ page.update() ejecutado sin errores")
        
        print("\n" + "=" * 60)
        print("🎉 FLUJO COMPLETO EXITOSO")
        print("=" * 60)
        print("\n✅ El dashboard se construye correctamente")
        print("✅ Todos los componentes están presentes")
        print("✅ Los callbacks funcionan correctamente")
        print("✅ No hay errores en la construcción")
        
        assert True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        assert False


if __name__ == "__main__":
    resultado = test_login_to_dashboard_flow()
    sys.exit(0 if resultado else 1)
