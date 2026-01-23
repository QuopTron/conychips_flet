import shutil
import os
from sqlalchemy import text
from core.base_datos.ConfiguracionBD import RUTA_BD, OBTENER_SESION


def main():
    if os.path.exists(RUTA_BD):
        respaldo = RUTA_BD + ".before_delete"
        shutil.copy2(RUTA_BD, respaldo)
        print(f"Respaldo creado: {respaldo}")
    else:
        print(f"No existe la BD en {RUTA_BD}")
        return

    sesion = OBTENER_SESION()
    try:
        sesion.execute(text("DELETE FROM SESIONES"))
        sesion.execute(text("DELETE FROM USUARIO_ROLES"))
        sesion.execute(text("DELETE FROM USUARIOS"))
        sesion.commit()
        print("Todos los usuarios y sus sesiones/roles asociados han sido eliminados.")
    except Exception as e:
        print(f"Error al eliminar usuarios: {e}")


if __name__ == "__main__":
    main()
