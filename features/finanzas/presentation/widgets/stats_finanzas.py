"""
Widget para estadísticas financieras centradas
Muestra ingresos, egresos y utilidad en Bs
"""
import flet as ft
from features.finanzas.presentation.bloc import EstadoFinanzasCargado, ResumenFinanciero
from core.ui.colores import PRIMARIO, EXITO, PELIGRO, ADVERTENCIA, FONDO_TARJETA


class StatsFinanzas(ft.Container):
    """Tarjetas de estadísticas financieras"""
    
    def __init__(self):
        super().__init__()
        
        self.padding = 0
        
        # Tarjetas de stats
        self.card_ingresos = self._crear_card_stat("", "Bs 0.00", EXITO, ft.icons.Icons.TRENDING_UP)
        self.card_egresos = self._crear_card_stat("", "Bs 0.00", PELIGRO, ft.icons.Icons.TRENDING_DOWN)
        self.card_utilidad = self._crear_card_stat("", "Bs 0.00", PRIMARIO, ft.icons.Icons.ACCOUNT_BALANCE_WALLET)
        
        # Layout centrado
        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        self.card_ingresos,
                        self.card_egresos,
                        self.card_utilidad
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                    wrap=True
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0
        )
    
    def _crear_card_stat(self, titulo: str, valor: str, color: str, icono: str) -> ft.Container:
        """Crear tarjeta de estadística"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(icono, color=color, size=20),
                            ft.Text(titulo, size=12, color=ft.Colors.ON_SURFACE_VARIANT, weight=ft.FontWeight.W_500)
                        ],
                        spacing=6
                    ),
                    ft.Text(valor, size=22, color=color, weight=ft.FontWeight.BOLD)
                ],
                spacing=4,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            width=220,
            height=75,
            padding=12,
            bgcolor=FONDO_TARJETA,
            border_radius=10,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT)
        )
    
    def actualizar_desde_estado(self, estado: EstadoFinanzasCargado):
        """Actualizar estadísticas desde estado del BLoC"""
        resumen = estado.resumen
        
        # Convertir centavos a Bs
        ingresos_bs = resumen.total_ingresos / 100
        egresos_bs = resumen.total_egresos / 100
        utilidad_bs = resumen.utilidad_neta / 100
        
        # Determinar color de utilidad
        color_utilidad = EXITO if utilidad_bs >= 0 else PELIGRO
        
        # Actualizar textos
        self.card_ingresos.content.controls[0].controls[1].value = "Ingresos Totales"
        self.card_ingresos.content.controls[1].value = f"Bs {ingresos_bs:,.2f}"
        
        self.card_egresos.content.controls[0].controls[1].value = "Egresos Totales"
        self.card_egresos.content.controls[1].value = f"Bs {egresos_bs:,.2f}"
        
        self.card_utilidad.content.controls[0].controls[1].value = "Utilidad Neta"
        self.card_utilidad.content.controls[1].value = f"Bs {utilidad_bs:,.2f}"
        self.card_utilidad.content.controls[1].color = color_utilidad
        
        # NO llamar update() - el padre se encargará de actualizar
