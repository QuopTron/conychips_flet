"""Constructor de tarjetas de voucher"""
import flet as ft
from datetime import datetime, timezone, timedelta

from core.Constantes import COLORES, TAMANOS, ICONOS
from features.vouchers.presentation.widgets.utils_vouchers import format_bs
from features.vouchers.domain.entities.Voucher import Voucher
from core.configuracion.ServicioConfiguracion import ServicioConfiguracion


class VoucherCardBuilder:
    """Construye las tarjetas visuales de vouchers"""
    
    @staticmethod
    def crear_card(
        voucher: Voucher,
        estado_actual: str,
        on_aprobar_click,
        on_rechazar_click,
        on_ver_comprobante_click,
        on_ver_detalles_click=None
    ) -> ft.Card:
        """
        Crea una tarjeta de voucher con toda su información y botones de acción
        
        Args:
            voucher: Entidad del voucher
            estado_actual: Estado actual del tab (PENDIENTE, APROBADO, RECHAZADO)
            on_aprobar_click: Handler para el botón Aprobar
            on_rechazar_click: Handler para el botón Rechazar
            on_ver_comprobante_click: Handler para el botón Ver Comprobante
            on_ver_detalles_click: Handler para el botón Ver Detalles Pedido (opcional)
            
        Returns:
            ft.Card configurada con el voucher
        """
        # Calcular si está bloqueado por tiempo
        bloqueado, tiempo_restante = VoucherCardBuilder._calcular_bloqueo(voucher)
        
        # Construir secciones de la tarjeta
        header = VoucherCardBuilder._crear_header(voucher)
        badges = VoucherCardBuilder._crear_badges(voucher, bloqueado, tiempo_restante)
        info_grid = VoucherCardBuilder._crear_info_grid(voucher)
        acciones = VoucherCardBuilder._crear_acciones(
            voucher, bloqueado,
            on_aprobar_click, on_rechazar_click, on_ver_comprobante_click,
            on_ver_detalles_click
        )
        
        # Ensamblar tarjeta completa
        contenido = ft.Container(
            content=ft.Column([
                header,
                ft.Divider(height=1, color=COLORES.BORDE),
                ft.Container(
                    content=ft.Row(badges + [ft.Container(expand=True)], spacing=6),
                    padding=ft.Padding(0, 6, 0, 6),
                ),
                info_grid,
                ft.Row(acciones, spacing=8, wrap=True) if acciones else ft.Container(),
            ], spacing=8),
            padding=ft.Padding(12, 10, 12, 10),
        )
        
        # Card con ancho máximo para responsive
        return ft.Card(
            content=contenido,
            elevation=3,
            width=None  # Ancho adaptativo al contenedor padre
        )
    
    @staticmethod
    def _calcular_bloqueo(voucher: Voucher):
        """Calcula si el voucher está bloqueado por tiempo (configurable desde BD)"""
        bloqueado = False
        tiempo_restante = None
        
        # Obtener tiempo de bloqueo desde configuración (default 5 minutos)
        minutos_bloqueo = ServicioConfiguracion.obtener_valor(
            "vouchers.tiempo_bloqueo_minutos", 
            default=5
        )
        
        if voucher.fecha_validacion:
            tiempo_transcurrido = datetime.now(timezone.utc) - voucher.fecha_validacion
            if tiempo_transcurrido > timedelta(minutes=minutos_bloqueo):
                bloqueado = True
            else:
                tiempo_restante = timedelta(minutes=minutos_bloqueo) - tiempo_transcurrido
        
        return bloqueado, tiempo_restante
    
    @staticmethod
    def _crear_header(voucher: Voucher) -> ft.Row:
        """Crea el header de la tarjeta con ID y monto"""
        return ft.Row([
            ft.Icon(ft.icons.Icons.ARTICLE, size=20, color=COLORES.PRIMARIO),
            ft.Text(f"Pedido #{voucher.pedido_id or voucher.id}", weight=ft.FontWeight.BOLD, size=16),
            ft.Container(expand=True),
            ft.Container(
                content=ft.Text(
                    format_bs(voucher.monto),
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=COLORES.TEXTO_BLANCO
                ),
                padding=ft.Padding(left=10, right=10, top=4, bottom=4),
                bgcolor=COLORES.EXITO,
                border_radius=6,
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    
    @staticmethod
    def _crear_badges(voucher: Voucher, bloqueado: bool, tiempo_restante) -> list:
        """Crea los badges de estado y tiempo"""
        color_estado = {
            "PENDIENTE": COLORES.ADVERTENCIA,
            "APROBADO": COLORES.EXITO,
            "RECHAZADO": COLORES.PELIGRO,
        }.get(voucher.estado, COLORES.INFO)
        
        badges = [ft.Container(
            content=ft.Text(
                voucher.estado,
                size=12,
                weight=ft.FontWeight.BOLD,
                color=COLORES.TEXTO_BLANCO
            ),
            padding=ft.Padding(left=8, right=8, top=4, bottom=4),
            bgcolor=color_estado,
            border_radius=4,
        )]
        
        # Badge de bloqueo o tiempo restante
        if voucher.fecha_validacion and voucher.estado != "PENDIENTE":
            if bloqueado:
                badges.append(ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.Icons.LOCK, size=14, color=COLORES.TEXTO_BLANCO),
                        ft.Text("BLOQUEADO", size=11, weight=ft.FontWeight.BOLD, color=COLORES.TEXTO_BLANCO),
                    ], spacing=4, tight=True),
                    padding=ft.Padding(6, 3, 6, 3),
                    bgcolor=ft.Colors.GREY_700,
                    border_radius=4,
                ))
            elif tiempo_restante:
                minutos = int(tiempo_restante.total_seconds() // 60)
                segundos = int(tiempo_restante.total_seconds() % 60)
                badges.append(ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.Icons.TIMER, size=14, color=COLORES.TEXTO_BLANCO),
                        ft.Text(f"{minutos}:{segundos:02d}", size=11, weight=ft.FontWeight.BOLD, color=COLORES.TEXTO_BLANCO),
                    ], spacing=4, tight=True),
                    padding=ft.Padding(6, 3, 6, 3),
                    bgcolor=ft.Colors.ORANGE_700,
                    border_radius=4,
                ))
        
        return badges
    
    @staticmethod
    def _crear_info_grid(voucher: Voucher) -> ft.Column:
        """Crea la grilla de información del voucher con datos del pedido"""
        info_rows = []
        
        # Información del pedido (si está disponible)
        if voucher.cliente_nombre:
            info_rows.append(
                ft.Row([
                    ft.Icon(ft.icons.Icons.PERSON, size=16, color=ft.Colors.BLUE_700),
                    ft.Text(voucher.cliente_nombre, size=13, weight=ft.FontWeight.W_600, color=ft.Colors.BLUE_900),
                ], spacing=6)
            )
        
        if voucher.sucursal_nombre:
            info_rows.append(
                ft.Row([
                    ft.Icon(ft.icons.Icons.STORE, size=14, color=COLORES.TEXTO_SECUNDARIO),
                    ft.Text(f"Sucursal: {voucher.sucursal_nombre}", size=12, weight=ft.FontWeight.W_500),
                ], spacing=6)
            )
        
        # Información del voucher
        info_rows.extend([
            ft.Row([
                ft.Icon(ft.icons.Icons.PAYMENT, size=14, color=COLORES.TEXTO_SECUNDARIO),
                ft.Text(voucher.metodo_pago or "No especificado", size=12, weight=ft.FontWeight.W_500),
            ], spacing=6, wrap=True),
            ft.Row([
                ft.Icon(ft.icons.Icons.CALENDAR_TODAY, size=14, color=COLORES.TEXTO_SECUNDARIO),
                ft.Text(voucher.fecha_subida.strftime("%d/%m/%Y %H:%M") if voucher.fecha_subida else "N/A", size=12, weight=ft.FontWeight.W_500),
            ], spacing=6, wrap=True),
        ])
        
        # Totales: Voucher vs Pedido
        if voucher.pedido_total:
            total_pedido_formatted = format_bs(voucher.pedido_total)
            total_voucher_formatted = format_bs(voucher.monto)
            
            coincide = abs(voucher.monto - voucher.pedido_total) < 1
            color_comparacion = ft.Colors.GREEN_700 if coincide else ft.Colors.ORANGE_700
            icono_comparacion = ft.icons.Icons.CHECK_CIRCLE if coincide else ft.icons.Icons.WARNING
            
            info_rows.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(icono_comparacion, size=16, color=color_comparacion),
                            ft.Text("Comparación de montos:", size=12, weight=ft.FontWeight.BOLD, color=color_comparacion)
                        ], spacing=4),
                        ft.Row([
                            ft.Text(f"Pedido: {total_pedido_formatted}", size=12),
                            ft.Text("•", size=12, color=COLORES.TEXTO_SECUNDARIO),
                            ft.Text(f"Voucher: {total_voucher_formatted}", size=12, weight=ft.FontWeight.BOLD)
                        ], spacing=6)
                    ], spacing=4),
                    padding=ft.Padding(10, 8, 10, 8),
                    bgcolor=ft.Colors.GREEN_50 if coincide else ft.Colors.ORANGE_50,
                    border_radius=6,
                    margin=ft.Margin(0, 6, 0, 0)
                )
            )
        
        # Estado del pedido
        if voucher.pedido_estado:
            info_rows.append(
                ft.Row([
                    ft.Icon(ft.icons.Icons.EVENT_NOTE, size=14, color=COLORES.TEXTO_SECUNDARIO),
                    ft.Text(f"Estado pedido: {voucher.pedido_estado}", size=12, weight=ft.FontWeight.W_500),
                ], spacing=6)
            )
        
        # Productos del pedido (resumen)
        if voucher.pedido_productos and len(voucher.pedido_productos) > 0:
            productos_texto = f"{len(voucher.pedido_productos)} producto(s)"
            if len(voucher.pedido_productos) <= 2:
                nombres = ", ".join([p['nombre'] for p in voucher.pedido_productos])
                productos_texto = nombres
            
            info_rows.append(
                ft.Row([
                    ft.Icon(ft.icons.Icons.SHOPPING_BAG, size=14, color=COLORES.TEXTO_SECUNDARIO),
                    ft.Text(productos_texto, size=12, weight=ft.FontWeight.W_500),
                ], spacing=6)
            )
        
        # Agregar motivo de rechazo si existe
        if voucher.estado == "RECHAZADO" and voucher.motivo_rechazo:
            info_rows.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.icons.Icons.INFO_OUTLINE, size=14, color=COLORES.PELIGRO),
                            ft.Text("Motivo rechazo:", size=12, weight=ft.FontWeight.BOLD, color=COLORES.PELIGRO),
                        ], spacing=4),
                        ft.Text(voucher.motivo_rechazo, size=11, color=COLORES.TEXTO),
                    ], spacing=3),
                    padding=ft.Padding(8, 6, 8, 6),
                    bgcolor=ft.Colors.RED_50,
                    border_radius=4,
                    margin=ft.Margin(0, 6, 0, 0),
                )
            )
        
        return ft.Column(info_rows, spacing=8)
    
    @staticmethod
    def _crear_acciones(
        voucher: Voucher,
        bloqueado: bool,
        on_aprobar_click,
        on_rechazar_click,
        on_ver_comprobante_click,
        on_ver_detalles_click=None
    ) -> list:
        """Crea los botones de acción según el estado del voucher"""
        acciones = []
        
        # Botón Ver Comprobante siempre visible
        btn_ver = ft.FilledButton(
            "Comprobante",
            icon=ICONOS.IMAGEN,
            icon_color=COLORES.TEXTO_BLANCO,
            style=ft.ButtonStyle(
                bgcolor=COLORES.INFO,
                color=COLORES.TEXTO_BLANCO,
                padding=ft.Padding(12, 8, 12, 8),
            ),
            data=voucher,
            on_click=on_ver_comprobante_click,
        )
        acciones.append(btn_ver)
        
        # Botón Ver Detalles del Pedido (si se proporcionó handler)
        if on_ver_detalles_click:
            btn_detalles = ft.OutlinedButton(
                "Detalles",
                icon=ft.icons.Icons.LIST_ALT,
                style=ft.ButtonStyle(
                    color=COLORES.INFO,
                    padding=ft.Padding(12, 8, 12, 8),
                ),
                data=voucher,
                on_click=on_ver_detalles_click,
            )
            acciones.append(btn_detalles)
        
        if not bloqueado:
            if voucher.es_pendiente():
                # Pendiente: Aprobar + Rechazar
                btn_aprobar = ft.FilledButton(
                    "Aprobar",
                    icon=ICONOS.CONFIRMAR,
                    style=ft.ButtonStyle(
                        bgcolor=COLORES.EXITO,
                        color=COLORES.TEXTO_BLANCO,
                        padding=ft.Padding(12, 8, 12, 8),
                    ),
                    data=voucher,
                    on_click=on_aprobar_click,
                )
                acciones.append(btn_aprobar)
                
                btn_rechazar = ft.OutlinedButton(
                    "Rechazar",
                    icon=ICONOS.CANCELAR,
                    style=ft.ButtonStyle(
                        color=COLORES.PELIGRO,
                        padding=ft.Padding(12, 8, 12, 8),
                    ),
                    data=voucher,
                    on_click=on_rechazar_click,
                )
                acciones.append(btn_rechazar)
                
            elif voucher.estado == "APROBADO":
                # Aprobado: solo Rechazar
                btn_rechazar = ft.OutlinedButton(
                    "Rechazar",
                    icon=ICONOS.CANCELAR,
                    style=ft.ButtonStyle(
                        color=COLORES.PELIGRO,
                        padding=ft.Padding(12, 8, 12, 8),
                    ),
                    data=voucher,
                    on_click=on_rechazar_click,
                )
                acciones.append(btn_rechazar)
                
            elif voucher.estado == "RECHAZADO":
                # Rechazado: solo Aprobar
                btn_aprobar = ft.FilledButton(
                    "Aprobar",
                    icon=ICONOS.CONFIRMAR,
                    style=ft.ButtonStyle(
                        bgcolor=COLORES.EXITO,
                        color=COLORES.TEXTO_BLANCO,
                        padding=ft.Padding(12, 8, 12, 8),
                    ),
                    data=voucher,
                    on_click=on_aprobar_click,
                )
                acciones.append(btn_aprobar)
        else:
            # Bloqueado: mensaje informativo con tiempo configurable
            minutos = ServicioConfiguracion.obtener_valor("vouchers.tiempo_bloqueo_minutos", default=5)
            acciones.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.Icons.INFO, size=16, color=COLORES.INFO),
                        ft.Text(
                            f"Este voucher está bloqueado (han pasado más de {minutos} minutos)",
                            size=12,
                            color=COLORES.TEXTO_SECUNDARIO,
                            italic=True
                        ),
                    ], spacing=8),
                    padding=ft.Padding(8, 8, 8, 8),
                    bgcolor=ft.Colors.BLUE_50,
                    border_radius=4,
                )
            )
        
        return acciones
