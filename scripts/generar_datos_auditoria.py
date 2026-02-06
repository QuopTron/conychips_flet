"""
Script para generar datos de ejemplo en la tabla de auditoría.
Útil para testing y visualización de la página de auditoría.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
import random
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_AUDITORIA, MODELO_USUARIO


# Datos de ejemplo
ACCIONES_EJEMPLO = {
    "LOGIN": [
        "Inicio de sesión exitoso",
        "Login desde nueva IP",
        "Inicio de sesión con 2FA",
        "Login después de cambio de contraseña",
    ],
    "LOGOUT": [
        "Cierre de sesión normal",
        "Sesión cerrada por inactividad",
        "Logout remoto por admin",
        "Cierre de sesión manual",
    ],
    "CREAR": [
        "Creó nuevo producto: Pollo Broaster",
        "Creó pedido para delivery",
        "Creó nueva sucursal",
        "Creó nuevo usuario empleado",
        "Creó nueva oferta promocional",
        "Creó nuevo proveedor",
        "Creó registro de insumo",
    ],
    "EDITAR": [
        "Editó precio de producto",
        "Modificó estado de pedido a 'en cocina'",
        "Actualizó información de sucursal",
        "Cambió permisos de rol",
        "Modificó stock de insumo",
        "Editó datos de proveedor",
        "Actualizó horario de sucursal",
    ],
    "ELIMINAR": [
        "Eliminó producto descontinuado",
        "Eliminó usuario inactivo",
        "Eliminó oferta vencida",
        "Eliminó registro duplicado",
        "Eliminó proveedor sin contratos",
    ],
    "VER": [
        "Consultó reporte de ventas",
        "Visualizó dashboard financiero",
        "Revisó inventario de insumos",
        "Consultó estado de pedidos",
        "Visualizó auditoría del sistema",
    ],
    "ERROR": [
        "Error al procesar pago: tarjeta rechazada",
        "Error de conexión con base de datos",
        "Intento de acceso sin permisos",
        "Error al generar reporte PDF",
        "Fallo en validación de datos",
    ]
}

ENTIDADES = [
    "USUARIOS",
    "PRODUCTOS",
    "PEDIDOS",
    "SUCURSALES",
    "ROLES",
    "PROVEEDORES",
    "INSUMOS",
    "CAJAS",
    "OFERTAS",
]

DETALLES_ADICIONALES = [
    "Operación completada exitosamente",
    "Cambios guardados en la base de datos",
    "Notificación enviada al usuario",
    "Registro actualizado correctamente",
    "Validaciones pasadas sin errores",
    "Datos sincronizados con sucursales",
    "Proceso ejecutado por el sistema automático",
    "Acción confirmada por supervisor",
    "Transacción completada y registrada",
    "Operación realizada desde panel de administración",
]


def generar_registros_auditoria(cantidad=200):
    """
    Genera registros de auditoría de ejemplo.
    
    Args:
        cantidad: Número de registros a generar (default: 200)
    """
    print(f"🔄 Generando {cantidad} registros de auditoría...")
    
    try:
        sesion = OBTENER_SESION()
        
        # Obtener usuarios existentes
        usuarios = sesion.query(MODELO_USUARIO).filter(
            MODELO_USUARIO.ACTIVO == True
        ).all()
        
        if not usuarios:
            print("⚠️ No hay usuarios en la base de datos. Crea usuarios primero.")
            return
        
        print(f"✅ Encontrados {len(usuarios)} usuarios activos")
        
        registros_creados = 0
        fecha_base = datetime.now()
        
        # Distribución de tipos de acción (con pesos)
        tipos_accion = ["LOGIN", "LOGOUT", "CREAR", "EDITAR", "ELIMINAR", "VER", "ERROR"]
        pesos = [10, 5, 20, 25, 5, 30, 5]  # Más ediciones y vistas
        
        for i in range(cantidad):
            # Fecha aleatoria en los últimos 30 días
            dias_atras = random.randint(0, 30)
            horas_atras = random.randint(0, 23)
            minutos_atras = random.randint(0, 59)
            
            fecha = fecha_base - timedelta(
                days=dias_atras,
                hours=horas_atras,
                minutes=minutos_atras
            )
            
            # Usuario aleatorio
            usuario = random.choice(usuarios)
            
            # Tipo de acción aleatoria (con distribución)
            tipo_accion = random.choices(tipos_accion, weights=pesos)[0]
            
            # Entidad y detalles según el tipo de acción
            if tipo_accion in ["LOGIN", "LOGOUT"]:
                accion = tipo_accion
                entidad = None
                entidad_id = None
                detalle = random.choice(ACCIONES_EJEMPLO[tipo_accion])
                detalle += f" | IP: 192.168.1.{random.randint(1, 255)}"
            else:
                # Para CREAR, EDITAR, ELIMINAR, VER
                entidad = random.choice(ENTIDADES)
                entidad_id = random.randint(1, 100) if random.random() > 0.2 else None
                
                # Formato de acción: "TIPO ENTIDAD"
                accion = f"{tipo_accion} {entidad}"
                
                # Detalle específico de la acción
                detalle_base = random.choice(ACCIONES_EJEMPLO.get(tipo_accion, ["Operación realizada"]))
                detalle_adicional = random.choice(DETALLES_ADICIONALES)
                detalle = f"{detalle_base} | {detalle_adicional}"
            
            # Crear registro
            registro = MODELO_AUDITORIA(
                USUARIO_ID=usuario.ID,
                ACCION=accion,
                ENTIDAD=entidad,
                ENTIDAD_ID=entidad_id,
                DETALLE=detalle,
                FECHA=fecha
            )
            
            sesion.add(registro)
            registros_creados += 1
            
            # Commit cada 50 registros
            if registros_creados % 50 == 0:
                sesion.commit()
                print(f"  ✓ Creados {registros_creados}/{cantidad} registros...")
        
        # Commit final
        sesion.commit()
        print(f"\n✅ ¡Completado! Se crearon {registros_creados} registros de auditoría")
        
        # Estadísticas
        print("\n📊 Estadísticas de registros creados:")
        for tipo in tipos_accion:
            count = sesion.query(MODELO_AUDITORIA).filter(
                MODELO_AUDITORIA.ACCION.ilike(f"%{tipo}%")
            ).count()
            print(f"  • {tipo}: {count} registros")
        
    except Exception as e:
        print(f"❌ Error al generar registros: {str(e)}")
        import traceback
        traceback.print_exc()
        sesion.rollback()


def limpiar_auditoria():
    """Limpia TODOS los registros de auditoría (¡usar con cuidado!)"""
    print("⚠️ ¿Estás seguro de que quieres ELIMINAR todos los registros de auditoría?")
    confirmacion = input("Escribe 'CONFIRMAR' para continuar: ")
    
    if confirmacion != "CONFIRMAR":
        print("❌ Operación cancelada")
        return
    
    try:
        sesion = OBTENER_SESION()
        count = sesion.query(MODELO_AUDITORIA).count()
        sesion.query(MODELO_AUDITORIA).delete()
        sesion.commit()
        print(f"✅ Se eliminaron {count} registros de auditoría")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sesion.rollback()


def mostrar_estadisticas():
    """Muestra estadísticas de los registros de auditoría"""
    try:
        sesion = OBTENER_SESION()
        
        total = sesion.query(MODELO_AUDITORIA).count()
        print(f"\n📊 Estadísticas de Auditoría")
        print(f"{'='*50}")
        print(f"Total de registros: {total}")
        
        if total > 0:
            # Por acción
            print(f"\nPor tipo de acción:")
            for tipo in ["LOGIN", "LOGOUT", "CREAR", "EDITAR", "ELIMINAR", "VER", "ERROR"]:
                count = sesion.query(MODELO_AUDITORIA).filter(
                    MODELO_AUDITORIA.ACCION.ilike(f"%{tipo}%")
                ).count()
                porcentaje = (count / total * 100) if total > 0 else 0
                print(f"  • {tipo:12s}: {count:4d} ({porcentaje:5.1f}%)")
            
            # Por entidad
            print(f"\nPor entidad:")
            for entidad in ENTIDADES:
                count = sesion.query(MODELO_AUDITORIA).filter(
                    MODELO_AUDITORIA.ENTIDAD == entidad
                ).count()
                if count > 0:
                    porcentaje = (count / total * 100)
                    print(f"  • {entidad:12s}: {count:4d} ({porcentaje:5.1f}%)")
            
            # Últimos registros
            print(f"\n📝 Últimos 5 registros:")
            ultimos = sesion.query(MODELO_AUDITORIA).order_by(
                MODELO_AUDITORIA.FECHA.desc()
            ).limit(5).all()
            
            for reg in ultimos:
                usuario_nombre = reg.USUARIO.NOMBRE_COMPLETO if reg.USUARIO else "Sistema"
                print(f"  [{reg.FECHA.strftime('%d/%m/%Y %H:%M')}] {usuario_nombre}: {reg.ACCION}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generador de datos de auditoría")
    parser.add_argument(
        "--generar",
        type=int,
        metavar="N",
        help="Generar N registros de ejemplo"
    )
    parser.add_argument(
        "--limpiar",
        action="store_true",
        help="Limpiar TODOS los registros (¡CUIDADO!)"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Mostrar estadísticas de auditoría"
    )
    
    args = parser.parse_args()
    
    if args.generar:
        generar_registros_auditoria(args.generar)
    elif args.limpiar:
        limpiar_auditoria()
    elif args.stats:
        mostrar_estadisticas()
    else:
        # Por defecto: generar 200 registros
        print("Uso:")
        print("  python generar_datos_auditoria.py --generar 200")
        print("  python generar_datos_auditoria.py --stats")
        print("  python generar_datos_auditoria.py --limpiar")
        print("\nGenerando 200 registros por defecto...")
        generar_registros_auditoria(200)
