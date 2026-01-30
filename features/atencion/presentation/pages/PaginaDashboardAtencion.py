import flet as ft
from datetime import datetime, timezone

from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION,
    MODELO_PEDIDO,
    MODELO_CAJA,
    MODELO_CAJA_MOVIMIENTO,
)
from core.constantes import COLORES, TAMANOS, ICONOS
from core.decoradores.DecoradorVistas import REQUIERE_ROL
from core.websocket.GestorNotificaciones import GestorNotificaciones
from core.realtime import dispatcher
from core.realtime.broker_notify import notify

@REQUIERE_ROL("ATENCION", "ADMIN", "SUPERADMIN")
class PaginaDashboardAtencion:
    
    def __init__(self, PAGINA: ft.Page, USUARIO_ID: int):
        self.PAGINA = PAGINA
        self.USUARIO_ID = USUARIO_ID
        self.GESTOR_NOTIFICACIONES = GestorNotificaciones()
        
        self.PEDIDOS_LISTOS = ft.ListView(spacing=10, expand=True)
        self.PEDIDOS_PENDIENTES = ft.ListView(spacing=8, expand=True)
        self.MOVIMIENTOS_CAJA = ft.ListView(spacing=10, expand=True)
        self.CAJA_ACTUAL = None
        self.SALDO_ACTUAL = ft.Text("S/ 0.00", size=24, weight=ft.FontWeight.BOLD, color=COLORES.EXITO)
        # Pending count badge
        self.PEDIDOS_PENDIENTES_CHIP = ft.Chip(label=ft.Text("0"), bgcolor=COLORES.ADVERTENCIA)
        
        self._CARGAR_DATOS()
        # load pending whatsapp orders and register realtime callbacks
        try:
            self._CARGAR_PENDIENTES()
        except Exception:
            pass
        try:
            dispatcher.register('pedido_creado', self._on_realtime_pedido)
            dispatcher.register('pedido_actualizado', self._on_realtime_pedido)
            dispatcher.register('pedido_alerta_cocina', self._on_realtime_pedido)
        except Exception:
            pass
        # initialize pending count
        try:
            self._actualizar_contador_pendientes()
        except Exception:
            pass
    
    
    def _CARGAR_DATOS(self):
        self._CARGAR_CAJA()
        self._CARGAR_PEDIDOS_LISTOS()
        self._CARGAR_MOVIMIENTOS()
    
    
    def _CARGAR_CAJA(self):
        sesion = OBTENER_SESION()
        
        caja = (
            sesion.query(MODELO_CAJA)
            .filter_by(USUARIO_ID=self.USUARIO_ID, ESTADO="abierta")
            .first()
        )
        
        self.CAJA_ACTUAL = caja
        
        if caja:
            self.SALDO_ACTUAL.value = f"S/ {caja.SALDO_ACTUAL:.2f}"
            self.SALDO_ACTUAL.color = COLORES.EXITO
        else:
            self.SALDO_ACTUAL.value = "CAJA CERRADA"
            self.SALDO_ACTUAL.color = COLORES.ERROR
        
        sesion.close()
        
        if self.PAGINA:
            self.PAGINA.update()
    
    
    def _CARGAR_PEDIDOS_LISTOS(self):
        sesion = OBTENER_SESION()
        
        pedidos = (
            sesion.query(MODELO_PEDIDO)
            .filter_by(ESTADO="listo")
            .order_by(MODELO_PEDIDO.FECHA_PEDIDO.asc())
            .all()
        )
        
        self.PEDIDOS_LISTOS.controls.clear()
        
        if not pedidos:
            self.PEDIDOS_LISTOS.controls.append(
                ft.Text("No hay pedidos listos", color=COLORES.TEXTO_SECUNDARIO)
            )
        else:
            for pedido in pedidos:
                self.PEDIDOS_LISTOS.controls.append(
                    self._CREAR_TARJETA_PEDIDO(pedido)
                )
        
        sesion.close()
        
        if self.PAGINA:
            self.PAGINA.update()

    def _CARGAR_PENDIENTES(self):
        sesion = OBTENER_SESION()
        try:
            # filter by user's assigned sucursal if available
            usuario = sesion.query(MODELO_USUARIO).filter_by(ID=self.USUARIO_ID).first()
            query = sesion.query(MODELO_PEDIDO)
            if usuario and hasattr(usuario, 'SUCURSAL_ID') and getattr(usuario, 'SUCURSAL_ID'):
                query = query.filter_by(ESTADO="PENDIENTE", SUCURSAL_ID=getattr(usuario, 'SUCURSAL_ID'))
            else:
                query = query.filter_by(ESTADO="PENDIENTE")

            pendientes = (
                query.order_by(MODELO_PEDIDO.FECHA_PEDIDO.desc()).limit(100).all()
            )
            # populate in-memory list (used by dialog)
            self.PEDIDOS_PENDIENTES.controls.clear()
            for p in pendientes:
                row = ft.Row([
                    ft.Text(f"#{p.ID} - {getattr(p,'CLIENTE','Cliente')} - S/ {getattr(p,'MONTO_TOTAL',0):.2f}"),
                    ft.Container(expand=True),
                    ft.Button("Aprobar", on_click=lambda e, pid=p.ID: self._aprobar(pid), bgcolor=COLORES.EXITO),
                    ft.Button("Alertar Cocina", on_click=lambda e, pid=p.ID: self._alertar_cocina(pid), bgcolor=COLORES.ADVERTENCIA),
                    ft.Button("Pedir Refill", on_click=lambda e, pid=p.ID: self._pedir_refill(pid), bgcolor=COLORES.PRIMARIO),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                self.PEDIDOS_PENDIENTES.controls.append(row)

            # update pending counter badge
            try:
                self.PEDIDOS_PENDIENTES_CHIP.label = ft.Text(str(len(pendientes)))
            except Exception:
                pass

            if self.PAGINA:
                self.PAGINA.update()
        finally:
            sesion.close()
    
    
    def _CREAR_TARJETA_PEDIDO(self, PEDIDO):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ICONOS.PEDIDO, color=COLORES.PRIMARIO),
                    ft.Text(f"Pedido #{PEDIDO.ID}", weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.Text(f"S/ {getattr(PEDIDO, 'MONTO_TOTAL', getattr(PEDIDO, 'TOTAL', 0)):.2f}", size=18, weight=ft.FontWeight.BOLD, color=COLORES.EXITO),
                ]),
                ft.Text(
                    f"Hora: {PEDIDO.FECHA_PEDIDO.strftime('%H:%M')}",
                    color=COLORES.TEXTO_SECUNDARIO,
                    size=12
                ),
                ft.Button(
                    "Servir y Cobrar",
                    icon=ICONOS.CONFIRMAR,
                    bgcolor=COLORES.EXITO,
                    on_click=lambda e, p=PEDIDO: self._SERVIR_PEDIDO(p),
                ),
            ], spacing=10),
            padding=15,
            border=ft.Border.all(1, COLORES.BORDE),
            border_radius=TAMANOS.RADIO_BORDE,
            bgcolor=COLORES.FONDO_TARJETA,
        )
    
    
    async def _SERVIR_PEDIDO(self, PEDIDO):
        if not self.CAJA_ACTUAL:
            self.PAGINA.snack_bar = ft.SnackBar(
                content=ft.Text("Debes abrir la caja primero"),
                bgcolor=COLORES.ERROR
            )
            self.PAGINA.snack_bar.open = True
            self.PAGINA.update()
            return
        
        sesion = OBTENER_SESION()
        
        pedido = sesion.query(MODELO_PEDIDO).filter_by(ID=PEDIDO.ID).first()
        if pedido:
            pedido.ESTADO = "entregado"
            sesion.commit()
            
            movimiento = MODELO_CAJA_MOVIMIENTO(
                CAJA_ID=self.CAJA_ACTUAL.ID,
                TIPO="ingreso",
                MONTO=getattr(pedido, 'MONTO_TOTAL', getattr(pedido, 'TOTAL', 0)),
                CONCEPTO=f"Venta pedido #{pedido.ID}",
            )
            
            sesion.add(movimiento)
            
            caja = sesion.query(MODELO_CAJA).filter_by(ID=self.CAJA_ACTUAL.ID).first()
            if caja:
                caja.SALDO_ACTUAL += getattr(pedido, 'MONTO_TOTAL', getattr(pedido, 'TOTAL', 0))
                sesion.commit()
            
            await self.GESTOR_NOTIFICACIONES.NOTIFICAR_CAMBIO_ESTADO_PEDIDO(
                PEDIDO_ID=pedido.ID,
                NUEVO_ESTADO="entregado",
                USUARIO_AFECTADO=pedido.CLIENTE_ID
            )
        
        sesion.close()
        
        self._CARGAR_DATOS()
        
        self.PAGINA.snack_bar = ft.SnackBar(
            content=ft.Text("Pedido servido y cobrado"),
            bgcolor=COLORES.EXITO
        )
        self.PAGINA.snack_bar.open = True
        self.PAGINA.update()
    
    
    def _ABRIR_CAJA(self):
        MONTO_INICIAL = ft.TextField(
            label="Monto Inicial",
            prefix_text="S/ ",
            value="100.00",
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        
        def CREAR_CAJA(e):
            sesion = OBTENER_SESION()
            
            caja = MODELO_CAJA(
                USUARIO_ID=self.USUARIO_ID,
                SALDO_INICIAL=float(MONTO_INICIAL.value),
                SALDO_ACTUAL=float(MONTO_INICIAL.value),
                ESTADO="abierta",
            )
            
            sesion.add(caja)
            sesion.commit()
            sesion.close()
            
            self._CERRAR_DIALOG()
            self._CARGAR_DATOS()
            
            self.PAGINA.snack_bar = ft.SnackBar(
                content=ft.Text("Caja abierta exitosamente"),
                bgcolor=COLORES.EXITO
            )
            self.PAGINA.snack_bar.open = True
            self.PAGINA.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Abrir Caja"),
            content=MONTO_INICIAL,
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self._CERRAR_DIALOG()),
                ft.Button("Abrir", on_click=CREAR_CAJA),
            ]
        )
        
        self.PAGINA.dialog = dialog
        dialog.open = True
        self.PAGINA.update()
    
    
    def _CERRAR_CAJA(self):
        if not self.CAJA_ACTUAL:
            return
        
        sesion = OBTENER_SESION()
        
        caja = sesion.query(MODELO_CAJA).filter_by(ID=self.CAJA_ACTUAL.ID).first()
        if caja:
            caja.ESTADO = "cerrada"
            caja.FECHA_CIERRE = datetime.now(timezone.utc)
            sesion.commit()
        
        sesion.close()
        
        self._CARGAR_DATOS()
        
        self.PAGINA.snack_bar = ft.SnackBar(
            content=ft.Text("Caja cerrada exitosamente"),
            bgcolor=COLORES.EXITO
        )
        self.PAGINA.snack_bar.open = True
        self.PAGINA.update()
    
    
    def _CARGAR_MOVIMIENTOS(self):
        if not self.CAJA_ACTUAL:
            self.MOVIMIENTOS_CAJA.controls.clear()
            self.MOVIMIENTOS_CAJA.controls.append(
                ft.Text("No hay caja abierta", color=COLORES.TEXTO_SECUNDARIO)
            )
            if self.PAGINA:
                self.PAGINA.update()
            return
        
        sesion = OBTENER_SESION()
        
        movimientos = (
            sesion.query(MODELO_CAJA_MOVIMIENTO)
            .filter_by(CAJA_ID=self.CAJA_ACTUAL.ID)
            .order_by(MODELO_CAJA_MOVIMIENTO.FECHA.desc())
            .all()
        )
        
        self.MOVIMIENTOS_CAJA.controls.clear()
        
        for mov in movimientos:
            self.MOVIMIENTOS_CAJA.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(
                            ICONOS.INGRESO if mov.TIPO == "ingreso" else ICONOS.EGRESO,
                            color=COLORES.EXITO if mov.TIPO == "ingreso" else COLORES.ERROR
                        ),
                        ft.Column([
                            ft.Text(mov.CONCEPTO, weight=ft.FontWeight.BOLD),
                            ft.Text(
                                mov.FECHA.strftime("%d/%m/%Y %H:%M"),
                                color=COLORES.TEXTO_SECUNDARIO,
                                size=12
                            ),
                        ], expand=True),
                        ft.Text(
                            f"S/ {mov.MONTO:.2f}",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=COLORES.EXITO if mov.TIPO == "ingreso" else COLORES.ERROR
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
    
    
    def _CERRAR_DIALOG(self):
        if self.PAGINA.dialog:
            self.PAGINA.dialog.open = False
            self.PAGINA.update()


    def _actualizar_contador_pendientes(self):
        sesion = OBTENER_SESION()
        try:
            count = (
                sesion.query(MODELO_PEDIDO)
                .filter_by(ESTADO='PENDIENTE')
                .count()
            )
            self.PEDIDOS_PENDIENTES_CHIP.label = ft.Text(str(count))
        finally:
            sesion.close()


    def _abrir_dialog_pendientes(self, e=None):
        dialog = ft.AlertDialog(
            title=ft.Text("Pedidos Pendientes"),
            content=ft.Container(content=self.PEDIDOS_PENDIENTES, width=600, height=400),
            actions=[ft.TextButton("Cerrar", on_click=lambda ev: self._CERRAR_DIALOG())]
        )
        self.PAGINA.dialog = dialog
        dialog.open = True
        self.PAGINA.update()


    def _registrar_pedido_tienda(self, e=None):
        NOMBRE = ft.TextField(label="Nombre cliente (opcional)")
        MONTO = ft.TextField(label="Monto (S/)", value="0.00", keyboard_type=ft.KeyboardType.NUMBER)

        def GUARDAR(e):
            try:
                monto = float(MONTO.value)
            except Exception:
                monto = 0.0
            sesion = OBTENER_SESION()
            try:
                pedido = MODELO_PEDIDO(
                    CLIENTE_ID=self.USUARIO_ID,
                    MONTO_TOTAL=int(round(monto * 100)),
                    ESTADO='PENDIENTE',
                )
                sesion.add(pedido)
                sesion.commit()
                sesion.refresh(pedido)
                # notify broker
                try:
                    from core.realtime.broker_notify import notify
                    sucursal_id = getattr(pedido, 'SUCURSAL_ID', None)
                    payload = {'type': 'pedido_creado', 'pedido_id': pedido.ID, 'nuevo_estado': 'PENDIENTE', 'cliente_id': self.USUARIO_ID}
                    if sucursal_id is not None:
                        payload['sucursal_id'] = sucursal_id
                    notify(payload)
                except Exception:
                    pass
            finally:
                sesion.close()

            self._CERRAR_DIALOG()
            self._CARGAR_PENDIENTES()
            self._CARGAR_DATOS()
            self.PAGINA.snack_bar = ft.SnackBar(content=ft.Text("Pedido registrado en tienda"), bgcolor=COLORES.EXITO)
            self.PAGINA.snack_bar.open = True
            self.PAGINA.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Registrar Pedido en Tienda"),
            content=ft.Column([NOMBRE, MONTO]),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda ev: self._CERRAR_DIALOG()),
                ft.Button("Registrar", on_click=GUARDAR),
            ]
        )

        self.PAGINA.dialog = dialog
        dialog.open = True
        self.PAGINA.update()

    def _aprobar(self, pedido_id: int):
        sesion = OBTENER_SESION()
        try:
            p = sesion.query(MODELO_PEDIDO).filter_by(ID=pedido_id).first()
            if p:
                p.ESTADO = 'EN_PREPARACION'
                sesion.commit()
                try:
                    notify({'type':'pedido_actualizado','pedido_id':pedido_id,'nuevo_estado':'EN_PREPARACION'})
                except Exception:
                    pass
        finally:
            sesion.close()
        self._CARGAR_PENDIENTES()

    def _alertar_cocina(self, pedido_id: int):
        try:
            notify({'type':'pedido_alerta_cocina','pedido_id':pedido_id})
        except Exception:
            pass

    def _pedir_refill(self, pedido_id: int):
        try:
            notify({'type':'pedido_refill','pedido_id':pedido_id})
        except Exception:
            pass

    def _on_realtime_pedido(self, payload: dict):
        # refresh pending list on incoming pedido events
        try:
            # Only refresh if the event is relevant to this sucursal (if provided)
            sucursal_evt = payload.get('sucursal_id')
            sesion = OBTENER_SESION()
            usuario = sesion.query(MODELO_USUARIO).filter_by(ID=self.USUARIO_ID).first()
            usuario_suc = getattr(usuario, 'SUCURSAL_ID', None) if usuario else None
            sesion.close()

            if sucursal_evt is None or usuario_suc is None or sucursal_evt == usuario_suc:
                self._CARGAR_PENDIENTES()
        except Exception:
            pass
    
    
    def CONSTRUIR(self) -> ft.Control:
        return ft.Column([
            ft.Row([ft.Text("Dashboard Atención", size=TAMANOS.TITULO, weight=ft.FontWeight.BOLD), ft.Container(expand=True), ft.Row([ft.Button("Registrar Pedido en Tienda", icon=ICONOS.PEDIDO, on_click=self._registrar_pedido_tienda, bgcolor=COLORES.PRIMARIO), ft.IconButton(icon=ICONOS.ALERTA, tooltip="Pedidos pendientes", on_click=self._abrir_dialog_pendientes), self.PEDIDOS_PENDIENTES_CHIP])]),
            
            ft.Container(
                content=ft.Column([
                    ft.Text("SALDO ACTUAL", size=14, color=COLORES.TEXTO_SECUNDARIO),
                    self.SALDO_ACTUAL,
                    ft.Row([
                        ft.Button(
                            "Abrir Caja",
                            icon=ICONOS.CAJA,
                            bgcolor=COLORES.EXITO,
                            on_click=lambda e: self._ABRIR_CAJA(),
                            visible=not self.CAJA_ACTUAL
                        ),
                        ft.Button(
                            "Cerrar Caja",
                            icon=ICONOS.CERRAR,
                            bgcolor=COLORES.ERROR,
                            on_click=lambda e: self._CERRAR_CAJA(),
                            visible=self.CAJA_ACTUAL is not None
                        ),
                    ]),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20,
                border=ft.Border.all(2, COLORES.PRIMARIO),
                border_radius=TAMANOS.RADIO_BORDE,
                bgcolor=COLORES.FONDO_TARJETA,
            ),
            
            ft.Divider(),
            
            ft.Tabs(
                content=ft.Column([
                    ft.TabBar(
                        tabs=[
                            ft.Tab(label="Pedidos Listos", icon=ICONOS.PEDIDO),
                            ft.Tab(label="Movimientos", icon=ICONOS.HISTORIAL),
                        ],
                    ),
                    ft.TabBarView(
                        controls=[
                            ft.Container(content=self.PEDIDOS_LISTOS, padding=10),
                            ft.Container(content=self.MOVIMIENTOS_CAJA, padding=10),
                        ],
                    ),
                ], expand=True),
                length=2,
                selected_index=0,
            )
        ], expand=True)
