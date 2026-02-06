"""
Chat Flotante tipo Messenger
Botón flotante con notificaciones y lista de conversaciones
"""
import flet as ft
from typing import Optional, Callable
from core.Constantes import COLORES
from core.chat.GestorChat import GestorChat
from core.chat.ChatDialog import ChatDialog
from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION,
    MODELO_PEDIDO,
    MODELO_USUARIO,
    MODELO_MENSAJE_CHAT
)
from sqlalchemy import func, and_, or_


class ChatFlotante(ft.Container):
    """Botón flotante de chat tipo Messenger con lista de conversaciones"""
    
    def __init__(
        self,
        pagina: ft.Page,
        usuario_id: int,
        usuario_rol: str,
    ):
        super().__init__()
        self.PAGINA = pagina
        self.USUARIO_ID = usuario_id
        self.USUARIO_ROL = usuario_rol
        self.GESTOR_CHAT = GestorChat()
        
        # Estado
        self.PANEL_ABIERTO = False
        self.MENSAJES_NO_LEIDOS = 0
        
        # Componentes
        self.BTN_FLOTANTE = None
        self.BADGE_NO_LEIDOS = None
        self.PANEL_CONVERSACIONES = None
        self.LISTA_CONVERSACIONES = None
        
        self._CONSTRUIR()
        self._CARGAR_MENSAJES_NO_LEIDOS()
    
    def _CONSTRUIR(self):
        """Construye el botón flotante"""
        
        # Badge de mensajes no leídos
        self.BADGE_NO_LEIDOS = ft.Container(
            content=ft.Text(
                "0",
                size=11,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE
            ),
            bgcolor=ft.Colors.RED_500,
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=6, vertical=2),
            visible=False,
            width=24,
            height=24
        )
        
        # Botón flotante
        self.BTN_FLOTANTE = ft.FloatingActionButton(
            content=ft.Stack([
                ft.Icon(ft.icons.Icons.CHAT, color=ft.Colors.WHITE, size=28),
                ft.Container(
                    content=self.BADGE_NO_LEIDOS,
                    alignment=ft.Alignment(1, -1),  # top_right
                    margin=ft.margin.only(top=-5, right=-5)
                )
            ]),
            bgcolor=COLORES.PRIMARIO,
            on_click=self._TOGGLE_PANEL,
            width=60,
            height=60
        )
        
        # Lista de conversaciones
        self.LISTA_CONVERSACIONES = ft.ListView(
            spacing=10,
            padding=10,
            auto_scroll=False,
            expand=True
        )
        
        # Panel de conversaciones
        self.PANEL_CONVERSACIONES = ft.Container(
            content=ft.Column([
                # Header
                ft.Container(
                    content=ft.Row([
                        ft.Text(
                            "Mensajes",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE
                        ),
                        ft.IconButton(
                            icon=ft.icons.Icons.CLOSE,
                            icon_color=ft.Colors.WHITE,
                            on_click=self._CERRAR_PANEL,
                            icon_size=20
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    bgcolor=COLORES.PRIMARIO,
                    padding=15,
                    border_radius=ft.border_radius.only(top_left=15, top_right=15)
                ),
                # Lista de conversaciones
                ft.Container(
                    content=self.LISTA_CONVERSACIONES,
                    expand=True,
                    padding=0
                )
            ], spacing=0, expand=True),
            bgcolor=ft.Colors.WHITE,
            border_radius=15,
            shadow=ft.BoxShadow(
                spread_radius=2,
                blur_radius=20,
                color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
                offset=ft.Offset(0, 8)
            ),
            width=350,
            height=500,
            visible=False
        )
        
        # Contenedor principal (Stack para posicionar elementos)
        # NO usar expand para evitar bloquear BottomNavigation
        self.content = ft.Stack(
            [
                # Panel de conversaciones (se posiciona abajo)
                ft.Container(
                    content=self.PANEL_CONVERSACIONES,
                    alignment=ft.Alignment(1, 1),  # bottom_right
                    margin=ft.margin.only(bottom=130, right=20)
                ),
                # Botón flotante (se posiciona encima)
                ft.Container(
                    content=self.BTN_FLOTANTE,
                    alignment=ft.Alignment(1, 1),  # bottom_right
                    margin=ft.margin.only(bottom=70, right=20)
                )
            ],
            width=500,  # Ancho fijo solo para el área del chat
            height=600  # Alto fijo
        )
        
        # Propiedades del contenedor - alineado a bottom_right
        self.alignment = ft.Alignment(1, 1)  # bottom_right
        self.expand = False
        self.width = 500
        self.height = 600
    
    def _CARGAR_MENSAJES_NO_LEIDOS(self):
        """Carga el contador de mensajes no leídos"""
        try:
            sesion = OBTENER_SESION()
            
            # Obtener pedidos según rol
            if self.USUARIO_ROL in ["SUPERADMIN", "ADMIN", "ATENCION"]:
                # Admin/Superadmin ve todos los pedidos
                pedidos = sesion.query(MODELO_PEDIDO.ID).all()
                pedidos_ids = [p.ID for p in pedidos]
            else:
                # Cliente ve solo sus pedidos
                pedidos = sesion.query(MODELO_PEDIDO.ID).filter(
                    MODELO_PEDIDO.CLIENTE_ID == self.USUARIO_ID
                ).all()
                pedidos_ids = [p.ID for p in pedidos]
            
            if not pedidos_ids:
                self.MENSAJES_NO_LEIDOS = 0
                return
            
            # Contar mensajes no leídos
            mensajes_no_leidos = sesion.query(func.count(MODELO_MENSAJE_CHAT.ID)).filter(
                and_(
                    MODELO_MENSAJE_CHAT.PEDIDO_ID.in_(pedidos_ids),
                    MODELO_MENSAJE_CHAT.USUARIO_ID != self.USUARIO_ID,
                    or_(
                        MODELO_MENSAJE_CHAT.ESTADO != "leido",
                        MODELO_MENSAJE_CHAT.ESTADO.is_(None)
                    )
                )
            ).scalar()
            
            self.MENSAJES_NO_LEIDOS = mensajes_no_leidos or 0
            
            # Actualizar badge
            if self.MENSAJES_NO_LEIDOS > 0:
                self.BADGE_NO_LEIDOS.content.value = str(
                    self.MENSAJES_NO_LEIDOS if self.MENSAJES_NO_LEIDOS < 100 else "99+"
                )
                self.BADGE_NO_LEIDOS.visible = True
            else:
                self.BADGE_NO_LEIDOS.visible = False
            
            sesion.close()
            
        except Exception as e:
            print(f"❌ Error al cargar mensajes no leídos: {e}")
            self.MENSAJES_NO_LEIDOS = 0
    
    def _TOGGLE_PANEL(self, e):
        """Abre/cierra el panel de conversaciones"""
        self.PANEL_ABIERTO = not self.PANEL_ABIERTO
        self.PANEL_CONVERSACIONES.visible = self.PANEL_ABIERTO
        
        if self.PANEL_ABIERTO:
            self._CARGAR_CONVERSACIONES()
        
        self.PAGINA.update()
    
    def _CERRAR_PANEL(self, e):
        """Cierra el panel"""
        self.PANEL_ABIERTO = False
        self.PANEL_CONVERSACIONES.visible = False
        self.PAGINA.update()
    
    def _CARGAR_CONVERSACIONES(self):
        """Carga la lista de conversaciones (pedidos con mensajes)"""
        try:
            sesion = OBTENER_SESION()
            
            # Query base
            query = sesion.query(
                MODELO_PEDIDO,
                func.count(MODELO_MENSAJE_CHAT.ID).label('total_mensajes'),
                func.count(
                    func.nullif(
                        MODELO_MENSAJE_CHAT.ESTADO != "leido",
                        False
                    )
                ).label('mensajes_no_leidos'),
                func.max(MODELO_MENSAJE_CHAT.FECHA).label('ultimo_mensaje')
            ).join(
                MODELO_MENSAJE_CHAT,
                MODELO_PEDIDO.ID == MODELO_MENSAJE_CHAT.PEDIDO_ID
            ).join(
                MODELO_USUARIO,
                MODELO_PEDIDO.CLIENTE_ID == MODELO_USUARIO.ID
            )
            
            # Filtrar según rol
            if self.USUARIO_ROL in ["SUPERADMIN", "ADMIN", "ATENCION"]:
                # Ver todos los pedidos con mensajes
                pass
            else:
                # Cliente ve solo sus pedidos
                query = query.filter(MODELO_PEDIDO.CLIENTE_ID == self.USUARIO_ID)
            
            # Agrupar y ordenar
            conversaciones = query.group_by(MODELO_PEDIDO.ID).order_by(
                func.max(MODELO_MENSAJE_CHAT.FECHA).desc()
            ).limit(20).all()
            
            # Limpiar lista
            self.LISTA_CONVERSACIONES.controls.clear()
            
            if not conversaciones:
                self.LISTA_CONVERSACIONES.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(
                                ft.icons.Icons.CHAT_BUBBLE_OUTLINE,
                                size=64,
                                color=ft.Colors.GREY_400
                            ),
                            ft.Text(
                                "No hay conversaciones",
                                size=16,
                                color=ft.Colors.GREY_600,
                                text_align=ft.TextAlign.CENTER
                            )
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                        padding=40
                    )
                )
            else:
                for pedido, total, no_leidos, ultimo in conversaciones:
                    # Obtener nombre del cliente
                    cliente = sesion.query(MODELO_USUARIO).get(pedido.CLIENTE_ID)
                    nombre_cliente = cliente.NOMBRE_USUARIO if cliente else "Cliente"
                    
                    # Crear tarjeta de conversación
                    self.LISTA_CONVERSACIONES.controls.append(
                        self._CREAR_TARJETA_CONVERSACION(
                            pedido=pedido,
                            nombre_cliente=nombre_cliente,
                            total_mensajes=total,
                            mensajes_no_leidos=no_leidos,
                            ultimo_mensaje=ultimo
                        )
                    )
            
            sesion.close()
            self.PAGINA.update()
            
        except Exception as e:
            print(f"❌ Error al cargar conversaciones: {e}")
            import traceback
            traceback.print_exc()
    
    def _CREAR_TARJETA_CONVERSACION(
        self,
        pedido,
        nombre_cliente: str,
        total_mensajes: int,
        mensajes_no_leidos: int,
        ultimo_mensaje
    ) -> ft.Container:
        """Crea una tarjeta de conversación"""
        
        # Badge de mensajes no leídos
        badge_no_leidos = None
        if mensajes_no_leidos > 0:
            badge_no_leidos = ft.Container(
                content=ft.Text(
                    str(mensajes_no_leidos if mensajes_no_leidos < 100 else "99+"),
                    size=11,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE
                ),
                bgcolor=ft.Colors.RED_500,
                border_radius=12,
                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                margin=ft.margin.only(left=5)
            )
        
        return ft.Container(
            content=ft.Row([
                # Avatar
                ft.Container(
                    content=ft.Icon(
                        ft.icons.Icons.RESTAURANT_MENU,
                        color=ft.Colors.WHITE,
                        size=24
                    ),
                    bgcolor=COLORES.PRIMARIO,
                    border_radius=25,
                    width=50,
                    height=50
                ),
                # Información
                ft.Column([
                    ft.Row([
                        ft.Text(
                            f"Pedido #{pedido.ID}",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLACK87
                        ),
                        badge_no_leidos if badge_no_leidos else ft.Container()
                    ], spacing=5),
                    ft.Text(
                        nombre_cliente,
                        size=12,
                        color=ft.Colors.GREY_700
                    ),
                    ft.Text(
                        f"{total_mensajes} mensaje{'s' if total_mensajes != 1 else ''}",
                        size=11,
                        color=ft.Colors.GREY_500
                    )
                ], spacing=3, expand=True)
            ], spacing=10, alignment=ft.MainAxisAlignment.START),
            bgcolor=ft.Colors.GREY_50 if mensajes_no_leidos > 0 else ft.Colors.WHITE,
            border=ft.border.all(
                1,
                COLORES.PRIMARIO if mensajes_no_leidos > 0 else ft.Colors.GREY_300
            ),
            border_radius=12,
            padding=12,
            on_click=lambda e, p=pedido: self._ABRIR_CHAT(p),
            ink=True
        )
    
    def _ABRIR_CHAT(self, pedido):
        """Abre el chat de un pedido específico"""
        # Cerrar panel
        self.PANEL_ABIERTO = False
        self.PANEL_CONVERSACIONES.visible = False
        
        # Abrir chat
        chat = ChatDialog(
            pagina=self.PAGINA,
            pedido_id=pedido.ID,
            usuario_id=self.USUARIO_ID,
            on_cerrar=self._ON_CERRAR_CHAT
        )
        chat.ABRIR()
    
    def _ON_CERRAR_CHAT(self):
        """Callback cuando se cierra el chat"""
        # Recargar contador de mensajes no leídos
        self._CARGAR_MENSAJES_NO_LEIDOS()
        self.PAGINA.update()
    
    def ACTUALIZAR_CONTADOR(self):
        """Actualiza el contador de mensajes no leídos (llamar desde WebSocket)"""
        self._CARGAR_MENSAJES_NO_LEIDOS()
        if self.PANEL_ABIERTO:
            self._CARGAR_CONVERSACIONES()
        self.PAGINA.update()
