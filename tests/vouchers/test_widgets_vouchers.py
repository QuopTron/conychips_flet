import sys
sys.path.insert(0, '/mnt/flox/conychips')

import flet as ft
from features.vouchers.presentation.widgets import VoucherCard, EstadisticasVouchersPanel
from features.vouchers.domain.entities.Voucher import Voucher
from datetime import datetime

def test_widgets():
    print("Testing EstadisticasVouchersPanel...")
    try:
        panel = EstadisticasVouchersPanel({"pendientes": 5, "aprobados": 10, "rechazados": 2, "monto_total_aprobado": 150.50})
        print("✓ EstadisticasVouchersPanel inicializado correctamente")
        print(f"  - Tiene contenido: {panel.content is not None}")
        print(f"  - Tiene padding: {panel.padding is not None}")
    except Exception as e:
        print(f"✗ Error en EstadisticasVouchersPanel: {e}")
        pytest.fail(str(e))
    
    print("\nTesting VoucherCard...")
    try:
        voucher = Voucher(
            id=1,
            usuario_id=1,
            pedido_id=1,
            monto=50.0,
            metodo_pago="YAPE",
            estado="PENDIENTE",
            imagen_url="http://example.com/img.jpg",
            codigo_operacion="12345",
            fecha_subida=datetime.now(),
            validado_por=None
        )
        
        card = VoucherCard(
            voucher=voucher,
            on_aprobar=lambda v: print(f"Aprobar {v.id}"),
            on_rechazar=lambda v: print(f"Rechazar {v.id}"),
            on_ver_imagen=lambda v: print(f"Ver imagen {v.id}")
        )
        print("✓ VoucherCard inicializado correctamente")
        print(f"  - Tiene contenido: {card.content is not None}")
        print(f"  - Tiene elevation: {card.elevation == 2}")
    except Exception as e:
        print(f"✗ Error en VoucherCard: {e}")
        import traceback
        traceback.print_exc()
        pytest.fail(str(e))
    
    print("\n✓ Todos los widgets se inicializan correctamente")
    assert True

if __name__ == "__main__":
    success = test_widgets()
    exit(0 if success else 1)
