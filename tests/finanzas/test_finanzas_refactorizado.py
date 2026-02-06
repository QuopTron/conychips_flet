"""
Script de prueba para el módulo de Finanzas refactorizado
Prueba:
- Stats centrados en Bs
- Tabla de pedidos
- Filtros funcionales
- Búsqueda por código
- Popup de detalle de pedido
- Popup anidado de voucher
"""
import flet as ft
from features.admin.presentation.pages.vistas.FinanzasPage import FinanzasPage
from core.base_datos.ConfiguracionBD import INICIALIZAR_BASE_DATOS, OBTENER_SESION, MODELO_USUARIO

def main(page: ft.Page):
    page.title = "Test Finanzas - Refactorizado"
    page.window.width = 1400
    page.window.height = 900
    
    # Inicializar BD
    INICIALIZAR_BASE_DATOS()
    
    # Obtener usuario admin
    sesion = OBTENER_SESION()
    admin = sesion.query(MODELO_USUARIO).filter_by(EMAIL="superadmin@conychips.com").first()
    sesion.close()
    
    if not admin:
        page.add(ft.Text("❌ Error: Usuario superadmin no encontrado", color=ft.Colors.ERROR))
        return
    
    # Crear página de finanzas
    finanzas = FinanzasPage(page, admin)
    page.add(finanzas)
    
    print("\n" + "="*60)
    print("🧪 TEST MÓDULO FINANZAS")
    print("="*60)
    print("\n✅ Funcionalidades a probar:")
    print("  1. Stats centrados en Bs (verde/rojo)")
    print("  2. Tabla de pedidos con datos")
    print("  3. Búsqueda por código (#00001, #00002, etc.)")
    print("  4. Filtro por estado (Completado/Pendiente/Cancelado)")
    print("  5. Filtro por voucher (Aprobado/Rechazado/Pendiente)")
    print("  6. Click en 👁️ → Ver detalle de pedido")
    print("  7. En detalle → Click 'Ver Voucher' → Popup anidado")
    print("  8. Verificar imagen del voucher")
    print("  9. Verificar productos con ofertas (icono 🏷️)")
    print(" 10. Estados coloreados (verde/amarillo/rojo)")
    print("\n" + "="*60)
    print("💡 Instrucciones:")
    print("  • Espera a que cargue (ProgressRing)")
    print("  • Verifica stats en Bs (no USD)")
    print("  • Usa filtros y búsqueda")
    print("  • Haz click en 👁️ para ver detalles")
    print("  • En el popup, click 'Ver Voucher' si está disponible")
    print("="*60 + "\n")

if __name__ == "__main__":
    ft.app(target=main)
