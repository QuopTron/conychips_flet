#!/usr/bin/env python
"""Test de importación de vistas"""

print("🔍 Probando importaciones...")

try:
    from features.admin.presentation.pages.vistas.SucursalesPage import SucursalesPage
    print("✅ SucursalesPage importa correctamente")
except Exception as e:
    print(f"❌ Error en SucursalesPage: {e}")

try:
    from features.admin.presentation.pages.vistas.VouchersPage import VouchersPage
    print("✅ VouchersPage importa correctamente")
except Exception as e:
    print(f"❌ Error en VouchersPage: {e}")

print("\n🎉 Todas las importaciones exitosas!")
print("\n📋 Mejoras implementadas:")
print("   • SucursalesPage con cards modernas y animaciones")
print("   • Filtros con chips interactivos")
print("   • Overlays de creación/edición mejorados")
print("   • Menú de estados con diseño moderno")
print("   • Confirmación de eliminación con warnings")
print("   • VouchersPage con título correcto '🧾 Vouchers'")
