import flet as ft
from typing import List, Dict, Any

from core.base_datos.ConfiguracionBD import MODELO_PRODUCTO
from core.Constantes import ICONOS
from features.admin.presentation.widgets.PaginaCRUDBase import PaginaCRUDBase
from features.admin.presentation.widgets.ComponentesGlobales import FormularioCRUD

class ProductosPage(PaginaCRUDBase):
    
    def __init__(self, pagina: ft.Page, usuario, on_volver_inicio=None):
        super().__init__(
            PAGINA=pagina,
            USUARIO=usuario,
            titulo="Gestión de Productos",
            icono=ICONOS.PRODUCTOS
        )
    
    def _OBTENER_MODELO(self):
        return MODELO_PRODUCTO
    
    def _OBTENER_CAMPOS_TABLA(self) -> List[str]:
        return ["NOMBRE", "DESCRIPCION", "PRECIO", "STOCK"]
    
    def _OBTENER_COLUMNAS_TABLA(self) -> List[str]:
        return ["Nombre", "Descripción", "Precio", "Stock"]
    
    def _CREAR_FORMULARIO(self, item: Any = None) -> List[ft.Control]:
        return [
            FormularioCRUD.CREAR_CAMPO(
                "Nombre",
                item.NOMBRE if item else "",
                icono=ICONOS.PRODUCTOS
            ),
            FormularioCRUD.CREAR_CAMPO(
                "Descripción",
                item.DESCRIPCION if item else "",
                multiline=True,
                max_lines=3
            ),
            FormularioCRUD.CREAR_CAMPO(
                "Precio",
                str(item.PRECIO) if item else "0",
                tipo="number"
            ),
            FormularioCRUD.CREAR_CAMPO(
                "Stock",
                str(item.STOCK) if item else "0",
                tipo="number"
            )
        ]
    
    def _EXTRAER_DATOS_FORMULARIO(self, campos: List[ft.Control]) -> Dict:
        return {
            "NOMBRE": campos[0].value,
            "DESCRIPCION": campos[1].value,
            "PRECIO": float(campos[2].value or 0),
            "STOCK": int(campos[3].value or 0)
        }
