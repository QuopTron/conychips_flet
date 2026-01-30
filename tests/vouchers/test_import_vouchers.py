import sys
sys.path.insert(0, '/mnt/flox/conychips')

print("Importando VouchersPage...")
try:
    from features.admin.presentation.pages.vistas.VouchersPage import VouchersPage
    print("✓ VouchersPage importado correctamente")
    print(f"  Clase: {VouchersPage}")
    print(f"  Módulo: {VouchersPage.__module__}")
except Exception as e:
    print(f"✗ Error al importar VouchersPage:")
    import traceback
    traceback.print_exc()
    exit(1)

print("\nVerificando BLoC...")
try:
    from features.vouchers.presentation.bloc import VOUCHERS_BLOC
    print("✓ VOUCHERS_BLOC importado correctamente")
    print(f"  Instancia: {VOUCHERS_BLOC}")
except Exception as e:
    print(f"✗ Error al importar VOUCHERS_BLOC:")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n✓ Todo OK - VouchersPage debería funcionar")
