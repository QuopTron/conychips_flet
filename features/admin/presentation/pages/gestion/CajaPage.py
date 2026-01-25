"""
Página de gestión de movimientos de caja.
Arquitectura: Clean Architecture + Hexagonal
"""
import flet as ft
from datetime import datetime
from core.base_datos.ConfiguracionBD import MODELO_CAJA
from core.Constantes import ROLES, COLORES
from core.decoradores.DecoradorVistas import REQUIERE_ROL
from features.admin.presentation.widgets.PaginaCRUDBase import PaginaCRUDBase
from features.admin.presentation.widgets.ComponentesGlobales import FormularioCRUD


@REQUIERE_ROL(ROLES.ADMINISTRADOR)
class CajaPage(PaginaCRUDBase):
    """Gestión de movimientos de caja y arqueos."""
    
    def __init__(self, PAGINA: ft.Page, USUARIO):
        super().__init__(PAGINA, USUARIO, "Caja y Movimientos")
    
    def _OBTENER_MODELO(self):
        return MODELO_CAJA
    
    def _OBTENER_CAMPOS_TABLA(self):
        return ["TIPO_MOVIMIENTO", "MONTO", "DESCRIPCION", "FECHA", "USUARIO"]
    
    def _OBTENER_COLUMNAS_TABLA(self):
        return ["Tipo", "Monto", "Descripción", "Fecha", "Responsable"]
    
    def _CREAR_FORMULARIO(self, item=None):
        """Crea formulario de registro de movimiento."""
        tipos_movimiento = [
            {"label": "Ingreso", "value": "INGRESO"},
            {"label": "Egreso", "value": "EGRESO"},
            {"label": "Apertura de Caja", "value": "APERTURA"},
            {"label": "Cierre de Caja", "value": "CIERRE"},
            {"label": "Retiro", "value": "RETIRO"},
        ]
        
        return [
            FormularioCRUD.CREAR_DROPDOWN(
                "Tipo de Movimiento",
                tipos_movimiento,
                item.TIPO_MOVIMIENTO if item else "INGRESO"
            ),
            FormularioCRUD.CREAR_CAMPO(
                "Monto",
                str(item.MONTO) if item else "0.00",
                hint="Monto en soles"
            ),
            FormularioCRUD.CREAR_CAMPO(
                "Descripción",
                item.DESCRIPCION if item else "",
                multiline=True,
                max_lines=3
            ),
            ft.Text(
                f"Responsable: {self._USUARIO.NOMBRE_COMPLETO}",
                size=12,
                color=COLORES.TEXTO_SECUNDARIO
            ),
        ]
    
    def _EXTRAER_DATOS_FORMULARIO(self, campos):
        """Extrae datos con información del usuario."""
        return {
            "TIPO_MOVIMIENTO": campos[0].value,
            "MONTO": float(campos[1].value),
            "DESCRIPCION": campos[2].value.strip(),
            "FECHA": datetime.now(),
            "USUARIO": self._USUARIO.USUARIO,
        }
    
    def _FORMATEAR_VALOR_CELDA(self, item, campo):
        """Formatea valores con colores según tipo."""
        if campo == "MONTO":
            monto_formateado = f"S/. {item.MONTO:.2f}"
            if item.TIPO_MOVIMIENTO in ["INGRESO", "APERTURA"]:
                return f"+ {monto_formateado}"
            elif item.TIPO_MOVIMIENTO in ["EGRESO", "RETIRO", "CIERRE"]:
                return f"- {monto_formateado}"
            return monto_formateado
        elif campo == "TIPO_MOVIMIENTO":
            return item.TIPO_MOVIMIENTO.replace("_", " ").title()
        elif campo == "FECHA":
            return item.FECHA.strftime("%d/%m/%Y %H:%M")
        return super()._FORMATEAR_VALOR_CELDA(item, campo)
