"""
Página de visualización y gestión de pedidos.
Vista compleja con filtros y estados.
Arquitectura: Clean Architecture + Hexagonal
"""
import flet as ft
from datetime import datetime
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_PEDIDO
from core.Constantes import COLORES, TAMANOS, ICONOS, ROLES
from core.decoradores.DecoradorVistas import REQUIERE_ROL
from features.admin.presentation.widgets.ComponentesGlobales import (
    HeaderAdmin, TablaGenerica, ContenedorPagina, Notificador, DialogoConfirmacion
)


@REQUIERE_ROL(ROLES.SUPERVISOR)
class PedidosPage(ft.Column):
    """Vista de gestión de pedidos con filtros y cambio de estado."""
    
    def __init__(self, PAGINA: ft.Page, USUARIO):
        super().__init__()
        self._PAGINA = PAGINA
        self._USUARIO = USUARIO
        self._FILTRO_ESTADO = "TODOS"
        
        self.expand = True
        self._CONSTRUIR_UI()
        self._CARGAR_PEDIDOS()
    
    def _CONSTRUIR_UI(self):
        """Construye la interfaz."""
        # Header
        header = HeaderAdmin(
            titulo="Gestión de Pedidos",
            icono=ICONOS.PEDIDOS,
            on_menu=self._IR_MENU,
            on_salir=self._SALIR
        )
        
        # Filtros
        filtros = ft.Row(
            controls=[
                ft.Dropdown(
                    label="Estado",
                    options=[
                        ft.dropdown.Option("TODOS", "Todos"),
                        ft.dropdown.Option("PENDIENTE", "Pendientes"),
                        ft.dropdown.Option("EN_PREPARACION", "En Preparación"),
                        ft.dropdown.Option("LISTO", "Listos"),
                        ft.dropdown.Option("EN_ENTREGA", "En Entrega"),
                        ft.dropdown.Option("COMPLETADO", "Completados"),
                        ft.dropdown.Option("CANCELADO", "Cancelados"),
                    ],
                    value=self._FILTRO_ESTADO,
                    on_change=self._CAMBIAR_FILTRO,
                    width=200
                ),
                ft.ElevatedButton(
                    "Actualizar",
                    icon=ICONOS.ACTUALIZAR,
                    on_click=lambda e: self._CARGAR_PEDIDOS()
                ),
            ],
            spacing=TAMANOS.ESPACIADO_MD
        )
        
        # Tabla de pedidos
        self._tabla = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
        
        # Contenedor principal
        contenido = ContenedorPagina(
            controles=[header, filtros, self._tabla]
        )
        
        self.controls = [contenido]
    
    def _CARGAR_PEDIDOS(self):
        """Carga pedidos desde BD."""
        try:
            sesion = OBTENER_SESION()
            query = sesion.query(MODELO_PEDIDO)
            
            if self._FILTRO_ESTADO != "TODOS":
                query = query.filter(MODELO_PEDIDO.ESTADO == self._FILTRO_ESTADO)
            
            pedidos = query.order_by(MODELO_PEDIDO.FECHA.desc()).limit(100).all()
            
            self._ACTUALIZAR_TABLA(pedidos)
            
        except Exception as e:
            Notificador.ERROR(self._PAGINA, f"Error al cargar pedidos: {str(e)}")
    
    def _ACTUALIZAR_TABLA(self, pedidos):
        """Actualiza tabla de pedidos."""
        self._tabla.controls.clear()
        
        if not pedidos:
            self._tabla.controls.append(
                ft.Text("No hay pedidos", size=16, color=COLORES.TEXTO_SECUNDARIO)
            )
        else:
            filas = []
            for pedido in pedidos:
                filas.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(f"#{pedido.ID}")),
                            ft.DataCell(ft.Text(pedido.CLIENTE or "Cliente")),
                            ft.DataCell(ft.Text(f"S/. {pedido.TOTAL:.2f}")),
                            ft.DataCell(ft.Container(
                                content=ft.Text(
                                    pedido.ESTADO.replace("_", " "),
                                    color=COLORES.TEXTO_BLANCO
                                ),
                                bgcolor=self._OBTENER_COLOR_ESTADO(pedido.ESTADO),
                                padding=5,
                                border_radius=5
                            )),
                            ft.DataCell(ft.Text(
                                pedido.FECHA.strftime("%d/%m/%Y %H:%M")
                            )),
                            ft.DataCell(ft.Row([
                                ft.IconButton(
                                    icon=ICONOS.VER,
                                    tooltip="Ver Detalles",
                                    on_click=lambda e, p=pedido: self._VER_DETALLES(p)
                                ),
                                ft.IconButton(
                                    icon=ICONOS.EDITAR,
                                    tooltip="Cambiar Estado",
                                    on_click=lambda e, p=pedido: self._CAMBIAR_ESTADO(p)
                                ),
                            ])),
                        ]
                    )
                )
            
            tabla = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Cliente", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Total", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Estado", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Fecha", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
                ],
                rows=filas,
                border=ft.border.all(1, COLORES.BORDE),
                heading_row_color=COLORES.FONDO_SECUNDARIO,
            )
            
            self._tabla.controls.append(
                ft.Container(
                    content=tabla,
                    border=ft.border.all(1, COLORES.BORDE),
                    border_radius=TAMANOS.RADIO_MD,
                    padding=TAMANOS.PADDING_MD
                )
            )
        
        self._PAGINA.update()
    
    def _OBTENER_COLOR_ESTADO(self, estado):
        """Retorna color según estado del pedido."""
        colores = {
            "PENDIENTE": COLORES.ADVERTENCIA,
            "EN_PREPARACION": COLORES.INFO,
            "LISTO": COLORES.PRIMARIO,
            "EN_ENTREGA": COLORES.SECUNDARIO,
            "COMPLETADO": COLORES.EXITO,
            "CANCELADO": COLORES.PELIGRO,
        }
        return colores.get(estado, COLORES.SECUNDARIO)
    
    def _VER_DETALLES(self, pedido):
        """Muestra detalles del pedido."""
        Notificador.INFO(self._PAGINA, f"Detalles del pedido #{pedido.ID}")
    
    def _CAMBIAR_ESTADO(self, pedido):
        """Cambia el estado del pedido."""
        Notificador.INFO(self._PAGINA, "Cambio de estado en desarrollo...")
    
    def _CAMBIAR_FILTRO(self, e):
        """Cambia filtro de estado."""
        self._FILTRO_ESTADO = e.control.value
        self._CARGAR_PEDIDOS()
    
    def _IR_MENU(self, e=None):
        """Retorna al menú principal."""
        from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
        self._PAGINA.controls.clear()
        self._PAGINA.add(PaginaAdmin(self._PAGINA, self._USUARIO))
        self._PAGINA.update()
    
    def _SALIR(self, e=None):
        """Cierra sesión."""
        from features.autenticacion.presentation.pages.PaginaLogin import PaginaLogin
        self._PAGINA.controls.clear()
        self._PAGINA.add(PaginaLogin(self._PAGINA))
        self._PAGINA.update()
