import flet as ft
from typing import List, Dict, Any

from core.base_datos.ConfiguracionBD import MODELO_SUCURSAL
from features.admin.presentation.widgets.PaginaCRUDBase import PaginaCRUDBase
from features.admin.presentation.widgets.ComponentesGlobales import FormularioCRUD
from features.admin.presentation.bloc.SucursalesBloc import (
    SUCURSALES_BLOC,
    CargarSucursales,
    SucursalesCargadas,
    SucursalError
)

class SucursalesPage(PaginaCRUDBase):
    
    def __init__(self, pagina: ft.Page, usuario, on_volver_inicio=None):
        SUCURSALES_BLOC.AGREGAR_LISTENER(self._ON_ESTADO_CAMBIO_BLOC)
        
        super().__init__(
            PAGINA=pagina,
            USUARIO=usuario,
            titulo="Gestión de Sucursales",
            icono=ft.icons.Icons.STORE
        )
        
        SUCURSALES_BLOC.AGREGAR_EVENTO(CargarSucursales())
    
    def _ON_ESTADO_CAMBIO_BLOC(self, estado):
        if isinstance(estado, SucursalesCargadas):
            self._ACTUALIZAR_LISTA(estado.sucursales)
        elif isinstance(estado, SucursalError):
            from features.admin.presentation.widgets.ComponentesGlobales import Notificador
            Notificador.ERROR(self._PAGINA, estado.mensaje)
    
    def _OBTENER_MODELO(self):
        return MODELO_SUCURSAL
    
    def _OBTENER_CAMPOS_TABLA(self) -> List[str]:
        return ["NOMBRE", "DIRECCION", "TELEFONO"]
    
    def _OBTENER_COLUMNAS_TABLA(self) -> List[str]:
        return ["Nombre", "Dirección", "Teléfono"]
    
    def _CREAR_FORMULARIO(self, item: Any = None) -> List[ft.Control]:
        return [
            FormularioCRUD.CREAR_CAMPO(
                "Nombre",
                item.NOMBRE if item else "",
                icono=ft.icons.Icons.STORE
            ),
            FormularioCRUD.CREAR_CAMPO(
                "Dirección",
                item.DIRECCION if item else "",
                icono=ft.icons.Icons.LOCATION_ON
            ),
            FormularioCRUD.CREAR_CAMPO(
                "Teléfono",
                item.TELEFONO if item else "",
                icono=ft.icons.Icons.PHONE
            )
        ]
    
    def _EXTRAER_DATOS_FORMULARIO(self, campos: List[ft.Control]) -> Dict:
        return {
            "NOMBRE": campos[0].value,
            "DIRECCION": campos[1].value,
            "TELEFONO": campos[2].value
        }
    
    def __del__(self):
        try:
            SUCURSALES_BLOC.REMOVER_LISTENER(self._ON_ESTADO_CAMBIO_BLOC)
        except:
            pass
