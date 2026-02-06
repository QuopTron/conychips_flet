"""
Script para crear roles faltantes en la base de datos
"""
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_ROL

def crear_roles_faltantes():
    """Crea los roles que faltan en el sistema"""
    
    roles_sistema = [
        {
            "nombre": "SUPERADMIN",
            "descripcion": "Administrador total del sistema con todos los permisos",
            "permisos": "*"  # Todos los permisos
        },
        {
            "nombre": "ADMIN",
            "descripcion": "Administrador con permisos de gestión general",
            "permisos": "usuarios.*,roles.*,sucursales.*,productos.*,pedidos.*,finanzas.*"
        },
        {
            "nombre": "GESTORA_CALIDAD",
            "descripcion": "Gestora de calidad - supervisa y audita operaciones",
            "permisos": "pedidos.ver,pedidos.listar,productos.ver,productos.listar,auditoria.*,reportes.*"
        },
        {
            "nombre": "ATENCION",
            "descripcion": "Atención al cliente - gestión de pedidos y clientes",
            "permisos": "pedidos.*,clientes.*,productos.ver,productos.listar"
        },
        {
            "nombre": "COCINERO",
            "descripcion": "Chef / Cocinero - gestión de cocina y preparación",
            "permisos": "cocina.*,pedidos.ver,pedidos.actualizar,productos.ver"
        },
        {
            "nombre": "MOTORIZADO",
            "descripcion": "Motorizado / Delivery - entregas y rutas",
            "permisos": "entregas.*,pedidos.ver,pedidos.actualizar,rutas.*"
        }
    ]
    
    print("=" * 80)
    print("CREANDO/ACTUALIZANDO ROLES DEL SISTEMA")
    print("=" * 80)
    
    with OBTENER_SESION() as sesion:
        for rol_data in roles_sistema:
            # Verificar si el rol ya existe
            existe = sesion.query(MODELO_ROL).filter_by(NOMBRE=rol_data["nombre"]).first()
            
            if existe:
                # Actualizar descripción y permisos
                existe.DESCRIPCION = rol_data["descripcion"]
                existe.PERMISOS = rol_data["permisos"]
                print(f"\n🔄 Rol '{rol_data['nombre']}' actualizado")
                print(f"   📝 {rol_data['descripcion']}")
                print(f"   🔑 Permisos: {rol_data['permisos']}")
            else:
                # Crear nuevo rol
                nuevo_rol = MODELO_ROL(
                    NOMBRE=rol_data["nombre"],
                    DESCRIPCION=rol_data["descripcion"],
                    PERMISOS=rol_data["permisos"],
                    ACTIVO=True
                )
                sesion.add(nuevo_rol)
                print(f"\n✅ Rol '{rol_data['nombre']}' creado")
                print(f"   📝 {rol_data['descripcion']}")
                print(f"   🔑 Permisos: {rol_data['permisos']}")
        
        sesion.commit()
    
    print("\n" + "=" * 80)
    print("✅ ROLES CREADOS/ACTUALIZADOS EXITOSAMENTE")
    print("=" * 80)

if __name__ == "__main__":
    crear_roles_faltantes()
