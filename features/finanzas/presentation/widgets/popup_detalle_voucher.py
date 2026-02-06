"""
Popup de detalle de voucher (anidado dentro del popup de pedido)
"""
import flet as ft
from core.ui.safe_actions import safe_update
from typing import Optional
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_VOUCHER, MODELO_USUARIO
from core.ui.colores import PRIMARIO, EXITO, PELIGRO, ADVERTENCIA, FONDO_TARJETA


class PopupDetalleVoucher(ft.AlertDialog):
    """Popup anidado que muestra el detalle del voucher"""
    
    def __init__(self, voucher_id: int):
        super().__init__()
        
        self.voucher_id = voucher_id
        self.modal = True
        
        # Cargar datos
        self._cargar_datos()
    
    def _cargar_datos(self):
        """Cargar datos del voucher desde la BD"""
        try:
            sesion = OBTENER_SESION()
            
            voucher = sesion.query(MODELO_VOUCHER).filter_by(ID=self.voucher_id).first()
            if not voucher:
                self._mostrar_error("Voucher no encontrado")
                sesion.close()
                return
            
            # Obtener validador si existe
            validador = None
            if voucher.VALIDADO_POR:
                validador = sesion.query(MODELO_USUARIO).filter_by(ID=voucher.VALIDADO_POR).first()
            
            self._construir_ui(voucher, validador)
            
            sesion.close()
            
        except Exception as e:
            self._mostrar_error(f"Error al cargar voucher: {str(e)}")
    
    def _construir_ui(self, voucher, validador):
        """Construir interfaz del popup"""
        
        # Determinar estado
        if voucher.VALIDADO:
            estado = "APROBADO"
            color_estado = EXITO
            icono_estado = ft.icons.Icons.CHECK_CIRCLE
        elif voucher.RECHAZADO:
            estado = "RECHAZADO"
            color_estado = PELIGRO
            icono_estado = ft.icons.Icons.CANCEL
        else:
            estado = "PENDIENTE"
            color_estado = ADVERTENCIA
            icono_estado = ft.icons.Icons.PENDING
        
        # Header
        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(icono_estado, color=color_estado, size=32),
                    ft.Column(
                        controls=[
                            ft.Text(
                                f"Voucher #{voucher.ID}",
                                size=20,
                                weight=ft.FontWeight.BOLD
                            ),
                            ft.Container(
                                content=ft.Text(
                                    estado,
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE
                                ),
                                bgcolor=color_estado,
                                padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                                border_radius=10
                            )
                        ],
                        spacing=5
                    )
                ],
                spacing=15
            ),
            padding=20,
            bgcolor=FONDO_TARJETA
        )
        
        # Imagen del voucher
        imagen = ft.Image(
            src=voucher.IMAGEN_URL,
            width=400,
            height=300,
            fit=ft.BoxFit.CONTAIN,
            border_radius=8
        )
        
        contenedor_imagen = ft.Container(
            content=imagen,
            bgcolor=ft.Colors.BLACK12,
            border_radius=8,
            padding=10,
            alignment=ft.Alignment(0, 0)  # center
        )
        
        # Información del voucher
        monto_bs = voucher.MONTO / 100
        
        info = ft.Container(
            content=ft.Column(
                controls=[
                    self._crear_campo_info("Monto:", f"Bs {monto_bs:,.2f}"),
                    self._crear_campo_info("Método de Pago:", voucher.METODO_PAGO.upper()),
                    self._crear_campo_info(
                        "Fecha de Subida:",
                        voucher.FECHA_SUBIDA.strftime("%d/%m/%Y %H:%M")
                    ),
                    self._crear_campo_info(
                        "Fecha de Validación:",
                        voucher.FECHA_VALIDACION.strftime("%d/%m/%Y %H:%M") if voucher.FECHA_VALIDACION else "N/A"
                    ),
                    self._crear_campo_info(
                        "Validado por:",
                        validador.NOMBRE_USUARIO if validador else "N/A"
                    )
                ],
                spacing=10
            ),
            padding=15,
            bgcolor=FONDO_TARJETA,
            border_radius=8
        )
        
        # Motivo de rechazo (si aplica)
        controles_contenido = [contenedor_imagen, info]
        
        if voucher.RECHAZADO and voucher.MOTIVO_RECHAZO:
            motivo = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(ft.icons.Icons.INFO, color=PELIGRO, size=20),
                                ft.Text("Motivo de Rechazo:", weight=ft.FontWeight.BOLD, color=PELIGRO)
                            ],
                            spacing=10
                        ),
                        ft.Text(voucher.MOTIVO_RECHAZO, size=14)
                    ],
                    spacing=5
                ),
                padding=15,
                bgcolor=ft.Colors.ERROR_CONTAINER,
                border_radius=8,
                border=ft.Border.all(1, PELIGRO)
            )
            controles_contenido.append(motivo)
        
        # Construir contenido final
        self.title = header
        self.content = ft.Container(
            content=ft.Column(
                controls=controles_contenido,
                spacing=15,
                scroll=ft.ScrollMode.AUTO
            ),
            width=500,
            height=600
        )
        self.actions = [
            ft.TextButton("Cerrar", on_click=self._cerrar)
        ]
        self.actions_alignment = ft.MainAxisAlignment.CENTER
    
    def _crear_campo_info(self, label: str, valor: str) -> ft.Row:
        """Crear fila de información"""
        return ft.Row(
            controls=[
                ft.Text(label, size=14, color=ft.Colors.ON_SURFACE_VARIANT, weight=ft.FontWeight.W_500),
                ft.Text(valor, size=14, weight=ft.FontWeight.W_500)
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
    
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
    
    def _cerrar(self, e):
        """Cerrar el popup"""
        self.open = False
        if self.page:
            safe_update(self.page)
