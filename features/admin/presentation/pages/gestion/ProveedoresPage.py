import flet as ft
from typing import List, Dict, Any

from core.base_datos.ConfiguracionBD import MODELO_PROVEEDOR
from features.admin.presentation.widgets.PaginaCRUDBase import PaginaCRUDBase
from features.admin.presentation.widgets.ComponentesGlobales import FormularioCRUD

class ProveedoresPage(PaginaCRUDBase):
    
    def __init__(self, pagina: ft.Page, usuario, on_volver_inicio=None):
        super().__init__(
            PAGINA=pagina,
            USUARIO=usuario,
            titulo="Gestión de Proveedores",
            icono=ft.icons.Icons.BUSINESS
        )
    
    def _OBTENER_MODELO(self):
        return MODELO_PROVEEDOR
    
    def _OBTENER_CAMPOS_TABLA(self) -> List[str]:
        return ["NOMBRE", "CONTACTO", "TELEFONO", "EMAIL"]
    
    def _OBTENER_COLUMNAS_TABLA(self) -> List[str]:
        return ["Nombre", "Contacto", "Teléfono", "Email"]
    
    def _CREAR_FORMULARIO(self, item: Any = None) -> List[ft.Control]:
        return [
            FormularioCRUD.CREAR_CAMPO(
                "Nombre",
                item.NOMBRE if item else "",
                icono=ft.icons.Icons.BUSINESS
            ),
            FormularioCRUD.CREAR_CAMPO(
                "Contacto",
                item.CONTACTO if item else "",
                icono=ft.icons.Icons.PERSON
            ),
            FormularioCRUD.CREAR_CAMPO(
                "Teléfono",
                item.TELEFONO if item else "",
                icono=ft.icons.Icons.PHONE
            ),
            FormularioCRUD.CREAR_CAMPO(
                "Email",
                item.EMAIL if item else "",
                icono=ft.icons.Icons.EMAIL
            )
        ]
    
    def _EXTRAER_DATOS_FORMULARIO(self, campos: List[ft.Control]) -> Dict:
        return {
            "NOMBRE": campos[0].value,
            "CONTACTO": campos[1].value,
            "TELEFONO": campos[2].value,
            "EMAIL": campos[3].value
        }
