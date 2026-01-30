import sys
sys.path.insert(0, '/mnt/flox/conychips')

def test_imports():
    print("\n" + "="*60)
    print("TEST 1: Verificando imports")
    print("="*60)
    
    try:
        from features.admin.presentation.pages.vistas.VouchersPage import VouchersPage
        print("✓ VouchersPage importado")
        
        from features.vouchers.presentation.bloc import (
            VOUCHERS_BLOC, VouchersCargados, VouchersError,
            CargarVouchers, AprobarVoucherEvento, RechazarVoucherEvento
        )
        print("✓ BLoC y eventos importados")
        
        from features.vouchers.domain.entities.Voucher import Voucher
        print("✓ Entidad Voucher importada")
        
        from features.vouchers.domain.usecases import (
            AprobarVoucher, RechazarVoucher
        )
        print("✓ Casos de uso importados")
        
        return True
    except Exception as e:
        print(f"✗ Error en imports: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_voucher_entity():
    print("\n" + "="*60)
    print("TEST 2: Verificando entidad Voucher")
    print("="*60)
    
    try:
        from features.vouchers.domain.entities.Voucher import Voucher
        from datetime import datetime
        
        voucher = Voucher(
            id=1,
            pedido_id=100,
            usuario_id=1,
            imagen_url="http://example.com/img.jpg",
            monto=50.0,
            metodo_pago="YAPE",
            estado="PENDIENTE",
            fecha_subida=datetime.now(),
            rechazado=False,
            motivo_rechazo=None
        )
        
        print(f"✓ Voucher creado: #{voucher.id}")
        print(f"  - Estado: {voucher.estado}")
        print(f"  - Rechazado: {voucher.rechazado}")
        print(f"  - Motivo: {voucher.motivo_rechazo}")
        print(f"  - Puede ser validado: {voucher.puede_ser_validado()}")
        
        voucher.rechazar(validador_id=2, motivo="Monto incorrecto en el comprobante")
        print(f"✓ Después de rechazar:")
        print(f"  - Estado: {voucher.estado}")
        print(f"  - Rechazado: {voucher.rechazado}")
        print(f"  - Motivo: {voucher.motivo_rechazo}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database():
    print("\n" + "="*60)
    print("TEST 3: Verificando estructura de BD")
    print("="*60)
    
    try:
        from core.base_datos.ConfiguracionBD import OBTENER_SESION
        from sqlalchemy import text
        
        sesion = OBTENER_SESION()
        
        
        columnas = [row[0] for row in result.fetchall()]
        sesion.close()
        
        print(f"Columnas en VOUCHERS: {', '.join(columnas)}")
        
        required = ['RECHAZADO', 'MOTIVO_RECHAZO']
        for col in required:
            if col in columnas:
                print(f"✓ Columna {col} existe")
            else:
                print(f"✗ Columna {col} NO existe")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_use_case():
    print("\n" + "="*60)
    print("TEST 4: Verificando caso de uso RechazarVoucher")
    print("="*60)
    
    try:
        from features.vouchers.domain.usecases.RechazarVoucher import RechazarVoucher
        from features.vouchers.data.RepositorioVouchersImpl import REPOSITORIO_VOUCHERS_IMPL
        
        rechazar = RechazarVoucher(REPOSITORIO_VOUCHERS_IMPL)
        
        resultado = rechazar.ejecutar(999, 1, "corto")
        print(f"Test motivo corto: {resultado}")
        
        if not resultado["exito"]:
            print("✓ Validación de motivo funciona correctamente")
        else:
            print("✗ Debería rechazar motivos cortos")
            return False
        
        resultado = rechazar.ejecutar(999999, 1, "Este es un motivo válido con más de 10 caracteres")
        print(f"Test voucher inexistente: {resultado}")
        
        if not resultado["exito"] and "no encontrado" in resultado["mensaje"].lower():
            print("✓ Validación de voucher inexistente funciona")
        else:
            print("✗ Debería detectar voucher inexistente")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_bloc():
    print("\n" + "="*60)
    print("TEST 5: Verificando BLoC")
    print("="*60)
    
    try:
        from features.vouchers.presentation.bloc import (
            VOUCHERS_BLOC,
            CargarVouchers,
            RechazarVoucherEvento,
        )
        
        print(f"✓ VOUCHERS_BLOC importado")
        print(f"  Tipo: {type(VOUCHERS_BLOC)}")
        print(f"  Estado actual: {type(VOUCHERS_BLOC.ESTADO).__name__}")
        
        assert hasattr(VOUCHERS_BLOC, 'AGREGAR_EVENTO'), "Falta método AGREGAR_EVENTO"
        assert hasattr(VOUCHERS_BLOC, 'AGREGAR_LISTENER'), "Falta método AGREGAR_LISTENER"
        assert hasattr(VOUCHERS_BLOC, 'REMOVER_LISTENER'), "Falta método REMOVER_LISTENER"
        
        print("✓ Todos los métodos del BLoC están disponibles")
        
        evento = RechazarVoucherEvento(voucher_id=1, validador_id=1, motivo="test")
        assert hasattr(evento, 'motivo'), "Falta campo motivo en RechazarVoucherEvento"
        print("✓ RechazarVoucherEvento tiene campo motivo")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("VERIFICACIÓN DE REFACTORIZACIÓN VOUCHERS")
    print("="*60)
    
    tests = [
        test_imports,
        test_voucher_entity,
        test_database,
        test_use_case,
        test_bloc,
    ]
    
    resultados = []
    for test in tests:
        try:
            resultado = test()
            resultados.append(resultado)
        except Exception as e:
            print(f"\n✗ Test falló con excepción: {e}")
            resultados.append(False)
    
    print("\n" + "="*60)
    print("RESUMEN")
    print("="*60)
    
    total = len(resultados)
    exitosos = sum(resultados)
    
    print(f"Tests ejecutados: {total}")
    print(f"Tests exitosos: {exitosos}")
    print(f"Tests fallidos: {total - exitosos}")
    
    if all(resultados):
        print("\n✓ TODOS LOS TESTS PASARON")
        sys.exit(0)
    else:
        print("\n✗ ALGUNOS TESTS FALLARON")
        sys.exit(1)
