import flet as ft
from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION,
    MODELO_PEDIDO,
    MODELO_PRODUCTO,
)
from datetime import datetime


class PaginaHistorialPedidos(ft.Column):
    def __init__(self, PAGINA: ft.Page, USUARIO_ID: int):
        super().__init__()
        self._PAGINA = PAGINA
        self._USUARIO_ID = USUARIO_ID
        self._LISTA = ft.Column()
        self._CONSTRUIR()

    def _CONSTRUIR(self):
        HEADER = ft.Text("Historial de pedidos", size=24, weight=ft.FontWeight.BOLD)
        self.controls = [
            ft.Container(
                content=ft.Column([HEADER, self._LISTA], spacing=10),
                padding=20,
                expand=True,
            )
        ]
        self.expand = True
        self._REFRESCAR()

    def _REFRESCAR(self):
        import asyncio

        asyncio.create_task(self._CARGAR_PEDIDOS())

    async def _CARGAR_PEDIDOS(self):
        sesion = OBTENER_SESION()
        pedidos = (
            sesion.query(MODELO_PEDIDO)
            .filter_by(CLIENTE_ID=self._USUARIO_ID)
            .order_by(MODELO_PEDIDO.FECHA_CREACION.desc())
            .limit(50)
            .all()
        )
        self._LISTA.controls.clear()
        for p in pedidos:
            prod = sesion.query(MODELO_PRODUCTO).filter_by(ID=p.PRODUCTO_ID).first()
            nombre = prod.NOMBRE if prod else "Producto"
            fecha = (
                p.FECHA_CREACION.strftime("%d/%m/%Y %H:%M") if p.FECHA_CREACION else ""
            )
            tarjeta = ft.Container(
                content=ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(f"Pedido #{p.ID}", weight=ft.FontWeight.BOLD),
                                ft.Text(nombre),
                                ft.Text(f"Total: {p.MONTO_TOTAL} Bs"),
                            ]
                        ),
                        ft.Column([ft.Text(p.ESTADO), ft.Text(fecha)]),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                padding=12,
                border=ft.border.all(1, ft.Colors.GREY_200),
                border_radius=8,
            )
            self._LISTA.controls.append(tarjeta)
        if getattr(self, "page", None):
            self.update()
