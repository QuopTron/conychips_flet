"""
Página de gestión de roles y permisos.
Arquitectura: Clean Architecture + Hexagonal
"""
import flet as ft
from core.base_datos.ConfiguracionBD import MODELO_ROL
from core.Constantes import ROLES
from core.decoradores.DecoradorVistas import REQUIERE_ROL
from features.admin.presentation.widgets.PaginaCRUDBase import PaginaCRUDBase
from features.admin.presentation.widgets.ComponentesGlobales import FormularioCRUD
from features.admin.presentation.bloc.RolesBloc import RolesBloc, RolesEvent, RolesState


@REQUIERE_ROL(ROLES.SUPERADMIN)
class RolesPage(PaginaCRUDBase):
    """Gestión de roles y permisos del sistema."""
    
    def __init__(self, PAGINA: ft.Page, USUARIO):
        self._BLOC = RolesBloc()
        super().__init__(PAGINA, USUARIO, "Roles y Permisos")
        self._SUSCRIBIR_BLOC()
    
    def _SUSCRIBIR_BLOC(self):
        """Suscribe al BLoC para actualizaciones reactivas."""
        def _listener(state: RolesState):
            if state.roles is not None:
                self._ITEMS = state.roles
                self._ACTUALIZAR_LISTA()
            
            if state.error:
                self._MOSTRAR_ERROR(state.error)
            
            if state.mensaje_exito:
                self._MOSTRAR_EXITO(state.mensaje_exito)
                self._CARGAR_DATOS_INICIAL()
        
        self._BLOC.stream.listen(_listener)
    
    def _OBTENER_MODELO(self):
        return MODELO_ROL
    
    def _OBTENER_CAMPOS_TABLA(self):
        return ["NOMBRE", "DESCRIPCION", "PERMISOS"]
    
    def _OBTENER_COLUMNAS_TABLA(self):
        return ["Nombre", "Descripción", "Permisos"]
    
    def _CREAR_FORMULARIO(self, item=None):
        """Crea formulario con selección múltiple de permisos."""
        permisos_disponibles = [
            "CREAR_USUARIOS", "EDITAR_USUARIOS", "ELIMINAR_USUARIOS",
            "VER_REPORTES", "GESTIONAR_PRODUCTOS", "GESTIONAR_PEDIDOS",
            "GESTIONAR_CAJA", "VER_AUDITORIA", "GESTIONAR_SUCURSALES"
        ]
        
        return [
            FormularioCRUD.CREAR_CAMPO(
                "Nombre del Rol",
                item.NOMBRE if item else ""
            ),
            FormularioCRUD.CREAR_CAMPO(
                "Descripción",
                item.DESCRIPCION if item else "",
                multiline=True,
                max_lines=3
            ),
            ft.Column(
                controls=[
                    ft.Text("Permisos:", weight=ft.FontWeight.BOLD),
                    *[
                        ft.Checkbox(
                            label=permiso.replace("_", " ").title(),
                            value=permiso in (item.PERMISOS.split(",") if item and item.PERMISOS else []),
                            data=permiso
                        )
                        for permiso in permisos_disponibles
                    ]
                ],
                spacing=5
            )
        ]
    
    def _EXTRAER_DATOS_FORMULARIO(self, campos):
        """Extrae datos incluyendo permisos seleccionados."""
        # Extraer permisos seleccionados del grupo de checkboxes
        permisos_seleccionados = []
        if len(campos) > 2 and isinstance(campos[2], ft.Column):
            for control in campos[2].controls[1:]:  # Skip el Text de título
                if isinstance(control, ft.Checkbox) and control.value:
                    permisos_seleccionados.append(control.data)
        
        return {
            "NOMBRE": campos[0].value.strip().upper(),
            "DESCRIPCION": campos[1].value.strip(),
            "PERMISOS": ",".join(permisos_seleccionados)
        }
    
    def _FORMATEAR_VALOR_CELDA(self, item, campo):
        """Formatea permisos para mostrar en tabla."""
        if campo == "PERMISOS":
            permisos = item.PERMISOS.split(",") if item.PERMISOS else []
            return f"{len(permisos)} permisos asignados"
        return super()._FORMATEAR_VALOR_CELDA(item, campo)
