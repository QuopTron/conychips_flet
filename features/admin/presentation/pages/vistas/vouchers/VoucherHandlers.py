"""Handlers de eventos y diálogos para vouchers usando overlay"""
import flet as ft
import sys

from core.Constantes import COLORES, ICONOS
from core.ui import alignments
from core.ui.colores import PRIMARIO, SECUNDARIO, EXITO, PELIGRO, ADVERTENCIA
from features.vouchers.presentation.widgets.utils_vouchers import format_bs
from features.vouchers.presentation.bloc import (
    VOUCHERS_BLOC,
    AprobarVoucherEvento,
    RechazarVoucherEvento,
)
from core.decoradores.DecoradorPermisosUI import requiere_rol_ui
from core.Constantes import ROLES
from core.ui.safe_actions import safe_update
from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION,
    MODELO_DETALLE_PEDIDO,
    MODELO_PRODUCTO,
    MODELO_PEDIDO,
)


class VoucherHandlers:
    """Manejadores de eventos para las acciones de vouchers"""
    
    def __init__(self, pagina, usuario):
        """
        Args:
            pagina: Instancia de ft.Page
            usuario: Usuario actual logueado
        """
        self.pagina = pagina
        self.usuario = usuario
    
    @requiere_rol_ui(ROLES.SUPERADMIN, ROLES.ADMIN)
    def aprobar_click(self, e):
        """Handler para el botón Aprobar voucher"""
        voucher = e.control.data
        boton_original = e.control
        print(f"[DEBUG] _APROBAR_VOUCHER_CLICK (pre-confirm) para voucher {voucher.id}")

        def cancelar_confirm(ev):
            if overlay_confirm in self.pagina.overlay:
                self.pagina.overlay.remove(overlay_confirm)
            safe_update(self.pagina)

        def confirmar_aprobar(ev):
            # Cerrar overlay
            if overlay_confirm in self.pagina.overlay:
                self.pagina.overlay.remove(overlay_confirm)

            # Animación y bloqueo del botón original
            try:
                boton_original.disabled = True
                boton_original.text = "✓ Aprobando..."
                boton_original.icon = ft.icons.Icons.CHECK_CIRCLE_OUTLINE
                boton_original.style = ft.ButtonStyle(color=COLORES.EXITO)
            except Exception:
                pass

            # Animar el card si es posible
            try:
                card = boton_original.parent.parent.parent
                if hasattr(card, 'opacity'):
                    card.opacity = 0.7
                    card.animate_opacity = ft.Animation(300, ft.AnimationCurve.EASE_OUT)
            except Exception:
                pass

            safe_update(self.pagina)

            VOUCHERS_BLOC.AGREGAR_EVENTO(
                AprobarVoucherEvento(
                    voucher_id=voucher.id,
                    validador_id=self.usuario.ID
                )
            )
            print(f"[DEBUG] Evento AprobarVoucherEvento emitido (post-confirm)")
            # Actualización optimista: eliminar la card localmente para respuesta instantánea
            try:
                card = boton_original.parent.parent.parent
                parent = card.control if hasattr(card, 'control') else None
                # Buscar lista de controls del padre y remover la card
                if hasattr(card, 'parent') and card.parent and hasattr(card.parent, 'controls'):
                    try:
                        card.parent.controls.remove(card)
                    except Exception:
                        pass
                safe_update(self.pagina)
            except Exception:
                pass

        # Contenido compacto con características clave del voucher
        detalle_col = ft.Column([
            ft.Row([ft.Text("Monto:", size=13, color=ft.Colors.BLACK54), ft.Text(format_bs(voucher.monto), size=13, weight=ft.FontWeight.BOLD)]),
            ft.Row([ft.Text("Método:", size=13, color=ft.Colors.BLACK54), ft.Text(voucher.metodo_pago or "-", size=13, weight=ft.FontWeight.BOLD)]),
            ft.Row([ft.Text("Usuario ID:", size=13, color=ft.Colors.BLACK54), ft.Text(str(voucher.usuario_id), size=13, weight=ft.FontWeight.BOLD)]),
            ft.Row([ft.Text("Fecha:", size=13, color=ft.Colors.BLACK54), ft.Text(voucher.fecha_subida.strftime("%d/%m/%Y %H:%M") if voucher.fecha_subida else "-", size=13, weight=ft.FontWeight.BOLD)]),
        ], spacing=8)

        dialogo_content = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.icons.Icons.CHECK_CIRCLE, color=EXITO, size=28),
                    ft.Text("Confirmar aprobación", size=20, weight=ft.FontWeight.BOLD),
                ], spacing=12),
                ft.Divider(height=1, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
                ft.Container(content=detalle_col, padding=ft.padding.only(top=12, bottom=6)),
                ft.Row([
                    ft.TextButton("Cancelar", on_click=cancelar_confirm, style=ft.ButtonStyle(color=ft.Colors.BLACK54)),
                    ft.Button("Aprobar", on_click=confirmar_aprobar, bgcolor=EXITO, color=ft.Colors.WHITE),
                ], spacing=10, alignment=ft.MainAxisAlignment.END),
            ], spacing=12, tight=True),
            padding=18,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            width=420,
            shadow=ft.BoxShadow(blur_radius=30, color=ft.Colors.with_opacity(0.25, ft.Colors.BLACK)),
        )

        overlay_confirm = ft.Container(content=dialogo_content, alignment=ft.Alignment(0, 0), bgcolor="#80000000", expand=True)
        self.pagina.overlay.append(overlay_confirm)
        safe_update(self.pagina)
        print(f"[DEBUG] Overlay de confirmación de aprobación mostrado")
    
    @requiere_rol_ui(ROLES.SUPERADMIN, ROLES.ADMIN)
    def rechazar_click(self, e):
        """Handler para el botón Rechazar voucher usando overlay.
        Muestra una primera confirmación '¿Está seguro?' y si se confirma
        abre el diálogo de motivo (segunda confirmación).
        """
        voucher = e.control.data
        boton_original = e.control
        print(f"[DEBUG] RECHAZAR CLICK usando OVERLAY - Voucher #{voucher.id}")

        def cancelar_primera(e2):
            if overlay_confirmacion in self.pagina.overlay:
                self.pagina.overlay.remove(overlay_confirmacion)
            safe_update(self.pagina)

        def confirmar_primera(e2):
            if overlay_confirmacion in self.pagina.overlay:
                self.pagina.overlay.remove(overlay_confirmacion)
            self._mostrar_dialogo_rechazo_overlay(voucher, boton_original)

        # Diálogo de confirmación compacto y bonito
        dialogo_content = ft.Container(
            content=ft.Column([
                # Header con icono y título
                ft.Row([
                    ft.Icon(ft.icons.Icons.WARNING_ROUNDED, color=ADVERTENCIA, size=32),
                    ft.Text(
                        "Confirmar rechazo", 
                        size=22, 
                        weight=ft.FontWeight.BOLD,
                        color=PELIGRO,
                    ),
                ], spacing=12),
                
                ft.Divider(height=1, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
                
                # Mensaje centrado
                ft.Container(
                    content=ft.Text(
                        f"¿Está seguro que desea rechazar\nel voucher #{voucher.id}?",
                        size=16,
                        text_align=ft.TextAlign.CENTER,
                        color=ft.Colors.BLACK87,
                        weight=ft.FontWeight.W_500,
                    ),
                    alignment=ft.Alignment(0, 0),
                    padding=ft.padding.only(top=10, bottom=10),
                ),
                
                # Botones con colores vibrantes
                ft.Row([
                    ft.TextButton(
                        "Cancelar",
                        on_click=cancelar_primera,
                        style=ft.ButtonStyle(
                            color=ft.Colors.BLACK54,
                            overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                        )
                    ),
                    ft.Button(
                        "Sí, rechazar",
                        on_click=confirmar_primera,
                        bgcolor=PELIGRO,
                        color=ft.Colors.WHITE,
                        style=ft.ButtonStyle(
                            overlay_color=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                        )
                    ),
                ], spacing=10, alignment=ft.MainAxisAlignment.END),
            ], spacing=15, tight=True),
            padding=25,
            bgcolor=ft.Colors.WHITE,
            border_radius=20,
            shadow=ft.BoxShadow(
                blur_radius=40,
                spread_radius=0,
                color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
                offset=ft.Offset(0, 10),
            ),
            width=400,
        )

        overlay_confirmacion = ft.Container(
            content=dialogo_content,
            alignment=ft.Alignment(0, 0),
            bgcolor="#80000000",
            expand=True,
        )

        self.pagina.overlay.append(overlay_confirmacion)
        safe_update(self.pagina)
        print(f"[DEBUG] Confirmación agregada a overlay, total items: {len(self.pagina.overlay)}")
    
    def ver_comprobante_click(self, e):
        """Handler para el botón Ver Comprobante - abre popup con imagen usando overlay"""
        voucher = e.control.data
        print(f"[DEBUG] Abriendo comprobante voucher #{voucher.id} usando OVERLAY")
        
        def cerrar_dialogo(ev):
            if overlay_container in self.pagina.overlay:
                self.pagina.overlay.remove(overlay_container)
            safe_update(self.pagina)
        
        # Diálogo compacto y moderno para imagen
        dialogo_content = ft.Container(
            content=ft.Column([
                # Header elegante con gradiente
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.Icons.RECEIPT_LONG, color=ft.Colors.WHITE, size=28),
                        ft.Column([
                            ft.Text(
                                f"Voucher #{voucher.id}", 
                                size=20, 
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            ft.Text(
                                f"{format_bs(voucher.monto)} • {voucher.metodo_pago}", 
                                size=14,
                                color=ft.Colors.with_opacity(0.9, ft.Colors.WHITE),
                            ),
                        ], spacing=2),
                    ], spacing=15),
                    padding=20,
                    bgcolor=PRIMARIO,
                    border_radius=ft.border_radius.only(top_left=20, top_right=20),
                ),
                
                # Imagen del comprobante - ocupa bien el espacio
                ft.Container(
                    content=ft.Image(
                        src=voucher.imagen_url if voucher.imagen_url else "",
                        fit=ft.BoxFit.CONTAIN,
                        error_content=ft.Container(
                            content=ft.Column([
                                ft.Icon(ft.icons.Icons.IMAGE_NOT_SUPPORTED_ROUNDED, 
                                    size=80, 
                                    color=ft.Colors.BLACK26
                                ),
                                ft.Text(
                                    "Sin comprobante", 
                                    color=ft.Colors.BLACK54,
                                    size=16,
                                ),
                            ], 
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=10),
                            alignment=ft.Alignment(0, 0),
                        ),
                    ),
                    width=700,
                    height=500,
                    bgcolor=ft.Colors.BLACK12,
                    alignment=ft.Alignment(0, 0),
                    padding=10,
                ),
                
                # Botón cerrar moderno
                ft.Container(
                    content=ft.Button(
                        "Cerrar",
                        icon=ft.icons.Icons.CLOSE_ROUNDED,
                        on_click=cerrar_dialogo,
                        bgcolor=PRIMARIO,
                        color=ft.Colors.WHITE,
                        height=45,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=12),
                            overlay_color=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                        ),
                    ),
                    padding=ft.padding.only(left=20, right=20, bottom=15, top=10),
                    alignment=ft.Alignment(0, 0),
                ),
            ], spacing=0, tight=True),
            width=700,  # Ancho fijo para que no se estire
            bgcolor=ft.Colors.WHITE,
            border_radius=20,
            shadow=ft.BoxShadow(
                blur_radius=50,
                spread_radius=0,
                color=ft.Colors.with_opacity(0.4, ft.Colors.BLACK),
                offset=ft.Offset(0, 15),
            ),
        )
        
        overlay_container = ft.Container(
            content=dialogo_content,
            alignment=ft.Alignment(0, 0),
            bgcolor="#80000000",
            expand=True,
        )
        
        self.pagina.overlay.append(overlay_container)
        safe_update(self.pagina)
        print(f"[DEBUG] Comprobante agregado a overlay, total items: {len(self.pagina.overlay)}")
    
    def _mostrar_dialogo_rechazo_overlay(self, voucher, boton_original):
        """Muestra el diálogo de motivo de rechazo usando overlay"""
        print(f"[DEBUG] _mostrar_dialogo_rechazo_overlay iniciado para voucher #{voucher.id}")
        
        motivo_input = ft.TextField(
            label="Motivo del rechazo",
            multiline=True,
            min_lines=3,
            max_lines=5,
            hint_text="Explique por qué se rechaza este voucher",
            hint_style=ft.TextStyle(color=ft.Colors.BLACK38),
            autofocus=True,
            border_color=PRIMARIO,
            focused_border_color=SECUNDARIO,
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
            text_style=ft.TextStyle(color=ft.Colors.BLACK87, size=15),
        )
        
        def cerrar_overlay(ev):
            if overlay_rechazo in self.pagina.overlay:
                self.pagina.overlay.remove(overlay_rechazo)
            safe_update(self.pagina)
        
        def confirmar_rechazo(ev):
            motivo = (motivo_input.value or "").strip()
            if not motivo:
                motivo = "Rechazado por el administrador"
            
            if overlay_rechazo in self.pagina.overlay:
                self.pagina.overlay.remove(overlay_rechazo)
            
            boton_original.disabled = True
            boton_original.text = "Rechazando..."
            boton_original.icon = ft.icons.Icons.HOURGLASS_EMPTY
            safe_update(self.pagina)
            
            print(f"[DEBUG] Emitiendo RechazarVoucherEvento: voucher={voucher.id}")
            VOUCHERS_BLOC.AGREGAR_EVENTO(
                RechazarVoucherEvento(
                    voucher_id=voucher.id,
                    validador_id=self.usuario.ID,
                    motivo=motivo.strip()
                )
            )
            
            # SnackBar con mejor diseño
            try:
                snack = ft.SnackBar(
                    content=ft.Row([
                        ft.Icon(ft.icons.Icons.CHECK_CIRCLE_ROUNDED, color=ft.Colors.WHITE),
                        ft.Text(
                            f"Voucher #{voucher.id} rechazado", 
                            color=ft.Colors.WHITE,
                            weight=ft.FontWeight.W_500,
                        ),
                    ], spacing=10),
                    bgcolor=PELIGRO,
                )
                snack.open = True
                self.pagina.overlay.append(snack)
                safe_update(self.pagina)
            except Exception:
                pass
            # Actualización optimista: eliminar la card localmente
            try:
                card = boton_original.parent.parent.parent
                if hasattr(card, 'parent') and card.parent and hasattr(card.parent, 'controls'):
                    try:
                        card.parent.controls.remove(card)
                    except Exception:
                        pass
                safe_update(self.pagina)
            except Exception:
                pass
        
        # Diálogo moderno y compacto
        dialogo_content = ft.Container(
            content=ft.Column([
                # Header con gradiente
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.Icons.CANCEL_ROUNDED, color=ft.Colors.WHITE, size=32),
                        ft.Column([
                            ft.Text(
                                "Rechazar Voucher",
                                size=22,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            ft.Text(
                                f"#{voucher.id} • {format_bs(voucher.monto)}",
                                size=15,
                                color=ft.Colors.with_opacity(0.9, ft.Colors.WHITE),
                                weight=ft.FontWeight.W_500,
                            ),
                        ], spacing=2),
                    ], spacing=15),
                    padding=20,
                    bgcolor=PELIGRO,
                    border_radius=ft.border_radius.only(top_left=20, top_right=20),
                ),
                
                # Contenido del formulario
                ft.Container(
                    content=ft.Column([
                        motivo_input,
                        
                        # Botones con mejor diseño
                        ft.Row([
                            ft.TextButton(
                                "Cancelar",
                                on_click=cerrar_overlay,
                                style=ft.ButtonStyle(
                                    color=ft.Colors.BLACK54,
                                    overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                                )
                            ),
                            ft.Button(
                                "Confirmar rechazo",
                                on_click=confirmar_rechazo,
                                bgcolor=PELIGRO,
                                color=ft.Colors.WHITE,
                                icon=ft.icons.Icons.CANCEL_ROUNDED,
                                height=45,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=12),
                                    overlay_color=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                                ),
                            ),
                        ], spacing=10, alignment=ft.MainAxisAlignment.END),
                    ], spacing=20),
                    padding=20,
                ),
            ], spacing=0, tight=True),
            bgcolor=ft.Colors.WHITE,
            border_radius=20,
            shadow=ft.BoxShadow(
                blur_radius=50,
                spread_radius=0,
                color=ft.Colors.with_opacity(0.4, ft.Colors.BLACK),
                offset=ft.Offset(0, 15),
            ),
            width=520,
        )
        
        overlay_rechazo = ft.Container(
            content=dialogo_content,
            alignment=ft.Alignment(0, 0),
            bgcolor="#80000000",
            expand=True,
        )
        
        self.pagina.overlay.append(overlay_rechazo)
        safe_update(self.pagina)
        print(f"[DEBUG] Diálogo motivo agregado a overlay, total items: {len(self.pagina.overlay)}")
    
    def ver_detalles_pedido(self, e):
        """Muestra detalles completos del pedido con productos en BottomSheet"""
        voucher = e.control.data
        
        try:
            sesion = OBTENER_SESION()
            
            # Buscar el pedido asociado al voucher
            pedido = sesion.query(MODELO_PEDIDO).filter_by(ID=voucher.pedido_id).first() if hasattr(voucher, 'pedido_id') else None
            
            if not pedido:
                # Si no hay pedido_id en voucher, mostrar info básica del voucher
                items_list = [
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Información del Voucher", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800),
                            ft.Divider(height=1, color=ft.Colors.GREY_300),
                            ft.Row([
                                ft.Text("Monto:", size=14, color=ft.Colors.GREY_600),
                                ft.Text(format_bs(voucher.monto), size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Row([
                                ft.Text("Método de pago:", size=14, color=ft.Colors.GREY_600),
                                ft.Text(voucher.metodo_pago or "N/A", size=14, weight=ft.FontWeight.W_600),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Row([
                                ft.Text("Estado:", size=14, color=ft.Colors.GREY_600),
                                ft.Text(voucher.estado, size=14, weight=ft.FontWeight.W_600, color=EXITO if voucher.estado == "APROBADO" else ADVERTENCIA),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ], spacing=12),
                        padding=ft.padding.all(16),
                        bgcolor=ft.Colors.GREY_50,
                        border_radius=8,
                    )
                ]
                total = voucher.monto
            else:
                # Obtener detalles del pedido
                detalles = sesion.query(MODELO_DETALLE_PEDIDO).filter_by(PEDIDO_ID=pedido.ID).all()
                
                items_list = []
                total = 0
                
                for detalle in detalles:
                    producto = sesion.query(MODELO_PRODUCTO).filter_by(ID=detalle.PRODUCTO_ID).first()
                    
                    nombre_producto = producto.NOMBRE if producto else f"Producto #{detalle.PRODUCTO_ID}"
                    precio_unit = getattr(detalle, 'PRECIO_UNITARIO', 0)
                    cantidad = getattr(detalle, 'CANTIDAD', 1)
                    subtotal = precio_unit * cantidad
                    total += subtotal
                    
                    items_list.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Text(f"{cantidad}x", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700, width=40),
                                ft.Text(nombre_producto, size=14, color=ft.Colors.GREY_900, expand=True),
                                ft.Text(f"S/. {subtotal:.2f}", size=14, weight=ft.FontWeight.W_600, color=ft.Colors.GREEN_700),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            padding=ft.padding.symmetric(vertical=8, horizontal=12),
                            bgcolor=ft.Colors.GREY_50,
                            border_radius=8,
                            margin=ft.margin.only(bottom=8)
                        )
                    )
        
        except Exception as ex:
            print(f"[ERROR] ver_detalles_pedido: {ex}")
            items_list = [ft.Text(f"Error al cargar detalles: {str(ex)}", color=ft.Colors.RED_700)]
            total = voucher.monto if hasattr(voucher, 'monto') else 0
        
        def cerrar_bottom_sheet(ev):
            if bottom_sheet in self.pagina.overlay:
                bottom_sheet.open = False
                self.pagina.overlay.remove(bottom_sheet)
            safe_update(self.pagina)
        
        # Crear BottomSheet
        bottom_sheet = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column([
                    # Header
                    ft.Row([
                        ft.Text(
                            f"Detalles Voucher #{voucher.id}",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_900
                        ),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE_ROUNDED,
                            on_click=cerrar_bottom_sheet,
                            icon_color=ft.Colors.GREY_700
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    
                    ft.Divider(height=1, color=ft.Colors.GREY_300),
                    
                    # Items
                    ft.Text("Detalles del Pedido", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800),
                    ft.Column(items_list, spacing=0, scroll=ft.ScrollMode.AUTO, height=300),
                    
                    ft.Divider(height=1, color=ft.Colors.GREY_300),
                    
                    # Total
                    ft.Row([
                        ft.Text("TOTAL:", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_900),
                        ft.Text(f"S/. {total:.2f}", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ], spacing=16, scroll=ft.ScrollMode.AUTO),
                padding=ft.padding.all(24),
                bgcolor=ft.Colors.WHITE,
                border_radius=ft.border_radius.only(top_left=20, top_right=20),
            ),
            open=True,
            on_dismiss=cerrar_bottom_sheet
        )
        
        self.pagina.overlay.append(bottom_sheet)
        safe_update(self.pagina)
