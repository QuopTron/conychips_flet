import flet as ft
from datetime import datetime

from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION,
    MODELO_PEDIDO,
    MODELO_PRODUCTO,
    MODELO_VOUCHER,
    MODELO_CALIFICACION,
    MODELO_USUARIO,
)
from core.constantes import COLORES, TAMANOS, ICONOS
from core.decoradores.DecoradorVistas import REQUIERE_ROL
from core.websocket.GestorNotificaciones import GestorNotificaciones
from core.chat.ChatFlotante import ChatFlotante

@REQUIERE_ROL("CLIENTE", "ADMIN", "SUPERADMIN")
class PaginaDashboardCliente:
    
    def __init__(self, PAGINA: ft.Page, USUARIO_ID: int):
        self.PAGINA = PAGINA
        self.USUARIO_ID = USUARIO_ID
        self.GESTOR_NOTIFICACIONES = GestorNotificaciones()
        
        self.PEDIDOS_ACTIVOS = ft.ListView(spacing=10, expand=True)
        self.PRODUCTOS_LISTA = ft.ListView(spacing=10, expand=True)
        self.DIALOG_PRODUCTO = None
        self.CARRITO = []
        
        # Obtener rol del usuario
        sesion = OBTENER_SESION()
        usuario = sesion.query(MODELO_USUARIO).get(USUARIO_ID)
        rol_usuario = usuario.ROLES[0].NOMBRE if usuario and usuario.ROLES else "CLIENTE"
        sesion.close()
        
        # Chat flotante
        self.CHAT_FLOTANTE = ChatFlotante(
            pagina=PAGINA,
            usuario_id=USUARIO_ID,
            usuario_rol=rol_usuario
        )
        
        self._CARGAR_DATOS()
    
    
    def _CARGAR_DATOS(self):
        self._CARGAR_PEDIDOS_ACTIVOS()
        self._CARGAR_PRODUCTOS()
    
    
    def _CARGAR_PEDIDOS_ACTIVOS(self):
        sesion = OBTENER_SESION()
        fecha_attr = getattr(MODELO_PEDIDO, 'FECHA_PEDIDO', None) or getattr(MODELO_PEDIDO, 'FECHA_CONFIRMACION', None) or getattr(MODELO_PEDIDO, 'FECHA_CREACION', None)

        query = sesion.query(MODELO_PEDIDO).filter(
            MODELO_PEDIDO.CLIENTE_ID == self.USUARIO_ID,
            MODELO_PEDIDO.ESTADO.in_(["pendiente", "confirmado", "en_preparacion", "listo", "en_camino"]),
        )

        if fecha_attr is not None:
            query = query.order_by(fecha_attr.desc())

        pedidos = query.all()
        
        self.PEDIDOS_ACTIVOS.controls.clear()
        
        if not pedidos:
            self.PEDIDOS_ACTIVOS.controls.append(
                ft.Text("No tienes pedidos activos", color=COLORES.TEXTO_SECUNDARIO)
            )
        else:
            for pedido in pedidos:
                self.PEDIDOS_ACTIVOS.controls.append(
                    self._CREAR_TARJETA_PEDIDO(pedido)
                )
        
        sesion.close()
        
        if self.PAGINA:
            self.PAGINA.update()
    
    
    def _CREAR_TARJETA_PEDIDO(self, PEDIDO):
        COLORES_ESTADO = {
            "pendiente": COLORES.ADVERTENCIA,
            "confirmado": COLORES.INFO,
            "en_preparacion": COLORES.PRIMARIO,
            "listo": COLORES.EXITO,
            "en_camino": COLORES.SECUNDARIO,
        }
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ICONOS.PEDIDO, color=COLORES.PRIMARIO),
                    ft.Text(f"Pedido #{PEDIDO.ID}", weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.Chip(
                        label=ft.Text(PEDIDO.ESTADO.upper(), size=12),
                        bgcolor=COLORES_ESTADO.get(PEDIDO.ESTADO, COLORES.PRIMARIO),
                    ),
                ]),
                ft.Row([
                    ft.Text(f"Total: S/ {getattr(PEDIDO, 'MONTO_TOTAL', getattr(PEDIDO, 'TOTAL', 0)):.2f}", size=16, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.Text(
                        (
                            getattr(PEDIDO, 'FECHA_CONFIRMACION', None)
                            or getattr(PEDIDO, 'FECHA_CREACION', None)
                            or getattr(PEDIDO, 'FECHA_PEDIDO', None)
                        ).strftime("%d/%m/%Y %H:%M") if (
                            getattr(PEDIDO, 'FECHA_CONFIRMACION', None)
                            or getattr(PEDIDO, 'FECHA_CREACION', None)
                            or getattr(PEDIDO, 'FECHA_PEDIDO', None)
                        ) else "",
                        color=COLORES.TEXTO_SECUNDARIO,
                        size=12
                    ),
                ]),
                ft.Row([
                    ft.Button(
                        "Ver Detalle",
                        icon=ICONOS.VER,
                        on_click=lambda e, p=PEDIDO: self._VER_DETALLE_PEDIDO(p)
                    ),
                    ft.Button(
                        "Subir Voucher",
                        icon=ICONOS.SUBIR,
                        on_click=lambda e, p=PEDIDO: self._SUBIR_VOUCHER(p),
                        visible=PEDIDO.ESTADO == "pendiente"
                    ),
                    ft.Button(
                        "Chat",
                        icon=ICONOS.CHAT,
                        on_click=lambda e, p=PEDIDO: self._ABRIR_CHAT(p),
                        visible=PEDIDO.ESTADO in ["en_camino", "listo"]
                    ),
                    ft.Button(
                        "Calificar",
                        icon=ICONOS.FAVORITO,
                        on_click=lambda e, p=PEDIDO: self._CALIFICAR_PEDIDO(p),
                        visible=PEDIDO.ESTADO == "entregado"
                    ),
                ], spacing=10),
            ], spacing=10),
            padding=15,
            border=ft.Border.all(1, COLORES.BORDE),
            border_radius=TAMANOS.RADIO_BORDE,
            bgcolor=COLORES.FONDO_TARJETA,
        )
    
    
    def _CARGAR_PRODUCTOS(self):
        sesion = OBTENER_SESION()
        
        productos = sesion.query(MODELO_PRODUCTO).filter_by(DISPONIBLE=True).all()
        
        self.PRODUCTOS_LISTA.controls.clear()
        
        for producto in productos:
            self.PRODUCTOS_LISTA.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(producto.NOMBRE, weight=ft.FontWeight.BOLD),
                            ft.Text(
                                producto.DESCRIPCION or "",
                                color=COLORES.TEXTO_SECUNDARIO,
                                size=12
                            ),
                            ft.Text(f"S/ {producto.PRECIO:.2f}", size=16, color=COLORES.EXITO),
                        ], expand=True),
                        ft.IconButton(
                            icon=ICONOS.AGREGAR,
                            bgcolor=COLORES.PRIMARIO,
                            icon_color=COLORES.TEXTO_BLANCO,
                            on_click=lambda e, p=producto: self._AGREGAR_AL_CARRITO(p)
                        ),
                    ]),
                    padding=10,
                    border=ft.Border.all(1, COLORES.BORDE),
                    border_radius=TAMANOS.RADIO_BORDE,
                )
            )
        
        sesion.close()
        
        if self.PAGINA:
            self.PAGINA.update()
    
    
    def _AGREGAR_AL_CARRITO(self, PRODUCTO):
        self.CARRITO.append({
            "producto": PRODUCTO,
            "cantidad": 1
        })
        
        self.PAGINA.snack_bar = ft.SnackBar(
            content=ft.Text(f"Agregado: {PRODUCTO.NOMBRE}"),
            bgcolor=COLORES.EXITO
        )
        self.PAGINA.snack_bar.open = True
        self.PAGINA.update()
    
    
    def _VER_CARRITO(self):
        if not self.CARRITO:
            self.PAGINA.snack_bar = ft.SnackBar(
                content=ft.Text("El carrito está vacío"),
                bgcolor=COLORES.ADVERTENCIA
            )
            self.PAGINA.snack_bar.open = True
            self.PAGINA.update()
            return
        
        TOTAL = sum(item["producto"].PRECIO * item["cantidad"] for item in self.CARRITO)
        
        dialog = ft.AlertDialog(
            title=ft.Text("Carrito de Compras"),
            content=ft.Column([
                *[
                    ft.Row([
                        ft.Text(f"{item['cantidad']}x {item['producto'].NOMBRE}"),
                        ft.Container(expand=True),
                        ft.Text(f"S/ {item['producto'].PRECIO * item['cantidad']:.2f}")
                    ])
                    for item in self.CARRITO
                ],
                ft.Divider(),
                ft.Row([
                    ft.Text("TOTAL:", weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.Text(f"S/ {TOTAL:.2f}", weight=ft.FontWeight.BOLD, size=18)
                ]),
            ], tight=True, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self._CERRAR_DIALOG()),
                ft.Button("Confirmar Pedido", on_click=lambda e: self._CONFIRMAR_PEDIDO()),
            ]
        )
        
        self.PAGINA.dialog = dialog
        dialog.open = True
        self.PAGINA.update()
    
    
    def _CONFIRMAR_PEDIDO(self):
        sesion = OBTENER_SESION()
        
        TOTAL = sum(item["producto"].PRECIO * item["cantidad"] for item in self.CARRITO)
        
        pedido = MODELO_PEDIDO(
            CLIENTE_ID=self.USUARIO_ID,
            MONTO_TOTAL=TOTAL,
            ESTADO="pendiente",
        )
        
        sesion.add(pedido)
        sesion.commit()
        sesion.refresh(pedido)
        # Notify realtime broker about newly created pedido (emulate WhatsApp incoming order)
        try:
            from core.realtime.broker_notify import notify
            sucursal_id = None
            try:
                from core.base_datos.ConfiguracionBD import MODELO_PEDIDO
                pedido_model = sesion.query(MODELO_PEDIDO).filter_by(ID=pedido.ID).first()
                if pedido_model:
                    sucursal_id = getattr(pedido_model, 'SUCURSAL_ID', None)
            except Exception:
                sucursal_id = None

            payload = {
                'type': 'pedido_creado',
                'pedido_id': pedido.ID,
                'nuevo_estado': 'PENDIENTE',
                'cliente_id': self.USUARIO_ID,
            }
            if sucursal_id is not None:
                payload['sucursal_id'] = sucursal_id
            notify(payload)
        except Exception:
            pass
        
        self.CARRITO.clear()
        sesion.close()
        
        self._CERRAR_DIALOG()
        self._CARGAR_PEDIDOS_ACTIVOS()
        
        self.PAGINA.snack_bar = ft.SnackBar(
            content=ft.Text("Pedido creado exitosamente"),
            bgcolor=COLORES.EXITO
        )
        self.PAGINA.snack_bar.open = True
        self.PAGINA.update()
    
    
    def _SUBIR_VOUCHER(self, PEDIDO):
        IMAGEN_URL = ft.TextField(
            label="URL de Imagen del Voucher",
            hint_text="https://ejemplo.com/voucher.jpg",
            prefix_icon=ICONOS.IMAGEN,
        )
        
        MONTO = ft.TextField(
            label="Monto (Bs)",
            value=str(getattr(PEDIDO, 'MONTO_TOTAL', getattr(PEDIDO, 'TOTAL', 0)) / 100),
            prefix_icon=ICONOS.DINERO,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        
        METODO = ft.Dropdown(
            label="Método de Pago",
            options=[
                ft.dropdown.Option("yape"),
                ft.dropdown.Option("plin"),
                ft.dropdown.Option("transferencia"),
                ft.dropdown.Option("efectivo"),
            ],
            value="yape"
        )
        
        def GUARDAR_VOUCHER(e):
            sesion = OBTENER_SESION()
            
            try:
                monto_cents = int(round(float(MONTO.value) * 100))
            except Exception:
                monto_cents = int(getattr(PEDIDO, 'MONTO_TOTAL', getattr(PEDIDO, 'TOTAL', 0)))

            voucher = MODELO_VOUCHER(
                PEDIDO_ID=PEDIDO.ID,
                USUARIO_ID=self.USUARIO_ID,
                IMAGEN_URL=IMAGEN_URL.value,
                MONTO=monto_cents,
                METODO_PAGO=METODO.value,
            )
            
            sesion.add(voucher)
            sesion.commit()
            # notify broker about new voucher (include sucursal if available)
            try:
                from core.realtime.broker_notify import notify
                sucursal_id = None
                try:
                    from core.base_datos.ConfiguracionBD import MODELO_PEDIDO
                    pedido_model = sesion.query(MODELO_PEDIDO).filter_by(ID=PEDIDO.ID).first()
                    if pedido_model:
                        sucursal_id = getattr(pedido_model, 'SUCURSAL_ID', None)
                except Exception:
                    sucursal_id = None

                payload = {
                    'type': 'voucher_creado',
                    'voucher_id': voucher.ID,
                    'nuevo_estado': 'PENDIENTE',
                    'usuario_id': self.USUARIO_ID,
                }
                if sucursal_id is not None:
                    payload['sucursal_id'] = sucursal_id
                notify(payload)
            except Exception:
                pass

            sesion.close()
            
            self._CERRAR_DIALOG()
            
            self.PAGINA.snack_bar = ft.SnackBar(
                content=ft.Text("Voucher subido exitosamente"),
                bgcolor=COLORES.EXITO
            )
            self.PAGINA.snack_bar.open = True
            self.PAGINA.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Subir Voucher de Pago"),
            content=ft.Column([IMAGEN_URL, MONTO, METODO], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self._CERRAR_DIALOG()),
                ft.Button("Subir", on_click=GUARDAR_VOUCHER),
            ]
        )
        
        self.PAGINA.dialog = dialog
        dialog.open = True
        self.PAGINA.update()
    
    
    def _CALIFICAR_PEDIDO(self, PEDIDO):
        CALIFICACION_COMIDA = ft.Slider(
            min=1, max=5, divisions=4, value=5, label="{value} estrellas"
        )
        CALIFICACION_SERVICIO = ft.Slider(
            min=1, max=5, divisions=4, value=5, label="{value} estrellas"
        )
        CALIFICACION_ENTREGA = ft.Slider(
            min=1, max=5, divisions=4, value=5, label="{value} estrellas"
        )
        COMENTARIO = ft.TextField(
            label="Comentario",
            multiline=True,
            min_lines=3,
            max_lines=5,
        )
        
        def GUARDAR_CALIFICACION(e):
            sesion = OBTENER_SESION()
            
            calificacion = MODELO_CALIFICACION(
                PEDIDO_ID=PEDIDO.ID,
                USUARIO_ID=self.USUARIO_ID,
                CALIFICACION_COMIDA=int(CALIFICACION_COMIDA.value),
                CALIFICACION_SERVICIO=int(CALIFICACION_SERVICIO.value),
                CALIFICACION_ENTREGA=int(CALIFICACION_ENTREGA.value),
                COMENTARIO=COMENTARIO.value,
            )
            
            sesion.add(calificacion)
            sesion.commit()
            sesion.close()
            
            self._CERRAR_DIALOG()
            
            self.PAGINA.snack_bar = ft.SnackBar(
                content=ft.Text("¡Gracias por tu calificación!"),
                bgcolor=COLORES.EXITO
            )
            self.PAGINA.snack_bar.open = True
            self.PAGINA.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Calificar Pedido"),
            content=ft.Column([
                ft.Text("Calificación de Comida"),
                CALIFICACION_COMIDA,
                ft.Text("Calificación de Servicio"),
                CALIFICACION_SERVICIO,
                ft.Text("Calificación de Entrega"),
                CALIFICACION_ENTREGA,
                COMENTARIO,
            ], tight=True, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self._CERRAR_DIALOG()),
                ft.Button("Enviar Calificación", on_click=GUARDAR_CALIFICACION),
            ]
        )
        
        self.PAGINA.dialog = dialog
        dialog.open = True
        self.PAGINA.update()
    
    
    def _VER_DETALLE_PEDIDO(self, PEDIDO):
        pass
    
    
    
    def _ABRIR_CHAT(self, PEDIDO):
        """Abre el chat para un pedido específico"""
        from core.chat.ChatDialog import ChatDialog
        
        chat = ChatDialog(
            pagina=self.PAGINA,
            pedido_id=PEDIDO.ID,
            usuario_id=self.USUARIO_ID,
            on_cerrar=lambda: None
        )
        
        chat.ABRIR()
        self.PAGINA.dialog = dialog
        dialog.open = True
        self.PAGINA.update()
    
    
    def _CERRAR_DIALOG(self):
        if self.PAGINA.dialog:
            self.PAGINA.dialog.open = False
            self.PAGINA.update()
    
    
    def CONSTRUIR(self) -> ft.Control:
        # Contenido principal
        contenido_principal = ft.Column([
            ft.Text("Dashboard Cliente", size=TAMANOS.TITULO, weight=ft.FontWeight.BOLD),
            
            ft.Tabs(
                content=ft.Column([
                    ft.TabBar(
                        tabs=[
                            ft.Tab(label="Pedidos Activos", icon=ICONOS.PEDIDO),
                            ft.Tab(label="Hacer Pedido", icon=ICONOS.AGREGAR),
                        ],
                    ),
                    ft.TabBarView(
                        controls=[
                            ft.Container(content=self.PEDIDOS_ACTIVOS, padding=10),
                            ft.Column([
                                ft.Row([
                                    ft.Text("Productos Disponibles", size=18, weight=ft.FontWeight.BOLD),
                                    ft.Container(expand=True),
                                    ft.Badge(
                                        content=ft.IconButton(
                                            icon=ICONOS.CARRITO,
                                            on_click=lambda e: self._VER_CARRITO()
                                        ),
                                        text=str(len(self.CARRITO)) if self.CARRITO else "",
                                    ),
                                ]),
                                ft.Container(
                                    content=self.PRODUCTOS_LISTA,
                                    expand=True,
                                    padding=10,
                                ),
                            ]),
                        ],
                    ),
                ], expand=True),
                length=2,
                selected_index=0,
            )
        ], expand=True)
        
        # Envolver en Stack para agregar chat flotante
        return ft.Stack([
            contenido_principal,
            self.CHAT_FLOTANTE
        ], expand=True)
