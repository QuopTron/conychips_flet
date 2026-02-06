"""
Test de Caja Negra - Interacción con Dropdown
Verifica el comportamiento del selector de sucursales
"""
import flet as ft
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_USUARIO
import time


def test_dropdown_sucursales(pagina: ft.Page):
    """Test de interacción con el dropdown de sucursales"""
    
    print("=" * 60)
    print("🧪 TEST DE CAJA NEGRA: DROPDOWN SUCURSALES")
    print("=" * 60)
    
    # 1. Setup
    print("\n1️⃣  Configurando test...")
    sesion = OBTENER_SESION()
    usuario = sesion.query(MODELO_USUARIO).filter_by(EMAIL='superadmin@conychips.com').first()
    sesion.close()
    
    dashboard = PaginaAdmin(pagina, usuario)
    pagina.add(dashboard)
    pagina.update()
    print("✅ Dashboard listo")
    
    # 2. Verificar navbar existe
    print("\n2️⃣  Verificando navbar...")
    if hasattr(dashboard, '_navbar'):
        print("✅ Navbar encontrado")
    else:
        print("❌ Navbar no encontrado")
        assert False
    
    # 3. Verificar botón de sucursales
    print("\n3️⃣  Verificando botón de sucursales...")
    navbar = dashboard._navbar
    if hasattr(navbar, '_btn_sucursales'):
        print("✅ Botón de sucursales encontrado")
    else:
        print("❌ Botón no encontrado")
        assert False
    
    # 4. Verificar panel de sucursales
    print("\n4️⃣  Verificando panel...")
    if hasattr(navbar, '_panel_sucursales'):
        print("✅ Panel de sucursales encontrado")
        print(f"   Visible: {navbar._panel_sucursales.visible}")
    else:
        print("❌ Panel no encontrado")
        assert False
    
    print("\n" + "=" * 60)
    print("✅ TEST DE DROPDOWN COMPLETADO")
    print("=" * 60)
    
    assert True


def main(pagina: ft.Page):
    pagina.title = "Test Dropdown"
    pagina.window.width = 1400
    pagina.window.height = 900
    
    resultado = test_dropdown_sucursales(pagina)
    
    if resultado:
        pagina.add(
            ft.Container(
                content=ft.Text(
                    "✅ Dropdown funcionando correctamente",
                    size=20,
                    color=ft.colors.GREEN
                ),
                alignment=ft.alignment.center,
                padding=50
            )
        )


if __name__ == "__main__":
    ft.app(target=main)
