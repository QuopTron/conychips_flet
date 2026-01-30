"""
Test de Caja Blanca - Estructura de LayoutBase
Verifica la estructura interna y componentes
"""
import flet as ft
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from features.admin.presentation.widgets.LayoutBase import LayoutBase
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_USUARIO


def test_layout_base_estructura(pagina: ft.Page):
    """Test de la estructura interna de LayoutBase"""
    
    print("=" * 60)
    print("🔬 TEST DE CAJA BLANCA: ESTRUCTURA LAYOUTBASE")
    print("=" * 60)
    
    # 1. Crear instancia
    print("\n1️⃣  Creando instancia de LayoutBase...")
    sesion = OBTENER_SESION()
    usuario = sesion.query(MODELO_USUARIO).first()
    sesion.close()
    
    layout = LayoutBase(
        pagina=pagina,
        usuario=usuario,
        titulo_vista="Test Vista",
        index_navegacion=0
    )
    print("✅ Instancia creada")
    
    # 2. Verificar atributos privados
    print("\n2️⃣  Verificando atributos privados...")
    atributos_esperados = [
        '_pagina', '_usuario', '_titulo_vista', 
        '_navbar', '_bottom_nav', '_index_navegacion'
    ]
    
    for attr in atributos_esperados:
        if hasattr(layout, attr):
            print(f"✅ {attr} presente")
        else:
            print(f"❌ {attr} faltante")
            return False
    
    # 3. Verificar navbar
    print("\n3️⃣  Verificando navbar...")
    if layout._navbar:
        print("✅ Navbar inicializado")
        print(f"   Título: {layout._navbar._titulo_vista}")
    else:
        print("❌ Navbar no inicializado")
        return False
    
    # 4. Verificar bottom nav
    print("\n4️⃣  Verificando bottom navigation...")
    if layout._bottom_nav:
        print("✅ Bottom nav inicializado")
        print(f"   Expand: {layout._bottom_nav.expand}")
        print(f"   Height: {layout._bottom_nav.height}")
    else:
        print("❌ Bottom nav no inicializado")
        return False
    
    # 5. Verificar método construir
    print("\n5️⃣  Verificando método construir...")
    if hasattr(layout, 'construir'):
        contenido_test = ft.Container(
            content=ft.Text("Test Content"),
            height=100
        )
        layout.construir(contenido_test)
        print("✅ Método construir ejecutado")
    else:
        print("❌ Método construir no encontrado")
        return False
    
    # 6. Verificar controls
    print("\n6️⃣  Verificando controls...")
    if hasattr(layout, 'controls') and len(layout.controls) == 2:
        print("✅ Controls correctamente estructurados")
        print(f"   Número de controls: {len(layout.controls)}")
    else:
        print("❌ Controls incorrectos")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ESTRUCTURA LAYOUTBASE VALIDADA")
    print("=" * 60)
    
    return True


def main(pagina: ft.Page):
    pagina.title = "Test Estructura LayoutBase"
    pagina.window.width = 1200
    pagina.window.height = 800
    
    resultado = test_layout_base_estructura(pagina)
    
    if resultado:
        pagina.add(
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        "✅ Estructura validada",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.GREEN
                    ),
                    ft.Text(
                        "Todos los componentes internos están correctos",
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
