
import sys
from datetime import datetime
import pytest

sys.path.insert(0, '/mnt/flox/conychips')

from features.vouchers.presentation.bloc import (
    VOUCHERS_BLOC, VouchersCargados, VouchersError,
    VoucherValidado, EstadisticasCargadas,
    CargarVouchers, CargarEstadisticas,
    AprobarVoucherEvento, RechazarVoucherEvento
)
from features.vouchers.domain.entities.Voucher import Voucher
import time

def test_cargar_vouchers():
    print("\n" + "="*60)
    print("TEST 1: Cargar vouchers pendientes")
    print("="*60)
    
    resultado = {"exito": False, "mensaje": ""}
    
    def on_estado_cambio(estado):
        if isinstance(estado, VouchersCargados):
            print(f"✓ Vouchers cargados: {len(estado.vouchers)}")
            for v in estado.vouchers[:3]:
                print(f"  - Voucher #{v.id}: S/. {v.monto} ({v.estado})")
            resultado["exito"] = True
            resultado["mensaje"] = f"{len(estado.vouchers)} vouchers cargados"
        elif isinstance(estado, VouchersError):
            print(f"✗ Error: {estado.mensaje}")
            resultado["mensaje"] = estado.mensaje
    
    VOUCHERS_BLOC.AGREGAR_LISTENER(on_estado_cambio)
    VOUCHERS_BLOC.AGREGAR_EVENTO(CargarVouchers(estado="PENDIENTE"))
    
    time.sleep(2)
    VOUCHERS_BLOC.REMOVER_LISTENER(on_estado_cambio)
    assert resultado["exito"], resultado["mensaje"]

def test_estadisticas():
    print("\n" + "="*60)
    print("TEST 2: Cargar estadísticas")
    print("="*60)
    
    resultado = {"exito": False, "mensaje": ""}
    
    def on_estado_cambio(estado):
        if isinstance(estado, EstadisticasCargadas):
            stats = estado.estadisticas
            print(f"✓ Estadísticas cargadas:")
            print(f"  - Pendientes: {stats.get('pendientes', 0)}")
            print(f"  - Aprobados: {stats.get('aprobados', 0)}")
            print(f"  - Rechazados: {stats.get('rechazados', 0)}")
            print(f"  - Monto total aprobado: S/. {stats.get('monto_total_aprobado', 0):.2f}")
            resultado["exito"] = True
            resultado["mensaje"] = f"Stats OK"
        elif isinstance(estado, VouchersError):
            print(f"✗ Error: {estado.mensaje}")
            resultado["mensaje"] = estado.mensaje
    
    VOUCHERS_BLOC.AGREGAR_LISTENER(on_estado_cambio)
    VOUCHERS_BLOC.AGREGAR_EVENTO(CargarEstadisticas())
    
    time.sleep(2)
    VOUCHERS_BLOC.REMOVER_LISTENER(on_estado_cambio)
    assert resultado["exito"], resultado["mensaje"]

def test_entity_metodos():
    print("\n" + "="*60)
    print("TEST 3: Métodos de entidad Voucher")
    print("="*60)
    
    try:
        voucher = Voucher(
            id=999,
            usuario_id=1,
            pedido_id=100,
            monto=50.00,
            metodo_pago="YAPE",
            estado="PENDIENTE",
            imagen_url="http://example.com/img.jpg",
            codigo_operacion="12345",
            fecha_subida=datetime.now(),
            validado_por=None
        )
        
        print(f"✓ Voucher creado: #{voucher.id}")
        print(f"  - es_pendiente(): {voucher.es_pendiente()}")
        print(f"  - puede_ser_validado(): {voucher.puede_ser_validado()}")
        
        voucher.aprobar(validador_id=2)
        print(f"  - Después de aprobar: {voucher.estado}")
        print(f"  - Validado por: {voucher.validado_por}")
        
        voucher2 = Voucher(
            id=998,
            usuario_id=1,
            pedido_id=101,
            monto=30.00,
            metodo_pago="PLIN",
            estado="PENDIENTE",
            imagen_url="http://example.com/img2.jpg",
            codigo_operacion="67890",
            fecha_subida=datetime.now(),
            validado_por=None
        )
        voucher2.rechazar(validador_id=2)
        print(f"  - Voucher2 después de rechazar: {voucher2.estado}")
        
        assert True
    
    except Exception as e:
        pytest.fail(str(e))

def main():
    print("\n" + "="*60)
    print("INICIANDO TESTS DE MÓDULO VOUCHERS")
    print("="*60)
    
    resultados = []
    
    exito, msg = test_entity_metodos()
    resultados.append(("Métodos de Entidad", exito, msg))
    
    exito, msg = test_estadisticas()
    resultados.append(("Estadísticas", exito, msg))
    
    exito, msg = test_cargar_vouchers()
    resultados.append(("Cargar Vouchers", exito, msg))
    
    print("\n" + "="*60)
    print("RESUMEN DE TESTS")
    print("="*60)
    
    total = len(resultados)
    exitosos = sum(1 for _, exito, _ in resultados if exito)
    
    for nombre, exito, msg in resultados:
        estado = "✓ PASS" if exito else "✗ FAIL"
        print(f"{estado} - {nombre}: {msg}")
    
    print(f"\nTotal: {exitosos}/{total} tests exitosos")
    
    if exitosos == total:
        print("\n✓ TODOS LOS TESTS PASARON")
        return 0
    else:
        print(f"\n✗ {total - exitosos} TESTS FALLARON")
        return 1

if __name__ == "__main__":
    exit(main())
