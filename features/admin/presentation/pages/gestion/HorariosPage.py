"""
Página de gestión de horarios del establecimiento.
Arquitectura: Clean Architecture + Hexagonal
"""
import flet as ft
from core.base_datos.ConfiguracionBD import MODELO_HORARIO
from core.Constantes import ROLES
from core.decoradores.DecoradorVistas import REQUIERE_ROL
from features.admin.presentation.widgets.PaginaCRUDBase import PaginaCRUDBase
from features.admin.presentation.widgets.ComponentesGlobales import FormularioCRUD


@REQUIERE_ROL(ROLES.ADMINISTRADOR)
class HorariosPage(PaginaCRUDBase):
    """Gestión de horarios de apertura y cierre."""
    
    def __init__(self, PAGINA: ft.Page, USUARIO):
        super().__init__(PAGINA, USUARIO, "Horarios")
    
    def _OBTENER_MODELO(self):
        return MODELO_HORARIO
    
    def _OBTENER_CAMPOS_TABLA(self):
        return ["DIA_SEMANA", "HORA_APERTURA", "HORA_CIERRE", "ACTIVO"]
    
    def _OBTENER_COLUMNAS_TABLA(self):
        return ["Día", "Apertura", "Cierre", "Estado"]
    
    def _CREAR_FORMULARIO(self, item=None):
        """Crea formulario con selector de día y horas."""
        dias_semana = [
            {"label": "Lunes", "value": "LUNES"},
            {"label": "Martes", "value": "MARTES"},
            {"label": "Miércoles", "value": "MIERCOLES"},
            {"label": "Jueves", "value": "JUEVES"},
            {"label": "Viernes", "value": "VIERNES"},
            {"label": "Sábado", "value": "SABADO"},
            {"label": "Domingo", "value": "DOMINGO"},
        ]
        
        return [
            FormularioCRUD.CREAR_DROPDOWN(
                "Día de la Semana",
                dias_semana,
                item.DIA_SEMANA if item else "LUNES"
            ),
            FormularioCRUD.CREAR_CAMPO(
                "Hora de Apertura",
                item.HORA_APERTURA if item else "08:00",
                hint="Formato: HH:MM"
            ),
            FormularioCRUD.CREAR_CAMPO(
                "Hora de Cierre",
                item.HORA_CIERRE if item else "22:00",
                hint="Formato: HH:MM"
            ),
            FormularioCRUD.CREAR_SWITCH(
                "Abierto este día",
                item.ACTIVO if item else True
            ),
        ]
    
    def _EXTRAER_DATOS_FORMULARIO(self, campos):
        """Extrae y valida datos de horarios."""
        return {
            "DIA_SEMANA": campos[0].value,
            "HORA_APERTURA": campos[1].value.strip(),
            "HORA_CIERRE": campos[2].value.strip(),
            "ACTIVO": campos[3].value,
        }
    
    def _FORMATEAR_VALOR_CELDA(self, item, campo):
        """Formatea valores para mejor visualización."""
        if campo == "DIA_SEMANA":
            return item.DIA_SEMANA.capitalize()
        elif campo == "ACTIVO":
            return "✓ Abierto" if item.ACTIVO else "✗ Cerrado"
        return super()._FORMATEAR_VALOR_CELDA(item, campo)
