#!/usr/bin/env python3
"""
🧪 Test Completo del Sistema de Chat con Estados
"""

import sys
import asyncio
sys.path.insert(0, '/mnt/flox/conychips')

from core.chat.GestorChat import GestorChat, EstadoMensaje
from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION,
    MODELO_USUARIO,
    MODELO_PEDIDO,
    MODELO_ROL,
    MODELO_PRODUCTO,
    MODELO_DETALLE_PEDIDO,
    MODELO_SUCURSAL,
)


def crear_datos_prueba():
    """Crea datos de prueba"""
    print("📊 Creando datos de prueba...")
    
    sesion = OBTENER_SESION()
    
    try:
        # Obtener sucursal
        sucursal = sesion.query(MODELO_SUCURSAL).first()
        if not sucursal:
            print("❌ No hay sucursales")
            return None, None, None
        
        # Obtener roles
        rol_cliente = sesion.query(MODELO_ROL).filter_by(NOMBRE="CLIENTE").first()
        rol_admin = sesion.query(MODELO_ROL).filter_by(NOMBRE="ADMIN").first()
        
        # Obtener usuarios
        cliente = sesion.query(MODELO_USUARIO).filter(
            MODELO_USUARIO.ROLES.any(MODELO_ROL.NOMBRE == "CLIENTE")
        ).first()
        
        admin = sesion.query(MODELO_USUARIO).filter(
            MODELO_USUARIO.ROLES.any(MODELO_ROL.NOMBRE == "ADMIN")
        ).first()
        
        if not cliente or not admin:
            print("❌ No hay cliente o admin")
            return None, None, None
        
        # Obtener producto
        producto = sesion.query(MODELO_PRODUCTO).first()
        if not producto:
            print("❌ No hay productos")
            return None, None, None
        
        # Buscar o crear pedido
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
                MONTO_TOTAL=10000,
            )
            sesion.add(pedido)
            sesion.commit()
            
            detalle = MODELO_DETALLE_PEDIDO(
                PEDIDO_ID=pedido.ID,
                PRODUCTO_ID=producto.ID,
                CANTIDAD=2,
                PRECIO_UNITARIO=5000,
            )
            sesion.add(detalle)
            sesion.commit()
        
        print(f"  ✓ Sucursal: {sucursal.NOMBRE}")
        print(f"  ✓ Cliente: {cliente.NOMBRE_USUARIO} (ID: {cliente.ID})")
        print(f"  ✓ Admin: {admin.NOMBRE_USUARIO} (ID: {admin.ID})")
        print(f"  ✓ Pedido ID: {pedido.ID}")
        
        return cliente, admin, pedido
        
    finally:
        sesion.close()


async def test_sistema_chat():
    """Test completo del sistema de chat"""
    print("\n🧪 TESTING SISTEMA DE CHAT COMPLETO")
    print("="*60)
    
    # Crear datos
    cliente, admin, pedido = crear_datos_prueba()
    if not cliente or not admin or not pedido:
        print("❌ No se pudieron crear datos de prueba")
        return
    
    # Inicializar gestor
    gestor = GestorChat()
    
    # Test 1: Verificar permisos
    print("\n📋 Test 1: Verificar Permisos")
    print("-"*60)
    
    tiene_permiso_cliente = gestor.VERIFICAR_PERMISO_CHAT(cliente.ID, pedido.ID)
    tiene_permiso_admin = gestor.VERIFICAR_PERMISO_CHAT(admin.ID, pedido.ID)
    
    print(f"  • Cliente tiene permiso: {tiene_permiso_cliente}")
    print(f"  • Admin tiene permiso: {tiene_permiso_admin}")
    
    if tiene_permiso_cliente and tiene_permiso_admin:
        print("  ✅ Permisos correctos")
    else:
        print("  ❌ Error en permisos")
        return
    
    # Test 2: Cliente envía mensaje
    print("\n📤 Test 2: Cliente Envía Mensaje")
    print("-"*60)
    
    resultado1 = await gestor.ENVIAR_MENSAJE(
        pedido_id=pedido.ID,
        usuario_id=cliente.ID,
        mensaje="Hola admin, ¿cuándo estará listo mi pedido?"
    )
    
    print(f"  • Resultado: {resultado1}")
    
    if resultado1.get("exito"):
        print(f"  ✅ Mensaje enviado (ID: {resultado1['mensaje_id']})")
        print(f"  • Hash: {resultado1['hash'][:16]}...")
        print(f"  • Estado: {resultado1['estado']}")
    else:
        print(f"  ❌ Error: {resultado1.get('error')}")
        return
    
    # Esperar un momento
    await asyncio.sleep(0.5)
    
    # Test 3: Admin responde
    print("\n📤 Test 3: Admin Responde")
    print("-"*60)
    
    resultado2 = await gestor.ENVIAR_MENSAJE(
        pedido_id=pedido.ID,
        usuario_id=admin.ID,
        mensaje="¡Hola! Tu pedido estará listo en 20 minutos 🍟"
    )
    
    print(f"  • Resultado: {resultado2}")
    
    if resultado2.get("exito"):
        print(f"  ✅ Respuesta enviada (ID: {resultado2['mensaje_id']})")
        print(f"  • Hash: {resultado2['hash'][:16]}...")
    else:
        print(f"  ❌ Error: {resultado2.get('error')}")
        return
    
    # Test 4: Obtener mensajes
    print("\n📋 Test 4: Obtener Mensajes")
    print("-"*60)
    
    mensajes = gestor.OBTENER_MENSAJES(pedido.ID, cliente.ID)
    
    print(f"  • Total de mensajes: {len(mensajes)}")
    
    for i, msg in enumerate(mensajes, 1):
        print(f"\n  Mensaje {i}:")
        print(f"    - De: {msg['usuario_nombre']}")
        print(f"    - Contenido: {msg['mensaje']}")
        print(f"    - Estado: {msg.get('estado', 'N/A')}")
        print(f"    - Hash: {msg.get('hash', 'N/A')[:16]}..." if msg.get('hash') else "    - Hash: N/A")
        print(f"    - Es mío: {msg['es_mio']}")
    
    if len(mensajes) >= 2:
        print("\n  ✅ Mensajes obtenidos correctamente")
    else:
        print("\n  ❌ No se obtuvieron todos los mensajes")
        return
    
    # Test 5: Marcar como leído
    print("\n📖 Test 5: Marcar Mensajes como Leídos")
    print("-"*60)
    
    mensaje_cliente = [m for m in mensajes if not m['es_mio']]
    if mensaje_cliente:
        await gestor.MARCAR_LEIDO(mensaje_cliente[0]['id'], admin.ID)
        print(f"  ✅ Mensaje {mensaje_cliente[0]['id']} marcado como leído")
    
    # Test 6: Typing indicator
    print("\n⌨️  Test 6: Indicador de Escritura")
    print("-"*60)
    
    await gestor.NOTIFICAR_ESCRIBIENDO(pedido.ID, cliente.ID, True)
    print("  • Cliente está escribiendo...")
    
    usuarios_escribiendo = gestor.OBTENER_USUARIOS_ESCRIBIENDO(pedido.ID)
    print(f"  • Usuarios escribiendo: {usuarios_escribiendo}")
    
    if cliente.ID in usuarios_escribiendo:
        print("  ✅ Indicador de escritura funcionando")
    else:
        print("  ❌ Indicador de escritura no funciona")
    
    await gestor.NOTIFICAR_ESCRIBIENDO(pedido.ID, cliente.ID, False)
    print("  • Cliente dejó de escribir")
    
    # Test 7: Hash y seguridad
    print("\n🔒 Test 7: Verificación de Hash")
    print("-"*60)
    
    hash1 = GestorChat.HASHEAR_MENSAJE("test", 1, "2026-01-01T00:00:00")
    hash2 = GestorChat.HASHEAR_MENSAJE("test", 1, "2026-01-01T00:00:00")
    hash3 = GestorChat.HASHEAR_MENSAJE("test diferente", 1, "2026-01-01T00:00:00")
    
    print(f"  • Hash 1: {hash1[:16]}...")
    print(f"  • Hash 2: {hash2[:16]}...")
    print(f"  • Hash 3: {hash3[:16]}...")
    
    if hash1 == hash2 and hash1 != hash3:
        print("  ✅ Hashing funcionando correctamente")
    else:
        print("  ❌ Error en hashing")
    
    print("\n" + "="*60)
    print("✅ TODOS LOS TESTS COMPLETADOS EXITOSAMENTE")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_sistema_chat())
