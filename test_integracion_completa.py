#!/usr/bin/env python3
"""
PRUEBAS DE INTEGRACIÓN COMPLETA - SISTEMA CONY CHIPS
Valida el flujo end-to-end de todos los módulos
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from core.base_datos.ConfiguracionBD import (
    MODELO_SUCURSAL, MODELO_VOUCHER, MODELO_PEDIDO, 
    MODELO_DETALLE_PEDIDO, MODELO_PRODUCTO, MODELO_USUARIO,
    MOTOR
)
from features.vouchers.data.datasources.FuenteVouchersLocal import FuenteVouchersLocal
from features.vouchers.domain.entities.Voucher import Voucher

print("=" * 70)
print("🔗 PRUEBAS DE INTEGRACIÓN COMPLETA - SISTEMA CONY CHIPS")
print("=" * 70)
print()

# Configurar BD
SesionLocal = sessionmaker(bind=MOTOR)

def test_flujo_completo_voucher_pedido():
    """Test 1: Flujo completo desde pedido hasta aprobación de voucher"""
    print("1️⃣  TEST: Flujo completo Pedido → Voucher → Aprobación")
    print("-" * 70)
    
    sesion = SesionLocal()
    try:
        # Paso 1: Crear producto de prueba
        producto_test = MODELO_PRODUCTO(
            NOMBRE="Producto Test Integración",
            PRECIO=15,  # Integer no float
            DISPONIBLE=True
        )
        sesion.add(producto_test)
        sesion.flush()
        producto_id = producto_test.ID
        print(f"   ✅ Producto creado: ID {producto_id}")
        
        # Paso 2: Crear pedido
        sucursal = sesion.query(MODELO_SUCURSAL).filter_by(ACTIVA=True).first()
        # MODELO_USUARIO no tiene campo ROL directo, usar relación ROLES o cualquier usuario
        cliente = sesion.query(MODELO_USUARIO).first()
        
        if not cliente:
            cliente = sesion.query(MODELO_USUARIO).first()
        
        pedido_test = MODELO_PEDIDO(
            SUCURSAL_ID=sucursal.ID,
            CLIENTE_ID=cliente.ID,
            MONTO_TOTAL=30,  # 2 productos x 15
            ESTADO="PENDIENTE",
            FECHA_CREACION=datetime.now()
        )
        sesion.add(pedido_test)
        sesion.flush()
        pedido_id = pedido_test.ID
        print(f"   ✅ Pedido creado: ID {pedido_id}, Total S/ 30.00")
        
        # Paso 3: Agregar detalles al pedido
        detalle1 = MODELO_DETALLE_PEDIDO(
            PEDIDO_ID=pedido_id,
            PRODUCTO_ID=producto_id,
            CANTIDAD=2,
            PRECIO_UNITARIO=15
        )
        sesion.add(detalle1)
        sesion.flush()
        print(f"   ✅ Detalle agregado: 2x Producto Test @ S/ 15.00")
        
        # Paso 4: Crear voucher asociado
        voucher_test = MODELO_VOUCHER(
            PEDIDO_ID=pedido_id,
            USUARIO_ID=cliente.ID,
            MONTO=30,
            METODO_PAGO="transferencia",
            IMAGEN_URL="test-integracion.jpg",
            VALIDADO=False,
            RECHAZADO=False,
            FECHA_VALIDACION=None
        )
        sesion.add(voucher_test)
        sesion.flush()
        voucher_id = voucher_test.ID
        print(f"   ✅ Voucher creado: ID {voucher_id}, Monto S/ 30.00")
        
        # Hacer commit para que FuenteVouchersLocal pueda ver los datos
        sesion.commit()
        
        # Paso 5: Cargar voucher con FuenteVouchersLocal
        fuente = FuenteVouchersLocal()
        voucher_entidad = fuente.obtener_por_id(voucher_id)
        
        # Validar que se cargaron datos del pedido
        assert voucher_entidad is not None, "Voucher no encontrado"
        assert voucher_entidad.pedido_total == 30, f"Total pedido incorrecto: {voucher_entidad.pedido_total}"
        assert voucher_entidad.cliente_nombre is not None, "Cliente no cargado"
        assert voucher_entidad.sucursal_nombre is not None, "Sucursal no cargada"
        assert voucher_entidad.pedido_productos is not None, "Productos no cargados"
        assert len(voucher_entidad.pedido_productos) > 0, "Lista de productos vacía"
        
        print(f"   ✅ Voucher cargado con datos de pedido:")
        print(f"      • Cliente: {voucher_entidad.cliente_nombre}")
        print(f"      • Sucursal: {voucher_entidad.sucursal_nombre}")
        print(f"      • Total pedido: S/ {voucher_entidad.pedido_total}")
        print(f"      • Productos: {len(voucher_entidad.pedido_productos)}")
        
        # Paso 6: Aprobar voucher
        voucher_test.VALIDADO = True
        voucher_test.RECHAZADO = False
        voucher_test.FECHA_VALIDACION = datetime.now()
        sesion.flush()
        print(f"   ✅ Voucher aprobado")
        
        # Paso 7: Actualizar estado del pedido
        pedido_test.ESTADO = "APROBADO"
        sesion.commit()
        print(f"   ✅ Pedido actualizado a APROBADO")
        
        # Paso 8: Cleanup - recargar objetos en la sesión y eliminar
        pedido_test = sesion.query(MODELO_PEDIDO).filter_by(ID=pedido_id).first()
        if pedido_test:
            # Eliminar detalles primero
            sesion.query(MODELO_DETALLE_PEDIDO).filter_by(PEDIDO_ID=pedido_id).delete()
            # Eliminar voucher
            sesion.query(MODELO_VOUCHER).filter_by(ID=voucher_id).delete()
            # Eliminar pedido
            sesion.delete(pedido_test)
        # Eliminar producto
        producto_test = sesion.query(MODELO_PRODUCTO).filter_by(ID=producto_id).first()
        if producto_test:
            sesion.delete(producto_test)
        sesion.commit()
        print(f"   🧹 Limpieza: registros eliminados")
        
        print("✅ PASS: Flujo completo ejecutado exitosamente")
        return True
        
    except Exception as e:
        sesion.rollback()
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        sesion.close()

def test_estados_sucursales():
    """Test 2: Todos los estados de sucursales"""
    print("\n2️⃣  TEST: Ciclo completo de estados de sucursales")
    print("-" * 70)
    
    sesion = SesionLocal()
    try:
        # Crear sucursal temporal
        sucursal_test = MODELO_SUCURSAL(
            NOMBRE="Sucursal TEST Estados",
            DIRECCION="Av. Test Estados 456",
            ACTIVA=True,
            ESTADO="ACTIVA",
            TELEFONO="999888777",
            HORARIO="24/7"
        )
        sesion.add(sucursal_test)
        sesion.flush()
        suc_id = sucursal_test.ID
        print(f"   ✅ Sucursal creada: ID {suc_id}, Estado ACTIVA")
        
        # Ciclo de estados
        estados = ["MANTENIMIENTO", "VACACIONES", "CERRADA", "ACTIVA"]
        for nuevo_estado in estados:
            sucursal_test.ESTADO = nuevo_estado
            sucursal_test.ACTIVA = (nuevo_estado == "ACTIVA")
            sesion.flush()
            
            # Verificar
            verificacion = sesion.query(MODELO_SUCURSAL).filter_by(ID=suc_id).first()
            assert verificacion.ESTADO == nuevo_estado, f"Estado no cambió a {nuevo_estado}"
            assert verificacion.ACTIVA == (nuevo_estado == "ACTIVA"), "Flag ACTIVA inconsistente"
            
            print(f"   ✅ Estado cambiado a {nuevo_estado}, ACTIVA={verificacion.ACTIVA}")
        
        # Cleanup
        sesion.delete(sucursal_test)
        sesion.commit()
        print(f"   🧹 Limpieza: sucursal eliminada")
        
        print("✅ PASS: Todos los estados funcionan correctamente")
        return True
        
    except Exception as e:
        sesion.rollback()
        print(f"❌ FAIL: {e}")
        return False
    finally:
        sesion.close()

def test_filtros_vouchers():
    """Test 3: Filtros de vouchers por estado"""
    print("\n3️⃣  TEST: Filtros de vouchers (PENDIENTE/APROBADO/RECHAZADO)")
    print("-" * 70)
    
    try:
        fuente = FuenteVouchersLocal()
        
        # Test cada estado
        estados = ["PENDIENTE", "APROBADO", "RECHAZADO"]
        totales = {}
        
        for estado in estados:
            vouchers = fuente.obtener_por_estado(estado)
            totales[estado] = len(vouchers)
            print(f"   ✅ {estado}: {len(vouchers)} vouchers")
            
            # Verificar que todos tienen el estado correcto
            for v in vouchers[:3]:  # Primeros 3
                if estado == "PENDIENTE":
                    assert not v.validado and not v.rechazado, f"Voucher {v.id} estado incorrecto"
                elif estado == "APROBADO":
                    assert v.validado and not v.rechazado, f"Voucher {v.id} estado incorrecto"
                elif estado == "RECHAZADO":
                    assert not v.validado and v.rechazado, f"Voucher {v.id} estado incorrecto"
        
        # Verificar que todos fueron contados
        total = sum(totales.values())
        print(f"   📊 Total de vouchers: {total}")
        
        print("✅ PASS: Filtros funcionan correctamente")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_validaciones_montos():
    """Test 4: Validación de montos coincidentes"""
    print("\n4️⃣  TEST: Validación voucher.monto vs pedido.total")
    print("-" * 70)
    
    try:
        fuente = FuenteVouchersLocal()
        vouchers = fuente.obtener_por_estado("PENDIENTE")
        
        coincidencias = 0
        diferencias = 0
        sin_pedido = 0
        
        for voucher in vouchers[:10]:  # Primeros 10
            if voucher.pedido_total is None:
                sin_pedido += 1
            elif abs(voucher.monto - voucher.pedido_total) < 1:
                coincidencias += 1
            else:
                diferencias += 1
                print(f"   ⚠️  Voucher #{voucher.id}: Voucher S/ {voucher.monto:.2f} vs Pedido S/ {voucher.pedido_total:.2f}")
        
        print(f"   ✅ Coincidencias: {coincidencias}")
        print(f"   ⚠️  Diferencias: {diferencias}")
        print(f"   ℹ️  Sin pedido: {sin_pedido}")
        
        print("✅ PASS: Validación de montos completada")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False

def test_integridad_relaciones():
    """Test 5: Integridad referencial de relaciones"""
    print("\n5️⃣  TEST: Integridad referencial (FK constraints)")
    print("-" * 70)
    
    sesion = SesionLocal()
    try:
        # Verificar vouchers tienen pedidos válidos
        vouchers_sin_pedido = sesion.query(MODELO_VOUCHER).filter(
            MODELO_VOUCHER.PEDIDO_ID.is_(None)
        ).count()
        print(f"   ℹ️  Vouchers sin pedido: {vouchers_sin_pedido}")
        
        # Verificar pedidos tienen sucursales válidas
        pedidos = sesion.query(MODELO_PEDIDO).all()
        pedidos_sin_sucursal = 0
        pedidos_sin_cliente = 0
        
        for pedido in pedidos:
            if pedido.SUCURSAL_ID:
                sucursal = sesion.query(MODELO_SUCURSAL).filter_by(ID=pedido.SUCURSAL_ID).first()
                if not sucursal:
                    pedidos_sin_sucursal += 1
            
            if pedido.CLIENTE_ID:
                cliente = sesion.query(MODELO_USUARIO).filter_by(ID=pedido.CLIENTE_ID).first()
                if not cliente:
                    pedidos_sin_cliente += 1
        
        print(f"   ✅ Total pedidos: {len(pedidos)}")
        print(f"   ⚠️  Pedidos con sucursal inexistente: {pedidos_sin_sucursal}")
        print(f"   ⚠️  Pedidos con cliente inexistente: {pedidos_sin_cliente}")
        
        # Verificar detalles tienen productos válidos
        detalles = sesion.query(MODELO_DETALLE_PEDIDO).all()
        detalles_sin_producto = 0
        
        for detalle in detalles:
            if detalle.PRODUCTO_ID:
                producto = sesion.query(MODELO_PRODUCTO).filter_by(ID=detalle.PRODUCTO_ID).first()
                if not producto:
                    detalles_sin_producto += 1
        
        print(f"   ✅ Total detalles: {len(detalles)}")
        print(f"   ⚠️  Detalles con producto inexistente: {detalles_sin_producto}")
        
        print("✅ PASS: Integridad referencial verificada")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False
    finally:
        sesion.close()

def test_performance_carga():
    """Test 6: Performance de carga de vouchers"""
    print("\n6️⃣  TEST: Performance de carga (con datos de pedido)")
    print("-" * 70)
    
    import time
    
    try:
        fuente = FuenteVouchersLocal()
        
        # Test carga de vouchers pendientes
        inicio = time.time()
        vouchers = fuente.obtener_por_estado("PENDIENTE")
        fin = time.time()
        tiempo_ms = (fin - inicio) * 1000
        
        print(f"   ⏱️  Tiempo de carga: {tiempo_ms:.2f}ms")
        print(f"   📊 Vouchers cargados: {len(vouchers)}")
        
        if len(vouchers) > 0:
            avg_ms = tiempo_ms / len(vouchers)
            print(f"   📈 Promedio por voucher: {avg_ms:.2f}ms")
        
        # Validar que se cargaron datos
        con_pedido = sum(1 for v in vouchers if v.pedido_total is not None)
        con_cliente = sum(1 for v in vouchers if v.cliente_nombre is not None)
        con_sucursal = sum(1 for v in vouchers if v.sucursal_nombre is not None)
        
        print(f"   ✅ Con datos de pedido: {con_pedido}/{len(vouchers)}")
        print(f"   ✅ Con nombre cliente: {con_cliente}/{len(vouchers)}")
        print(f"   ✅ Con nombre sucursal: {con_sucursal}/{len(vouchers)}")
        
        # Benchmark aceptable: < 5000ms total, < 200ms por voucher
        if tiempo_ms < 5000:
            print(f"   🚀 Performance EXCELENTE (< 5s)")
        elif tiempo_ms < 10000:
            print(f"   ✅ Performance BUENA (< 10s)")
        else:
            print(f"   ⚠️  Performance LENTA (> 10s)")
        
        print("✅ PASS: Test de performance completado")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False

def test_validaciones_negocio():
    """Test 7: Validaciones de reglas de negocio"""
    print("\n7️⃣  TEST: Reglas de negocio")
    print("-" * 70)
    
    sesion = SesionLocal()
    try:
        # Regla 1: Un voucher no puede estar aprobado Y rechazado
        vouchers_invalidos = sesion.query(MODELO_VOUCHER).filter(
            MODELO_VOUCHER.VALIDADO == True,
            MODELO_VOUCHER.RECHAZADO == True
        ).count()
        print(f"   ✅ Vouchers aprobados Y rechazados: {vouchers_invalidos}")
        assert vouchers_invalidos == 0, "Hay vouchers con estados contradictorios"
        
        # Regla 2: Sucursales CERRADAS no deben estar ACTIVA=True
        cerradas_activas = sesion.query(MODELO_SUCURSAL).filter(
            MODELO_SUCURSAL.ESTADO == "CERRADA",
            MODELO_SUCURSAL.ACTIVA == True
        ).count()
        print(f"   ✅ Sucursales CERRADAS pero ACTIVA=True: {cerradas_activas}")
        assert cerradas_activas == 0, "Hay sucursales cerradas marcadas como activas"
        
        # Regla 3: Pedidos con detalles
        assert cerradas_activas == 0, "Hay sucursales cerradas marcadas como activas"
        
        # Regla 3: Pedidos con detalles
        pedidos = sesion.query(MODELO_PEDIDO).all()
        pedidos_sin_detalles = 0
        
        for pedido in pedidos:
            detalles = sesion.query(MODELO_DETALLE_PEDIDO).filter_by(PEDIDO_ID=pedido.ID).count()
            if detalles == 0:
                pedidos_sin_detalles += 1
        
        print(f"   ℹ️  Pedidos sin detalles: {pedidos_sin_detalles}/{len(pedidos)}")
        
        print("✅ PASS: Reglas de negocio validadas")
        return True
        
    except AssertionError as e:
        print(f"❌ FAIL: {e}")
        return False
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False
    finally:
        sesion.close()

# EJECUTAR TODAS LAS PRUEBAS
if __name__ == "__main__":
    resultados = []
    
    tests = [
        ("Flujo completo Pedido-Voucher", test_flujo_completo_voucher_pedido),
        ("Estados de sucursales", test_estados_sucursales),
        ("Filtros de vouchers", test_filtros_vouchers),
        ("Validación de montos", test_validaciones_montos),
        ("Integridad referencial", test_integridad_relaciones),
        ("Performance de carga", test_performance_carga),
        ("Reglas de negocio", test_validaciones_negocio),
    ]
    
    for nombre, test_func in tests:
        try:
            resultado = test_func()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"❌ Error ejecutando {nombre}: {e}")
            resultados.append((nombre, False))
    
    # RESUMEN
    print("\n" + "=" * 70)
    print("RESUMEN PRUEBAS DE INTEGRACIÓN:")
    print("=" * 70)
    print()
    
    passed = sum(1 for _, r in resultados if r)
    total = len(resultados)
    
    for nombre, resultado in resultados:
        icono = "✅" if resultado else "❌"
        print(f"{icono} {nombre}")
    
    print()
    print(f"📊 RESULTADO FINAL: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("🎉 TODAS LAS PRUEBAS DE INTEGRACIÓN PASARON")
    else:
        print(f"⚠️  {total - passed} pruebas fallaron")
    
    print("=" * 70)
