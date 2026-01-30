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
        on_ver_comprobante_click
    ) -> ft.Card:
        """
        Crea una tarjeta de voucher con toda su información y botones de acción
        
        Args:
            voucher: Entidad del voucher
            estado_actual: Estado actual del tab (PENDIENTE, APROBADO, RECHAZADO)
            on_aprobar_click: Handler para el botón Aprobar
            on_rechazar_click: Handler para el botón Rechazar
            on_ver_comprobante_click: Handler para el botón Ver Comprobante
            
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
            on_aprobar_click, on_rechazar_click, on_ver_comprobante_click
        )
        
        # Ensamblar tarjeta completa
        contenido = ft.Container(
            content=ft.Column([
                header,
                ft.Divider(height=1, color=COLORES.BORDE),
                ft.Container(
                    content=ft.Row(badges + [ft.Container(expand=True)], spacing=8),
                    padding=ft.Padding(0, 8, 0, 8),
                ),
                info_grid,
                ft.Row(acciones, spacing=10, wrap=True) if acciones else ft.Container(),
            ], spacing=12),
            padding=TAMANOS.PADDING_MD,
        )
        
        # Card con ancho máximo para responsive
        return ft.Card(
            content=contenido,
            elevation=2,
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
            ft.Icon(ICONOS.VOUCHER, size=24, color=COLORES.PRIMARIO),
            ft.Text(f"Voucher #{voucher.id}", weight=ft.FontWeight.BOLD, size=18),
            ft.Container(expand=True),
            ft.Container(
                content=ft.Text(
                    format_bs(voucher.monto),
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=COLORES.TEXTO_BLANCO
                ),
                padding=ft.Padding(left=12, right=12, top=6, bottom=6),
                bgcolor=COLORES.EXITO,
                border_radius=8,
            ),
        ])
    
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
        """Crea la grilla de información del voucher"""
        info_rows = [
            ft.Row([
                ft.Text("Método de pago:", size=13, color=COLORES.TEXTO_SECUNDARIO),
                ft.Text(voucher.metodo_pago, size=13, weight=ft.FontWeight.BOLD),
            ], spacing=8, wrap=True),
            ft.Row([
                ft.Text("Fecha:", size=13, color=COLORES.TEXTO_SECUNDARIO),
                ft.Text(voucher.fecha_subida.strftime("%d/%m/%Y %H:%M"), size=13, weight=ft.FontWeight.BOLD),
            ], spacing=8, wrap=True),
            ft.Row([
                ft.Text("Usuario ID:", size=13, color=COLORES.TEXTO_SECUNDARIO),
                ft.Text(str(voucher.usuario_id), size=13, weight=ft.FontWeight.BOLD),
            ], spacing=8, wrap=True),
        ]
        
        # Agregar motivo de rechazo si existe
        if voucher.estado == "RECHAZADO" and voucher.motivo_rechazo:
            info_rows.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text("Motivo de rechazo:", size=13, weight=ft.FontWeight.BOLD, color=COLORES.PELIGRO),
                        ft.Text(voucher.motivo_rechazo, size=12, color=COLORES.TEXTO),
                    ], spacing=4),
                    padding=ft.Padding(8, 8, 8, 8),
                    bgcolor=ft.Colors.RED_50,
                    border_radius=4,
                    margin=ft.Margin(0, 8, 0, 0),
                )
            )
        
        return ft.Column(info_rows, spacing=8)
    
    @staticmethod
    def _crear_acciones(
        voucher: Voucher,
        bloqueado: bool,
        on_aprobar_click,
        on_rechazar_click,
        on_ver_comprobante_click
    ) -> list:
        """Crea los botones de acción según el estado del voucher"""
        import sys
        print(f"[DEBUG CardBuilder] _crear_acciones para voucher #{getattr(voucher, 'id', None)}", file=sys.stderr, flush=True)
        print(f"[DEBUG CardBuilder]   estado={getattr(voucher, 'estado', None)}, bloqueado={bloqueado}", file=sys.stderr, flush=True)
        print(f"[DEBUG CardBuilder]   on_rechazar_click={on_rechazar_click}", file=sys.stderr, flush=True)
        print(f"[DEBUG CardBuilder]   on_rechazar_click is None: {on_rechazar_click is None}", file=sys.stderr, flush=True)
        
        acciones = []
        
        # Botón Ver Comprobante siempre visible
        btn_ver = ft.Button(
            "Ver Comprobante",
            icon=ICONOS.IMAGEN,
            bgcolor=COLORES.INFO,
            color=COLORES.TEXTO_BLANCO,
            data=voucher,
            on_click=on_ver_comprobante_click,
        )
        acciones.append(btn_ver)
        
        if not bloqueado:
            if voucher.es_pendiente():
                # Pendiente: Aprobar + Rechazar
                btn_aprobar = ft.Button(
                    "Aprobar",
                    icon=ICONOS.CONFIRMAR,
                    bgcolor=COLORES.EXITO,
                    color=COLORES.TEXTO_BLANCO,
                    data=voucher,
                    on_click=on_aprobar_click,
                )
                acciones.append(btn_aprobar)
                
                import sys
                print(f"[DEBUG CardBuilder] Creando botón Rechazar para PENDIENTE", file=sys.stderr, flush=True)
                btn_rechazar = ft.OutlinedButton(
                    "Rechazar",
                    icon=ICONOS.CANCELAR,
                    style=ft.ButtonStyle(color=COLORES.PELIGRO),
                    data=voucher,
                    on_click=on_rechazar_click,
                )
                print(f"[DEBUG CardBuilder]   btn_rechazar.on_click={btn_rechazar.on_click}", file=sys.stderr, flush=True)
                print(f"[DEBUG CardBuilder]   btn_rechazar.data={getattr(btn_rechazar.data, 'id', None) if btn_rechazar.data else None}", file=sys.stderr, flush=True)
                acciones.append(btn_rechazar)
                
            elif voucher.estado == "APROBADO":
                # Aprobado: solo Rechazar
                btn_rechazar = ft.OutlinedButton(
                    "Rechazar",
                    icon=ICONOS.CANCELAR,
                    style=ft.ButtonStyle(color=COLORES.PELIGRO),
                    data=voucher,
                    on_click=on_rechazar_click,
                )
                acciones.append(btn_rechazar)
                
            elif voucher.estado == "RECHAZADO":
                # Rechazado: solo Aprobar
                btn_aprobar = ft.Button(
                    "Aprobar",
                    icon=ICONOS.CONFIRMAR,
                    bgcolor=COLORES.EXITO,
                    color=COLORES.TEXTO_BLANCO,
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
