import flet as ft
from core.base_datos.ConfiguracionBD import MODELO_USUARIO
from core.Constantes import COLORES, ROLES
from core.decoradores.DecoradorVistas import REQUIERE_ROL
from features.admin.presentation.widgets.PaginaCRUDBase import PaginaCRUDBase
from features.admin.presentation.widgets.ComponentesGlobales import FormularioCRUD
from features.admin.presentation.bloc.UsuariosBloc import (
    UsuariosBloc,
    UsuariosEvento,
    UsuariosEstado,
    UsuariosCargados,
    UsuarioError
)

@REQUIERE_ROL(ROLES.ADMIN)
class UsuariosPage(PaginaCRUDBase):
    
    def __init__(self, PAGINA: ft.Page, USUARIO):
        self._BLOC = UsuariosBloc()
        super().__init__(PAGINA, USUARIO, "Usuarios")
        self._SUSCRIBIR_BLOC()
    
    def _SUSCRIBIR_BLOC(self):
        def _listener(state):
            if hasattr(state, 'usuarios') and state.usuarios is not None:
                self._ITEMS = state.usuarios
                self._ACTUALIZAR_LISTA()
            
            if hasattr(state, 'error') and state.error:
                self._MOSTRAR_ERROR(state.error)
            
            if state.mensaje_exito:
                self._MOSTRAR_EXITO(state.mensaje_exito)
                self._CARGAR_DATOS_INICIAL()
        
        self._BLOC.AGREGAR_LISTENER(_listener)
    
    def _OBTENER_MODELO(self):
        return MODELO_USUARIO
    
    def _OBTENER_CAMPOS_TABLA(self):
        return ["USUARIO", "NOMBRE_COMPLETO", "ROL", "ACTIVO"]
    
    def _OBTENER_COLUMNAS_TABLA(self):
        return ["Usuario", "Nombre Completo", "Rol", "Estado"]
    
    def _CREAR_FORMULARIO(self, item=None):
        roles_opciones = [
            {"label": "SuperAdmin", "value": "SUPERADMIN"},
            {"label": "Administrador", "value": "ADMINISTRADOR"},
            {"label": "Supervisor", "value": "SUPERVISOR"},
            {"label": "Empleado", "value": "EMPLEADO"},
        ]
        
        return [
            FormularioCRUD.CREAR_CAMPO(
                "Usuario",
                item.USUARIO if item else "",
                read_only=item is not None
            ),
            FormularioCRUD.CREAR_CAMPO(
                "Nombre Completo",
                item.NOMBRE_COMPLETO if item else ""
            ),
            FormularioCRUD.CREAR_CAMPO(
                "Contraseña",
                "",
                password=True,
                hint="Dejar vacío para mantener la actual" if item else "Mínimo 8 caracteres"
            ) if not item else None,
            FormularioCRUD.CREAR_DROPDOWN(
                "Rol",
                roles_opciones,
                item.ROL if item else "EMPLEADO"
            ),
            FormularioCRUD.CREAR_SWITCH(
                "Activo",
                item.ACTIVO if item else True
            ),
        ]
    
    def _EXTRAER_DATOS_FORMULARIO(self, campos):
        datos = {
            "USUARIO": campos[0].value.strip().upper(),
            "NOMBRE_COMPLETO": campos[1].value.strip(),
            "ROL": campos[3].value if len(campos) > 3 else campos[2].value,
            "ACTIVO": campos[4].value if len(campos) > 4 else campos[3].value,
        }
        
        if campos[2] and hasattr(campos[2], 'password') and campos[2].value:
            datos["CONTRASENA"] = campos[2].value
        
        return datos
    
    def _FORMATEAR_VALOR_CELDA(self, item, campo):
        if campo == "ACTIVO":
            return "✓ Activo" if item.ACTIVO else "✗ Inactivo"
        elif campo == "ROL":
            return item.ROL.replace("_", " ").title()
        return super()._FORMATEAR_VALOR_CELDA(item, campo)
