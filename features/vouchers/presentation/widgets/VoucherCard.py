
import flet as ft
from typing import Callable, Optional

from core.Constantes import COLORES, TAMANOS, ICONOS
from .utils_vouchers import format_bs
from ...domain.entities.Voucher import Voucher

class VoucherCard(ft.Card):
    
    def __init__(
        self,
        voucher: Voucher,
        on_aprobar: Optional[Callable] = None,
        on_rechazar: Optional[Callable] = None,
        on_ver_imagen: Optional[Callable] = None,
    ):
        self._voucher = voucher
        self._on_aprobar = on_aprobar
        self._on_rechazar = on_rechazar
        self._on_ver_imagen = on_ver_imagen
        
        contenido = self._construir_contenido()
        
        super().__init__(
            content=contenido,
            elevation=2
        )
    
    def _construir_contenido(self):
        header = ft.Container(
            content=ft.Row([
                ft.Icon(ICONOS.VOUCHER, size=24, color=COLORES.PRIMARIO),
                ft.Text(
                    f"Voucher #{self._voucher.id}",
                    weight=ft.FontWeight.BOLD,
                    size=18,
                    color=COLORES.TEXTO
                ),
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Text(
                        format_bs(getattr(self._voucher, 'monto', 0)),
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=COLORES.TEXTO_BLANCO
                    ),
                    padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                    bgcolor=COLORES.EXITO,
                    border_radius=8,
                ),
            ]),
            padding=ft.Padding.only(bottom=12),
        )
        
        color_estado = {
            "PENDIENTE": COLORES.ADVERTENCIA,
            "APROBADO": COLORES.EXITO,
            "RECHAZADO": COLORES.PELIGRO,
        }.get(self._voucher.estado, COLORES.INFO)
        
        badge_estado = ft.Container(
            content=ft.Text(
                self._voucher.estado,
                size=12,
                weight=ft.FontWeight.BOLD,
                color=COLORES.TEXTO_BLANCO
            ),
            padding=ft.Padding.symmetric(horizontal=8, vertical=4),
            bgcolor=color_estado,
            border_radius=4,
        )
        
        info_grid = ft.Column([
            self._crear_fila_info("Método de pago", self._voucher.metodo_pago),
            self._crear_fila_info("Fecha", self._voucher.fecha_subida.strftime("%d/%m/%Y %H:%M")),
            self._crear_fila_info("Usuario ID", str(self._voucher.usuario_id)),
            self._crear_fila_info("Pedido ID", str(self._voucher.pedido_id)),
        ], spacing=8)
        
        acciones = []
        
        if self._on_ver_imagen and self._voucher.imagen_url:
            acciones.append(
                ft.Button(
                    "Ver Comprobante",
                    icon=ICONOS.IMAGEN,
                    bgcolor=COLORES.INFO,
                    color=COLORES.TEXTO_BLANCO,
                    on_click=lambda e: self._on_ver_imagen(self._voucher),
                )
            )
        
        if self._voucher.es_pendiente():
            if self._on_aprobar:
                acciones.append(
                    ft.Button(
                        "Aprobar",
                        icon=ICONOS.CONFIRMAR,
                        bgcolor=COLORES.EXITO,
                        color=COLORES.TEXTO_BLANCO,
                        on_click=lambda e: self._on_aprobar(self._voucher),
                    )
                )
            
            if self._on_rechazar:
                acciones.append(
                    ft.OutlinedButton(
                        "Rechazar",
                        icon=ICONOS.CANCELAR,
                        style=ft.ButtonStyle(
                            color=COLORES.PELIGRO,
                        ),
                        on_click=lambda e: self._on_rechazar(self._voucher),
                    )
                )
        
        return ft.Container(
            content=ft.Column([
                header,
                ft.Divider(height=1, color=COLORES.BORDE),
                ft.Container(
                    content=ft.Row([
                        badge_estado,
                        ft.Container(expand=True),
                    ]),
                    padding=ft.Padding.symmetric(vertical=8),
                ),
                info_grid,
                ft.Row(acciones, spacing=10, wrap=True) if acciones else ft.Container(),
            ], spacing=12),
            padding=TAMANOS.PADDING_MD,
        )
    
    def _crear_fila_info(self, etiqueta: str, valor: str) -> ft.Row:
        return ft.Row([
            ft.Text(
                f"{etiqueta}:",
                size=13,
                color=COLORES.TEXTO_SECUNDARIO,
                weight=ft.FontWeight.W_500,
            ),
            ft.Text(
                valor,
                size=13,
                color=COLORES.TEXTO,
                weight=ft.FontWeight.BOLD,
            ),
        ], spacing=8)
