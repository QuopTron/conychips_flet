"""
Tabla de pedidos con filtros y búsqueda
Usa componentes globales reutilizables
"""
import flet as ft
from typing import Callable, Optional
from datetime import datetime
from features.finanzas.presentation.bloc import PedidoResumen
from core.ui.colores import PRIMARIO, EXITO, PELIGRO, ADVERTENCIA, FONDO_TARJETA
from core.ui.componentes_globales import (
    DateRangePicker, BotonBuscar, BotonLimpiar, 
    CampoBusqueda, FiltroDropdown, TablaResponsive
)


class TablaPedidos(ft.Container):
    """Tabla de pedidos con filtros"""
    
    def __init__(self, on_ver_detalle: Optional[Callable[[int], None]] = None):
        super().__init__()
        
        self.on_ver_detalle = on_ver_detalle
        self.pedidos_actuales = []
        self._page = None  # Guardar referencia a la página
        
        self.expand = True
        self.padding = 0
        
        # Usar componentes globales
        self.campo_busqueda = CampoBusqueda(
            hint="Buscar por código...",
            on_submit=self._buscar
        )
        
        self.selector_fechas = DateRangePicker(
            on_change=self._on_fecha_change
        )
        
        self.btn_buscar = BotonBuscar(on_click=self._buscar)
        self.btn_limpiar = BotonLimpiar(on_click=self._limpiar_filtros)
        
        # Filtros
        self.filtro_estado = FiltroDropdown(
            label="Estado",
            opciones=[
                ("TODOS", "Todos"),
                ("COMPLETADO", "Completados"),
                ("PENDIENTE", "Pendientes"),
                ("CANCELADO", "Cancelados")
            ],
            on_change=self._filtrar_estado
        )
        
        self.filtro_voucher = FiltroDropdown(
            label="Voucher",
            opciones=[
                ("TODOS", "Todos"),
                ("APROBADO", "Aprobados"),
                ("RECHAZADO", "Rechazados"),
                ("PENDIENTE", "Pendientes")
            ],
            on_change=self._filtrar_voucher
        )
        
        # Tabla optimizada con mejor espaciado
        self.tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Código", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Cliente", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Fecha", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Estado", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Monto", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Voucher", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Ofertas", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acciones", size=12, weight=ft.FontWeight.BOLD))
            ],
            rows=[],
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=8,
            vertical_lines=ft.BorderSide(0.5, ft.Colors.GREY_200),
            horizontal_lines=ft.BorderSide(0.5, ft.Colors.GREY_200),
            heading_row_color=ft.Colors.BLUE_50,
            show_checkbox_column=False,
            column_spacing=8,
            heading_row_height=40,
            data_row_min_height=36,
            data_row_max_height=36
        )
        
        # Layout ultra responsive - altura 100%
        self.content = ft.Column(
            controls=[
                # Barra de filtros compacta
                ft.Container(
                    content=ft.ResponsiveRow([
                        # Búsqueda
                        ft.Container(self.campo_busqueda, col={"xs": 12, "sm": 6, "md": 3}),
                        # Fechas
                        ft.Container(self.selector_fechas, col={"xs": 12, "sm": 6, "md": 3}),
                        # Filtros
                        ft.Container(self.filtro_estado, col={"xs": 6, "sm": 4, "md": 2}),
                        ft.Container(self.filtro_voucher, col={"xs": 6, "sm": 4, "md": 2}),
                        # Botones
                        ft.Container(
                            ft.Row([self.btn_buscar, self.btn_limpiar], spacing=5),
                            col={"xs": 12, "sm": 4, "md": 2}
                        ),
                    ], spacing=6, run_spacing=6),
                    bgcolor=ft.Colors.BLUE_50,
                    border_radius=4,
                    padding=6,
                    border=ft.border.all(1, ft.Colors.BLUE_200)
                ),
                # Tabla 100% altura restante con scroll horizontal y vertical
                ft.Container(
                    content=ft.Row(
                        [self.tabla],
                        scroll=ft.ScrollMode.ADAPTIVE,
                        expand=True,
                    ),
                    expand=True,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=4,
                    padding=0,
                    border=ft.border.all(1, ft.Colors.BLUE_200)
                )
            ],
            spacing=4,
            expand=True
        )
    
    def _get_color_estado(self, estado: str) -> str:
        """Obtener color según estado"""
        colores = {
            "COMPLETADO": EXITO,
            "PENDIENTE": ADVERTENCIA,
            "CANCELADO": PELIGRO
        }
        return colores.get(estado, ft.Colors.ON_SURFACE)
    
    def _get_color_voucher(self, voucher_estado: Optional[str]) -> str:
        """Obtener color según estado de voucher"""
        if not voucher_estado:
            return ft.Colors.ON_SURFACE_VARIANT
        
        colores = {
            "APROBADO": EXITO,
            "RECHAZADO": PELIGRO,
            "PENDIENTE": ADVERTENCIA
        }
        return colores.get(voucher_estado, ft.Colors.ON_SURFACE_VARIANT)
    
    def _crear_fila_pedido(self, pedido: PedidoResumen) -> ft.DataRow:
        """Crear fila de tabla para un pedido"""
        # Formatear fecha
        fecha_str = pedido.fecha.strftime("%d/%m/%Y %H:%M")
        
        # Formatear monto en Bs
        monto_bs = pedido.monto_total / 100
        
        # Estado del voucher
        voucher_texto = pedido.voucher_estado if pedido.tiene_voucher else "Sin voucher"
        
        # Ofertas
        ofertas_icono = ft.Icon(ft.icons.Icons.LOYALTY,
            color=PRIMARIO,
            size=20
        ) if pedido.tiene_oferta else ft.Text("-", color=ft.Colors.ON_SURFACE_VARIANT)
        
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(pedido.codigo, weight=ft.FontWeight.W_500)),
                ft.DataCell(ft.Text(pedido.cliente[:25])),  # Truncar nombre largo
                ft.DataCell(ft.Text(fecha_str, size=13)),
                ft.DataCell(
                    ft.Container(
                        content=ft.Text(
                            pedido.estado,
                            color=ft.Colors.WHITE,
                            size=12,
                            weight=ft.FontWeight.BOLD
                        ),
                        bgcolor=self._get_color_estado(pedido.estado),
                        padding=ft.padding.symmetric(horizontal=10, vertical=5),
                        border_radius=12
                    )
                ),
                ft.DataCell(ft.Text(f"Bs {monto_bs:.2f}", weight=ft.FontWeight.W_500)),
                ft.DataCell(
                    ft.Text(
                        voucher_texto,
                        color=self._get_color_voucher(pedido.voucher_estado),
                        weight=ft.FontWeight.W_500
                    )
                ),
                ft.DataCell(ofertas_icono),
                ft.DataCell(
                    ft.IconButton(
                        icon=ft.icons.Icons.REMOVE_RED_EYE,
                        icon_color=PRIMARIO,
                        icon_size=18,
                        tooltip="Ver detalle",
                        on_click=lambda e, p=pedido: self._abrir_modal_detalle(e, p)
                    )
                )
            ]
        )
    
    def actualizar_pedidos(self, pedidos: list[PedidoResumen]):
        """Actualizar tabla con lista de pedidos"""
        self.pedidos_actuales = pedidos
        
        self.tabla.rows.clear()
        for pedido in pedidos:
            self.tabla.rows.append(self._crear_fila_pedido(pedido))
        
        # NO llamar update() - el padre se encargará
    
    def _buscar(self, e):
        """Evento de búsqueda"""
        # Este evento será manejado por la página principal
        pass
    
    def _filtrar_estado(self, e):
        """Evento de filtro por estado"""
        pass
    
    def _filtrar_voucher(self, e):
        """Evento de filtro por voucher"""
        pass
    
    def _abrir_modal_detalle(self, e, pedido: PedidoResumen):
        """Abrir modal con detalles del pedido - overlay ultraligero"""
        def cerrar_modal(ev):
            modal.open = False
            e.page.update()
        
        # Formatear datos
        fecha_str = pedido.fecha.strftime("%d/%m/%Y %H:%M")
        monto_bs = pedido.monto_total / 100
        voucher_texto = pedido.voucher_estado if pedido.tiene_voucher else "Sin voucher"
        
        # Crear contenido del modal ultraligero
        contenido = ft.Column([
            # Código y fecha
            ft.Row([
                ft.Column([
                    ft.Text("Código", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                    ft.Text(pedido.codigo, size=16, weight=ft.FontWeight.BOLD)
                ], spacing=2),
                ft.Column([
                    ft.Text("Fecha", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                    ft.Text(fecha_str, size=14)
                ], spacing=2)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            ft.Divider(height=1),
            
            # Cliente
            ft.Column([
                ft.Text("Cliente", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                ft.Text(pedido.cliente, size=14, weight=ft.FontWeight.W_500)
            ], spacing=2),
            
            # Estado y Monto
            ft.Row([
                ft.Column([
                    ft.Text("Estado", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                    ft.Container(
                        content=ft.Text(
                            pedido.estado,
                            color=ft.Colors.WHITE,
                            size=12,
                            weight=ft.FontWeight.BOLD
                        ),
                        bgcolor=self._get_color_estado(pedido.estado),
                        padding=ft.padding.symmetric(horizontal=10, vertical=5),
                        border_radius=12
                    )
                ], spacing=2),
                ft.Column([
                    ft.Text("Monto Total", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                    ft.Text(f"Bs {monto_bs:.2f}", size=16, weight=ft.FontWeight.BOLD, color=PRIMARIO)
                ], spacing=2)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            ft.Divider(height=1),
            
            # Voucher y Ofertas
            ft.Row([
                ft.Column([
                    ft.Text("Voucher", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                    ft.Text(
                        voucher_texto,
                        size=14,
                        color=self._get_color_voucher(pedido.voucher_estado),
                        weight=ft.FontWeight.W_500
                    )
                ], spacing=2),
                ft.Column([
                    ft.Text("Ofertas", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                    ft.Icon(ft.icons.Icons.LOYALTY, color=PRIMARIO, size=20) if pedido.tiene_oferta else ft.Text("Sin ofertas", size=14)
                ], spacing=2)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ], spacing=12, tight=True)
        
        # Crear AlertDialog ultraligero
        modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Detalle del Pedido", size=18, weight=ft.FontWeight.BOLD),
            content=contenido,
            actions=[
                ft.TextButton("Cerrar", on_click=cerrar_modal)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            content_padding=20,
            shape=ft.RoundedRectangleBorder(radius=12)
        )
        
        # Agregar a overlay y abrir
        e.page.overlay.append(modal)
        modal.open = True
        e.page.update()
    
    def _limpiar_filtros(self, e):
        """Limpiar todos los filtros"""
        self.campo_busqueda.value = ""
        self.selector_fechas.limpiar()
        self.filtro_estado.value = "TODOS"
        self.filtro_voucher.value = "TODOS"
        # Triggear búsqueda con filtros limpios
        self._buscar(e)
    
    def _on_fecha_change(self, fecha_inicio, fecha_fin):
        """Callback cuando cambia el rango de fechas"""
        # Aquí puedes triggerar búsqueda automática si lo deseas
        pass
