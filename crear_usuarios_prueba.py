"""
Script para crear usuarios de prueba con contraseñas conocidas
"""
import bcrypt
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_USUARIO, MODELO_ROL

def crear_usuarios_prueba():
    """Crea usuarios de prueba para cada rol"""
    
    usuarios_prueba = [
        {
            "nombre": "superadmin",
            "email": "superadmin@conychips.com",
            "password": "super123",
            "rol": "SUPERADMIN",
            "descripcion": "👑 Administrador Total del Sistema"
        },
        {
            "nombre": "admin",
            "email": "admin@conychips.com",
            "password": "admin123",
            "rol": "ADMIN",
            "descripcion": "🔧 Administrador General"
        },
        {
            "nombre": "gestora",
            "email": "gestora@conychips.com",
            "password": "gestora123",
            "rol": "GESTORA_CALIDAD",
            "descripcion": "✅ Gestora de Calidad"
        },
        {
            "nombre": "atencion",
            "email": "atencion@conychips.com",
            "password": "atencion123",
            "rol": "ATENCION",
            "descripcion": "🎯 Atención al Cliente"
        },
        {
            "nombre": "cocinero",
            "email": "cocinero@conychips.com",
            "password": "cocina123",
            "rol": "COCINERO",
            "descripcion": "👨‍🍳 Chef / Cocinero"
        },
        {
            "nombre": "motorizado",
            "email": "motorizado@conychips.com",
            "password": "moto123",
            "rol": "MOTORIZADO",
            "descripcion": "🏍️ Motorizado / Delivery"
        }
    ]
    
    print("=" * 80)
    print("CREANDO USUARIOS DE PRUEBA")
    print("=" * 80)
    
    with OBTENER_SESION() as sesion:
        for user_data in usuarios_prueba:
            # Verificar si el usuario ya existe
            existe = sesion.query(MODELO_USUARIO).filter_by(
                NOMBRE_USUARIO=user_data["nombre"]
            ).first()
            
            if existe:
                print(f"\n⚠️  Usuario '{user_data['nombre']}' ya existe - SALTANDO")
                continue
            
            # Hashear contraseña
            password_hash = bcrypt.hashpw(
                user_data["password"].encode('utf-8'), 
                bcrypt.gensalt()
            ).decode('utf-8')
            
            # Crear usuario
            nuevo_usuario = MODELO_USUARIO(
                NOMBRE_USUARIO=user_data["nombre"],
                EMAIL=user_data["email"],
                CONTRASENA_HASH=password_hash,
                HUELLA_DISPOSITIVO="test-device",
                ACTIVO=True,
                VERIFICADO=True
            )
            
            sesion.add(nuevo_usuario)
            sesion.flush()  # Para obtener el ID
            
            # Buscar y asignar rol
            rol = sesion.query(MODELO_ROL).filter_by(NOMBRE=user_data["rol"]).first()
            
            if rol:
                nuevo_usuario.ROLES.append(rol)
                print(f"\n✅ Usuario creado: {user_data['nombre']}")
                print(f"   {user_data['descripcion']}")
                print(f"   📧 Email: {user_data['email']}")
                print(f"   🔑 Contraseña: {user_data['password']}")
                print(f"   👤 Rol: {user_data['rol']}")
            else:
                print(f"\n❌ Rol '{user_data['rol']}' no encontrado para {user_data['nombre']}")
        
        sesion.commit()
    
    print("\n" + "=" * 80)
    print("✅ USUARIOS DE PRUEBA CREADOS EXITOSAMENTE")
    print("=" * 80)
    print("\n📋 CREDENCIALES DE ACCESO:\n")
    
    for user_data in usuarios_prueba:
        print(f"{user_data['descripcion']}")
        print(f"   Usuario: {user_data['nombre']}")
        print(f"   Contraseña: {user_data['password']}")
        print()

if __name__ == "__main__":
    crear_usuarios_prueba()
