"""
Script para crear datos de prueba del módulo Finanzas
Genera pedidos, vouchers, insumos y ofertas aplicadas
"""
import asyncio
from datetime import datetime, timedelta, timezone
from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION, INICIALIZAR_BASE_DATOS,
    MODELO_PEDIDO, MODELO_VOUCHER, MODELO_USUARIO,
    MODELO_PRODUCTO, MODELO_INSUMO, MODELO_OFERTA,
    MODELO_CAJA_MOVIMIENTO, MODELO_DETALLE_PEDIDO,
    MODELO_SUCURSAL
)
import random

# Datos realistas en Bs
CLIENTES = [
    "Juan Pérez", "María González", "Carlos Rodríguez", 
    "Ana Martínez", "Luis Fernández", "Carmen López",
    "José Sánchez", "Rosa Díaz", "Pedro Torres", "Laura Ramírez"
]

BANCOS = ["Mercantil", "Venezuela", "Banesco", "Provincial", "BOD"]
METODOS_PAGO = ["pago_movil", "transferencia", "efectivo"]
ESTADOS_PEDIDO = ["COMPLETADO", "PENDIENTE", "CANCELADO"]
ESTADOS_VOUCHER = ["APROBADO", "RECHAZADO", "PENDIENTE"]

async def crear_datos_finanzas():
    """Crea datos de prueba completos para el módulo de finanzas"""
    
    print("🔧 Inicializando base de datos...")
    INICIALIZAR_BASE_DATOS()
    
    sesion = OBTENER_SESION()
    
    try:
        # 1. Obtener usuario admin y sucursal
        admin = sesion.query(MODELO_USUARIO).filter_by(EMAIL="superadmin@conychips.com").first()
        if not admin:
            print("❌ Error: No se encontró el usuario superadmin")
            return
        
        sucursal = sesion.query(MODELO_SUCURSAL).first()
        if not sucursal:
            print("❌ Error: No hay sucursales registradas")
            return
        
        # 2. Crear productos si no existen
        print("\n📦 Verificando productos...")
        productos = sesion.query(MODELO_PRODUCTO).limit(5).all()
        if len(productos) < 3:
            print("⚠️  Pocos productos, creando más...")
            productos_nuevos = [
                MODELO_PRODUCTO(
                    NOMBRE="Hamburguesa Clásica",
                    DESCRIPCION="Carne, queso, lechuga, tomate",
                    PRECIO=12000,  # Bs 120
                    IMAGEN="assets/hamburguesa.jpg",
                    ACTIVO=True
                ),
                MODELO_PRODUCTO(
                    NOMBRE="Papas Fritas Grandes",
                    DESCRIPCION="Papas crujientes",
                    PRECIO=3000,  # Bs 30
                    IMAGEN="assets/papas.jpg",
                    ACTIVO=True
                ),
                MODELO_PRODUCTO(
                    NOMBRE="Refresco 500ml",
                    DESCRIPCION="Bebida gaseosa",
                    PRECIO=2000,  # Bs 20
                    IMAGEN="assets/refresco.jpg",
                    ACTIVO=True
                ),
            ]
            for prod in productos_nuevos:
                sesion.add(prod)
            sesion.commit()
            productos = sesion.query(MODELO_PRODUCTO).limit(5).all()
        
        print(f"✓ {len(productos)} productos disponibles")
        
        # 3. Crear 20 pedidos con vouchers
        print("\n💰 Creando 20 pedidos con vouchers...")
        
        fecha_base = datetime.now(timezone.utc)
        
        for i in range(1, 21):
            # Variar fechas (últimos 7 días)
            dias_atras = random.randint(0, 7)
            fecha_pedido = fecha_base - timedelta(days=dias_atras, hours=random.randint(0, 23))
            
            # Crear pedido
            estado = random.choice(ESTADOS_PEDIDO)
            metodo_pago = random.choice(METODOS_PAGO)
            
            # Calcular total aleatorio (entre Bs 50 y Bs 300)
            num_productos = random.randint(1, 4)
            total = 0
            
            pedido = MODELO_PEDIDO(
                CLIENTE_ID=admin.ID,
                SUCURSAL_ID=sucursal.ID,
                ESTADO=estado.upper(),
                FECHA_CREACION=fecha_pedido,
                FECHA_CONFIRMACION=fecha_pedido + timedelta(minutes=5) if estado != "PENDIENTE" else None,
                TIPO=("DELIVERY" if random.random() > 0.5 else "RECOGER").lower(),
                NOTAS=f"Pedido de prueba #{i} - {random.choice(CLIENTES)}",
                MONTO_TOTAL=0  # Se actualiza después
            )
            sesion.add(pedido)
            sesion.flush()  # Para obtener el ID
            
            # Agregar productos al pedido
            for _ in range(num_productos):
                producto = random.choice(productos)
                cantidad = random.randint(1, 3)
                subtotal = producto.PRECIO * cantidad
                total += subtotal
                
                detalle = MODELO_DETALLE_PEDIDO(
                    PEDIDO_ID=pedido.ID,
                    PRODUCTO_ID=producto.ID,
                    CANTIDAD=cantidad,
                    PRECIO_UNITARIO=producto.PRECIO
                )
                sesion.add(detalle)
            
            # Actualizar total del pedido
            pedido.MONTO_TOTAL = total
            
            # Crear voucher solo si el método es pago móvil o transferencia
            if metodo_pago in ["pago_movil", "transferencia"] and estado != "PENDIENTE":
                # Determinar estado del voucher
                validado = False
                rechazado = False
                motivo_rechazo = None
                
                if estado == "COMPLETADO":
                    # 70% aprobados, 30% rechazados
                    if random.random() < 0.7:
                        validado = True
                    else:
                        rechazado = True
                        motivo_rechazo = random.choice([
                            "Monto no coincide",
                            "Imagen borrosa",
                            "Referencia duplicada",
                            "Banco no válido"
                        ])
                
                voucher = MODELO_VOUCHER(
                    USUARIO_ID=admin.ID,
                    PEDIDO_ID=pedido.ID,
                    MONTO=total,
                    METODO_PAGO=metodo_pago,
                    IMAGEN_URL=f"https://picsum.photos/400/600?random={i}",
                    VALIDADO=validado,
                    RECHAZADO=rechazado,
                    MOTIVO_RECHAZO=motivo_rechazo,
                    FECHA_SUBIDA=fecha_pedido,
                    FECHA_VALIDACION=fecha_pedido + timedelta(minutes=10) if validado else None,
                    VALIDADO_POR=admin.ID if validado else None
                )
                sesion.add(voucher)
            
            if i % 5 == 0:
                print(f"  ✓ Creados {i}/20 pedidos...")
        
        sesion.commit()
        print("✓ 20 pedidos creados exitosamente")
        
        # 4. Crear movimientos de insumos (egresos)
        print("\n📦 Creando movimientos de insumos...")
        
        insumos_nombres = [
            ("Papas 25kg", 5000),
            ("Aceite 5L", 3500),
            ("Pan Hamburguesa x50", 2000),
            ("Carne Molida 5kg", 8000),
            ("Queso 2kg", 4000),
            ("Lechuga", 500),
            ("Tomate 5kg", 1500),
            ("Cebolla 5kg", 1000),
        ]
        
        # Crear insumos si no existen
        for nombre, precio_ref in insumos_nombres:
            insumo_existe = sesion.query(MODELO_INSUMO).filter_by(NOMBRE=nombre).first()
            if not insumo_existe:
                insumo = MODELO_INSUMO(
                    NOMBRE=nombre,
                    UNIDAD="kg" if "kg" in nombre else ("L" if "L" in nombre else "unidad"),
                    STOCK=random.randint(10, 50),
                    COSTO_UNITARIO=precio_ref,
                    SUCURSAL_ID=sucursal.ID,
                    ACTIVO=True
                )
                sesion.add(insumo)
        
        sesion.commit()
        
        # Crear movimientos de compra
        insumos = sesion.query(MODELO_INSUMO).all()
        for i in range(10):
            dias_atras = random.randint(0, 7)
            fecha_compra = fecha_base - timedelta(days=dias_atras)
            
            insumo = random.choice(insumos)
            cantidad = random.randint(5, 20)
            monto = insumo.COSTO_UNITARIO * cantidad
            
            movimiento = MODELO_CAJA_MOVIMIENTO(
                USUARIO_ID=admin.ID,
                SUCURSAL_ID=sucursal.ID,
                TIPO="egreso",
                CATEGORIA="insumos",
                MONTO=monto,
                DESCRIPCION=f"Compra de {insumo.NOMBRE} x{cantidad}",
                FECHA=fecha_compra
            )
            sesion.add(movimiento)
        
        sesion.commit()
        print("✓ 10 movimientos de insumos creados")
        
        # 5. Crear ofertas si no existen
        print("\n🎁 Creando ofertas de prueba...")
        
        # Necesitamos productos para las ofertas
        productos_oferta = sesion.query(MODELO_PRODUCTO).limit(2).all()
        
        ofertas_datos = [
            {
                "PRODUCTO_ID": productos_oferta[0].ID,
                "DESCUENTO_PORCENTAJE": 50,
                "FECHA_INICIO": fecha_base - timedelta(days=30),
                "FECHA_FIN": fecha_base + timedelta(days=30),
                "ACTIVA": True
            },
            {
                "PRODUCTO_ID": productos_oferta[1].ID if len(productos_oferta) > 1 else productos_oferta[0].ID,
                "DESCUENTO_PORCENTAJE": 20,
                "FECHA_INICIO": fecha_base - timedelta(days=15),
                "FECHA_FIN": fecha_base + timedelta(days=15),
                "ACTIVA": True
            }
        ]
        
        for oferta_data in ofertas_datos:
            # Verificar si ya existe oferta para ese producto
            existe = sesion.query(MODELO_OFERTA).filter_by(
                PRODUCTO_ID=oferta_data["PRODUCTO_ID"],
                ACTIVA=True
            ).first()
            if not existe:
                oferta = MODELO_OFERTA(**oferta_data)
                sesion.add(oferta)
        
        sesion.commit()
        print("✓ Ofertas creadas")
        
        # 6. Resumen final
        print("\n" + "="*60)
        print("✅ DATOS DE PRUEBA CREADOS EXITOSAMENTE")
        print("="*60)
        
        # Estadísticas
        total_pedidos = sesion.query(MODELO_PEDIDO).count()
        total_vouchers = sesion.query(MODELO_VOUCHER).count()
        total_insumos = sesion.query(MODELO_INSUMO).count()
        total_ofertas = sesion.query(MODELO_OFERTA).count()
        
        # Calcular totales en Bs
        pedidos_completados = sesion.query(MODELO_PEDIDO).filter_by(ESTADO="COMPLETADO").all()
        total_ingresos = sum([p.MONTO_TOTAL for p in pedidos_completados if p.MONTO_TOTAL])
        
        movimientos_egreso = sesion.query(MODELO_CAJA_MOVIMIENTO).filter_by(TIPO="egreso").all()
        total_egresos = sum([m.MONTO for m in movimientos_egreso])
        
        print(f"\n📊 Estadísticas:")
        print(f"  • Pedidos totales: {total_pedidos}")
        print(f"  • Vouchers: {total_vouchers}")
        print(f"  • Insumos: {total_insumos}")
        print(f"  • Ofertas: {total_ofertas}")
        print(f"\n💰 Financiero:")
        print(f"  • Ingresos: Bs {total_ingresos/100:.2f}")
        print(f"  • Egresos: Bs {total_egresos/100:.2f}")
        print(f"  • Utilidad: Bs {(total_ingresos - total_egresos)/100:.2f}")
        
        print("\n✅ Ejecuta la app y ve a Finanzas para ver los datos")
        
    except Exception as e:
        sesion.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        sesion.close()

if __name__ == "__main__":
    asyncio.run(crear_datos_finanzas())
