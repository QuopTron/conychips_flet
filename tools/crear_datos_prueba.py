
import asyncio
from datetime import datetime, timedelta
from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION, INICIALIZAR_BASE_DATOS,
    MODELO_USUARIO, MODELO_ROL, MODELO_PRODUCTO, MODELO_INSUMO,
    MODELO_PEDIDO, MODELO_SUCURSAL, MODELO_CAJA, MODELO_CAJA_MOVIMIENTO, MODELO_VOUCHER
)

async def crear_datos_prueba():

    print("🚀 Iniciando creación de datos de prueba...")

    INICIALIZAR_BASE_DATOS()

    sesion = OBTENER_SESION()

    try:
        print("📋 Creando roles...")
        roles_prueba = [
            {"NOMBRE": "ADMIN", "DESCRIPCION": "Administrador del sistema"},
            {"NOMBRE": "COCINA", "DESCRIPCION": "Personal de cocina"},
            {"NOMBRE": "ATENCION", "DESCRIPCION": "Personal de atención al cliente"},
            {"NOMBRE": "LIMPIEZA", "DESCRIPCION": "Personal de limpieza"},
        ]

        for rol_data in roles_prueba:
            rol_existente = sesion.query(MODELO_ROL).filter_by(NOMBRE=rol_data["NOMBRE"]).first()
            if not rol_existente:
                nuevo_rol = MODELO_ROL(**rol_data)
                sesion.add(nuevo_rol)
                print(f"   ✅ Rol creado: {rol_data['NOMBRE']}")

        sesion.commit()

        print("\n👥 Creando usuarios de prueba...")
        usuarios_prueba = [
            {
                "EMAIL": "admin@conychips.com",
                "NOMBRE_USUARIO": "admin",
                "CONTRASENA_HASH": "Admin123.",
                "HUELLA_DISPOSITIVO": "test_huella_admin",
                "ACTIVO": True,
                "VERIFICADO": True
            },
            {
                "EMAIL": "cocinero@conychips.com",
                "NOMBRE_USUARIO": "cocinero",
                "CONTRASENA_HASH": "Cocinero123.",
                "HUELLA_DISPOSITIVO": "test_huella_cocinero",
                "ACTIVO": True,
                "VERIFICADO": True
            },
            {
                "EMAIL": "mesero@conychips.com",
                "NOMBRE_USUARIO": "mesero",
                "CONTRASENA_HASH": "Mesero123.",
                "HUELLA_DISPOSITIVO": "test_huella_mesero",
                "ACTIVO": True,
                "VERIFICADO": True
            }
        ]

        for usuario_data in usuarios_prueba:
            usuario_existente = sesion.query(MODELO_USUARIO).filter_by(EMAIL=usuario_data["EMAIL"]).first()
            if not usuario_existente:
                nuevo_usuario = MODELO_USUARIO(**usuario_data)
                sesion.add(nuevo_usuario)
                print(f"   ✅ Usuario creado: {usuario_data['EMAIL']}")

        sesion.commit()

        print("\n🔗 Asignando roles a usuarios...")
        admin_user = sesion.query(MODELO_USUARIO).filter_by(EMAIL="admin@conychips.com").first()
        cocinero_user = sesion.query(MODELO_USUARIO).filter_by(EMAIL="cocinero@conychips.com").first()
        mesero_user = sesion.query(MODELO_USUARIO).filter_by(EMAIL="mesero@conychips.com").first()

        admin_rol = sesion.query(MODELO_ROL).filter_by(NOMBRE="ADMIN").first()
        cocina_rol = sesion.query(MODELO_ROL).filter_by(NOMBRE="COCINA").first()
        atencion_rol = sesion.query(MODELO_ROL).filter_by(NOMBRE="ATENCION").first()

        if admin_user and admin_rol:
            admin_user.ROLES.append(admin_rol)
        if cocinero_user and cocina_rol:
            cocinero_user.ROLES.append(cocina_rol)
        if mesero_user and atencion_rol:
            mesero_user.ROLES.append(atencion_rol)

        sesion.commit()
        print("   ✅ Roles asignados")

        print("\n🍔 Creando productos de prueba...")
        productos_prueba = [
            {
                "NOMBRE": "Hamburguesa Clásica",
                "DESCRIPCION": "Hamburguesa con queso, lechuga y tomate",
                "PRECIO": 1550,
                "DISPONIBLE": True,
                "IMAGEN": "/assets/productos/hamburguesa.jpg"
            },
            {
                "NOMBRE": "Pizza Margherita",
                "DESCRIPCION": "Pizza con queso mozzarella y albahaca",
                "PRECIO": 2200,
                "DISPONIBLE": True,
                "IMAGEN": "/assets/productos/pizza.jpg"
            },
            {
                "NOMBRE": "Coca Cola 500ml",
                "DESCRIPCION": "Refresco de cola",
                "PRECIO": 500,
                "DISPONIBLE": True,
                "IMAGEN": "/assets/productos/coca.jpg"
            },
            {
                "NOMBRE": "Helado de Vainilla",
                "DESCRIPCION": "Helado cremoso de vainilla",
                "PRECIO": 800,
                "DISPONIBLE": True,
                "IMAGEN": "/assets/productos/helado.jpg"
            }
        ]

        for prod_data in productos_prueba:
            prod_existente = sesion.query(MODELO_PRODUCTO).filter_by(NOMBRE=prod_data["NOMBRE"]).first()
            if not prod_existente:
                nuevo_prod = MODELO_PRODUCTO(**prod_data)
                sesion.add(nuevo_prod)
                print(f"   ✅ Producto creado: {prod_data['NOMBRE']} - ${prod_data['PRECIO']}")

        sesion.commit()

        print("\n📦 Creando insumos de prueba...")
        insumos_prueba = [
            {"NOMBRE": "Carne Molida", "STOCK": 50, "COSTO_UNITARIO": 2500, "UNIDAD": "kg"},
            {"NOMBRE": "Queso Cheddar", "STOCK": 30, "COSTO_UNITARIO": 1500, "UNIDAD": "kg"},
            {"NOMBRE": "Pan de Hamburguesa", "STOCK": 100, "COSTO_UNITARIO": 250, "UNIDAD": "unidades"},
            {"NOMBRE": "Tomate", "STOCK": 40, "COSTO_UNITARIO": 800, "UNIDAD": "kg"}
        ]

        for insumo_data in insumos_prueba:
            insumo_existente = sesion.query(MODELO_INSUMO).filter_by(NOMBRE=insumo_data["NOMBRE"]).first()
            if not insumo_existente:
                nuevo_insumo = MODELO_INSUMO(**insumo_data)
                sesion.add(nuevo_insumo)
                print(f"   ✅ Insumo creado: {insumo_data['NOMBRE']} - {insumo_data['STOCK']} {insumo_data['UNIDAD']}")

        sesion.commit()

        sucursal = sesion.query(MODELO_SUCURSAL).first()
        if not sucursal:
            sucursal = MODELO_SUCURSAL(NOMBRE="Sucursal Central", DIRECCION="Av. Principal 123", ACTIVA=True)
            sesion.add(sucursal)
            sesion.commit()

        print("\n📦 Creando pedidos de prueba para Finanzas...")
        estados = ["pendiente", "confirmado", "en_preparacion", "listo", "en_camino", "entregado"]
        cliente = sesion.query(MODELO_USUARIO).filter_by(EMAIL="mesero@conychips.com").first() or sesion.query(MODELO_USUARIO).first()
        created_pedidos = []
        for i, est in enumerate(estados, start=1):
            p = MODELO_PEDIDO(
                CLIENTE_ID=cliente.ID,
                SUCURSAL_ID=sucursal.ID,
                TIPO='delivery',
                ESTADO=est,
                MONTO_TOTAL=100 + i * 50,
                FECHA_CREACION=datetime.utcnow() - timedelta(days=i),
                FECHA_CONFIRMACION=(datetime.utcnow() - timedelta(days=i-1)) if est != 'pendiente' else None
            )
            sesion.add(p)
            created_pedidos.append(p)
        sesion.commit()
        print(f"   ✅ Pedidos creados: {len(created_pedidos)}")

        print("\n💰 Creando caja y movimientos demo...")
        admin_user = sesion.query(MODELO_USUARIO).filter_by(EMAIL="admin@conychips.com").first()
        caja = sesion.query(MODELO_CAJA).filter_by(ACTIVA=True).first()
        if not caja and admin_user:
            caja = MODELO_CAJA(USUARIO_ID=admin_user.ID, SUCURSAL_ID=sucursal.ID, FECHA_APERTURA=datetime.utcnow() - timedelta(days=1), MONTO_INICIAL=1000, ACTIVA=True)
            sesion.add(caja)
            sesion.commit()
            movimientos = [
                ('INGRESO', 'Venta', 250),
                ('EGRESO', 'Compra insumos', 120),
                ('RETIRO', 'Retiro', 50),
            ]
            for tipo, cat, monto in movimientos:
                m = MODELO_CAJA_MOVIMIENTO(USUARIO_ID=admin_user.ID, SUCURSAL_ID=sucursal.ID, TIPO=tipo, CATEGORIA=cat, MONTO=monto, DESCRIPCION=f"Demo {cat}")
                sesion.add(m)
            sesion.commit()
            print(f"   ✅ Caja y {len(movimientos)} movimientos creados")

        print("\n🎫 Creando vouchers demo...")
        try:
            vouchers_created = 0
            for i, pedido in enumerate(created_pedidos[:3], start=1):
                v = MODELO_VOUCHER(PEDIDO_ID=pedido.ID, USUARIO_ID=admin_user.ID if admin_user else cliente.ID, IMAGEN_URL=f"/uploads/voucher_{i}.jpg", MONTO=pedido.MONTO_TOTAL, METODO_PAGO='transferencia', VALIDADO=(i % 2 == 0), VALIDADO_POR=(admin_user.ID if i % 2 == 0 else None))
                sesion.add(v)
                vouchers_created += 1
            sesion.commit()
            print(f"   ✅ Vouchers creados: {vouchers_created}")
        except Exception:
            print("   ⚠️ No fue posible crear vouchers demo (modelo ausente o error)")

            print("\n🎉 ¡Datos de prueba creados exitosamente!")
            print("\n📊 Resumen:")
            print(f"   👥 Usuarios: {sesion.query(MODELO_USUARIO).count()}")
            print(f"   🍕 Productos: {sesion.query(MODELO_PRODUCTO).count()}")
            print(f"   📦 Insumos: {sesion.query(MODELO_INSUMO).count()}")
            print(f"   📦 Pedidos: {sesion.query(MODELO_PEDIDO).count()}")
            print(f"   💰 Movimientos: {sesion.query(MODELO_CAJA_MOVIMIENTO).count()}")
            print(f"   🎫 Vouchers: {sesion.query(MODELO_VOUCHER).count()}")

            print("\n🔑 Credenciales de prueba:")
            print("   Admin: admin@conychips.com / Admin123.")
            print("   Cocinero: cocinero@conychips.com / Cocinero123.")
            print("   Mesero: mesero@conychips.com / Mesero123.")

        print("\n🔑 Credenciales de prueba:")
        print("   Admin: admin@conychips.com / Admin123.")
        print("   Cocinero: cocinero@conychips.com / Cocinero123.")
        print("   Mesero: mesero@conychips.com / Mesero123.")

    except Exception as e:
        print(f"❌ Error creando datos de prueba: {e}")
        import traceback
        traceback.print_exc()
        sesion.rollback()
    finally:
        sesion.close()

if __name__ == "__main__":
    asyncio.run(crear_datos_prueba())