import flet as ft
from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION,
    MODELO_PEDIDO,
    MODELO_SUCURSAL,
)
from datetime import datetime, timezone

class PaginaCocina(ft.Column):
    def __init__(self, PAGINA: ft.Page, USUARIO_ID: int):
        super().__init__()
        self._PAGINA = PAGINA
        self._USUARIO_ID = USUARIO_ID
        self._SUCURSAL_SELECCIONADA = None
        self._LISTA_CONTROLES = ft.Column()
        self._CONSTRUIR()

    def _CONSTRUIR(self):
        HEADER = ft.Text("Dashboard Cocina", size=24, weight=ft.FontWeight.BOLD)

        self._DROPDOWN_SUCURSAL = ft.Dropdown(
            label="Seleccionar Sucursal", on_select=self._CAMBIAR_SUCURSAL
        )

        self._LISTA_CONTROLES = ft.Column(spacing=10)

        self.controls = [
            ft.Container(
                content=ft.Column(
                    [
                        HEADER,
                        self._DROPDOWN_SUCURSAL,
                        ft.Text(
                            "Pedidos para preparar", size=18, weight=ft.FontWeight.BOLD
                        ),
                        self._LISTA_CONTROLES,
                    ]
                ),
                padding=20,
                expand=True,
            )
        ]
        self.expand = True
        self._CARGAR_SUCURSALES()

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
        self._REFRESCAR()

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
                MODELO_PEDIDO.ESTADO.in_(["confirmado", "preparado"]),
                MODELO_PEDIDO.FECHA_CREACION >= hoy,
            )
            .order_by(MODELO_PEDIDO.FECHA_CREACION.asc())
            .all()
        )

        self._LISTA_CONTROLES.controls.clear()
        for p in pedidos:
            producto = sesion.query(MODELO_PRODUCTO).filter_by(ID=p.PRODUCTO_ID).first()
            nombre_prod = producto.NOMBRE if producto else "Producto desconocido"
            estado_color = (
                ft.Colors.ORANGE_400 if p.ESTADO == "confirmado" else ft.Colors.BLUE_600
            )
            fila = ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(f"Pedido #{p.ID}", weight=ft.FontWeight.BOLD),
                            ft.Text(f"{nombre_prod} x{p.CANTIDAD}"),
                            ft.Text(f"Estado: {p.ESTADO}", color=estado_color),
                        ]
                    ),
                    ft.Column(
                        [
                            ft.Button(
                                "Marcar Listo",
                                on_click=lambda e, ped=p: asyncio.create_task(
                                    self._MARCAR_LISTO(ped)
                                ),
                            ),
                            ft.Button(
                                "Prioridad Alta",
                                on_click=lambda e, ped=p: asyncio.create_task(
                                    self._NOTIFICAR_ATENCION(ped, True)
                                ),
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

    async def _MARCAR_LISTO(self, PEDIDO):
        sesion = OBTENER_SESION()
        PEDIDO.ESTADO = "preparado"
        sesion.commit()
        from core.websocket.ManejadorConexion import ManejadorConexion

        manejador = ManejadorConexion()
        try:
            await manejador.BROADCAST(
                {
                    "tipo": "pedido_listo",
                    "pedido_id": PEDIDO.ID,
                    "sucursal_id": PEDIDO.SUCURSAL_ID,
                }
            )
        except Exception:
            pass
        self._REFRESCAR()

    async def _NOTIFICAR_ATENCION(self, PEDIDO, PRIORIDAD_ALTA: bool):
        from core.websocket.ManejadorConexion import ManejadorConexion

        manejador = ManejadorConexion()
        try:
            await manejador.BROADCAST(
                {
                    "tipo": "pedido_prioridad",
                    "pedido_id": PEDIDO.ID,
                    "sucursal_id": PEDIDO.SUCURSAL_ID,
                    "prioridad_alta": PRIORIDAD_ALTA,
                }
            )
        except Exception:
            pass
