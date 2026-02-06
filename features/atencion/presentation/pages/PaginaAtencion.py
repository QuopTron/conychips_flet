import flet as ft
from typing import Optional
from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION,
    MODELO_PEDIDO,
    MODELO_CAJA,
    MODELO_SUCURSAL,
)
from datetime import datetime, timezone

class PaginaAtencion(ft.Column):
    def __init__(self, PAGINA: ft.Page, USUARIO_ID: int):
        super().__init__()
        self._PAGINA = PAGINA
        self._USUARIO_ID = USUARIO_ID
        self._SUCURSAL_SELECCIONADA = None
        self._CAJA_ACTIVA = None
        self._LISTA_CONTROLES = ft.Column()
        self._CONSTRUIR()

    def _CONSTRUIR(self):
        HEADER = ft.Text("Dashboard Atención", size=24, weight=ft.FontWeight.BOLD)

        self._DROPDOWN_SUCURSAL = ft.Dropdown(
            label="Seleccionar Sucursal", on_select=self._CAMBIAR_SUCURSAL
        )

        self._TEXTO_CAJA = ft.Text("Caja cerrada", size=16)
        self._BOTON_CAJA = ft.Button("Abrir Caja", on_click=self._TOGGLE_CAJA)

        self._LISTA_CONTROLES = ft.Column(spacing=10)

        self.controls = [
            ft.Container(
                content=ft.Column(
                    [
                        HEADER,
                        self._DROPDOWN_SUCURSAL,
                        ft.Row(
                            [self._TEXTO_CAJA, self._BOTON_CAJA],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Text("Pedidos del día", size=18, weight=ft.FontWeight.BOLD),
                        self._LISTA_CONTROLES,
                    ]
                ),
                padding=20,
                expand=True,
            )
        ]
        self.expand = True
        self._CARGAR_SUCURSALES()
        import asyncio

        asyncio.create_task(self._INICIALIZAR_WEBSOCKET())

    async def _INICIALIZAR_WEBSOCKET(self):
        from core.websocket.ManejadorConexion import ManejadorConexion

        manejador = ManejadorConexion()
        while True:
            cliente = manejador.OBTENER_CONEXION(self._USUARIO_ID)
            if cliente:

                async def _on_msg(mensaje):
                    try:
                        tipo = mensaje.get("tipo")
                        if tipo in (
                            "nuevo_pedido",
                            "pedido_confirmado",
                            "pedido_pagado",
                        ):
                            if (
                                mensaje.get("sucursal_id")
                                == self._SUCURSAL_SELECCIONADA
                            ):
                                self._REFRESCAR()
                    except Exception:
                        pass

                cliente.REGISTRAR_CALLBACK_MENSAJE(_on_msg)
                break
            await asyncio.sleep(1)

    def _CARGAR_SUCURSALES(self):
        sesion = OBTENER_SESION()
        sucursales = sesion.query(MODELO_SUCURSAL).filter_by(ACTIVA=True).all()
        opciones = [
            ft.dropdown.Option(key=str(s.ID), text=s.NOMBRE) for s in sucursales
        ]
        self._DROPDOWN_SUCURSAL.options = opciones
        if opciones:
            self._DROPDOWN_SUCURSAL.value = opciones[0].key
            self._SUCURSAL_SELECCIONADA = int(opciones[0].key)
        self._REFRESCAR()

    def _CAMBIAR_SUCURSAL(self, e):
        self._SUCURSAL_SELECCIONADA = int(e.control.value) if e.control.value else None
        self._VERIFICAR_CAJA()
        self._REFRESCAR()

    def _VERIFICAR_CAJA(self):
        if not self._SUCURSAL_SELECCIONADA:
            return
        sesion = OBTENER_SESION()
        caja = (
            sesion.query(MODELO_CAJA)
            .filter_by(
                USUARIO_ID=self._USUARIO_ID,
                SUCURSAL_ID=self._SUCURSAL_SELECCIONADA,
                ACTIVA=True,
            )
            .first()
        )
        self._CAJA_ACTIVA = caja
        if caja:
            self._TEXTO_CAJA.value = (
                f"Caja abierta - Monto inicial: {caja.MONTO_INICIAL} Bs"
            )
            self._BOTON_CAJA.text = "Cerrar Caja"
        else:
            self._TEXTO_CAJA.value = "Caja cerrada"
            self._BOTON_CAJA.text = "Abrir Caja"
        if getattr(self, "page", None):
            self.update()

    def _TOGGLE_CAJA(self, e):
        import asyncio

        asyncio.create_task(self._MANEJAR_CAJA())

    async def _MANEJAR_CAJA(self):
        if not self._SUCURSAL_SELECCIONADA:
            return
        sesion = OBTENER_SESION()
        if self._CAJA_ACTIVA:
            caja = sesion.query(MODELO_CAJA).filter_by(ID=self._CAJA_ACTIVA.ID).first()
            if caja is None:
                return
            caja.FECHA_CIERRE = datetime.now(timezone.utc)
            caja.ACTIVA = False
            pedidos_hoy = (
                sesion.query(MODELO_PEDIDO)
                .filter(
                    MODELO_PEDIDO.SUCURSAL_ID == self._SUCURSAL_SELECCIONADA,
                    MODELO_PEDIDO.FECHA_CREACION >= caja.FECHA_APERTURA,
                    MODELO_PEDIDO.ESTADO == "confirmado",
                )
                .all()
            )
            ganancias = sum(p.MONTO_TOTAL for p in pedidos_hoy)
            caja.GANANCIAS = ganancias
            sesion.commit()
            self._CAJA_ACTIVA = None
            self._TEXTO_CAJA.value = f"Caja cerrada - Ganancias: {ganancias} Bs"
            self._BOTON_CAJA.text = "Abrir Caja"
        else:
            monto_inicial = 0
            caja = MODELO_CAJA(
                USUARIO_ID=self._USUARIO_ID,
                SUCURSAL_ID=self._SUCURSAL_SELECCIONADA,
                MONTO_INICIAL=monto_inicial,
                ACTIVA=True,
            )
            sesion.add(caja)
            sesion.commit()
            self._CAJA_ACTIVA = caja
            self._TEXTO_CAJA.value = f"Caja abierta - Monto inicial: {monto_inicial} Bs"
            self._BOTON_CAJA.text = "Cerrar Caja"
        if getattr(self, "page", None):
            self.update()

    def _REFRESCAR(self):
        import asyncio

        asyncio.create_task(self._CARGAR_PEDIDOS())

    async def _CARGAR_PEDIDOS(self):
        if not self._SUCURSAL_SELECCIONADA:
            return
        sesion = OBTENER_SESION()
        hoy = datetime.now(timezone.utc).date()
        pedidos = (
            sesion.query(MODELO_PEDIDO)
            .filter(
                MODELO_PEDIDO.SUCURSAL_ID == self._SUCURSAL_SELECCIONADA,
                MODELO_PEDIDO.FECHA_CREACION >= hoy,
            )
            .order_by(MODELO_PEDIDO.FECHA_CREACION.desc())
            .all()
        )

        self._LISTA_CONTROLES.controls.clear()
        for p in pedidos:
            producto = sesion.query(MODELO_PRODUCTO).filter_by(ID=p.PRODUCTO_ID).first()
            nombre_prod = producto.NOMBRE if producto else "Producto desconocido"
            estado_color = (
                ft.Colors.GREEN_600
                if p.ESTADO == "confirmado"
                else (
                    ft.Colors.ORANGE_400
                    if p.ESTADO == "preparado"
                    else ft.Colors.RED_600
                )
            )
            fila = ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(f"Pedido #{p.ID}", weight=ft.FontWeight.BOLD),
                            ft.Text(f"{nombre_prod} x{p.CANTIDAD}"),
                            ft.Text(f"Total: {p.MONTO_TOTAL} Bs"),
                            ft.Text(f"Estado: {p.ESTADO}", color=estado_color),
                        ]
                    ),
                    ft.Column(
                        [
                            ft.Button(
                                "Confirmar Pago",
                                on_click=lambda e, ped=p: asyncio.create_task(
                                    self._CONFIRMAR_PAGO(ped)
                                ),
                            ),
                            ft.Button(
                                "Imprimir Recibo",
                                on_click=lambda e, ped=p: self._IMPRIMIR_RECIBO(ped),
                            ),
                        ]
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )
            self._LISTA_CONTROLES.controls.append(
                ft.Container(
                    content=fila,
                    padding=10,
                    border=ft.Border.all(1, ft.Colors.GREY_200),
                    border_radius=8,
                )
            )
        if getattr(self, "page", None):
            self.update()

    async def _CONFIRMAR_PAGO(self, PEDIDO):
        sesion = OBTENER_SESION()
        PEDIDO.ESTADO = "confirmado"
        PEDIDO.FECHA_CONFIRMACION = datetime.now(timezone.utc)
        sesion.commit()
        from core.websocket.ManejadorConexion import ManejadorConexion

        manejador = ManejadorConexion()
        try:
            await manejador.BROADCAST(
                {
                    "tipo": "pedido_confirmado",
                    "pedido_id": PEDIDO.ID,
                    "sucursal_id": PEDIDO.SUCURSAL_ID,
                }
            )
        except Exception:
            pass
        self._REFRESCAR()

    def _IMPRIMIR_RECIBO(self, PEDIDO):
        recibo = f
        print(recibo)
