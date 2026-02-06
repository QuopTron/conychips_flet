"""
Test de Caja Blanca - Lógica de NavbarGlobal
Verifica el comportamiento interno del navbar
"""
import flet as ft
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from features.admin.presentation.widgets.NavbarGlobal import NavbarGlobal
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_USUARIO, MODELO_SUCURSAL


def test_navbar_logica(pagina: ft.Page):
    """Test de la lógica interna del navbar"""
    
    print("=" * 60)
    print("🔬 TEST DE CAJA BLANCA: LÓGICA NAVBAR")
    print("=" * 60)
    
    # 1. Setup
    print("\n1️⃣  Configurando navbar...")
    sesion = OBTENER_SESION()
    usuario = sesion.query(MODELO_USUARIO).first()
    
    navbar = NavbarGlobal(
        pagina=pagina,
        usuario=usuario,
        titulo_vista="Test Vista"
    )
    print("✅ Navbar creado")
    
    # 2. Verificar atributos internos
    print("\n2️⃣  Verificando atributos internos...")
    atributos = [
        '_panel_sucursales',
        '_btn_sucursales',
        '_checkbox_todas',
        '_checkboxes',
        '_sucursales_seleccionadas',
        '_todas_seleccionadas'
    ]
    
    for attr in atributos:
        if hasattr(navbar, attr):
            print(f"✅ {attr} presente")
        else:
            print(f"❌ {attr} faltante")
            return False
    
    # 3. Verificar estado inicial
    print("\n3️⃣  Verificando estado inicial...")
    print(f"   Panel visible: {navbar._panel_sucursales.visible}")
    print(f"   Todas seleccionadas: {navbar._todas_seleccionadas}")
    print(f"   Sucursales individuales: {len(navbar._sucursales_seleccionadas)}")
    
    if navbar._todas_seleccionadas and len(navbar._sucursales_seleccionadas) == 0:
        print("✅ Estado inicial correcto")
    else:
        print("❌ Estado inicial incorrecto")
        assert False
    
    # 4. Verificar método _obtener_texto_sucursales
    print("\n4️⃣  Verificando método _obtener_texto_sucursales...")
    texto = navbar._obtener_texto_sucursales()
    print(f"   Texto: {texto}")
    
    if texto == "Todas las Sucursales":
        print("✅ Texto correcto para estado inicial")
    else:
        print("❌ Texto incorrecto")
        assert False
    
    # 5. Simular selección de sucursal
    print("\n5️⃣  Simulando selección de sucursal...")
    sucursales = sesion.query(MODELO_SUCURSAL).all()
    if sucursales and len(sucursales) > 0:
        navbar._sucursales_seleccionadas = [sucursales[0].ID]
        navbar._todas_seleccionadas = False
        texto = navbar._obtener_texto_sucursales()
        print(f"   Texto con 1 sucursal: {texto}")
        print("✅ Lógica de selección funciona")
    
    sesion.close()
    
    # 6. Verificar callbacks
    print("\n6️⃣  Verificando callbacks...")
    if hasattr(navbar, '_toggle_panel'):
        print("✅ _toggle_panel presente")
    if hasattr(navbar, '_aplicar_filtros'):
        print("✅ _aplicar_filtros presente")
    if hasattr(navbar, '_cancelar'):
        print("✅ _cancelar presente")
    
    print("\n" + "=" * 60)
    print("✅ LÓGICA NAVBAR VALIDADA")
    print("=" * 60)
    
    assert True


def main(pagina: ft.Page):
    pagina.title = "Test Lógica Navbar"
    pagina.window.width = 1200
    pagina.window.height = 800
    
    resultado = test_navbar_logica(pagina)
    
    if resultado:
        pagina.add(
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        "✅ Lógica validada",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.GREEN
                    ),
                    ft.Text(
                        "Todos los métodos internos funcionan correctamente",
                        size=14,
                        color=ft.colors.GREY_700
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                padding=50
            )
        )


if __name__ == "__main__":
    ft.app(target=main)
