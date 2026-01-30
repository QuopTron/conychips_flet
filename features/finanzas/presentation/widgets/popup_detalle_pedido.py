"""
Popup de detalle de pedido con tabla de productos
"""
import flet as ft
from core.ui.safe_actions import safe_update
from typing import Optional, Callable
from datetime import datetime
from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION, MODELO_PEDIDO, MODELO_DETALLE_PEDIDO,
    MODELO_PRODUCTO, MODELO_VOUCHER, MODELO_USUARIO, MODELO_OFERTA
)
from core.ui.colores import PRIMARIO, EXITO, PELIGRO, ADVERTENCIA, FONDO_TARJETA


class PopupDetallePedido(ft.AlertDialog):
    """Popup que muestra el detalle completo de un pedido"""
    
    def __init__(
        self, 
        pedido_id: int,
        on_ver_voucher: Optional[Callable[[int], None]] = None
    ):
        super().__init__()
        
        self.pedido_id = pedido_id
        self.on_ver_voucher = on_ver_voucher
        self.voucher_id = None
        
        # Configuración del diálogo
        self.modal = True
        
        # Cargar datos
        self._cargar_datos()
    
    def _cargar_datos(self):
        """Cargar datos del pedido desde la BD"""
        try:
            sesion = OBTENER_SESION()
            
            # Obtener pedido
            pedido = sesion.query(MODELO_PEDIDO).filter_by(ID=self.pedido_id).first()
            if not pedido:
                self._mostrar_error("Pedido no encontrado")
                sesion.close()
                return
            
            # Obtener cliente
            cliente = sesion.query(MODELO_USUARIO).filter_by(ID=pedido.CLIENTE_ID).first()
            nombre_cliente = cliente.NOMBRE_USUARIO if cliente else "Cliente desconocido"
            
            # Obtener detalles del pedido
            detalles = sesion.query(MODELO_DETALLE_PEDIDO).filter_by(PEDIDO_ID=self.pedido_id).all()
            
            # Obtener voucher si existe
            voucher = sesion.query(MODELO_VOUCHER).filter_by(PEDIDO_ID=self.pedido_id).first()
            if voucher:
                self.voucher_id = voucher.ID
            
            # Construir UI
            self._construir_ui(pedido, nombre_cliente, detalles, voucher)
            
            sesion.close()
            
        except Exception as e:
            self._mostrar_error(f"Error al cargar pedido: {str(e)}")
    
    def _construir_ui(self, pedido, nombre_cliente: str, detalles, voucher):
        """Construir interfaz del popup"""
        
        # Color según estado
        color_estado = self._get_color_estado(pedido.ESTADO)
        
        # Header
        header = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(
                                f"Pedido #{pedido.ID:05d}",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=PRIMARIO
                            ),
                            ft.Container(
                                content=ft.Text(
                                    pedido.ESTADO,
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE
                                ),
                                bgcolor=color_estado,
                                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                                border_radius=12
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Divider(height=1),
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text("Cliente:", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                                    ft.Text(nombre_cliente, size=16, weight=ft.FontWeight.W_500)
                                ],
                                spacing=2
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text("Fecha:", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                                    ft.Text(
                                        pedido.FECHA_CREACION.strftime("%d/%m/%Y %H:%M"),
                                        size=16,
                                        weight=ft.FontWeight.W_500
                                    )
                                ],
                                spacing=2
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text("Tipo:", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                                    ft.Text(pedido.TIPO.upper(), size=16, weight=ft.FontWeight.W_500)
                                ],
                                spacing=2
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_AROUND
                    )
                ],
                spacing=10
            ),
            padding=20,
            bgcolor=FONDO_TARJETA
        )
        
        # Tabla de productos
        tabla_productos = self._crear_tabla_productos(detalles)
        
        # Total
        monto_total_bs = pedido.MONTO_TOTAL / 100
        resumen = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text("TOTAL:", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text(
                        f"Bs {monto_total_bs:,.2f}",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=PRIMARIO
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=20,
            bgcolor=FONDO_TARJETA,
            border_radius=8
        )
        
        # Botón ver voucher (si existe)
        acciones = []
        if voucher:
            estado_voucher = "APROBADO" if voucher.VALIDADO else ("RECHAZADO" if voucher.RECHAZADO else "PENDIENTE")
            color_voucher = EXITO if voucher.VALIDADO else (PELIGRO if voucher.RECHAZADO else ADVERTENCIA)
            
            btn_voucher = ft.Button(
                f"Ver Voucher ({estado_voucher})",
                icon=ft.icons.Icons.RECEIPT,
                bgcolor=color_voucher,
                color=ft.Colors.WHITE,
                on_click=self._abrir_voucher
            )
            acciones.append(btn_voucher)
        
        btn_cerrar = ft.TextButton("Cerrar", on_click=self._cerrar)
        acciones.append(btn_cerrar)
        
        # Construir contenido final
        self.title = header
        self.content = ft.Container(
            content=ft.Column(
                controls=[
                    tabla_productos,
                    ft.Divider(height=20),
                    resumen
                ],
                spacing=0,
                scroll=ft.ScrollMode.AUTO
            ),
            width=700,
            height=400
        )
        self.actions = acciones
        self.actions_alignment = ft.MainAxisAlignment.END
    
    def _crear_tabla_productos(self, detalles) -> ft.Container:
        """Crear tabla de productos del pedido"""
        
        filas = []
        sesion = OBTENER_SESION()
        
        for detalle in detalles:
            producto = sesion.query(MODELO_PRODUCTO).filter_by(ID=detalle.PRODUCTO_ID).first()
            nombre_producto = producto.NOMBRE if producto else "Producto desconocido"
            
            # Verificar si tiene oferta
            oferta = sesion.query(MODELO_OFERTA).filter_by(
                PRODUCTO_ID=detalle.PRODUCTO_ID,
                ACTIVA=True
            ).first()
            
            precio_unitario = detalle.PRECIO_UNITARIO / 100
            subtotal = (detalle.PRECIO_UNITARIO * detalle.CANTIDAD) / 100
            
            # Agregar icono de oferta si aplica
            nombre_col = [ft.Text(nombre_producto)]
            if oferta:
                nombre_col.append(ft.Icon(ft.icons.Icons.LOYALTY, color=PRIMARIO, size=16))
            
            filas.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Row(nombre_col, spacing=5)),
                        ft.DataCell(ft.Text(str(detalle.CANTIDAD), text_align=ft.TextAlign.CENTER)),
                        ft.DataCell(ft.Text(f"Bs {precio_unitario:.2f}", text_align=ft.TextAlign.RIGHT)),
                        ft.DataCell(ft.Text(f"Bs {subtotal:.2f}", text_align=ft.TextAlign.RIGHT, weight=ft.FontWeight.W_500))
                    ]
                )
            )
        
        sesion.close()
        
        tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Producto", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Cant.", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Precio Unit.", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Subtotal", weight=ft.FontWeight.BOLD))
            ],
            rows=filas,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=8,
            horizontal_lines=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT)
        )
        
        return ft.Container(
            content=ft.Column([tabla], scroll=ft.ScrollMode.AUTO),
            padding=10,
            bgcolor=FONDO_TARJETA,
            border_radius=8
        )
    
    def _get_color_estado(self, estado: str) -> str:
        """Obtener color según estado del pedido"""
        colores = {
            "COMPLETADO": EXITO,
            "PENDIENTE": ADVERTENCIA,
            "CANCELADO": PELIGRO
        }
        return colores.get(estado.upper(), ft.Colors.ON_SURFACE)
    
    def _mostrar_error(self, mensaje: str):
        """Mostrar error en el popup"""
        self.title = ft.Text("Error", size=20, weight=ft.FontWeight.BOLD, color=PELIGRO)
        self.content = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.icons.Icons.ERROR_OUTLINE, color=PELIGRO, size=48),
                    ft.Text(mensaje, size=16, text_align=ft.TextAlign.CENTER)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            ),
            width=400,
            height=150,
            padding=20
        )
        self.actions = [ft.TextButton("Cerrar", on_click=self._cerrar)]
    
    def _abrir_voucher(self, e):
        """Abrir popup de voucher anidado"""
        if self.on_ver_voucher and self.voucher_id:
            self.on_ver_voucher(self.voucher_id)
    
    def _cerrar(self, e):
        """Cerrar el popup"""
        self.open = False
        if self.page:
            safe_update(self.page)
