
from typing import Dict, Any

from ..RepositorioAdmin import RepositorioAdmin

class ActualizarRolUsuario:

    def __init__(self, repositorio: RepositorioAdmin):
        self._repositorio = repositorio

    def EJECUTAR(self, usuario_id: int, nombre_rol: str) -> Dict[str, Any]:
        try:
            if not usuario_id or usuario_id <= 0:
                return {
                    "exito": False,
                    "mensaje": "ID de usuario inválido"
                }

            if not nombre_rol or not nombre_rol.strip():
                return {
                    "exito": False,
                    "mensaje": "Nombre de rol inválido"
                }

            resultado = self._repositorio.ACTUALIZAR_ROL_USUARIO(
                usuario_id, 
                nombre_rol.strip()
            )

            if resultado:
                return {
                    "exito": True,
                    "mensaje": "Rol actualizado correctamente"
                }
            else:
                return {
                    "exito": False,
                    "mensaje": "No se pudo actualizar el rol"
                }

        except Exception as error:
            print(f"Error en ActualizarRolUsuario: {error}")
            return {
                "exito": False,
                "mensaje": f"Error: {str(error)}"
            }
