import flet as ft
from datetime import datetime

from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION,
    MODELO_PEDIDO,
    MODELO_INSUMO,
    MODELO_REFILL_SOLICITUD,
    MODELO_USUARIO,
    MODELO_ALERTA_COCINA,
)
from core.constantes import COLORES, TAMANOS, ICONOS
from core.decoradores.DecoradorVistas import REQUIERE_ROL
from core.websocket.GestorNotificaciones import GestorNotificaciones
from core.realtime import dispatcher

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
        # register for realtime cocina alerts and refill requests
        try:
            dispatcher.register('alerta_cocina', self._on_realtime_alert)
            dispatcher.register('refill_solicitado', self._on_realtime_refill)
        except Exception:
            pass
    
    
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

    def _on_realtime_alert(self, payload: dict):
        """Maneja alertas de cocina en tiempo real"""
        try:
            alerta_id = payload.get('alerta_id')
            pid = payload.get('pedido_id')
            prioridad = payload.get('prioridad', 'normal')
            mensaje = payload.get('mensaje', f'Alerta para pedido #{pid}')
            
            # Filter by sucursal if event provides it
            sucursal_evt = payload.get('sucursal_id')
            try:
                sesion = OBTENER_SESION()
                usuario = sesion.query(MODELO_USUARIO).filter_by(ID=self.USUARIO_ID).first()
                usuario_suc = getattr(usuario, 'SUCURSAL_ID', None) if usuario else None
                sesion.close()
            except Exception:
                usuario_suc = None

            if sucursal_evt is not None and usuario_suc is not None and sucursal_evt != usuario_suc:
                return

            # Color según prioridad
            color_borde = COLORES.ADVERTENCIA if prioridad == 'normal' else COLORES.ERROR
            icono_color = COLORES.ADVERTENCIA if prioridad == 'normal' else COLORES.ERROR
            
            # Añadir alerta visual al inicio de la lista
            self.PEDIDOS_PREPARACION.controls.insert(0, ft.Container(
                content=ft.Row([
                    ft.Icon(ICONOS.ALERTA, color=icono_color),
                    ft.Column([
                        ft.Text(f"🔔 ALERTA: {mensaje}", weight=ft.FontWeight.BOLD, color=icono_color),
                        ft.Text(f"Prioridad: {prioridad.upper()}", size=12, color=COLORES.TEXTO_SECUNDARIO),
                    ], spacing=5),
                    ft.Container(expand=True),
                    ft.IconButton(
                        icon=ft.icons.CLOSE,
                        on_click=lambda e, aid=alerta_id: self._marcar_alerta_leida(aid, e),
                        tooltip="Marcar como leída"
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=15,
                border=ft.Border.all(2, color_borde),
                border_radius=TAMANOS.RADIO_BORDE,
                bgcolor=COLORES.FONDO_TARJETA,
            ))
            
            # keep list manageable
            if len(self.PEDIDOS_PREPARACION.controls) > 200:
                self.PEDIDOS_PREPARACION.controls.pop()
            
            if self.PAGINA:
                self.PAGINA.update()
        except Exception as e:
            pass
    
    def _on_realtime_refill(self, payload: dict):
        """Maneja solicitudes de refill en tiempo real"""
        try:
            # Recargar lista de solicitudes de refill
            self._CARGAR_SOLICITUDES_REFILL()
            
            # Mostrar notificación
            if self.PAGINA:
                self.PAGINA.snack_bar = ft.SnackBar(
                    content=ft.Text(f"🔔 Nueva solicitud de refill: {payload.get('insumo_nombre', 'Insumo')}"),
                    bgcolor=COLORES.ADVERTENCIA
                )
                self.PAGINA.snack_bar.open = True
                self.PAGINA.update()
        except Exception:
            pass
    
    def _marcar_alerta_leida(self, alerta_id: int, e):
        """Marca una alerta como leída y la oculta"""
        try:
            if not alerta_id:
                return
            
            sesion = OBTENER_SESION()
            alerta = sesion.query(MODELO_ALERTA_COCINA).filter_by(ID=alerta_id).first()
            if alerta:
                alerta.LEIDA = True
                alerta.FECHA_LECTURA = datetime.utcnow()
                sesion.commit()
            sesion.close()
            
            # Remover de la vista
            if e and e.control and e.control.parent and e.control.parent.parent:
                container = e.control.parent.parent
                if container in self.PEDIDOS_PREPARACION.controls:
                    self.PEDIDOS_PREPARACION.controls.remove(container)
                    if self.PAGINA:
                        self.PAGINA.update()
        except Exception:
            pass
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
                    ft.Button(
                        "Iniciar Preparación",
                        icon=ICONOS.COCINA,
                        bgcolor=COLORES.ADVERTENCIA,
                        on_click=lambda e, p=PEDIDO: self._INICIAR_PREPARACION(p),
                        visible=PEDIDO.ESTADO == "confirmado"
                    ),
                    ft.Button(
                        "Marcar Listo",
                        icon=ICONOS.CONFIRMAR,
                        bgcolor=COLORES.EXITO,
                        on_click=lambda e, p=PEDIDO: self._MARCAR_LISTO(p),
                        visible=PEDIDO.ESTADO == "en_preparacion"
                    ),
                ], spacing=10),
            ], spacing=10),
            padding=15,
            border=ft.Border.all(1, COLORES.BORDE),
            border_radius=TAMANOS.RADIO_BORDE,
            bgcolor=COLORES.FONDO_TARJETA,
        )
    
    
    async def _INICIAR_PREPARACION(self, PEDIDO):
        sesion = OBTENER_SESION()
        
        pedido = sesion.query(MODELO_PEDIDO).filter_by(ID=PEDIDO.ID).first()
        if pedido:
            pedido.ESTADO = "en_preparacion"
            sesion.commit()
            try:
                from core.realtime.broker_notify import notify
                notify({'type': 'pedido_actualizado', 'pedido_id': pedido.ID, 'nuevo_estado': 'en_preparacion', 'sucursal_id': getattr(pedido, 'SUCURSAL_ID', None)})
            except Exception:
                pass

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
            try:
                from core.realtime.broker_notify import notify
                notify({'type': 'pedido_actualizado', 'pedido_id': pedido.ID, 'nuevo_estado': 'listo', 'sucursal_id': getattr(pedido, 'SUCURSAL_ID', None)})
            except Exception:
                pass

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
                    border=ft.Border.all(1, COLORES.ERROR if STOCK_BAJO else COLORES.BORDE),
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
            try:
                from core.realtime.broker_notify import notify
                notify({'type': 'refill_solicitado', 'insumo_id': INSUMO.ID, 'insumo_nombre': INSUMO.NOMBRE, 'cantidad': float(CANTIDAD.value)})
            except Exception:
                pass
            
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
                ft.Button("Solicitar", on_click=ENVIAR_SOLICITUD),
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
                        border=ft.Border.all(1, COLORES.BORDE),
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
                content=ft.Column([
                    ft.TabBar(
                        tabs=[
                            ft.Tab(label="Pedidos", icon=ICONOS.PEDIDO),
                            ft.Tab(label="Inventario", icon=ICONOS.INVENTARIO),
                            ft.Tab(label="Mis Solicitudes", icon=ICONOS.HISTORIAL),
                        ],
                    ),
                    ft.TabBarView(
                        controls=[
                            ft.Container(content=self.PEDIDOS_PREPARACION, padding=10),
                            ft.Container(content=self.INSUMOS_LISTA, padding=10),
                            ft.Container(content=self.SOLICITUDES_REFILL, padding=10),
                        ],
                    ),
                ], expand=True),
                length=3,
                selected_index=0,
            )
        ], expand=True)
