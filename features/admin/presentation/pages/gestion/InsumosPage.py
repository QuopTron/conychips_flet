import flet as ft
from typing import List, Dict, Any

from core.base_datos.ConfiguracionBD import MODELO_INSUMO
from core.Constantes import ICONOS
from features.admin.presentation.widgets.PaginaCRUDBase import PaginaCRUDBase
from features.admin.presentation.widgets.ComponentesGlobales import FormularioCRUD

class InsumosPage(PaginaCRUDBase):
    
    def __init__(self, pagina: ft.Page, usuario, on_volver_inicio=None):
        super().__init__(
            PAGINA=pagina,
            USUARIO=usuario,
            titulo="Gestión de Insumos",
            icono=ICONOS.INSUMOS
        )
    
    def _OBTENER_MODELO(self):
        return MODELO_INSUMO
    
    def _OBTENER_CAMPOS_TABLA(self) -> List[str]:
        return ["NOMBRE", "CANTIDAD", "UNIDAD", "STOCK_MINIMO"]
    
    def _OBTENER_COLUMNAS_TABLA(self) -> List[str]:
        return ["Nombre", "Cantidad", "Unidad", "Stock Mínimo"]
    
    def _CREAR_FORMULARIO(self, item: Any = None) -> List[ft.Control]:
        return [
            FormularioCRUD.CREAR_CAMPO(
                "Nombre",
                item.NOMBRE if item else "",
                icono=ICONOS.INSUMOS
            ),
            FormularioCRUD.CREAR_CAMPO(
                "Cantidad",
                str(item.CANTIDAD) if item else "0",
                tipo="number"
            ),
            FormularioCRUD.CREAR_CAMPO(
                "Unidad",
                item.UNIDAD if item else ""
            ),
            FormularioCRUD.CREAR_CAMPO(
                "Stock Mínimo",
                str(item.STOCK_MINIMO) if item else "0",
                tipo="number"
            )
        ]
    
    def _EXTRAER_DATOS_FORMULARIO(self, campos: List[ft.Control]) -> Dict:
        return {
            "NOMBRE": campos[0].value,
            "CANTIDAD": float(campos[1].value or 0),
            "UNIDAD": campos[2].value,
            "STOCK_MINIMO": float(campos[3].value or 0)
        }
