"""
Test de Caja Negra - Flujo de Navegación Completo
Simula el recorrido de un usuario por todas las vistas
"""
import flet as ft
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
from features.admin.presentation.pages.vistas.VouchersPage import VouchersPage
from features.admin.presentation.pages.vistas.FinanzasPage import FinanzasPage
from features.gestion_usuarios.presentation.pages.PaginaGestionUsuarios import PaginaGestionUsuarios
from features.admin.presentation.pages.vistas.AuditoriaPage import AuditoriaPage
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_USUARIO


def test_flujo_navegacion(pagina: ft.Page):
    """Test del flujo completo de navegación entre todas las vistas"""
    
    print("=" * 60)
    print("🧪 TEST DE CAJA NEGRA: FLUJO DE NAVEGACIÓN")
    print("=" * 60)
    
    # 1. Obtener usuario de prueba
    print("\n1️⃣  Obteniendo usuario de prueba...")
    sesion = OBTENER_SESION()
    usuario = sesion.query(MODELO_USUARIO).filter_by(EMAIL='superadmin@conychips.com').first()
    sesion.close()
    
    if not usuario:
        print("❌ Error: Usuario no encontrado")
        return False
    print(f"✅ Usuario cargado: {usuario.EMAIL}")
    
    # 2. Crear Dashboard
    print("\n2️⃣  Cargando Dashboard...")
    dashboard = PaginaAdmin(pagina, usuario)
    pagina.add(dashboard)
    pagina.update()
    print("✅ Dashboard cargado")
    
    # 3. Navegar a Vouchers
    print("\n3️⃣  Navegando a Vouchers...")
    pagina.clean()
    vouchers = VouchersPage(pagina, usuario)
    pagina.add(vouchers)
    pagina.update()
    print("✅ Vista Vouchers cargada")
    
    # 4. Navegar a Finanzas
    print("\n4️⃣  Navegando a Finanzas...")
    pagina.clean()
    finanzas = FinanzasPage(pagina, usuario)
    pagina.add(finanzas)
    pagina.update()
    print("✅ Vista Finanzas cargada")
    
    # 5. Navegar a Usuarios
    print("\n5️⃣  Navegando a Gestión de Usuarios...")
    pagina.clean()
    usuarios = PaginaGestionUsuarios(pagina, usuario)
    pagina.add(usuarios)
    pagina.update()
    print("✅ Vista Usuarios cargada")
    
    # 6. Navegar a Auditoría
    print("\n6️⃣  Navegando a Auditoría...")
    pagina.clean()
    auditoria = AuditoriaPage(pagina, usuario)
    pagina.add(auditoria)
    pagina.update()
    print("✅ Vista Auditoría cargada")
    
    # 7. Volver al Dashboard
    print("\n7️⃣  Regresando al Dashboard...")
    pagina.clean()
    dashboard_final = PaginaAdmin(pagina, usuario)
    pagina.add(dashboard_final)
    pagina.update()
    print("✅ De vuelta en Dashboard")
    
    print("\n" + "=" * 60)
    print("✅ FLUJO DE NAVEGACIÓN COMPLETADO EXITOSAMENTE")
    print("=" * 60)
    
    return True


def main(pagina: ft.Page):
    pagina.title = "Test Flujo Navegación"
    pagina.window.width = 1400
    pagina.window.height = 900
    
    resultado = test_flujo_navegacion(pagina)
    
    if resultado:
        pagina.add(
            ft.Container(
                content=ft.Text(
                    "✅ Test completado exitosamente",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.GREEN
                ),
                alignment=ft.alignment.center,
                padding=50
            )
        )
    else:
        pagina.add(
            ft.Container(
                content=ft.Text(
                    "❌ Test falló",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.RED
                ),
                alignment=ft.alignment.center,
                padding=50
            )
        )


if __name__ == "__main__":
    ft.app(target=main)
