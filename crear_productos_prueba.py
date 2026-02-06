"""
Script para crear productos de prueba con sucursales y extras
"""
from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION,
    MODELO_PRODUCTO,
    MODELO_SUCURSAL,
    MODELO_EXTRA,
)


def crear_productos_prueba():
    """Crea productos de prueba variados para testing"""
    
    productos_data = [
        {
            "NOMBRE": "Pizza Margarita",
            "DESCRIPCION": "Pizza clásica con salsa de tomate, mozzarella y albahaca fresca",
            "PRECIO": 12000,
            "DISPONIBLE": True,
        },
        {
            "NOMBRE": "Pizza Pepperoni",
            "DESCRIPCION": "Pizza con salsa de tomate, mozzarella y pepperoni premium",
            "PRECIO": 15000,
            "DISPONIBLE": True,
        },
        {
            "NOMBRE": "Pizza Hawaiana",
            "DESCRIPCION": "Pizza con jamón, piña, mozzarella y salsa especial",
            "PRECIO": 14000,
            "DISPONIBLE": True,
        },
        {
            "NOMBRE": "Hamburguesa Clásica",
            "DESCRIPCION": "Carne de res, lechuga, tomate, cebolla y salsa especial",
            "PRECIO": 8000,
            "DISPONIBLE": True,
        },
        {
            "NOMBRE": "Hamburguesa BBQ",
            "DESCRIPCION": "Carne de res, bacon, cebolla caramelizada y salsa BBQ",
            "PRECIO": 10000,
            "DISPONIBLE": True,
        },
        {
            "NOMBRE": "Coca Cola 500ml",
            "DESCRIPCION": "Bebida gaseosa sabor cola",
            "PRECIO": 2500,
            "DISPONIBLE": True,
        },
        {
            "NOMBRE": "Sprite 500ml",
            "DESCRIPCION": "Bebida gaseosa sabor lima-limón",
            "PRECIO": 2500,
            "DISPONIBLE": True,
        },
        {
            "NOMBRE": "Fanta 500ml",
            "DESCRIPCION": "Bebida gaseosa sabor naranja",
            "PRECIO": 2500,
            "DISPONIBLE": True,
        },
        {
            "NOMBRE": "Papas Fritas Medianas",
            "DESCRIPCION": "Papas fritas crujientes con sal",
            "PRECIO": 3500,
            "DISPONIBLE": True,
        },
        {
            "NOMBRE": "Papas Fritas Grandes",
            "DESCRIPCION": "Porción grande de papas fritas crujientes",
            "PRECIO": 5000,
            "DISPONIBLE": True,
        },
        {
            "NOMBRE": "Helado de Vainilla",
            "DESCRIPCION": "Copa de helado de vainilla premium",
            "PRECIO": 4000,
            "DISPONIBLE": False,  # No disponible por temporada
        },
        {
            "NOMBRE": "Ensalada César",
            "DESCRIPCION": "Lechuga romana, pollo, croutons, parmesano y aderezo césar",
            "PRECIO": 9000,
            "DISPONIBLE": True,
        },
    ]
    
    extras_data = [
        {
            "NOMBRE": "Extra Queso",
            "DESCRIPCION": "Porción adicional de queso mozzarella",
            "PRECIO_ADICIONAL": 2000,
            "ACTIVO": True,
        },
        {
            "NOMBRE": "Extra Bacon",
            "DESCRIPCION": "Tiras de bacon crujiente",
            "PRECIO_ADICIONAL": 2500,
            "ACTIVO": True,
        },
        {
            "NOMBRE": "Extra Champiñones",
            "DESCRIPCION": "Champiñones frescos salteados",
            "PRECIO_ADICIONAL": 1500,
            "ACTIVO": True,
        },
        {
            "NOMBRE": "Extra Salsa Picante",
            "DESCRIPCION": "Salsa picante especial de la casa",
            "PRECIO_ADICIONAL": 500,
            "ACTIVO": True,
        },
        {
            "NOMBRE": "Extra Aguacate",
            "DESCRIPCION": "Rodajas de aguacate fresco",
            "PRECIO_ADICIONAL": 3000,
            "ACTIVO": True,
        },
        {
            "NOMBRE": "Extra Pepperoni",
            "DESCRIPCION": "Pepperoni adicional",
            "PRECIO_ADICIONAL": 2000,
            "ACTIVO": True,
        },
    ]
    
    print("=" * 80)
    print("CREANDO PRODUCTOS Y EXTRAS DE PRUEBA")
    print("=" * 80)
    
    with OBTENER_SESION() as sesion:
        # === CREAR EXTRAS ===
        print("\n📦 CREANDO EXTRAS:")
        extras_creados = []
        for extra_data in extras_data:
            existe = sesion.query(MODELO_EXTRA).filter_by(NOMBRE=extra_data["NOMBRE"]).first()
            if existe:
                print(f"   ⚠️  Extra '{extra_data['NOMBRE']}' ya existe - SALTANDO")
                extras_creados.append(existe)
            else:
                nuevo_extra = MODELO_EXTRA(**extra_data)
                sesion.add(nuevo_extra)
                sesion.flush()
                extras_creados.append(nuevo_extra)
                print(f"   ✅ Extra creado: {extra_data['NOMBRE']} (+${extra_data['PRECIO_ADICIONAL']:,})")
        
        sesion.commit()
        
        # === OBTENER SUCURSALES ===
        sucursales = sesion.query(MODELO_SUCURSAL).filter_by(ELIMINADA=False).all()
        print(f"\n🏪 Sucursales disponibles: {len(sucursales)}")
        for suc in sucursales:
            print(f"   - {suc.NOMBRE}")
        
        # === CREAR PRODUCTOS ===
        print("\n🍕 CREANDO PRODUCTOS:")
        productos_creados = []
        for prod_data in productos_data:
            existe = sesion.query(MODELO_PRODUCTO).filter_by(NOMBRE=prod_data["NOMBRE"]).first()
            if existe:
                print(f"   ⚠️  Producto '{prod_data['NOMBRE']}' ya existe - SALTANDO")
                productos_creados.append(existe)
            else:
                nuevo_producto = MODELO_PRODUCTO(**prod_data)
                sesion.add(nuevo_producto)
                sesion.flush()
                productos_creados.append(nuevo_producto)
                print(f"   ✅ Producto creado: {prod_data['NOMBRE']} (${prod_data['PRECIO']:,})")
        
        sesion.commit()
        
        # === ASIGNAR SUCURSALES A PRODUCTOS ===
        print("\n🔗 ASIGNANDO SUCURSALES A PRODUCTOS:")
        if sucursales:
            for i, producto in enumerate(productos_creados):
                # Limpiar asignaciones previas
                producto.SUCURSALES.clear()
                
                # Asignar sucursales (alternando patrones)
                if i % 3 == 0:
                    # Todas las sucursales
                    producto.SUCURSALES.extend(sucursales)
                    print(f"   📍 {producto.NOMBRE}: Todas las sucursales ({len(sucursales)})")
                elif i % 3 == 1:
                    # Primera sucursal
                    producto.SUCURSALES.append(sucursales[0])
                    print(f"   📍 {producto.NOMBRE}: {sucursales[0].NOMBRE}")
                else:
                    # Dos primeras sucursales (si hay)
                    producto.SUCURSALES.extend(sucursales[:min(2, len(sucursales))])
                    nombres = ", ".join([s.NOMBRE for s in sucursales[:min(2, len(sucursales))]])
                    print(f"   📍 {producto.NOMBRE}: {nombres}")
        
        sesion.commit()
        
        # === ASIGNAR EXTRAS A PRODUCTOS ===
        print("\n🎁 ASIGNANDO EXTRAS A PRODUCTOS:")
        # Solo pizzas y hamburguesas tienen extras
        productos_con_extras = [p for p in productos_creados if "Pizza" in p.NOMBRE or "Hamburguesa" in p.NOMBRE]
        
        for producto in productos_con_extras:
            producto.EXTRAS.clear()
            
            if "Pizza" in producto.NOMBRE:
                # Pizzas: queso, champiñones, pepperoni
                extras_pizza = [e for e in extras_creados if e.NOMBRE in ["Extra Queso", "Extra Champiñones", "Extra Pepperoni"]]
                producto.EXTRAS.extend(extras_pizza)
                nombres_extras = ", ".join([e.NOMBRE for e in extras_pizza])
                print(f"   🎁 {producto.NOMBRE}: {nombres_extras}")
            
            elif "Hamburguesa" in producto.NOMBRE:
                # Hamburguesas: queso, bacon, aguacate, salsa picante
                extras_burger = [e for e in extras_creados if e.NOMBRE in ["Extra Queso", "Extra Bacon", "Extra Aguacate", "Extra Salsa Picante"]]
                producto.EXTRAS.extend(extras_burger)
                nombres_extras = ", ".join([e.NOMBRE for e in extras_burger])
                print(f"   🎁 {producto.NOMBRE}: {nombres_extras}")
        
        sesion.commit()
    
    print("\n" + "=" * 80)
    print("✅ PRODUCTOS Y EXTRAS CREADOS EXITOSAMENTE")
    print("=" * 80)
    print(f"\n📊 RESUMEN:")
    print(f"   🍕 Productos: {len(productos_data)}")
    print(f"   🎁 Extras: {len(extras_data)}")
    print(f"   🏪 Sucursales: {len(sucursales) if sucursales else 0}")
    print(f"   🔗 Productos con extras: {len(productos_con_extras)}")


if __name__ == "__main__":
    crear_productos_prueba()
