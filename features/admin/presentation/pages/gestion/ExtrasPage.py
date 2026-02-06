import flet as ft
from typing import List, Dict, Any

from core.base_datos.ConfiguracionBD import MODELO_EXTRA
from features.admin.presentation.widgets.PaginaCRUDBase import PaginaCRUDBase
from features.admin.presentation.widgets.ComponentesGlobales import FormularioCRUD
from core.Constantes import ROLES
from core.decoradores.DecoradorVistas import REQUIERE_ROL

@REQUIERE_ROL(ROLES.ADMIN)
class ExtrasPage(PaginaCRUDBase):
    
    def __init__(self, PAGINA: ft.Page, USUARIO):
        super().__init__(
            PAGINA=PAGINA,
            USUARIO=USUARIO,
            titulo="Gestión de Extras",
            icono=ft.icons.Icons.ADD_CIRCLE
        )
    
    def _OBTENER_MODELO(self):
        return MODELO_EXTRA
    
    def _OBTENER_CAMPOS_TABLA(self) -> List[str]:
        return ["NOMBRE", "DESCRIPCION", "PRECIO_ADICIONAL"]
    
    def _OBTENER_COLUMNAS_TABLA(self) -> List[str]:
        return ["Nombre", "Descripción", "Precio Adicional"]
    
    def _CREAR_FORMULARIO(self, item: Any = None) -> List[ft.Control]:
        return [
            FormularioCRUD.CREAR_CAMPO(
                "Nombre",
                item.NOMBRE if item else "",
                icono=ft.icons.Icons.ADD_CIRCLE
            ),
            FormularioCRUD.CREAR_CAMPO(
                "Descripción",
                item.DESCRIPCION if item else "",
                multiline=True,
                max_lines=3
            ),
            FormularioCRUD.CREAR_CAMPO(
                "Precio Adicional",
                str(item.PRECIO_ADICIONAL) if item else "0",
                tipo="number"
            )
        ]
    
    def _EXTRAER_DATOS_FORMULARIO(self, campos: List[ft.Control]) -> Dict:
        return {
            "NOMBRE": campos[0].value,
            "DESCRIPCION": campos[1].value,
            "PRECIO_ADICIONAL": float(campos[2].value or 0)
        }
