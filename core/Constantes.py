"""Constantes globales del sistema"""

# SEGURIDAD
LONGITUD_SAL = 32
LONGITUD_CLAVE = 32
ITERACIONES_PBKDF2 = 100000
ALGORITMO_JWT = "HS256"
EXPIRACION_ACCESS_TOKEN = 900  # 15 minutos
EXPIRACION_REFRESH_TOKEN = 604800  # 7 días

# ROLES DEL SISTEMA
class ROLES:
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERADOR = "moderador"
    USUARIO = "usuario"
    INVITADO = "invitado"

# PERMISOS
PERMISOS_POR_ROL = {
    ROLES.SUPER_ADMIN: ["*"],  # Todos los permisos
    ROLES.ADMIN: [
        "usuarios.crear", "usuarios.editar", "usuarios.eliminar",
        "roles.asignar", "contenido.moderar"
    ],
    ROLES.MODERADOR: [
        "contenido.moderar", "usuarios.ver"
    ],
    ROLES.USUARIO: [
        "perfil.editar", "contenido.crear"
    ],
    ROLES.INVITADO: [
        "contenido.ver"
    ]
}

# WEBSOCKET
WS_INTENTOS_RECONEXION = 5
WS_TIMEOUT = 30

# BASE DE DATOS
BD_NOMBRE = "app_segura.db"
BD_POOL_SIZE = 5