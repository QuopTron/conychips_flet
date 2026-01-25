class ROLES:
    INVITADO = "INVITADO"
    COCINERO = "COCINERO"
    CLIENTE = "CLIENTE"
    ATENCION = "ATENCION"
    MOTORIZADO = "MOTORIZADO"
    ADMIN = "ADMIN"
    LIMPIEZA = "LIMPIEZA"
    SUPERADMIN = "SUPERADMIN"


def OBTENER_PERMISOS_ROL(NOMBRE_ROL: str) -> list:
    if NOMBRE_ROL == ROLES.SUPERADMIN:
        return ["*"]

    try:
        from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_ROL
        import json

        with OBTENER_SESION() as sesion:
            rol = sesion.query(MODELO_ROL).filter_by(NOMBRE=NOMBRE_ROL).first()
            if rol and rol.PERMISOS:
                return json.loads(rol.PERMISOS)
            return []
    except Exception:
        return []


PERMISOS_POR_ROL = {
    ROLES.SUPERADMIN: ["*"],
}
