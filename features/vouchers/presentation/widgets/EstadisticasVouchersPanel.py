
import flet as ft
from core.Constantes import COLORES, TAMANOS, ICONOS
from .utils_vouchers import format_bs

class EstadisticasVouchersPanel(ft.Container):
    
    def __init__(self, estadisticas: dict = None):
        self._estadisticas = estadisticas or {}
        cards = self._crear_contenido()
        super().__init__(
            content=cards,
            padding=TAMANOS.PADDING_MD
        )
    
    def _crear_contenido(self):
        return ft.Row([
            self._crear_card_stat(
                "Pendientes",
                str(self._estadisticas.get("pendientes", 0)),
                ICONOS.RELOJ,
                COLORES.ADVERTENCIA
            ),
            self._crear_card_stat(
                "Aprobados",
                str(self._estadisticas.get("aprobados", 0)),
                ICONOS.CONFIRMAR,
                COLORES.EXITO
            ),
            self._crear_card_stat(
                "Rechazados",
                str(self._estadisticas.get("rechazados", 0)),
                ICONOS.CANCELAR,
                COLORES.PELIGRO
            ),
            self._crear_card_stat(
                "Monto Aprobado",
                format_bs(int(self._estadisticas.get('monto_total_aprobado', 0))),
                ICONOS.CAJA,
                COLORES.INFO
            ),
        ], spacing=12, wrap=True)
    
    def _crear_card_stat(self, titulo: str, valor: str, icono: str, color: str) -> ft.Container:
        return ft.Container(
            content=ft.Column([
                ft.Icon(icono, size=32, color=color),
                ft.Text(
                    valor,
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=COLORES.TEXTO
                ),
                ft.Text(
                    titulo,
                    size=13,
                    color=COLORES.TEXTO_SECUNDARIO
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
            padding=TAMANOS.PADDING_MD,
            bgcolor=COLORES.FONDO_BLANCO,
            border=ft.Border.all(1, COLORES.BORDE),
            border_radius=TAMANOS.RADIO_MD,
            width=180,
        )
    
    def ACTUALIZAR_ESTADISTICAS(self, nuevas_stats: dict):
        self._estadisticas = nuevas_stats
        self.content = self._crear_contenido()
        try:
            if hasattr(self, 'page') and self.page:
                self.update()
        except Exception:
            pass
