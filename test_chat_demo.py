#!/usr/bin/env python3
"""
Script de prueba de chat entre cliente y admin
"""

import sys
import asyncio
sys.path.insert(0, '/mnt/flox/conychips')

from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION,
    MODELO_USUARIO,
    MODELO_PEDIDO,
    MODELO_SUCURSAL,
    MODELO_DETALLE_PEDIDO,
    MODELO_PRODUCTO,
    MODELO_MENSAJE_CHAT,
)
from core.websocket.GestorNotificaciones import GestorNotificaciones

def crear_datos_prueba():
    """Crea datos de prueba para el chat"""
    print("📊 Creando datos de prueba...")
    
    sesion = OBTENER_SESION()
    
    # Obtener o crear sucursal
    sucursal = sesion.query(MODELO_SUCURSAL).first()
    if not sucursal:
        print("❌ No hay sucursales en la base de datos")
        sesion.close()
        return None, None, None, None
    
    # Obtener usuarios con rol CLIENTE y ADMIN
    from core.base_datos.ConfiguracionBD import MODELO_ROL
    
    rol_cliente = sesion.query(MODELO_ROL).filter_by(NOMBRE="CLIENTE").first()
    rol_admin = sesion.query(MODELO_ROL).filter_by(NOMBRE="ADMIN").first()
    
    if not rol_cliente:
        print("❌ No existe rol CLIENTE en la base de datos")
        sesion.close()
        return None, None, None, None
    
    if not rol_admin:
        print("❌ No existe rol ADMIN en la base de datos")
        sesion.close()
        return None, None, None, None
    
    # Obtener un cliente y un admin
    cliente = sesion.query(MODELO_USUARIO).filter(
        MODELO_USUARIO.ROLES.any(MODELO_ROL.NOMBRE == "CLIENTE")
    ).first()
    
    admin = sesion.query(MODELO_USUARIO).filter(
        MODELO_USUARIO.ROLES.any(MODELO_ROL.NOMBRE == "ADMIN")
    ).first()
    
    if not cliente:
        print("❌ No hay clientes en la base de datos")
        sesion.close()
        return None, None, None, None
    
    if not admin:
        print("❌ No hay admins en la base de datos")
        sesion.close()
        return None, None, None, None
    
    # Obtener un producto
    producto = sesion.query(MODELO_PRODUCTO).first()
    if not producto:
        print("❌ No hay productos en la base de datos")
        sesion.close()
        return None, None, None, None
    
    # Crear un pedido de prueba
    print(f"  • Sucursal: {sucursal.NOMBRE}")
    print(f"  • Cliente: {cliente.NOMBRE_USUARIO} (ID: {cliente.ID})")
    print(f"  • Admin: {admin.NOMBRE_USUARIO} (ID: {admin.ID})")
    print(f"  • Producto: {producto.NOMBRE}")
    
    # Buscar si ya existe un pedido de prueba
    pedido = sesion.query(MODELO_PEDIDO).filter_by(
        CLIENTE_ID=cliente.ID,
        ESTADO="pendiente"
    ).first()
    
    if not pedido:
        print("  • Creando nuevo pedido...")
        pedido = MODELO_PEDIDO(
            CLIENTE_ID=cliente.ID,
            SUCURSAL_ID=sucursal.ID,
            TIPO="delivery",
            ESTADO="pendiente",
            MONTO_TOTAL=10000,  # S/ 100
        )
        sesion.add(pedido)
        sesion.commit()
        
        # Crear detalle del pedido
        detalle = MODELO_DETALLE_PEDIDO(
            PEDIDO_ID=pedido.ID,
            PRODUCTO_ID=producto.ID,
            CANTIDAD=2,
            PRECIO_UNITARIO=5000,  # S/ 50 c/u
        )
        sesion.add(detalle)
        sesion.commit()
    
    print(f"  ✓ Pedido ID: {pedido.ID}")
    
    sesion.close()
    return cliente, admin, pedido, sucursal


async def test_chat():
    """Test del sistema de chat"""
    print("\n🧪 TESTING SISTEMA DE CHAT")
    print("=" * 60)
    
    # Crear datos de prueba
    cliente, admin, pedido, sucursal = crear_datos_prueba()
    
    if not cliente or not admin or not pedido:
        print("❌ No se pudieron crear datos de prueba")
        return
    
    # Inicializar gestor de notificaciones
    gestor = GestorNotificaciones()
    
    # Test 1: Cliente envía mensaje
    print("\n📤 Test 1: Cliente envía mensaje al admin")
    print("  • Cliente ID:", cliente.ID)
    print("  • Pedido ID:", pedido.ID)
    print("  • Mensaje: 'Hola admin, ¿cuándo estará listo mi pedido?'")
    
    await gestor.ENVIAR_MENSAJE_CHAT(
        PEDIDO_ID=pedido.ID,
        USUARIO_ID=cliente.ID,
        MENSAJE="Hola admin, ¿cuándo estará listo mi pedido?",
        TIPO="texto"
    )
    print("  ✅ Mensaje enviado")
    
    # Test 2: Admin responde
    print("\n📤 Test 2: Admin responde al cliente")
    print("  • Admin ID:", admin.ID)
    print("  • Pedido ID:", pedido.ID)
    print("  • Mensaje: 'Hola! Tu pedido estará listo en 20 minutos'")
    
    await gestor.ENVIAR_MENSAJE_CHAT(
        PEDIDO_ID=pedido.ID,
        USUARIO_ID=admin.ID,
        MENSAJE="Hola! Tu pedido estará listo en 20 minutos",
        TIPO="texto"
    )
    print("  ✅ Mensaje enviado")
    
    # Test 3: Verificar mensajes en BD
    print("\n📋 Test 3: Verificar mensajes en base de datos")
    sesion = OBTENER_SESION()
    
    mensajes = (
        sesion.query(MODELO_MENSAJE_CHAT)
        .filter_by(PEDIDO_ID=pedido.ID)
        .order_by(MODELO_MENSAJE_CHAT.FECHA.asc())
        .all()
    )
    
    print(f"  • Total de mensajes: {len(mensajes)}")
    for i, msg in enumerate(mensajes, 1):
        usuario = sesion.query(MODELO_USUARIO).filter_by(ID=msg.USUARIO_ID).first()
        print(f"\n  Mensaje {i}:")
        print(f"    - De: {usuario.NOMBRE_USUARIO if usuario else f'Usuario {msg.USUARIO_ID}'}")
        print(f"    - Contenido: {msg.MENSAJE}")
        print(f"    - Hora: {msg.FECHA.strftime('%H:%M:%S')}")
    
    sesion.close()
    
    print("\n" + "=" * 60)
    print("✅ TEST DE CHAT COMPLETADO")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_chat())
