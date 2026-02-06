#!/usr/bin/env python3
"""
📊 Script para Agregar Datos de Prueba Completos
Incluye: Reseñas, Productos, Proveedores, Ventas y más
"""

import sys
sys.path.insert(0, '/mnt/flox/conychips')

from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION,
    MODELO_RESENA_ATENCION,
    MODELO_PRODUCTO,
    MODELO_PROVEEDOR,
    MODELO_PEDIDO,
    MODELO_DETALLE_PEDIDO,
    MODELO_USUARIO,
    MODELO_SUCURSAL,
)
from datetime import datetime, timedelta
import random


def agregar_reseñas():
    """Agrega reseñas de clientes"""
    print("\n📝 Agregando Reseñas...")
    
    sesion = OBTENER_SESION()
    
    # Verificar si ya existen reseñas
    count = sesion.query(MODELO_RESENA_ATENCION).count()
    if count > 0:
        print(f"  ℹ️  Ya existen {count} reseñas")
        sesion.close()
        return
    
    # Obtener usuarios para las reseñas
    usuarios = sesion.query(MODELO_USUARIO).limit(5).all()
    if not usuarios:
        print("  ❌ No hay usuarios en el sistema")
        sesion.close()
        return
    
    comentarios_positivos = [
        "Excelente servicio, muy rápido y la comida deliciosa",
        "La mejor hamburguesa que he probado, 100% recomendado",
        "Siempre llega caliente y en buen estado",
        "El sabor es increíble, volveré seguro",
        "Atención de primera, muy amables",
        "La comida superó mis expectativas",
        "Delivery muy rápido, llegó antes de lo esperado"
    ]
    
    comentarios_neutrales = [
        "Estuvo bien, nada extraordinario",
        "La comida es buena, pero podría mejorar",
        "Cumplió mis expectativas",
        "Normal, igual que otros lugares"
    ]
    
    comentarios_negativos = [
        "Tardó mucho en llegar",
        "La comida llegó fría",
        "No es lo que esperaba",
        "El precio es muy alto para la cantidad"
    ]
    
    # Crear 30 reseñas variadas
    for i in range(30):
        calificacion = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 15, 30, 40])[0]
        
        if calificacion >= 4:
            comentario = random.choice(comentarios_positivos)
        elif calificacion == 3:
            comentario = random.choice(comentarios_neutrales)
        else:
            comentario = random.choice(comentarios_negativos)
        
        resena = MODELO_RESENA_ATENCION(
            USUARIO_ID=random.choice(usuarios).ID,
            CALIFICACION=calificacion,
            COMENTARIO=comentario,
            FECHA=datetime.now() - timedelta(days=random.randint(0, 30))
        )
        
        sesion.add(resena)
    
    sesion.commit()
    print(f"  ✅ Se agregaron 30 reseñas de prueba")
    sesion.close()


def agregar_proveedores():
    """Agrega proveedores"""
    print("\n🏭 Agregando Proveedores...")
    
    sesion = OBTENER_SESION()
    
    count = sesion.query(MODELO_PROVEEDOR).count()
    if count > 0:
        print(f"  ℹ️  Ya existen {count} proveedores")
        sesion.close()
        return
    
    proveedores_data = [
        {
            "nombre": "Distribuidora San José",
            "contacto": "Juan Ramírez",
            "telefono": "987654321",
            "email": "ventas@sanjose.com",
            "direccion": "Av. Industrial 123",
            "productos": "Carnes, Embutidos"
        },
        {
            "nombre": "Verduras Frescas del Valle",
            "contacto": "María Torres",
            "telefono": "987654322",
            "email": "info@verdurasvallle.com",
            "direccion": "Jr. Los Agricultores 456",
            "productos": "Verduras, Hortalizas"
        },
        {
            "nombre": "Panadería El Trigal",
            "contacto": "Carlos Mendoza",
            "telefono": "987654323",
            "email": "pedidos@eltrigal.com",
            "direccion": "Calle Principal 789",
            "productos": "Pan, Bollería"
        },
        {
            "nombre": "Lácteos Premium",
            "contacto": "Ana Silva",
            "telefono": "987654324",
            "email": "ventas@lacteospremium.com",
            "direccion": "Av. Los Ganaderos 321",
            "productos": "Leche, Quesos, Yogurt"
        },
        {
            "nombre": "Bebidas y Refrescos SAC",
            "contacto": "Luis Vega",
            "telefono": "987654325",
            "email": "distribuidora@bebidas.com",
            "direccion": "Parque Industrial 555",
            "productos": "Gaseosas, Jugos, Agua"
        }
    ]
    
    for data in proveedores_data:
        proveedor = MODELO_PROVEEDOR(
            NOMBRE=data["nombre"],
            CONTACTO=data["contacto"],
            TELEFONO=data["telefono"],
            EMAIL=data["email"],
            DIRECCION=data["direccion"]
        )
        sesion.add(proveedor)
    
    sesion.commit()
    print(f"  ✅ Se agregaron {len(proveedores_data)} proveedores")
    sesion.close()


def agregar_productos():
    """Agrega más productos"""
    print("\n🍔 Agregando Productos...")
    
    sesion = OBTENER_SESION()
    
    count = sesion.query(MODELO_PRODUCTO).count()
    print(f"  ℹ️  Productos actuales: {count}")
    
    productos_nuevos = [
        {"nombre": "Hamburguesa BBQ", "precio": 18.50, "descripcion": "Con salsa BBQ y cebolla caramelizada"},
        {"nombre": "Hamburguesa Veggie", "precio": 16.00, "descripcion": "Hamburguesa vegetariana con quinoa"},
        {"nombre": "Papas Rústicas", "precio": 8.00, "descripcion": "Papas con piel, estilo casero"},
        {"nombre": "Alitas Picantes", "precio": 22.00, "descripcion": "12 alitas con salsa picante"},
        {"nombre": "Ensalada César", "precio": 14.00, "descripcion": "Lechuga, pollo, queso parmesano"},
        {"nombre": "Nuggets (6 unid)", "precio": 12.00, "descripcion": "Nuggets de pollo crispy"},
        {"nombre": "Limonada Frozen", "precio": 6.00, "descripcion": "Limonada helada natural"},
        {"nombre": "Chicha Morada", "precio": 5.50, "descripcion": "Chicha morada casera"},
        {"nombre": "Combo Pareja", "precio": 45.00, "descripcion": "2 hamburguesas + 2 bebidas + papas"},
        {"nombre": "Combo Niños", "precio": 18.00, "descripcion": "Nuggets + papas + jugo + helado"},
    ]
    
    agregados = 0
    for prod_data in productos_nuevos:
        # Verificar si ya existe
        existe = sesion.query(MODELO_PRODUCTO).filter_by(NOMBRE=prod_data["nombre"]).first()
        if not existe:
            producto = MODELO_PRODUCTO(
                NOMBRE=prod_data["nombre"],
                PRECIO=prod_data["precio"],
                DESCRIPCION=prod_data["descripcion"],
                DISPONIBLE=True
            )
            sesion.add(producto)
            agregados += 1
    
    if agregados > 0:
        sesion.commit()
        print(f"  ✅ Se agregaron {agregados} productos nuevos")
    else:
        print(f"  ℹ️  Todos los productos ya existen")
    
    sesion.close()


def agregar_ventas_ejemplo():
    """Agrega pedidos de ejemplo (ventas)"""
    print("\n💰 Agregando Pedidos/Ventas de Ejemplo...")
    
    sesion = OBTENER_SESION()
    
    # Obtener datos necesarios
    cliente = sesion.query(MODELO_USUARIO).filter(
        MODELO_USUARIO.ROLES.any()
    ).first()
    
    sucursal = sesion.query(MODELO_SUCURSAL).first()
    productos = sesion.query(MODELO_PRODUCTO).limit(5).all()
    
    if not cliente or not sucursal or not productos:
        print("  ❌ No hay datos base (cliente, sucursal, productos)")
        sesion.close()
        return
    
    # Verificar pedidos existentes
    count = sesion.query(MODELO_PEDIDO).count()
    print(f"  ℹ️  Pedidos actuales: {count}")
    
    estados = ["pendiente", "confirmado", "en_preparacion", "listo", "en_camino", "entregado"]
    
    # Crear 20 pedidos de los últimos 7 días
    agregados = 0
    for i in range(20):
        fecha = datetime.now() - timedelta(days=random.randint(0, 7))
        estado = random.choice(estados)
        
        # Seleccionar 1-3 productos aleatorios
        num_productos = random.randint(1, 3)
        productos_pedido = random.sample(productos, min(num_productos, len(productos)))
        
        monto_total = sum(p.PRECIO * random.randint(1, 3) for p in productos_pedido)
        
        pedido = MODELO_PEDIDO(
            CLIENTE_ID=cliente.ID,
            SUCURSAL_ID=sucursal.ID,
            TIPO=random.choice(["delivery", "tienda", "recoger"]),
            ESTADO=estado,
            MONTO_TOTAL=monto_total,
            FECHA_CREACION=fecha
        )
        
        sesion.add(pedido)
        sesion.flush()  # Para obtener el ID
        
        # Agregar detalles
        for producto in productos_pedido:
            cantidad = random.randint(1, 3)
            detalle = MODELO_DETALLE_PEDIDO(
                PEDIDO_ID=pedido.ID,
                PRODUCTO_ID=producto.ID,
                CANTIDAD=cantidad,
                PRECIO_UNITARIO=producto.PRECIO
            )
            sesion.add(detalle)
        
        agregados += 1
    
    sesion.commit()
    print(f"  ✅ Se agregaron {agregados} pedidos/ventas de ejemplo")
    sesion.close()


def mostrar_resumen():
    """Muestra resumen de datos en el sistema"""
    print("\n" + "="*60)
    print("📊 RESUMEN DE DATOS EN EL SISTEMA")
    print("="*60)
    
    sesion = OBTENER_SESION()
    
    datos = {
        "Reseñas": sesion.query(MODELO_RESENA_ATENCION).count(),
        "Productos": sesion.query(MODELO_PRODUCTO).count(),
        "Proveedores": sesion.query(MODELO_PROVEEDOR).count(),
        "Pedidos/Ventas": sesion.query(MODELO_PEDIDO).count(),
        "Usuarios": sesion.query(MODELO_USUARIO).count(),
        "Sucursales": sesion.query(MODELO_SUCURSAL).count(),
    }
    
    for nombre, cantidad in datos.items():
        print(f"  • {nombre:20} : {cantidad:>5}")
    
    # Resumen de reseñas por calificación
    print("\n📝 Reseñas por Calificación:")
    for i in range(5, 0, -1):
        count = sesion.query(MODELO_RESENA_ATENCION).filter_by(CALIFICACION=i).count()
        estrellas = "⭐" * i
        print(f"  {estrellas:10} : {count:>3}")
    
    # Ventas por estado
    print("\n💰 Pedidos por Estado:")
    estados = sesion.query(MODELO_PEDIDO.ESTADO).distinct().all()
    for (estado,) in estados:
        count = sesion.query(MODELO_PEDIDO).filter_by(ESTADO=estado).count()
        print(f"  • {estado:20} : {count:>3}")
    
    sesion.close()
    print("="*60)


if __name__ == "__main__":
    print("🚀 INICIANDO CARGA DE DATOS DE PRUEBA")
    print("="*60)
    
    try:
        agregar_reseñas()
        agregar_proveedores()
        agregar_productos()
        agregar_ventas_ejemplo()
        
        mostrar_resumen()
        
        print("\n✅ PROCESO COMPLETADO EXITOSAMENTE")
        
    except Exception as e:
        print(f"\n❌ Error durante el proceso: {e}")
        import traceback
        traceback.print_exc()
