import flet as ft
from datetime import datetime

from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION,
    MODELO_PEDIDO,
    MODELO_CAJA,
    MODELO_CAJA_MOVIMIENTO,
)
from core.constantes import COLORES, TAMANOS, ICONOS
from core.decoradores.DecoradorVistas import REQUIERE_ROL
from core.websocket.GestorNotificaciones import GestorNotificaciones


@REQUIERE_ROL("ATENCION", "ADMIN", "SUPERADMIN")
class PaginaDashboardAtencion:
    
    def __init__(self, PAGINA: ft.Page, USUARIO_ID: int):
        self.PAGINA = PAGINA
        self.USUARIO_ID = USUARIO_ID
        self.GESTOR_NOTIFICACIONES = GestorNotificaciones()
        
        self.PEDIDOS_LISTOS = ft.ListView(spacing=10, expand=True)
        self.MOVIMIENTOS_CAJA = ft.ListView(spacing=10, expand=True)
        self.CAJA_ACTUAL = None
        self.SALDO_ACTUAL = ft.Text("S/ 0.00", size=24, weight=ft.FontWeight.BOLD, color=COLORES.EXITO)
        
        self._CARGAR_DATOS()
    
    
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
    
    
    def _CREAR_TARJETA_PEDIDO(self, PEDIDO):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ICONOS.PEDIDO, color=COLORES.PRIMARIO),
                    ft.Text(f"Pedido #{PEDIDO.ID}", weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.Text(f"S/ {PEDIDO.TOTAL:.2f}", size=18, weight=ft.FontWeight.BOLD, color=COLORES.EXITO),
                ]),
                ft.Text(
                    f"Hora: {PEDIDO.FECHA_PEDIDO.strftime('%H:%M')}",
                    color=COLORES.TEXTO_SECUNDARIO,
                    size=12
                ),
                ft.ElevatedButton(
                    "Servir y Cobrar",
                    icon=ICONOS.CONFIRMAR,
                    bgcolor=COLORES.EXITO,
                    on_click=lambda e, p=PEDIDO: self._SERVIR_PEDIDO(p),
                ),
            ], spacing=10),
            padding=15,
            border=ft.border.all(1, COLORES.BORDE),
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
                MONTO=pedido.TOTAL,
                CONCEPTO=f"Venta pedido #{pedido.ID}",
            )
            
            sesion.add(movimiento)
            
            caja = sesion.query(MODELO_CAJA).filter_by(ID=self.CAJA_ACTUAL.ID).first()
            if caja:
                caja.SALDO_ACTUAL += pedido.TOTAL
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
                ft.ElevatedButton("Abrir", on_click=CREAR_CAJA),
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
            caja.FECHA_CIERRE = datetime.utcnow()
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
            ft.Text("Dashboard Atención", size=TAMANOS.TITULO, weight=ft.FontWeight.BOLD),
            
            ft.Container(
                content=ft.Column([
                    ft.Text("SALDO ACTUAL", size=14, color=COLORES.TEXTO_SECUNDARIO),
                    self.SALDO_ACTUAL,
                    ft.Row([
                        ft.ElevatedButton(
                            "Abrir Caja",
                            icon=ICONOS.CAJA,
                            bgcolor=COLORES.EXITO,
                            on_click=lambda e: self._ABRIR_CAJA(),
                            visible=not self.CAJA_ACTUAL
                        ),
                        ft.ElevatedButton(
                            "Cerrar Caja",
                            icon=ICONOS.CERRAR,
                            bgcolor=COLORES.ERROR,
                            on_click=lambda e: self._CERRAR_CAJA(),
                            visible=self.CAJA_ACTUAL is not None
                        ),
                    ]),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20,
                border=ft.border.all(2, COLORES.PRIMARIO),
                border_radius=TAMANOS.RADIO_BORDE,
                bgcolor=COLORES.FONDO_TARJETA,
            ),
            
            ft.Divider(),
            
            ft.Tabs(
                selected_index=0,
                tabs=[
                    ft.Tab(
                        text="Pedidos Listos",
                        icon=ICONOS.PEDIDO,
                        content=ft.Container(
                            content=self.PEDIDOS_LISTOS,
                            padding=10,
                        )
                    ),
                    ft.Tab(
                        text="Movimientos",
                        icon=ICONOS.HISTORIAL,
                        content=ft.Container(
                            content=self.MOVIMIENTOS_CAJA,
                            padding=10,
                        )
                    ),
                ],
                expand=True,
            )
        ], expand=True)
