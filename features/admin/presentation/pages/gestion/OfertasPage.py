import flet as ft
from typing import List, Dict, Any
from datetime import datetime

from core.base_datos.ConfiguracionBD import MODELO_OFERTA, MODELO_PRODUCTO, OBTENER_SESION
from features.admin.presentation.widgets.PaginaCRUDBase import PaginaCRUDBase
from features.admin.presentation.widgets.ComponentesGlobales import FormularioCRUD

class OfertasPage(PaginaCRUDBase):
    
    def __init__(self, pagina: ft.Page, usuario, on_volver_inicio=None):
        super().__init__(
            PAGINA=pagina,
            USUARIO=usuario,
            titulo="Gestión de Ofertas",
            icono=ft.icons.Icons.LOCAL_OFFER
        )
        self._productos = []
        self._cargar_productos()
    
    def _cargar_productos(self):
        sesion = OBTENER_SESION()
        self._productos = sesion.query(MODELO_PRODUCTO).all()
        sesion.close()
    
    def _OBTENER_MODELO(self):
        return MODELO_OFERTA
    
    def _OBTENER_CAMPOS_TABLA(self) -> List[str]:
        return ["DESCUENTO_PORCENTAJE", "FECHA_INICIO", "FECHA_FIN", "ACTIVA"]
    
    def _OBTENER_COLUMNAS_TABLA(self) -> List[str]:
        return ["Descuento %", "Inicio", "Fin", "Activa"]
    
    def _CREAR_FORMULARIO(self, item: Any = None) -> List[ft.Control]:
        opciones_productos = [(p.NOMBRE, p.ID) for p in self._productos]
        
        return [
            FormularioCRUD.CREAR_DROPDOWN(
                "Producto",
                opciones_productos,
                item.PRODUCTO_ID if item else None,
                icono=ft.icons.Icons.SHOPPING_CART
            ),
            FormularioCRUD.CREAR_CAMPO(
                "Descuento %",
                str(item.DESCUENTO_PORCENTAJE) if item else "0",
                tipo="number"
            ),
            FormularioCRUD.CREAR_CAMPO(
                "Fecha Inicio (YYYY-MM-DD)",
                str(item.FECHA_INICIO) if item else datetime.now().strftime("%Y-%m-%d")
            ),
            FormularioCRUD.CREAR_CAMPO(
                "Fecha Fin (YYYY-MM-DD)",
                str(item.FECHA_FIN) if item else ""
            ),
            FormularioCRUD.CREAR_SWITCH(
                "Oferta Activa",
                item.ACTIVA if item else True
            )
        ]
    
    def _EXTRAER_DATOS_FORMULARIO(self, campos: List[ft.Control]) -> Dict:
        return {
            "PRODUCTO_ID": int(campos[0].value),
            "DESCUENTO_PORCENTAJE": float(campos[1].value or 0),
            "FECHA_INICIO": campos[2].value,
            "FECHA_FIN": campos[3].value,
            "ACTIVA": campos[4].value
        }
