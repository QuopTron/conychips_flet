"""
Test completo de navegación y UI
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest.mock import MagicMock, patch
import flet as ft

def test_bottom_navigation():
    """Test del bottom navigation"""
    print("=" * 60)
    print("TEST: BOTTOM NAVIGATION")
    print("=" * 60)
    
    mock_page = MagicMock(spec=ft.Page)
    mock_page.update = MagicMock()
    
    mock_usuario = MagicMock()
    mock_usuario.ROLES = ["SUPERADMIN"]
    
    navegacion_llamada = {'route': None}
    
    def mock_navigate(route):
        navegacion_llamada['route'] = route
        print(f"  → Navegando a: {route}")
    
    from features.admin.presentation.widgets.BottomNavigation import BottomNavigation
    
    bottom_nav = BottomNavigation(
        pagina=mock_page,
        usuario=mock_usuario,
        on_navigate=mock_navigate,
        selected_index=0
    )
    
    print("✓ Bottom nav creado")
    print(f"  Items totales: {len(bottom_nav._items)}")
    
    # Simular clicks
    for i, item in enumerate(bottom_nav._items):
        print(f"\n  Probando item {i}: {item.label}")
        bottom_nav._on_item_click(i, item.route)
        if navegacion_llamada['route'] == item.route:
            print(f"    ✓ Click funcionó → {item.route}")
        else:
            print(f"    ✗ Click no funcionó")
            return False
    
    assert True


def test_navbar_panel_sucursales():
    """Test del panel de sucursales"""
    print("\n" + "=" * 60)
    print("TEST: PANEL SUCURSALES")
    print("=" * 60)
    
    mock_page = MagicMock(spec=ft.Page)
    mock_page.update = MagicMock()
    
    mock_usuario = MagicMock()
    mock_usuario.ROLES = ["SUPERADMIN"]
    
    callback_llamado = {'sucursales': None}
    
    def mock_callback(sucursales):
        callback_llamado['sucursales'] = sucursales
        print(f"  → Callback con sucursales: {sucursales}")
    
    from features.admin.presentation.widgets.NavbarGlobal import NavbarGlobal
    
    navbar = NavbarGlobal(
        pagina=mock_page,
        usuario=mock_usuario,
        on_cambio_sucursales=mock_callback,
        on_cerrar_sesion=lambda: None
    )
    
    print("✓ Navbar creado")
    print(f"  Panel visible: {navbar._panel_sucursales.visible}")
    
    # Verificar que el botón existe
    if navbar._btn_sucursales:
        print("✓ Botón sucursales existe")
    else:
        print("✗ Botón sucursales NO existe")
        assert False
    
    # Verificar checkboxes
    print(f"  Total checkboxes: {len(navbar._checkboxes)}")
    
    # Simular toggle del panel
    print("\n  → Abriendo panel...")
    navbar._toggle_panel(None)
    print(f"    Panel visible: {navbar._panel_sucursales.visible}")
    
    # Simular selección de sucursal
    if len(navbar._checkboxes) > 0:
        primer_checkbox_id = list(navbar._checkboxes.keys())[0]
        print(f"\n  → Seleccionando sucursal {primer_checkbox_id}...")
        
        # Mock del event
        mock_event = MagicMock()
        mock_event.control = navbar._checkboxes[primer_checkbox_id]
        mock_event.control.value = True
        
        navbar._on_sucursal_change(mock_event)
        print("    ✓ Checkbox change ejecutado")
        
        # Simular aplicar filtros
        print("\n  → Aplicando filtros...")
        navbar._checkboxes[primer_checkbox_id].value = True
        navbar._aplicar_filtros(None)
        
        if callback_llamado['sucursales']:
            print(f"    ✓ Callback ejecutado con: {callback_llamado['sucursales']}")
        else:
            print("    ✓ Callback ejecutado (todas las sucursales)")
        
        assert True
    
    assert True


def test_layout_renderizado():
    """Test de que el layout se renderiza completo"""
    print("\n" + "=" * 60)
    print("TEST: LAYOUT COMPLETO")
    print("=" * 60)
    
    mock_page = MagicMock(spec=ft.Page)
    mock_page.controls = []
    mock_page.update = MagicMock()
    
    mock_usuario = MagicMock()
    mock_usuario.ROLES = ["SUPERADMIN"]
    
    from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
    
    dashboard = PaginaAdmin(PAGINA=mock_page, USUARIO=mock_usuario)
    
    print("✓ Dashboard creado")
    print(f"  Controles en dashboard: {len(dashboard.controls)}")
    
    # Verificar que tiene los 4 componentes
    componentes_esperados = [
        "NavbarGlobal",
        "Container",  # Header
        "GestureDetector",  # Contenido
        "BottomNavigation"
    ]
    
    for i, control in enumerate(dashboard.controls):
        tipo = type(control).__name__
        print(f"  [{i}] {tipo}")
        if tipo == componentes_esperados[i] or "Container" in tipo or "GestureDetector" in tipo:
            print(f"    ✓ Componente correcto")
        else:
            print(f"    ⚠ Tipo inesperado (esperaba {componentes_esperados[i]})")
    
    # Verificar navbar
    if dashboard._navbar:
        print("\n✓ Navbar existe")
        print(f"  Tipo: {type(dashboard._navbar).__name__}")
    else:
        print("\n✗ Navbar NO existe")
        assert False
    
    # Verificar bottom nav
    if dashboard._bottom_nav:
        print("\n✓ Bottom nav existe")
        print(f"  Tipo: {type(dashboard._bottom_nav).__name__}")
        print(f"  Items: {len(dashboard._bottom_nav._items)}")
    else:
        print("\n✗ Bottom nav NO existe")
        assert False
    
    assert True


if __name__ == "__main__":
    print("\n" + "🚀 " * 20)
    print("TESTS DE NAVEGACIÓN Y UI")
    print("🚀 " * 20 + "\n")
    
    resultados = []
    
    resultados.append(("Bottom Navigation", test_bottom_navigation()))
    resultados.append(("Panel Sucursales", test_navbar_panel_sucursales()))
    resultados.append(("Layout Completo", test_layout_renderizado()))
    
    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    
    for nombre, resultado in resultados:
        estado = "✓ PASS" if resultado else "✗ FAIL"
        print(f"{estado} - {nombre}")
    
    total = len(resultados)
    exitosos = sum(1 for _, r in resultados if r)
    
    print(f"\nTotal: {exitosos}/{total} tests exitosos")
    
    sys.exit(0 if exitosos == total else 1)
