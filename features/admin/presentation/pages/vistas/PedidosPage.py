import flet as ft
from datetime import datetime
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_PEDIDO
from core.Constantes import COLORES, TAMANOS, ICONOS, ROLES
from core.decoradores.DecoradorVistas import REQUIERE_ROL
from features.admin.presentation.widgets.ComponentesGlobales import (
    HeaderAdmin, TablaGenerica, ContenedorPagina, Notificador, DialogoConfirmacion
)
from core.decoradores.DecoradorPermisosUI import requiere_rol_ui
from core.Constantes import ROLES
from core.ui.safe_actions import safe_update

@REQUIERE_ROL(ROLES.ADMIN)
class PedidosPage(ft.Column):
    
    def __init__(self, PAGINA: ft.Page, USUARIO):
        super().__init__()
        self._PAGINA = PAGINA
        self._USUARIO = USUARIO
        self._FILTRO_ESTADO = "TODOS"
        
        self.expand = True
        self._CONSTRUIR_UI()
        self._CARGAR_PEDIDOS()
    
    def _CONSTRUIR_UI(self):
        header = HeaderAdmin(
            titulo="Gestión de Pedidos",
            icono=ICONOS.PEDIDOS,
            on_menu=self._IR_MENU,
            on_salir=self._SALIR
        )
        
        filtros = ft.Container(
            content=ft.ResponsiveRow([
                ft.Container(
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
                    ),
                    col={"xs": 12, "sm": 6, "md": 3}
                ),
                ft.Container(
                    ft.Button(
                        "Actualizar",
                        icon=ft.icons.Icons.REFRESH,
                        on_click=lambda e: self._CARGAR_PEDIDOS()
                    ),
                    col={"xs": 12, "sm": 6, "md": 2}
                ),
            ], spacing=6, run_spacing=6),
            bgcolor=ft.Colors.BLUE_50,
            border_radius=4,
            padding=6,
            border=ft.border.all(1, ft.Colors.BLUE_200)
        )
        
        self._tabla = ft.Column(spacing=3, scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        
        contenido = ft.Container(
            content=ft.Column([header, filtros, self._tabla], spacing=4, expand=True),
            padding=0,
            expand=True
        )
        
        self.controls = [contenido]
    
    def _CARGAR_PEDIDOS(self):
        try:
            sesion = OBTENER_SESION()
            query = sesion.query(MODELO_PEDIDO)
            # Filtrar por estado si aplica
            if self._FILTRO_ESTADO != "TODOS":
                query = query.filter(MODELO_PEDIDO.ESTADO == self._FILTRO_ESTADO)

            # Filtrar por sucursal seleccionada en navbar (None = Todas)
            try:
                suc_sel = getattr(self._USUARIO, 'SUCURSAL_SELECCIONADA', None)
            except Exception:
                suc_sel = None

            if suc_sel is not None:
                query = query.filter(MODELO_PEDIDO.SUCURSAL_ID == suc_sel)
            
            fecha_attr = getattr(MODELO_PEDIDO, 'FECHA_CONFIRMACION', None) or getattr(MODELO_PEDIDO, 'FECHA_CREACION', None) or getattr(MODELO_PEDIDO, 'FECHA_PEDIDO', None)
            if fecha_attr is not None:
                pedidos = query.order_by(fecha_attr.desc()).limit(100).all()
            else:
                pedidos = query.limit(100).all()
            
            self._ACTUALIZAR_TABLA(pedidos)
            
        except Exception as e:
            Notificador.ERROR(self._PAGINA, f"Error al cargar pedidos: {str(e)}")
    
    def _ACTUALIZAR_TABLA(self, pedidos):
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
                            ft.DataCell(ft.Container(
                                content=ft.Text(
                                    pedido.ESTADO.replace("_", " "),
                                    color=COLORES.TEXTO_BLANCO
                                ),
                                bgcolor=self._OBTENER_COLOR_ESTADO(pedido.ESTADO),
                                padding=5,
                                border_radius=5
                            )),
                            ft.DataCell(ft.Text(f"S/. {getattr(pedido, 'MONTO_TOTAL', getattr(pedido, 'TOTAL', 0)):.2f}")),
                            ft.DataCell(ft.Text(
                                (getattr(pedido, 'FECHA_CONFIRMACION', None) or getattr(pedido, 'FECHA_CREACION', None) or getattr(pedido, 'FECHA_PEDIDO', None) or datetime.now()).strftime("%d/%m/%Y %H:%M")
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
                border=ft.Border.all(1, COLORES.BORDE),
                heading_row_color=COLORES.FONDO_SECUNDARIO,
            )
            
            self._tabla.controls.append(
                ft.Container(
                    content=tabla,
                    border=ft.Border.all(1, COLORES.BORDE),
                    border_radius=TAMANOS.RADIO_MD,
                    padding=TAMANOS.PADDING_MD
                )
            )
        
        safe_update(self._PAGINA)
    
    def _OBTENER_COLOR_ESTADO(self, estado):
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
        Notificador.INFO(self._PAGINA, f"Detalles del pedido #{pedido.ID}")
    
    @requiere_rol_ui(ROLES.SUPERADMIN, ROLES.ADMIN)
    def _CAMBIAR_ESTADO(self, pedido):
        Notificador.INFO(self._PAGINA, "Cambio de estado en desarrollo...")
    
    def _CAMBIAR_FILTRO(self, e):
        self._FILTRO_ESTADO = e.control.value
        self._CARGAR_PEDIDOS()
    
    def _IR_MENU(self, e=None):
        from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
        self._PAGINA.controls.clear()
        self._PAGINA.add(PaginaAdmin(self._PAGINA, self._USUARIO))
        safe_update(self._PAGINA)
    
    def _SALIR(self, e=None):
        from features.autenticacion.presentation.pages.PaginaLogin import PaginaLogin
        self._PAGINA.controls.clear()
        self._PAGINA.add(PaginaLogin(self._PAGINA))
        safe_update(self._PAGINA)
