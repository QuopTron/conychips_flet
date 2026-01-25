import flet as ft
from datetime import datetime

from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION,
    MODELO_PEDIDO,
    MODELO_INSUMO,
    MODELO_REFILL_SOLICITUD,
    MODELO_USUARIO,
)
from core.constantes import COLORES, TAMANOS, ICONOS
from core.decoradores.DecoradorVistas import REQUIERE_ROL
from core.websocket.GestorNotificaciones import GestorNotificaciones


@REQUIERE_ROL("COCINERO", "ADMIN", "SUPERADMIN")
class PaginaDashboardCocina:
    
    def __init__(self, PAGINA: ft.Page, USUARIO_ID: int):
        self.PAGINA = PAGINA
        self.USUARIO_ID = USUARIO_ID
        self.GESTOR_NOTIFICACIONES = GestorNotificaciones()
        
        self.PEDIDOS_PREPARACION = ft.ListView(spacing=10, expand=True)
        self.INSUMOS_LISTA = ft.ListView(spacing=10, expand=True)
        self.SOLICITUDES_REFILL = ft.ListView(spacing=10, expand=True)
        
        self._CARGAR_DATOS()
    
    
    def _CARGAR_DATOS(self):
        self._CARGAR_PEDIDOS()
        self._CARGAR_INSUMOS()
        self._CARGAR_SOLICITUDES_REFILL()
    
    
    def _CARGAR_PEDIDOS(self):
        sesion = OBTENER_SESION()
        
        pedidos = (
            sesion.query(MODELO_PEDIDO)
            .filter(MODELO_PEDIDO.ESTADO.in_(["confirmado", "en_preparacion"]))
            .order_by(MODELO_PEDIDO.FECHA_PEDIDO.asc())
            .all()
        )
        
        self.PEDIDOS_PREPARACION.controls.clear()
        
        if not pedidos:
            self.PEDIDOS_PREPARACION.controls.append(
                ft.Text("No hay pedidos en preparación", color=COLORES.TEXTO_SECUNDARIO)
            )
        else:
            for pedido in pedidos:
                self.PEDIDOS_PREPARACION.controls.append(
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
                        bgcolor=COLORES.ADVERTENCIA if PEDIDO.ESTADO == "confirmado" else COLORES.PRIMARIO,
                    ),
                ]),
                ft.Text(
                    f"Hora: {PEDIDO.FECHA_PEDIDO.strftime('%H:%M')}",
                    color=COLORES.TEXTO_SECUNDARIO,
                    size=12
                ),
                ft.Row([
                    ft.ElevatedButton(
                        "Iniciar Preparación",
                        icon=ICONOS.COCINA,
                        bgcolor=COLORES.ADVERTENCIA,
                        on_click=lambda e, p=PEDIDO: self._INICIAR_PREPARACION(p),
                        visible=PEDIDO.ESTADO == "confirmado"
                    ),
                    ft.ElevatedButton(
                        "Marcar Listo",
                        icon=ICONOS.CONFIRMAR,
                        bgcolor=COLORES.EXITO,
                        on_click=lambda e, p=PEDIDO: self._MARCAR_LISTO(p),
                        visible=PEDIDO.ESTADO == "en_preparacion"
                    ),
                ], spacing=10),
            ], spacing=10),
            padding=15,
            border=ft.border.all(1, COLORES.BORDE),
            border_radius=TAMANOS.RADIO_BORDE,
            bgcolor=COLORES.FONDO_TARJETA,
        )
    
    
    async def _INICIAR_PREPARACION(self, PEDIDO):
        sesion = OBTENER_SESION()
        
        pedido = sesion.query(MODELO_PEDIDO).filter_by(ID=PEDIDO.ID).first()
        if pedido:
            pedido.ESTADO = "en_preparacion"
            sesion.commit()
            
            await self.GESTOR_NOTIFICACIONES.NOTIFICAR_CAMBIO_ESTADO_PEDIDO(
                PEDIDO_ID=pedido.ID,
                NUEVO_ESTADO="en_preparacion",
                USUARIO_AFECTADO=pedido.CLIENTE_ID
            )
        
        sesion.close()
        
        self._CARGAR_PEDIDOS()
        
        self.PAGINA.snack_bar = ft.SnackBar(
            content=ft.Text("Preparación iniciada"),
            bgcolor=COLORES.EXITO
        )
        self.PAGINA.snack_bar.open = True
        self.PAGINA.update()
    
    
    async def _MARCAR_LISTO(self, PEDIDO):
        sesion = OBTENER_SESION()
        
        pedido = sesion.query(MODELO_PEDIDO).filter_by(ID=PEDIDO.ID).first()
        if pedido:
            pedido.ESTADO = "listo"
            sesion.commit()
            
            await self.GESTOR_NOTIFICACIONES.NOTIFICAR_CAMBIO_ESTADO_PEDIDO(
                PEDIDO_ID=pedido.ID,
                NUEVO_ESTADO="listo",
                USUARIO_AFECTADO=pedido.CLIENTE_ID
            )
        
        sesion.close()
        
        self._CARGAR_PEDIDOS()
        
        self.PAGINA.snack_bar = ft.SnackBar(
            content=ft.Text("Pedido marcado como listo"),
            bgcolor=COLORES.EXITO
        )
        self.PAGINA.snack_bar.open = True
        self.PAGINA.update()
    
    
    def _CARGAR_INSUMOS(self):
        sesion = OBTENER_SESION()
        
        insumos = sesion.query(MODELO_INSUMO).all()
        
        self.INSUMOS_LISTA.controls.clear()
        
        for insumo in insumos:
            STOCK_BAJO = insumo.CANTIDAD_ACTUAL < insumo.STOCK_MINIMO
            
            self.INSUMOS_LISTA.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(insumo.NOMBRE, weight=ft.FontWeight.BOLD),
                            ft.Text(
                                f"Stock: {insumo.CANTIDAD_ACTUAL} {insumo.UNIDAD_MEDIDA}",
                                color=COLORES.ERROR if STOCK_BAJO else COLORES.EXITO
                            ),
                            ft.Text(
                                f"Mínimo: {insumo.STOCK_MINIMO}",
                                color=COLORES.TEXTO_SECUNDARIO,
                                size=12
                            ),
                        ], expand=True),
                        ft.IconButton(
                            icon=ICONOS.ALERTA if STOCK_BAJO else ICONOS.AGREGAR,
                            bgcolor=COLORES.ERROR if STOCK_BAJO else COLORES.PRIMARIO,
                            icon_color=COLORES.TEXTO_BLANCO,
                            on_click=lambda e, i=insumo: self._SOLICITAR_REFILL(i),
                            tooltip="Solicitar Refill"
                        ),
                    ]),
                    padding=10,
                    border=ft.border.all(1, COLORES.ERROR if STOCK_BAJO else COLORES.BORDE),
                    border_radius=TAMANOS.RADIO_BORDE,
                    bgcolor=COLORES.FONDO_TARJETA,
                )
            )
        
        sesion.close()
        
        if self.PAGINA:
            self.PAGINA.update()
    
    
    async def _SOLICITAR_REFILL(self, INSUMO):
        CANTIDAD = ft.TextField(
            label="Cantidad a Solicitar",
            value=str(INSUMO.STOCK_MINIMO * 2),
            suffix_text=INSUMO.UNIDAD_MEDIDA,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        
        async def ENVIAR_SOLICITUD(e):
            sesion = OBTENER_SESION()
            
            solicitud = MODELO_REFILL_SOLICITUD(
                INSUMO_ID=INSUMO.ID,
                USUARIO_SOLICITA=self.USUARIO_ID,
                CANTIDAD_SOLICITADA=float(CANTIDAD.value),
                ESTADO="pendiente",
            )
            
            sesion.add(solicitud)
            sesion.commit()
            
            admins = sesion.query(MODELO_USUARIO).filter(
                MODELO_USUARIO.ROL.in_(["ADMIN", "SUPERADMIN"])
            ).all()
            
            ADMIN_IDS = [admin.ID for admin in admins]
            
            sesion.close()
            
            await self.GESTOR_NOTIFICACIONES.NOTIFICAR_REFILL_SOLICITADO(
                INSUMO_NOMBRE=INSUMO.NOMBRE,
                CANTIDAD=float(CANTIDAD.value),
                USUARIOS_ADMIN=ADMIN_IDS
            )
            
            self._CERRAR_DIALOG()
            self._CARGAR_SOLICITUDES_REFILL()
            
            self.PAGINA.snack_bar = ft.SnackBar(
                content=ft.Text("Solicitud de refill enviada"),
                bgcolor=COLORES.EXITO
            )
            self.PAGINA.snack_bar.open = True
            self.PAGINA.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text(f"Solicitar Refill - {INSUMO.NOMBRE}"),
            content=ft.Column([
                ft.Text(f"Stock actual: {INSUMO.CANTIDAD_ACTUAL} {INSUMO.UNIDAD_MEDIDA}"),
                ft.Text(f"Stock mínimo: {INSUMO.STOCK_MINIMO} {INSUMO.UNIDAD_MEDIDA}"),
                CANTIDAD,
            ], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self._CERRAR_DIALOG()),
                ft.ElevatedButton("Solicitar", on_click=ENVIAR_SOLICITUD),
            ]
        )
        
        self.PAGINA.dialog = dialog
        dialog.open = True
        self.PAGINA.update()
    
    
    def _CARGAR_SOLICITUDES_REFILL(self):
        sesion = OBTENER_SESION()
        
        solicitudes = (
            sesion.query(MODELO_REFILL_SOLICITUD)
            .filter_by(USUARIO_SOLICITA=self.USUARIO_ID)
            .order_by(MODELO_REFILL_SOLICITUD.FECHA_SOLICITUD.desc())
            .limit(10)
            .all()
        )
        
        self.SOLICITUDES_REFILL.controls.clear()
        
        if not solicitudes:
            self.SOLICITUDES_REFILL.controls.append(
                ft.Text("No tienes solicitudes de refill", color=COLORES.TEXTO_SECUNDARIO)
            )
        else:
            for solicitud in solicitudes:
                insumo = sesion.query(MODELO_INSUMO).filter_by(ID=solicitud.INSUMO_ID).first()
                
                COLOR_ESTADO = {
                    "pendiente": COLORES.ADVERTENCIA,
                    "aprobado": COLORES.EXITO,
                    "rechazado": COLORES.ERROR,
                }
                
                self.SOLICITUDES_REFILL.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(insumo.NOMBRE if insumo else "Insumo", weight=ft.FontWeight.BOLD),
                                ft.Container(expand=True),
                                ft.Chip(
                                    label=ft.Text(solicitud.ESTADO.upper(), size=12),
                                    bgcolor=COLOR_ESTADO.get(solicitud.ESTADO, COLORES.PRIMARIO),
                                ),
                            ]),
                            ft.Text(f"Cantidad: {solicitud.CANTIDAD_SOLICITADA}"),
                            ft.Text(
                                solicitud.FECHA_SOLICITUD.strftime("%d/%m/%Y %H:%M"),
                                color=COLORES.TEXTO_SECUNDARIO,
                                size=12
                            ),
                        ], spacing=5),
                        padding=10,
                        border=ft.border.all(1, COLORES.BORDE),
                        border_radius=TAMANOS.RADIO_BORDE,
                    )
                )
        
        sesion.close()
        
        if self.PAGINA:
            self.PAGINA.update()
    
    
    def _CERRAR_DIALOG(self):
        if self.PAGINA.dialog:
            self.PAGINA.dialog.open = False
            self.PAGINA.update()
    
    
    def CONSTRUIR(self) -> ft.Control:
        return ft.Column([
            ft.Text("Dashboard Cocina", size=TAMANOS.TITULO, weight=ft.FontWeight.BOLD),
            
            ft.Tabs(
                selected_index=0,
                tabs=[
                    ft.Tab(
                        text="Pedidos",
                        icon=ICONOS.PEDIDO,
                        content=ft.Container(
                            content=self.PEDIDOS_PREPARACION,
                            padding=10,
                        )
                    ),
                    ft.Tab(
                        text="Inventario",
                        icon=ICONOS.INVENTARIO,
                        content=ft.Container(
                            content=self.INSUMOS_LISTA,
                            padding=10,
                        )
                    ),
                    ft.Tab(
                        text="Mis Solicitudes",
                        icon=ICONOS.HISTORIAL,
                        content=ft.Container(
                            content=self.SOLICITUDES_REFILL,
                            padding=10,
                        )
                    ),
                ],
                expand=True,
            )
        ], expand=True)
