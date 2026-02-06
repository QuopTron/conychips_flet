"""
Componentes UI Globales Reutilizables
Todos los componentes siguen la sintaxis correcta de Flet 0.80.3
"""
import flet as ft
from typing import Optional, Callable, List
from datetime import datetime
from core.Constantes import COLORES


class DateRangePicker(ft.Container):
    """Selector de rango de fechas reutilizable"""
    
    def __init__(
        self,
        on_change: Optional[Callable] = None,
        width: int = 200,
        label: str = "Rango de Fechas"
    ):
        super().__init__()
        self.on_change = on_change
        self.fecha_inicio = None
        self.fecha_fin = None
        
        # Botón principal
        self.btn = ft.Button(
            content=ft.Row([
                ft.Icon(ft.icons.Icons.DATE_RANGE, size=18),
                ft.Text(label, size=14)
            ], spacing=8, tight=True),
            on_click=self._abrir_selector,
            width=width,
            height=45,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE
            )
        )
        
        # Texto del rango
        self.texto_rango = ft.Text(
            "Sin filtro",
            size=12,
            color=ft.Colors.GREY_600,
            italic=True
        )
        
        self.content = ft.Column([
            self.btn,
            self.texto_rango
        ], spacing=5, tight=True)
    
    def _abrir_selector(self, e):
        """Abrir selector de fecha inicio"""
        dialog_fin_ref = [None]  # Referencia mutable
        
        def seleccionar_inicio(ev):
            self.fecha_inicio = ev.control.value
            if self.fecha_inicio:
                # Cerrar primer dialog
                dialog_inicio.open = False
                e.page.update()
                
                # Abrir selector de fecha fin
                dialog_fin = ft.DatePicker(
                    first_date=self.fecha_inicio,
                    on_change=seleccionar_fin
                )
                dialog_fin_ref[0] = dialog_fin
                e.page.overlay.append(dialog_fin)
                dialog_fin.open = True
                e.page.update()
        
        def seleccionar_fin(ev):
            self.fecha_fin = ev.control.value
            if self.fecha_fin:
                # Actualizar texto
                self.texto_rango.value = f"{self.fecha_inicio.strftime('%Y-%m-%d')} - {self.fecha_fin.strftime('%Y-%m-%d')}"
                
                # Cerrar dialog
                if dialog_fin_ref[0]:
                    dialog_fin_ref[0].open = False
                    e.page.update()
                
                # Callback
                if self.on_change:
                    self.on_change(self.fecha_inicio, self.fecha_fin)
        
        # Abrir selector de fecha inicio
        dialog_inicio = ft.DatePicker(
            on_change=seleccionar_inicio
        )
        e.page.overlay.append(dialog_inicio)
        dialog_inicio.open = True
        e.page.update()
    
    def limpiar(self):
        """Limpiar selección"""
        self.fecha_inicio = None
        self.fecha_fin = None
        self.texto_rango.value = "Sin filtro"
    
    def obtener_valores(self):
        """Obtener valores seleccionados"""
        return (self.fecha_inicio, self.fecha_fin)


class BotonBuscar(ft.IconButton):
    """Botón de búsqueda estandarizado"""
    
    def __init__(self, on_click: Optional[Callable] = None, tooltip: str = "Buscar"):
        super().__init__()
        self.icon = ft.icons.Icons.SEARCH
        self.tooltip = tooltip
        self.on_click = on_click
        self.icon_size = 24
        self.style = ft.ButtonStyle(
            bgcolor=ft.Colors.BLUE_700,
            color=ft.Colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=8)
        )
        self.width = 48
        self.height = 48


class BotonLimpiar(ft.IconButton):
    """Botón de limpiar estandarizado"""
    
    def __init__(self, on_click: Optional[Callable] = None, tooltip: str = "Limpiar filtros"):
        super().__init__()
        self.icon = ft.icons.Icons.CLEAR_ALL
        self.tooltip = tooltip
        self.on_click = on_click
        self.icon_size = 24
        self.icon_color = ft.Colors.RED_400
        self.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8)
        )
        self.width = 48
        self.height = 48


class CampoBusqueda(ft.TextField):
    """Campo de búsqueda estandarizado"""
    
    def __init__(
        self,
        hint: str = "Buscar...",
        width: int = 250,
        on_submit: Optional[Callable] = None
    ):
        super().__init__()
        self.hint_text = hint
        self.prefix_icon = ft.icons.Icons.SEARCH
        self.width = width
        self.height = 45
        self.on_submit = on_submit
        self.border_radius = 8
        self.text_size = 14


class FiltroDropdown(ft.Dropdown):
    """Dropdown de filtro estandarizado"""
    
    def __init__(
        self,
        label: str,
        opciones: List[tuple],  # [(value, text), ...]
        on_change: Optional[Callable] = None,
        width: int = 180
    ):
        super().__init__()
        self.label = label
        self.hint_text = "Todos"
        self.width = width
        self.height = 45
        self.on_change = on_change
        self.border_radius = 8
        
        # Agregar opciones
        self.options = [
            ft.dropdown.Option(key=valor, text=texto)
            for valor, texto in opciones
        ]


class ContenedorFiltros(ft.Container):
    """Contenedor estandarizado para filtros"""
    
    def __init__(self, controles: List[ft.Control]):
        super().__init__()
        self.content = ft.Column([
            ft.Row(
                controls=controles,
                spacing=15,
                alignment=ft.MainAxisAlignment.START,
                wrap=True
            )
        ], spacing=10)
        self.bgcolor = ft.Colors.GREY_50
        self.border_radius = 8
        self.padding = 15
        self.border = ft.Border.all(1, ft.Colors.GREY_300)


class TablaResponsive(ft.Container):
    """Contenedor responsive para tablas - scroll bidireccional perfecto"""
    
    def __init__(self, tabla: ft.DataTable):
        super().__init__()
        self.tabla = tabla
        
        # Scroll bidireccional optimizado
        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[tabla],
                    scroll=ft.ScrollMode.ADAPTIVE
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=0
        )
        
        self.expand = True
        self.border = ft.Border.all(1, ft.Colors.GREY_300)
        self.border_radius = 8
        self.bgcolor = ft.Colors.WHITE
        self.padding = 8


class TarjetaEstadistica(ft.Container):
    """Tarjeta de estadística reutilizable"""
    
    def __init__(
        self,
        titulo: str,
        valor: str,
        icono: str,
        color: str = None
    ):
        super().__init__()
        
        color_final = color or COLORES.PRIMARIO
        
        self.content = ft.Column([
            ft.Row([
                ft.Icon(icono, size=32, color=color_final),
                ft.Column([
                    ft.Text(titulo, size=12, color=ft.Colors.GREY_600),
                    ft.Text(valor, size=20, weight=ft.FontWeight.BOLD, color=color_final)
                ], spacing=2, tight=True)
            ], spacing=10, alignment=ft.MainAxisAlignment.START)
        ], spacing=5)
        
        self.bgcolor = ft.Colors.WHITE
        self.border = ft.Border.all(2, color_final)
        self.border_radius = 12
        self.padding = 15
        self.shadow = ft.BoxShadow(
            spread_radius=0,
            blur_radius=8,
            color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
            offset=ft.Offset(0, 2)
        )


class IndicadorCarga(ft.Container):
    """Indicador de carga estandarizado"""
    
    def __init__(self, mensaje: str = "Cargando..."):
        super().__init__()
        self.content = ft.Column(
            controls=[
                ft.ProgressRing(),
                ft.Text(mensaje, size=16, color=ft.Colors.GREY_600)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        )
        self.alignment = ft.alignment.center
        self.expand = True
