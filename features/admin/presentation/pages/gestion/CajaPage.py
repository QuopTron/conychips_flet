import flet as ft
from datetime import datetime
from core.base_datos.ConfiguracionBD import MODELO_CAJA_MOVIMIENTO
from core.Constantes import ROLES, COLORES
from core.decoradores.DecoradorVistas import REQUIERE_ROL
from features.admin.presentation.widgets.PaginaCRUDBase import PaginaCRUDBase
from features.admin.presentation.widgets.ComponentesGlobales import FormularioCRUD

@REQUIERE_ROL(ROLES.ADMIN)
class CajaPage(PaginaCRUDBase):
    
    def __init__(self, PAGINA: ft.Page, USUARIO):
        super().__init__(PAGINA, USUARIO, "Caja y Movimientos")
    
    def _OBTENER_MODELO(self):
        return MODELO_CAJA_MOVIMIENTO
    
    def _OBTENER_CAMPOS_TABLA(self):
        return ["TIPO", "MONTO", "DESCRIPCION", "FECHA", "USUARIO"]
    
    def _OBTENER_COLUMNAS_TABLA(self):
        return ["Tipo", "Monto", "Descripción", "Fecha", "Responsable"]
    
    def _CREAR_FORMULARIO(self, item=None):
        tipos_movimiento = [
            {"label": "Ingreso", "value": "ingreso"},
            {"label": "Egreso", "value": "egreso"},
            {"label": "Apertura de Caja", "value": "apertura"},
            {"label": "Cierre de Caja", "value": "cierre"},
            {"label": "Retiro", "value": "retiro"},
        ]
        
        return [
            FormularioCRUD.CREAR_DROPDOWN(
                "Tipo de Movimiento",
                tipos_movimiento,
                item.TIPO if item else "ingreso"
            ),
            FormularioCRUD.CREAR_CAMPO(
                "Monto",
                str((item.MONTO / 100) if item else "0.00"),
                hint="Monto en soles"
            ),
            FormularioCRUD.CREAR_CAMPO(
                "Descripción",
                item.DESCRIPCION if item else "",
                multiline=True,
                max_lines=3
            ),
            ft.Text(
                f"Responsable: {getattr(self._USUARIO, 'NOMBRE_USUARIO', str(getattr(self._USUARIO, 'ID', '')))}",
                size=12,
                color=COLORES.TEXTO_SECUNDARIO
            ),
        ]
    
    def _EXTRAER_DATOS_FORMULARIO(self, campos):
        monto_val = 0
        try:
            monto_val = int(float(campos[1].value) * 100)
        except Exception:
            monto_val = 0

        # Preferir la sucursal seleccionada en el navbar; si es None, usar SUCURSAL_ID del usuario
        sucursal_seleccionada = getattr(self._USUARIO, 'SUCURSAL_SELECCIONADA', None)
        if sucursal_seleccionada is None:
            sucursal_seleccionada = getattr(self._USUARIO, 'SUCURSAL_ID', None)

        return {
            "TIPO": campos[0].value,
            "MONTO": monto_val,
            "DESCRIPCION": campos[2].value.strip(),
            "FECHA": datetime.now(),
            "USUARIO_ID": getattr(self._USUARIO, 'ID', None),
            "SUCURSAL_ID": sucursal_seleccionada,
        }
    
    def _FORMATEAR_VALOR_CELDA(self, item, campo):
        if campo == "MONTO":
            monto = (item.MONTO or 0) / 100
            monto_formateado = f"S/. {monto:.2f}"
            tipo = getattr(item, 'TIPO', '')
            if tipo in ["ingreso", "apertura"]:
                return f"+ {monto_formateado}"
            if tipo in ["egreso", "retiro", "cierre"]:
                return f"- {monto_formateado}"
            return monto_formateado
        elif campo == "TIPO":
            return getattr(item, 'TIPO', '').replace("_", " ").title()
        elif campo == "FECHA":
            return item.FECHA.strftime("%d/%m/%Y %H:%M")
        return super()._FORMATEAR_VALOR_CELDA(item, campo)
