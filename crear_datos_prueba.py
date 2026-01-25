#!/usr/bin/env python3
"""
Script para crear datos de prueba en el sistema Cony Chips
"""

import asyncio
import bcrypt
from datetime import datetime
from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION, INICIALIZAR_BASE_DATOS,
    MODELO_USUARIO, MODELO_ROL, MODELO_PRODUCTO, MODELO_INSUMO
)


async def crear_datos_prueba():
    """Crea datos de prueba en la base de datos"""

    print("🚀 Iniciando creación de datos de prueba...")

    # Inicializar BD
    INICIALIZAR_BASE_DATOS()

    sesion = OBTENER_SESION()

    try:
        # Crear roles de prueba
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

        # Crear usuarios de prueba
        print("\n👥 Creando usuarios de prueba...")
        usuarios_prueba = [
            {
                "EMAIL": "admin@conychips.com",
                "NOMBRE_USUARIO": "admin",
                "CONTRASENA_HASH": bcrypt.hashpw("Admin123.".encode(), bcrypt.gensalt()).decode(),
                "HUELLA_DISPOSITIVO": "test_huella_admin",
                "ACTIVO": True,
                "VERIFICADO": True
            },
            {
                "EMAIL": "cocinero@conychips.com",
                "NOMBRE_USUARIO": "cocinero",
                "CONTRASENA_HASH": bcrypt.hashpw("Cocinero123.".encode(), bcrypt.gensalt()).decode(),
                "HUELLA_DISPOSITIVO": "test_huella_cocinero",
                "ACTIVO": True,
                "VERIFICADO": True
            },
            {
                "EMAIL": "mesero@conychips.com",
                "NOMBRE_USUARIO": "mesero",
                "CONTRASENA_HASH": bcrypt.hashpw("Mesero123.".encode(), bcrypt.gensalt()).decode(),
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

        # Asignar roles a usuarios
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

        # Crear productos de prueba
        print("\n🍔 Creando productos de prueba...")
        productos_prueba = [
            {
                "NOMBRE": "Hamburguesa Clásica",
                "DESCRIPCION": "Hamburguesa con queso, lechuga y tomate",
                "PRECIO": 1550,  # En centavos
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

        # Crear insumos de prueba
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

        print("\n🎉 ¡Datos de prueba creados exitosamente!")
        print("\n📊 Resumen:")
        print(f"   👥 Usuarios: {sesion.query(MODELO_USUARIO).count()}")
        print(f"   🍕 Productos: {sesion.query(MODELO_PRODUCTO).count()}")
        print(f"   📦 Insumos: {sesion.query(MODELO_INSUMO).count()}")

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