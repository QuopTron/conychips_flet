LONGITUD_SAL = 32
LONGITUD_CLAVE = 32
ITERACIONES_PBKDF2 = 100000
ALGORITMO_JWT = "HS256"
EXPIRACION_ACCESS_TOKEN = 900  # 15 minutos
EXPIRACION_REFRESH_TOKEN = 604800  # 7 días

class ROLES:
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    ATENCION = "atencion"
    COCINERO = "cocinero"
    LIMPIEZA = "limpieza"
    CLIENTE = "cliente"

PERMISOS_POR_ROL = {
    ROLES.SUPER_ADMIN: ["*"],  # Todos los permisos
    ROLES.ADMIN: [
        "usuarios.crear", "usuarios.editar", "usuarios.eliminar", "usuarios.ver",
        "roles.asignar", "productos.crear", "productos.editar", "productos.eliminar", "productos.ver",
        "sucursales.crear", "sucursales.editar", "sucursales.ver",
        "extras.crear", "extras.editar", "extras.ver",
        "ofertas.crear", "ofertas.editar", "ofertas.ver",
        "horarios.asignar", "horarios.ver",
        "pedidos.ver", "pedidos.editar", "pedidos.confirmar",
        "reportes.ver", "stats.ver", "cajas.ver"
    ],
    ROLES.ATENCION: [
        "pedidos.ver", "pedidos.confirmar", "pedidos.actualizar_estado",
        "productos.ver", "sucursales.ver", "clientes.ver",
        "cajas.abrir", "cajas.cerrar", "cajas.ver"
    ],
    ROLES.COCINERO: [
        "pedidos.ver", "pedidos.marcar_listo", "pedidos.notificar_atencion",
        "productos.ver", "sucursales.ver"
    ],
    ROLES.LIMPIEZA: [
        "reportes.crear", "reportes.ver", "sucursales.ver",
        "asistencia.ver"
    ],
    ROLES.CLIENTE: [
        "productos.ver", "sucursales.ver", "pedidos.crear", "pedidos.ver",
        "perfil.editar", "perfil.ver"
    ]
}

WS_INTENTOS_RECONEXION = 5
WS_TIMEOUT = 30

BD_NOMBRE = "app_segura.db"
BD_POOL_SIZE = 5
