"""
PedidosPage Refactorizada - Siguiendo patrón VouchersPage
Con tabs, overlays modernos y diseño optimizado
"""
import flet as ft
from typing import Optional, List
import threading
from datetime import datetime

from core.Constantes import COLORES, TAMANOS, ICONOS, ROLES
from core.decoradores.DecoradorVistas import REQUIERE_ROL
from core.ui.safe_actions import safe_update
from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION,
    MODELO_PEDIDO,
    MODELO_DETALLE_PEDIDO,
    MODELO_PRODUCTO,
    MODELO_USUARIO,
)

from features.admin.presentation.widgets import LayoutBase


@REQUIERE_ROL(ROLES.ADMIN)
class PedidosPage(LayoutBase):
    """Página de pedidos con diseño moderno estilo Vouchers"""
    
    def __init__(self, PAGINA: ft.Page, USUARIO):
        # Inicializar layout base
        super().__init__(
            pagina=PAGINA,
            usuario=USUARIO,
            titulo_vista="🛒 Gestión de Pedidos",
            mostrar_boton_volver=True,
            index_navegacion=2,  # Pedidos es el 3er item
            on_volver_dashboard=self._ir_dashboard,
            on_cerrar_sesion=self._cerrar_sesion
        )
        
        self._estado_actual: str = "PENDIENTE"
        self._tab_index = 0
        self._auto_refresh_activo = True
        self._cache_pedidos = {
            "PENDIENTE": [],
            "EN_PREPARACION": [],
            "LISTO": [],
            "COMPLETADO": [],
        }
        
        # Overlays
        self._bottom_sheet = None
        self._dialog_cambiar_estado = None
        
        # Construir UI
        self._CONSTRUIR_UI()
        
        # Carga inicial
        threading.Timer(0.2, self._CARGAR_INICIAL).start()
        self._INICIAR_AUTO_REFRESH()
    
    def _on_sucursales_change(self, sucursales_ids: Optional[List[int]]):
        """OVERRIDE: Callback cuando cambian las sucursales"""
        self._CARGAR_INICIAL()
    
    def _CONSTRUIR_UI(self):
        """Construye la interfaz con tabs estilo VouchersPage"""
        
        # Skeleton shimmer animado (3 tarjetas)
        def shimmer_card():
            return ft.Container(
                bgcolor=ft.Colors.GREY_100,
                border_radius=12,
                padding=ft.padding.all(16),
                margin=ft.margin.symmetric(vertical=8, horizontal=0),
                content=ft.Column([
                    ft.Row([
                        ft.Container(
                            width=56,
                            height=56,
                            bgcolor=ft.Colors.GREY_300,
                            border_radius=28,
                            animate_opacity=300
                        ),
                        ft.Column([
                            ft.Container(
                                width=140,
                                height=14,
                                bgcolor=ft.Colors.GREY_300,
                                border_radius=7,
                                animate_opacity=300
                            ),
                            ft.Container(
                                width=100,
                                height=12,
                                bgcolor=ft.Colors.GREY_200,
                                border_radius=6,
                                margin=ft.margin.only(top=6),
                                animate_opacity=300
                            ),
                        ], spacing=0),
                    ], spacing=12),
                    ft.Container(
                        width=200,
                        height=12,
                        bgcolor=ft.Colors.GREY_200,
                        border_radius=6,
                        margin=ft.margin.only(top=12),
                        animate_opacity=300
                    ),
                ], spacing=0),
                animate_opacity=300
            )
        
        self._indicador_carga = ft.Container(
            content=ft.Column(
                controls=[
                    shimmer_card(),
                    shimmer_card(),
                    shimmer_card(),
                    ft.Container(
                        content=ft.Text(
                            "Cargando pedidos...",
                            size=15,
                            color=ft.Colors.GREY_600,
                            weight=ft.FontWeight.W_500
                        ),
                        alignment=ft.Alignment(0, 0),
                        margin=ft.margin.only(top=20)
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0
            ),
            alignment=ft.Alignment(0, 0),
            expand=True,
            padding=ft.padding.symmetric(vertical=32, horizontal=16)
        )
        
        # DataTables para cada estado
        def _crear_tabla_pedidos():
            return ft.DataTable(
                columns=[
                    ft.DataColumn(label=ft.Text("Pedido", weight=ft.FontWeight.BOLD, size=13)),
                    ft.DataColumn(label=ft.Text("Cliente", weight=ft.FontWeight.BOLD, size=13)),
                    ft.DataColumn(label=ft.Text("Fecha", weight=ft.FontWeight.BOLD, size=13)),
                    ft.DataColumn(label=ft.Text("Monto", weight=ft.FontWeight.BOLD, size=13), numeric=True),
                    ft.DataColumn(label=ft.Text("Estado", weight=ft.FontWeight.BOLD, size=13)),
                    ft.DataColumn(label=ft.Text("Acciones", weight=ft.FontWeight.BOLD, size=13)),
                ],
                rows=[],
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=10,
                horizontal_lines=ft.border.BorderSide(1, ft.Colors.GREY_200),
                heading_row_color={ft.ControlState.DEFAULT: ft.Colors.BLUE_50},
                data_row_max_height=float("inf"),
                column_spacing=20,
            )
        
        self._tabla_pendiente = _crear_tabla_pedidos()
        self._tabla_preparacion = _crear_tabla_pedidos()
        self._tabla_listo = _crear_tabla_pedidos()
        self._tabla_completado = _crear_tabla_pedidos()
        
        # Contenedores scrollables para las tablas
        self._contenedor_pendiente = ft.Column(
            controls=[self._indicador_carga],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
            spacing=8
        )
        
        self._contenedor_preparacion = ft.Column(
            controls=[self._tabla_preparacion],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
            spacing=8
        )
        
        self._contenedor_listo = ft.Column(
            controls=[self._tabla_listo],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
            spacing=8
        )
        
        self._contenedor_completado = ft.Column(
            controls=[self._tabla_completado],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
            spacing=8
        )
        
        # Tabs con los diferentes estados
        def _on_tab_click(e, idx):
            self._tab_index = idx
            estados = ["PENDIENTE", "EN_PREPARACION", "LISTO", "COMPLETADO"]
            self._estado_actual = estados[idx]
            self._actualizar_tabs()
            # Cargar si cache está vacío
            if not self._cache_pedidos[self._estado_actual]:
                threading.Timer(0.1, self._CARGAR_PEDIDOS).start()

        def _tab(label, icon, idx):
            activo = self._tab_index == idx
            return ft.Container(
                content=ft.Column([
                    ft.Icon(
                        icon,
                        size=24,
                        color=ft.Colors.BLUE_700 if activo else ft.Colors.GREY_500
                    ),
                    ft.Text(
                        label,
                        size=13,
                        weight=ft.FontWeight.W_600 if activo else ft.FontWeight.W_500,
                        color=ft.Colors.BLUE_700 if activo else ft.Colors.GREY_500
                    ),
                    ft.Container(
                        height=3,
                        width=50,
                        bgcolor=ft.Colors.BLUE_700 if activo else ft.Colors.TRANSPARENT,
                        border_radius=2,
                        margin=ft.margin.only(top=4),
                    )
                ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.symmetric(vertical=10, horizontal=8),
                on_click=lambda e, i=idx: _on_tab_click(e, i),
                expand=True,
                ink=True,
                border_radius=8,
            )

        self._tab_bar = ft.Container(
            content=ft.Row([
                _tab("Pendientes", ft.icons.PENDING_ACTIONS, 0),
                _tab("Preparación", ft.icons.RESTAURANT_MENU, 1),
                _tab("Listos", ft.icons.CHECK_CIRCLE_OUTLINE, 2),
                _tab("Completados", ft.icons.DONE_ALL, 3),
            ], spacing=4, alignment=ft.MainAxisAlignment.SPACE_AROUND),
            bgcolor=ft.Colors.WHITE,
            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_300)),
            padding=ft.padding.symmetric(horizontal=8, vertical=0)
        )

        self._tab_views = [
            self._contenedor_pendiente,
            self._contenedor_preparacion,
            self._contenedor_listo,
            self._contenedor_completado,
        ]

        self._tab_view_container = ft.Container(
            content=self._tab_views[self._tab_index],
            expand=True,
            padding=ft.padding.all(12)
        )

        contenido = ft.Container(
            content=ft.Column([
                self._tab_bar,
                self._tab_view_container
            ], spacing=0, expand=True),
            expand=True,
            bgcolor=ft.Colors.GREY_50,
            padding=0
        )

        self.construir(contenido)

    def _actualizar_tabs(self):
        """Actualiza la visualización de tabs"""
        self._tab_bar.content.controls.clear()
        
        def _on_tab_click(e, idx):
            self._tab_index = idx
            estados = ["PENDIENTE", "EN_PREPARACION", "LISTO", "COMPLETADO"]
            self._estado_actual = estados[idx]
            self._actualizar_tabs()
            if not self._cache_pedidos[self._estado_actual]:
                threading.Timer(0.1, self._CARGAR_PEDIDOS).start()
        
        def _tab(label, icon, idx):
            activo = self._tab_index == idx
            return ft.Container(
                content=ft.Column([
                    ft.Icon(icon, size=24, color=ft.Colors.BLUE_700 if activo else ft.Colors.GREY_500),
                    ft.Text(label, size=13, weight=ft.FontWeight.W_600 if activo else ft.FontWeight.W_500, color=ft.Colors.BLUE_700 if activo else ft.Colors.GREY_500),
                    ft.Container(height=3, width=50, bgcolor=ft.Colors.BLUE_700 if activo else ft.Colors.TRANSPARENT, border_radius=2, margin=ft.margin.only(top=4)),
                ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.symmetric(vertical=10, horizontal=8),
                on_click=lambda e, i=idx: _on_tab_click(e, i),
                expand=True,
                ink=True,
                border_radius=8,
            )
        
        self._tab_bar.content.controls.extend([
            _tab("Pendientes", ft.icons.PENDING_ACTIONS, 0),
            _tab("Preparación", ft.icons.RESTAURANT_MENU, 1),
            _tab("Listos", ft.icons.CHECK_CIRCLE_OUTLINE, 2),
            _tab("Completados", ft.icons.DONE_ALL, 3),
        ])
        
        # Actualizar vista activa
        self._tab_view_container.content = self._tab_views[self._tab_index]
        safe_update(self._pagina)
    
    def _CARGAR_INICIAL(self):
        """Carga inicial de todos los estados"""
        def cargar_async():
            for estado in ["PENDIENTE", "EN_PREPARACION", "LISTO", "COMPLETADO"]:
                self._estado_actual = estado
                self._CARGAR_PEDIDOS()
            # Volver a pendientes
            self._estado_actual = "PENDIENTE"
            self._tab_index = 0
        
        threading.Timer(0.1, cargar_async).start()
    
    def _CARGAR_PEDIDOS(self):
        """Carga pedidos del estado actual"""
        try:
            with OBTENER_SESION() as sesion:
                query = sesion.query(MODELO_PEDIDO).filter(
                    MODELO_PEDIDO.ESTADO == self._estado_actual
                )
                
                # Filtrar por sucursal si está seleccionada
                sucursales = self.obtener_sucursales_seleccionadas()
                if sucursales:
                    query = query.filter(MODELO_PEDIDO.SUCURSAL_ID.in_(sucursales))
                
                # Ordenar por fecha
                fecha_attr = getattr(MODELO_PEDIDO, 'FECHA_CREACION', None) or \
                            getattr(MODELO_PEDIDO, 'FECHA_PEDIDO', None)
                if fecha_attr:
                    query = query.order_by(fecha_attr.desc())
                
                pedidos = query.limit(50).all()
                
                # Actualizar cache
                self._cache_pedidos[self._estado_actual] = pedidos
            
            # Actualizar UI (fuera del context manager)
            self._ACTUALIZAR_LISTA(self._cache_pedidos[self._estado_actual])
            
        except Exception as e:
            print(f"[ERROR] _CARGAR_PEDIDOS: {e}")
            import traceback
            traceback.print_exc()
            self._MOSTRAR_ERROR(f"Error al cargar pedidos: {str(e)}")
    
    def _ACTUALIZAR_LISTA(self, pedidos):
        """Actualiza la tabla de pedidos"""
        # Determinar tabla según estado actual
        tabla_map = {
            "PENDIENTE": self._tabla_pendiente,
            "EN_PREPARACION": self._tabla_preparacion,
            "LISTO": self._tabla_listo,
            "COMPLETADO": self._tabla_completado,
        }
        
        contenedor_map = {
            "PENDIENTE": self._contenedor_pendiente,
            "EN_PREPARACION": self._contenedor_preparacion,
            "LISTO": self._contenedor_listo,
            "COMPLETADO": self._contenedor_completado,
        }
        
        tabla = tabla_map.get(self._estado_actual)
        contenedor = contenedor_map.get(self._estado_actual)
        if not tabla or not contenedor:
            return
        
        tabla.rows.clear()
        
        # Actualizar contenedor para mostrar la tabla
        if self._estado_actual == "PENDIENTE":
            contenedor.controls.clear()
            contenedor.controls.append(tabla)
        
        if not pedidos:
            tabla.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.INBOX, size=40, color=ft.Colors.GREY_400),
                            ft.Text("No hay pedidos", weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                    )),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                ])
            )
        else:
            for pedido in pedidos:
                tabla.rows.append(self._CREAR_FILA_PEDIDO(pedido))
        
        safe_update(self._pagina)
    
    def _CREAR_FILA_PEDIDO(self, pedido) -> ft.DataRow:
        """Crea fila de DataTable para un pedido"""
        
        # Color de badge según estado
        badge_color_map = {
            "PENDIENTE": ft.Colors.ORANGE_600,
            "EN_PREPARACION": ft.Colors.BLUE_600,
            "LISTO": ft.Colors.GREEN_600,
            "COMPLETADO": ft.Colors.GREY_600,
        }
        badge_color = badge_color_map.get(pedido.ESTADO, ft.Colors.GREY_600)
        
        # Obtener fecha
        fecha = getattr(pedido, 'FECHA_CREACION', None) or \
                getattr(pedido, 'FECHA_PEDIDO', None) or datetime.now()
        fecha_str = fecha.strftime("%d/%m %H:%M")
        
        # Monto total
        monto = getattr(pedido, 'MONTO_TOTAL', getattr(pedido, 'TOTAL', 0))
        
        # Cliente
        cliente_id = getattr(pedido, 'CLIENTE_ID', None)
        cliente_nombre = "Cliente"
        if cliente_id:
            try:
                with OBTENER_SESION() as sesion:
                    usuario = sesion.query(MODELO_USUARIO).filter_by(ID=cliente_id).first()
                    if usuario:
                        cliente_nombre = getattr(usuario, 'NOMBRE', getattr(usuario, 'EMAIL', 'Cliente'))
            except:
                pass
        
        # Badge de estado
        badge_estado = ft.Container(
            content=ft.Text(
                pedido.ESTADO.replace("_", " "),
                size=11,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE,
            ),
            padding=ft.Padding(8, 4, 8, 4),
            border_radius=12,
            bgcolor=badge_color,
        )
        
        # Monto formateado
        monto_cell = ft.Container(
            content=ft.Text(
                f"S/ {monto:.2f}",
                size=13,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.GREEN_700,
            ),
            padding=ft.Padding(8, 4, 8, 4),
            border_radius=8,
            bgcolor=ft.Colors.GREEN_50,
        )
        
        # Botones de acción según estado
        acciones_btns = [
            ft.IconButton(
                icon=ft.Icons.VISIBILITY,
                tooltip="Ver detalles",
                icon_color=ft.Colors.BLUE_600,
                icon_size=20,
                on_click=lambda e, p=pedido: self._VER_DETALLES(p),
            ),
        ]
        
        if pedido.ESTADO == "PENDIENTE":
            acciones_btns.append(
                ft.IconButton(
                    icon=ft.Icons.PLAY_ARROW,
                    tooltip="Iniciar Preparación",
                    icon_color=ft.Colors.GREEN_600,
                    icon_size=20,
                    on_click=lambda e, p=pedido: self._CAMBIAR_ESTADO_PEDIDO(p, "EN_PREPARACION"),
                )
            )
        elif pedido.ESTADO == "EN_PREPARACION":
            acciones_btns.append(
                ft.IconButton(
                    icon=ft.Icons.CHECK_CIRCLE,
                    tooltip="Marcar Listo",
                    icon_color=ft.Colors.GREEN_600,
                    icon_size=20,
                    on_click=lambda e, p=pedido: self._CAMBIAR_ESTADO_PEDIDO(p, "LISTO"),
                )
            )
        elif pedido.ESTADO == "LISTO":
            acciones_btns.append(
                ft.IconButton(
                    icon=ft.Icons.DONE_ALL,
                    tooltip="Completar",
                    icon_color=ft.Colors.PURPLE_600,
                    icon_size=20,
                    on_click=lambda e, p=pedido: self._CAMBIAR_ESTADO_PEDIDO(p, "COMPLETADO"),
                )
            )
        
        acciones = ft.Row(acciones_btns, spacing=0)
        
        # Color de fila según estado
        row_color_map = {
            "PENDIENTE": {ft.ControlState.DEFAULT: ft.Colors.ORANGE_50},
            "EN_PREPARACION": {ft.ControlState.DEFAULT: ft.Colors.BLUE_50},
            "LISTO": {ft.ControlState.DEFAULT: ft.Colors.GREEN_50},
            "COMPLETADO": {ft.ControlState.DEFAULT: ft.Colors.GREY_100},
        }
        row_color = row_color_map.get(pedido.ESTADO)
        
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Row([
                    ft.Icon(ft.Icons.SHOPPING_BAG, size=18, color=badge_color),
                    ft.Text(f"#{pedido.ID}", weight=ft.FontWeight.BOLD, size=13),
                ], spacing=6)),
                ft.DataCell(ft.Text(cliente_nombre, size=13, color=ft.Colors.GREY_700)),
                ft.DataCell(ft.Row([
                    ft.Icon(ft.Icons.SCHEDULE, size=14, color=ft.Colors.GREY_500),
                    ft.Text(fecha_str, size=12, color=ft.Colors.GREY_600),
                ], spacing=4)),
                ft.DataCell(monto_cell),
                ft.DataCell(badge_estado),
                ft.DataCell(acciones),
            ],
            color=row_color
        )
    
    def _VER_DETALLES(self, pedido):
        """Muestra detalles del pedido en BottomSheet overlay"""
        
        # Obtener detalles del pedido
        try:
            with OBTENER_SESION() as sesion:
                detalles = sesion.query(MODELO_DETALLE_PEDIDO).filter_by(
                    PEDIDO_ID=pedido.ID
                ).all()
                
                items_list = []
                total = 0
                
                for detalle in detalles:
                    producto = sesion.query(MODELO_PRODUCTO).filter_by(
                        ID=detalle.PRODUCTO_ID
                    ).first()
                    
                    nombre_producto = producto.NOMBRE if producto else f"Producto #{detalle.PRODUCTO_ID}"
                    precio_unit = getattr(detalle, 'PRECIO_UNITARIO', 0)
                    cantidad = getattr(detalle, 'CANTIDAD', 1)
                    subtotal = precio_unit * cantidad
                    total += subtotal
                    
                    items_list.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Text(f"{cantidad}x", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700, width=40),
                                ft.Text(nombre_producto, size=14, color=ft.Colors.GREY_900, expand=True),
                                ft.Text(f"S/. {subtotal:.2f}", size=14, weight=ft.FontWeight.W_600, color=ft.Colors.GREEN_700),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            padding=ft.padding.symmetric(vertical=8, horizontal=12),
                            bgcolor=ft.Colors.GREY_50,
                            border_radius=8,
                            margin=ft.margin.only(bottom=8)
                        )
                    )
            
        except Exception as e:
            print(f"[ERROR] _VER_DETALLES: {e}")
            import traceback
            traceback.print_exc()
            items_list = [ft.Text("Error al cargar detalles", color=ft.Colors.RED_700)]
            total = getattr(pedido, 'MONTO_TOTAL', getattr(pedido, 'TOTAL', 0))
        
        # Crear BottomSheet
        self._bottom_sheet = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column([
                    # Header
                    ft.Row([
                        ft.Text(
                            f"Detalles Pedido #{pedido.ID}",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_900
                        ),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE_ROUNDED,
                            on_click=lambda e: self._CERRAR_BOTTOM_SHEET(),
                            icon_color=ft.Colors.GREY_700
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    
                    ft.Divider(height=1, color=ft.Colors.GREY_300),
                    
                    # Items
                    ft.Text("Productos", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800),
                    ft.Column(items_list, spacing=0, scroll=ft.ScrollMode.AUTO, height=300),
                    
                    ft.Divider(height=1, color=ft.Colors.GREY_300),
                    
                    # Total
                    ft.Row([
                        ft.Text("TOTAL:", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_900),
                        ft.Text(f"S/. {total:.2f}", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ], spacing=16, scroll=ft.ScrollMode.AUTO),
                padding=ft.padding.all(24),
                bgcolor=ft.Colors.WHITE,
                border_radius=ft.border_radius.only(top_left=20, top_right=20),
            ),
            open=True,
            on_dismiss=lambda e: self._CERRAR_BOTTOM_SHEET()
        )
        
        self._pagina.overlay.append(self._bottom_sheet)
        safe_update(self._pagina)
    
    def _CERRAR_BOTTOM_SHEET(self):
        """Cierra el BottomSheet"""
        if self._bottom_sheet:
            self._bottom_sheet.open = False
            safe_update(self._pagina)
            self._pagina.overlay.remove(self._bottom_sheet)
            self._bottom_sheet = None
    
    def _CAMBIAR_ESTADO_PEDIDO(self, pedido, nuevo_estado):
        """Cambia el estado del pedido con confirmación en Dialog overlay"""
        
        estados_texto = {
            "EN_PREPARACION": "Iniciar Preparación",
            "LISTO": "Marcar como Listo",
            "COMPLETADO": "Completar Pedido",
        }
        
        def confirmar(e):
            try:
                with OBTENER_SESION() as sesion:
                    pedido_db = sesion.query(MODELO_PEDIDO).filter_by(ID=pedido.ID).first()
                    if pedido_db:
                        pedido_db.ESTADO = nuevo_estado
                        sesion.commit()
                        
                        # Notificar realtime
                        try:
                            from core.realtime.broker_notify import notify
                            notify({
                                'type': 'pedido_actualizado',
                                'pedido_id': pedido.ID,
                                'nuevo_estado': nuevo_estado,
                                'sucursal_id': getattr(pedido, 'SUCURSAL_ID', None),
                            })
                        except:
                            pass
                        
                        # Recargar pedidos
                        self._CARGAR_INICIAL()
                        
                        self._MOSTRAR_EXITO(f"Pedido #{pedido.ID} actualizado")
            except Exception as ex:
                print(f"[ERROR] _CAMBIAR_ESTADO_PEDIDO: {ex}")
                import traceback
                traceback.print_exc()
                self._MOSTRAR_ERROR(f"Error: {str(ex)}")
            finally:
                self._CERRAR_DIALOG()
        
        self._dialog_cambiar_estado = ft.AlertDialog(
            modal=True,
            title=ft.Text(estados_texto.get(nuevo_estado, "Cambiar Estado")),
            content=ft.Text(
                f"¿Confirmar cambio de estado para Pedido #{pedido.ID}?",
                size=14
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self._CERRAR_DIALOG()),
                ft.ElevatedButton(
                    "Confirmar",
                    icon=ft.icons.CHECK,
                    style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE),
                    on_click=confirmar
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self._pagina.overlay.append(self._dialog_cambiar_estado)
        self._dialog_cambiar_estado.open = True
        safe_update(self._pagina)
    
    def _CERRAR_DIALOG(self):
        """Cierra el dialog"""
        if self._dialog_cambiar_estado:
            self._dialog_cambiar_estado.open = False
            safe_update(self._pagina)
            self._pagina.overlay.remove(self._dialog_cambiar_estado)
            self._dialog_cambiar_estado = None
    
    def _INICIAR_AUTO_REFRESH(self):
        """Inicia el refresco automático"""
        def refresh():
            if self._auto_refresh_activo:
                self._CARGAR_PEDIDOS()
                threading.Timer(30, refresh).start()
        
        threading.Timer(30, refresh).start()
    
    def _MOSTRAR_EXITO(self, mensaje):
        """Muestra snackbar de éxito"""
        snack = ft.SnackBar(
            content=ft.Text(mensaje, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.GREEN_600,
            duration=2000,
        )
        self._pagina.overlay.append(snack)
        snack.open = True
        safe_update(self._pagina)
    
    def _MOSTRAR_ERROR(self, mensaje):
        """Muestra snackbar de error"""
        snack = ft.SnackBar(
            content=ft.Text(mensaje, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.RED_600,
            duration=3000,
        )
        self._pagina.overlay.append(snack)
        snack.open = True
        safe_update(self._pagina)
    
    def _ir_dashboard(self):
        """Vuelve al dashboard"""
        from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
        self._auto_refresh_activo = False
        self._pagina.controls.clear()
        self._pagina.add(PaginaAdmin(self._pagina, self._usuario))
        safe_update(self._pagina)
    
    def _cerrar_sesion(self):
        """Cierra sesión"""
        from features.autenticacion.presentation.pages.PaginaLogin import PaginaLogin
        self._auto_refresh_activo = False
        self._pagina.controls.clear()
        self._pagina.add(PaginaLogin(self._pagina))
        safe_update(self._pagina)
