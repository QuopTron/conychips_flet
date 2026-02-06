import flet as ft
from datetime import datetime

from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION,
    MODELO_PEDIDO,
    MODELO_UBICACION_MOTORIZADO,
    MODELO_MENSAJE_CHAT,
)
from core.constantes import COLORES, TAMANOS, ICONOS
from core.decoradores.DecoradorVistas import REQUIERE_ROL
from core.websocket.GestorNotificaciones import GestorNotificaciones

@REQUIERE_ROL("MOTORIZADO", "ADMIN", "SUPERADMIN")
class PaginaDashboardMotorizado:
    
    def __init__(self, PAGINA: ft.Page, USUARIO_ID: int):
        self.PAGINA = PAGINA
        self.USUARIO_ID = USUARIO_ID
        self.GESTOR_NOTIFICACIONES = GestorNotificaciones()
        
        self.PEDIDOS_ASIGNADOS = ft.ListView(spacing=10, expand=True)
        self.GPS_ACTIVO = False
        self.PEDIDO_ACTUAL = None
        
        self._CARGAR_PEDIDOS_ASIGNADOS()
    
    
    def _CARGAR_PEDIDOS_ASIGNADOS(self):
        sesion = OBTENER_SESION()
        
        pedidos = (
            sesion.query(MODELO_PEDIDO)
            .filter(
                MODELO_PEDIDO.MOTORIZADO_ID == self.USUARIO_ID,
                MODELO_PEDIDO.ESTADO.in_(["listo", "en_camino"])
            )
            .order_by(MODELO_PEDIDO.FECHA_PEDIDO.desc())
            .all()
        )
        
        self.PEDIDOS_ASIGNADOS.controls.clear()
        
        if not pedidos:
            self.PEDIDOS_ASIGNADOS.controls.append(
                ft.Text("No tienes pedidos asignados", color=COLORES.TEXTO_SECUNDARIO)
            )
        else:
            for pedido in pedidos:
                self.PEDIDOS_ASIGNADOS.controls.append(
                    self._CREAR_TARJETA_PEDIDO(pedido)
                )
        
        sesion.close()
        
        if self.PAGINA:
            self.PAGINA.update()
    
    
    def _CREAR_TARJETA_PEDIDO(self, PEDIDO):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ICONOS.PEDIDO, color=COLORES.PRIMARIO),
                    ft.Text(f"Pedido #{PEDIDO.ID}", weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.Chip(
                        label=ft.Text(PEDIDO.ESTADO.upper(), size=12),
                        bgcolor=COLORES.ACENTO if PEDIDO.ESTADO == "en_camino" else COLORES.ADVERTENCIA,
                    ),
                ]),
                ft.Text(f"Total: S/ {getattr(PEDIDO, 'MONTO_TOTAL', getattr(PEDIDO, 'TOTAL', 0)):.2f}", size=16),
                ft.Text(
                    f"Dirección: {PEDIDO.DIRECCION_ENTREGA or 'No especificada'}",
                    color=COLORES.TEXTO_SECUNDARIO,
                    size=12
                ),
                ft.Row([
                    ft.Button(
                        "Confirmar Salida",
                        icon=ICONOS.ENVIAR,
                        bgcolor=COLORES.ADVERTENCIA,
                        on_click=lambda e, p=PEDIDO: self._CONFIRMAR_SALIDA(p),
                        visible=PEDIDO.ESTADO == "listo"
                    ),
                    ft.Button(
                        "Activar GPS",
                        icon=ICONOS.UBICACION,
                        bgcolor=COLORES.EXITO if not self.GPS_ACTIVO else COLORES.ERROR,
                        on_click=lambda e, p=PEDIDO: self._TOGGLE_GPS(p),
                        visible=PEDIDO.ESTADO == "en_camino"
                    ),
                    ft.Button(
                        "Chat",
                        icon=ICONOS.CHAT,
                        on_click=lambda e, p=PEDIDO: self._ABRIR_CHAT(p),
                    ),
                    ft.Button(
                        "Confirmar Entrega",
                        icon=ICONOS.CONFIRMAR,
                        bgcolor=COLORES.EXITO,
                        on_click=lambda e, p=PEDIDO: self._CONFIRMAR_ENTREGA(p),
                        visible=PEDIDO.ESTADO == "en_camino"
                    ),
                ], spacing=10, wrap=True),
            ], spacing=10),
            padding=15,
            border=ft.Border.all(1, COLORES.BORDE),
            border_radius=TAMANOS.RADIO_BORDE,
            bgcolor=COLORES.FONDO_TARJETA,
        )
    
    
    async def _CONFIRMAR_SALIDA(self, PEDIDO):
        sesion = OBTENER_SESION()
        
        pedido = sesion.query(MODELO_PEDIDO).filter_by(ID=PEDIDO.ID).first()
        if pedido:
            pedido.ESTADO = "en_camino"
            sesion.commit()
            
            await self.GESTOR_NOTIFICACIONES.NOTIFICAR_CAMBIO_ESTADO_PEDIDO(
                PEDIDO_ID=pedido.ID,
                NUEVO_ESTADO="en_camino",
                USUARIO_AFECTADO=pedido.CLIENTE_ID
            )
        
        sesion.close()
        
        self._CARGAR_PEDIDOS_ASIGNADOS()
        
        self.PAGINA.snack_bar = ft.SnackBar(
            content=ft.Text("Salida confirmada"),
            bgcolor=COLORES.EXITO
        )
        self.PAGINA.snack_bar.open = True
        self.PAGINA.update()
    
    
    async def _TOGGLE_GPS(self, PEDIDO):
        self.GPS_ACTIVO = not self.GPS_ACTIVO
        self.PEDIDO_ACTUAL = PEDIDO if self.GPS_ACTIVO else None
        
        if self.GPS_ACTIVO:
            await self._ACTUALIZAR_UBICACION("salida")
            
            self.PAGINA.snack_bar = ft.SnackBar(
                content=ft.Text("GPS activado - Enviando ubicación"),
                bgcolor=COLORES.EXITO
            )
        else:
            self.PAGINA.snack_bar = ft.SnackBar(
                content=ft.Text("GPS desactivado"),
                bgcolor=COLORES.ADVERTENCIA
            )
        
        self.PAGINA.snack_bar.open = True
        self._CARGAR_PEDIDOS_ASIGNADOS()
    
    
    async def _ACTUALIZAR_UBICACION(self, ESTADO: str):
        LATITUD = "-12.0464"
        LONGITUD = "-77.0428"
        
        await self.GESTOR_NOTIFICACIONES.ACTUALIZAR_GPS(
            USUARIO_ID=self.USUARIO_ID,
            PEDIDO_ID=self.PEDIDO_ACTUAL.ID,
            LATITUD=LATITUD,
            LONGITUD=LONGITUD,
            ESTADO=ESTADO
        )
    
    
    async def _CONFIRMAR_ENTREGA(self, PEDIDO):
        sesion = OBTENER_SESION()
        
        pedido = sesion.query(MODELO_PEDIDO).filter_by(ID=PEDIDO.ID).first()
        if pedido:
            pedido.ESTADO = "entregado"
            sesion.commit()
            
            await self.GESTOR_NOTIFICACIONES.NOTIFICAR_CAMBIO_ESTADO_PEDIDO(
                PEDIDO_ID=pedido.ID,
                NUEVO_ESTADO="entregado",
                USUARIO_AFECTADO=pedido.CLIENTE_ID
            )
            
            if self.GPS_ACTIVO and self.PEDIDO_ACTUAL and self.PEDIDO_ACTUAL.ID == PEDIDO.ID:
                await self._ACTUALIZAR_UBICACION("llegada")
                self.GPS_ACTIVO = False
                self.PEDIDO_ACTUAL = None
        
        sesion.close()
        
        self._CARGAR_PEDIDOS_ASIGNADOS()
        
        self.PAGINA.snack_bar = ft.SnackBar(
            content=ft.Text("Entrega confirmada"),
            bgcolor=COLORES.EXITO
        )
        self.PAGINA.snack_bar.open = True
        self.PAGINA.update()
    
    
    def _ABRIR_CHAT(self, PEDIDO):
        MENSAJES_LISTA = ft.ListView(spacing=10, expand=True)
        MENSAJE_INPUT = ft.TextField(
            hint_text="Escribe un mensaje...",
            expand=True,
        )
        
        def CARGAR_MENSAJES():
            sesion = OBTENER_SESION()
            
            mensajes = (
                sesion.query(MODELO_MENSAJE_CHAT)
                .filter_by(PEDIDO_ID=PEDIDO.ID)
                .order_by(MODELO_MENSAJE_CHAT.FECHA.asc())
                .all()
            )
            
            MENSAJES_LISTA.controls.clear()
            
            for msg in mensajes:
                ES_MIO = msg.USUARIO_ID == self.USUARIO_ID
                
                MENSAJES_LISTA.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(msg.MENSAJE, size=14),
                            ft.Text(
                                msg.FECHA.strftime("%H:%M"),
                                size=10,
                                color=COLORES.TEXTO_SECUNDARIO
                            ),
                        ], tight=True),
                        padding=10,
                        bgcolor=COLORES.PRIMARIO if ES_MIO else COLORES.FONDO_TARJETA,
                        border_radius=TAMANOS.RADIO_BORDE,
                        alignment=ft.Alignment(1, 0) if ES_MIO else ft.Alignment(-1, 0),
                    )
                )
            
            sesion.close()
        
        async def ENVIAR_MENSAJE(e):
            if not MENSAJE_INPUT.value:
                return
            
            mensaje_texto = MENSAJE_INPUT.value
            MENSAJE_INPUT.value = ""
            
            # Agregar mensaje localmente ANTES de enviar
            ES_MIO = True
            MENSAJES_LISTA.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(mensaje_texto, size=14),
                        ft.Text(
                            datetime.now().strftime("%H:%M"),
                            size=10,
                            color=COLORES.TEXTO_SECUNDARIO
                        ),
                    ], tight=True),
                    padding=10,
                    bgcolor=COLORES.PRIMARIO if ES_MIO else COLORES.FONDO_TARJETA,
                    border_radius=TAMANOS.RADIO_BORDE,
                    alignment=ft.Alignment(1, 0) if ES_MIO else ft.Alignment(-1, 0),
                )
            )
            
            if self.PAGINA.dialog:
                self.PAGINA.dialog.update()
            
            await self.GESTOR_NOTIFICACIONES.ENVIAR_MENSAJE_CHAT(
                PEDIDO_ID=PEDIDO.ID,
                USUARIO_ID=self.USUARIO_ID,
                MENSAJE=mensaje_texto,
            )
        
        # Cargar mensajes SOLO UNA VEZ al abrir el chat
        CARGAR_MENSAJES()
        
        dialog = ft.AlertDialog(
            title=ft.Text(f"Chat - Pedido #{PEDIDO.ID}"),
            content=ft.Container(
                content=MENSAJES_LISTA,
                width=500,
                height=400,
            ),
            actions=[
                ft.Row([
                    MENSAJE_INPUT,
                    ft.IconButton(
                        icon=ICONOS.ENVIAR,
                        on_click=ENVIAR_MENSAJE,
                        bgcolor=COLORES.PRIMARIO,
                        icon_color=COLORES.TEXTO_BLANCO,
                    ),
                ]),
                ft.TextButton("Cerrar", on_click=lambda e: self._CERRAR_DIALOG()),
            ]
        )
        
        self._PAGINA.dialog = dialog
        dialog.open = True
        self._PAGINA.update()
    
    
    def _CERRAR_DIALOG(self):
        if self.PAGINA.dialog:
            self.PAGINA.dialog.open = False
            self.PAGINA.update()
    
    
    def CONSTRUIR(self) -> ft.Control:
        return ft.Column([
            ft.Text("Dashboard Motorizado", size=TAMANOS.TITULO, weight=ft.FontWeight.BOLD),
            
            ft.Row([
                ft.Icon(ICONOS.UBICACION,
                    color=COLORES.EXITO if self.GPS_ACTIVO else COLORES.TEXTO_SECUNDARIO
                ),
                ft.Text(
                    "GPS ACTIVO" if self.GPS_ACTIVO else "GPS INACTIVO",
                    weight=ft.FontWeight.BOLD,
                    color=COLORES.EXITO if self.GPS_ACTIVO else COLORES.TEXTO_SECUNDARIO
                ),
            ]),
            
            ft.Divider(),
            
            ft.Text("Pedidos Asignados", size=18, weight=ft.FontWeight.BOLD),
            
            ft.Container(
                content=self.PEDIDOS_ASIGNADOS,
                expand=True,
                padding=10,
            ),
        ], expand=True)
