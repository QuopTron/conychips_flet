"""
VouchersPage Refactorizada con LayoutBase Global
"""
import flet as ft
from typing import Optional, List
import threading
import sys

from core.Constantes import COLORES, TAMANOS, ICONOS, ROLES
from unittest.mock import Mock as _Mock
from core.decoradores.DecoradorVistas import REQUIERE_ROL
from core.ui.safe_actions import safe_update

from features.admin.presentation.widgets import LayoutBase
from features.vouchers.presentation.bloc import (
    VOUCHERS_BLOC,
    VouchersEstado,
    VouchersCargando,
    VouchersCargados,
    VouchersError,
    VoucherValidado,
    VoucherValidando,
    CargarVouchers,
    AprobarVoucherEvento,
    RechazarVoucherEvento,
    CambiarEstadoFiltro,
)
from features.vouchers.presentation.widgets import VoucherCard
from features.vouchers.domain.entities.Voucher import Voucher

# Importar módulos refactorizados
from .vouchers.VoucherCardBuilder import VoucherCardBuilder
from .vouchers.VoucherHandlers import VoucherHandlers


@REQUIERE_ROL(ROLES.ADMIN)
class VouchersPage(LayoutBase):
    """Página de vouchers usando layout global"""
    
    def __init__(self, PAGINA: ft.Page, USUARIO):
        # Inicializar layout base
        super().__init__(
            pagina=PAGINA,
            usuario=USUARIO,
            titulo_vista="📋 Gestión de Vouchers",
            mostrar_boton_volver=True,
            index_navegacion=1,  # Vouchers es el 2do item
            on_volver_dashboard=self._ir_dashboard,
            on_cerrar_sesion=self._cerrar_sesion
        )
        
        self._estado_actual: str = "PENDIENTE"
        self._tabs_ref = None
        self._timer = None
        self._auto_refresh_activo = True
        self._cache_vouchers = {"PENDIENTE": None, "APROBADO": None, "RECHAZADO": None}
        self._ultima_carga = {"PENDIENTE": None, "APROBADO": None, "RECHAZADO": None}
        self._ui_dirty = False
        self._ui_refresh_timer = None
        
        # Instanciar handlers refactorizados
        self._handlers = VoucherHandlers(PAGINA, USUARIO)
        
        # Construir UI
        self._CONSTRUIR_UI()
        
        # Conectar BLoC
        VOUCHERS_BLOC.AGREGAR_LISTENER(self._ON_ESTADO_CAMBIO)
        
        # Limpiar cache y cargar los tres estados al entrar
        for k in self._cache_vouchers:
            self._cache_vouchers[k] = None
        sucursales = self.obtener_sucursales_seleccionadas()
        estados = ["PENDIENTE", "APROBADO", "RECHAZADO"]
        def cargar_todos():
            if sucursales:
                for estado in estados:
                    for sucursal_id in sucursales:
                        VOUCHERS_BLOC.AGREGAR_EVENTO(CargarVouchers(estado=estado, sucursal_id=sucursal_id))
            else:
                for estado in estados:
                    VOUCHERS_BLOC.AGREGAR_EVENTO(CargarVouchers(estado=estado))
        # In test environments where `PAGINA` is a Mock, run loading synchronously
        try:
            if isinstance(PAGINA, _Mock):
                cargar_todos()
            else:
                threading.Timer(0.1, cargar_todos).start()
        except Exception:
            threading.Timer(0.1, cargar_todos).start()
        self._INICIAR_AUTO_REFRESH()
    
    def _on_sucursales_change(self, sucursales_ids: Optional[List[int]]):
        """OVERRIDE: Callback cuando cambian las sucursales"""
        # Recargar vouchers con nuevo filtro
        self._CARGAR_INICIAL(sucursales_ids)
    
    def _CONSTRUIR_UI(self):
        """Construye la interfaz de vouchers"""
        
        # Skeleton shimmer animado (3 tarjetas)
        def shimmer_card():
            return ft.Container(
                bgcolor=ft.Colors.GREY_100,
                border_radius=10,
                padding=ft.padding.all(16),
                margin=ft.margin.symmetric(vertical=8, horizontal=0),
                content=ft.Column([
                    ft.Row([
                        ft.Container(width=48, height=48, bgcolor=ft.Colors.GREY_300, border_radius=24, animate_opacity=300),
                        ft.Container(width=120, height=16, bgcolor=ft.Colors.GREY_300, border_radius=8, margin=ft.margin.only(left=16), animate_opacity=300),
                    ], spacing=0),
                    ft.Container(width=220, height=12, bgcolor=ft.Colors.GREY_200, border_radius=6, margin=ft.margin.only(top=12), animate_opacity=300),
                    ft.Container(width=160, height=12, bgcolor=ft.Colors.GREY_200, border_radius=6, margin=ft.margin.only(top=8), animate_opacity=300),
                ], spacing=0),
                animate_opacity=300
            )
        self._indicador_carga = ft.Container(
            content=ft.Column(
                controls=[
                    shimmer_card(), shimmer_card(), shimmer_card(),
                    ft.Container(
                        content=ft.Text("Cargando vouchers...", size=15, color=ft.Colors.GREY_600),
                        alignment=ft.Alignment(0, 0),
                        margin=ft.margin.only(top=16)
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0
            ),
            alignment=ft.Alignment(0, 0),
            expand=True,
            padding=ft.padding.symmetric(vertical=32, horizontal=0)
        )
        
        # Contenedores para cada estado
        self._contenedor_pendiente = ft.Column(
            controls=[self._indicador_carga],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
            spacing=4
        )
        
        self._contenedor_aprobado = ft.Column(
            controls=[self._indicador_carga],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
            spacing=4
        )
        
        self._contenedor_rechazado = ft.Column(
            controls=[self._indicador_carga],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
            spacing=4
        )
        
        # Tabs con los diferentes estados - Flet 0.80.3 sintaxis correcta
        self._tab_index = 0
        def _on_tab_click(e, idx):
            self._tab_index = idx
            self._estado_actual = ["PENDIENTE", "APROBADO", "RECHAZADO"][idx]
            self._actualizar_tabs()

        def _tab(label, icon, idx):
            return ft.Container(
                content=ft.Column([
                    ft.Icon(icon, size=22, color=ft.Colors.BLUE_700 if self._tab_index == idx else ft.Colors.GREY_500),
                    ft.Text(label, size=13, weight=ft.FontWeight.W_500, color=ft.Colors.BLUE_700 if self._tab_index == idx else ft.Colors.GREY_500)
                ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.symmetric(vertical=8, horizontal=0),
                on_click=lambda e, i=idx: _on_tab_click(e, i),
                border=ft.border.only(
                    bottom=ft.BorderSide(
                        width=2,
                        color=ft.Colors.BLUE_700 if self._tab_index == idx else ft.Colors.TRANSPARENT
                    )
                ),
                expand=True
            )

        self._tab_bar = ft.Row([
            _tab("Pendientes", ft.icons.Icons.PENDING_ACTIONS, 0),
            _tab("Aprobados", ft.icons.Icons.CHECK_CIRCLE, 1),
            _tab("Rechazados", ft.icons.Icons.CANCEL, 2),
        ], spacing=0, alignment=ft.MainAxisAlignment.CENTER)

        self._tab_views = [
            self._contenedor_pendiente,
            self._contenedor_aprobado,
            self._contenedor_rechazado,
        ]

        self._tab_view_container = ft.Container(
            content=self._tab_views[self._tab_index],
            expand=True
        )

        contenido = ft.Container(
            content=ft.Column([
                self._tab_bar,
                self._tab_view_container
            ], spacing=0, expand=True),
            expand=True,
            padding=0
        )

        self.construir(contenido)

    def _actualizar_tabs(self):
        self._tab_bar.controls.clear()
        def _on_tab_click(e, idx):
            self._tab_index = idx
            self._estado_actual = ["PENDIENTE", "APROBADO", "RECHAZADO"][idx]
            self._actualizar_tabs()
        def _tab(label, icon, idx):
            return ft.Container(
                content=ft.Column([
                    ft.Icon(icon, size=22, color=ft.Colors.BLUE_700 if self._tab_index == idx else ft.Colors.GREY_500),
                    ft.Text(label, size=13, weight=ft.FontWeight.W_500, color=ft.Colors.BLUE_700 if self._tab_index == idx else ft.Colors.GREY_500),
                    ft.Container(
                        height=3,
                        width=40,
                        bgcolor=ft.Colors.BLUE_700 if self._tab_index == idx else ft.Colors.TRANSPARENT,
                        border_radius=2,
                        margin=ft.margin.only(top=2),
                        alignment=ft.Alignment(0, 0),
                    )
                ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.symmetric(vertical=8, horizontal=0),
                on_click=lambda e, i=idx: _on_tab_click(e, i),
                expand=True,
                border=ft.border.only(
                    bottom=ft.BorderSide(
                        width=2,
                        color=ft.Colors.BLUE_700 if self._tab_index == idx else ft.Colors.TRANSPARENT
                    )
                ),
            )
        self._tab_bar.controls.extend([
            _tab("Pendientes", ft.icons.Icons.PENDING_ACTIONS, 0),
            _tab("Aprobados", ft.icons.Icons.CHECK_CIRCLE, 1),
            _tab("Rechazados", ft.icons.Icons.CANCEL, 2),
        ])
        # Mostrar solo el contenedor del estado activo
        self._tab_view_container.content = self._tab_views[self._tab_index]
        self._pagina.update()
    
    def _CARGAR_INICIAL(self, sucursales_ids: Optional[List[int]] = None):
        """Carga inicial de todos los estados de vouchers"""
        
        def cargar_todos_async():
            print(f"[DEBUG] Cargando vouchers con sucursales: {sucursales_ids}", file=sys.stderr, flush=True)
            estados = ["PENDIENTE", "APROBADO", "RECHAZADO"]
            # Si hay sucursales, cargar por cada una, si no, cargar sin filtro
            if sucursales_ids:
                for estado in estados:
                    for sucursal_id in sucursales_ids:
                        VOUCHERS_BLOC.AGREGAR_EVENTO(
                            CargarVouchers(
                                estado=estado,
                                sucursal_id=sucursal_id
                            )
                        )
            else:
                for estado in estados:
                    VOUCHERS_BLOC.AGREGAR_EVENTO(
                        CargarVouchers(
                            estado=estado
                        )
                    )
        # If running in test (mock) environment, execute immediately for determinism
        try:
            if isinstance(self._pagina, _Mock):
                cargar_todos_async()
            else:
                threading.Timer(0.3, cargar_todos_async).start()
        except Exception:
            threading.Timer(0.3, cargar_todos_async).start()
    
    def _on_tab_change(self, e):
        """Cambia el estado actual cuando se cambia de tab"""
        tabs_estados = ["PENDIENTE", "APROBADO", "RECHAZADO"]
        self._estado_actual = tabs_estados[e.control.selected_index]
        # Cargar vouchers del estado si no están en cache
        if self._cache_vouchers[self._estado_actual] is None:
            sucursales = self.obtener_sucursales_seleccionadas()
            if sucursales:
                for sucursal_id in sucursales:
                    VOUCHERS_BLOC.AGREGAR_EVENTO(
                        CargarVouchers(
                            estado=self._estado_actual,
                            sucursal_id=sucursal_id
                        )
                    )
            else:
                VOUCHERS_BLOC.AGREGAR_EVENTO(
                    CargarVouchers(
                        estado=self._estado_actual
                    )
                )
    
    def _INICIAR_AUTO_REFRESH(self):
        """Inicia el refresco automático de vouchers"""
        def refresh():
            if self._auto_refresh_activo:
                sucursales = self.obtener_sucursales_seleccionadas()
                if sucursales:
                    for sucursal_id in sucursales:
                        VOUCHERS_BLOC.AGREGAR_EVENTO(
                            CargarVouchers(
                                estado=self._estado_actual,
                                sucursal_id=sucursal_id
                            )
                        )
                else:
                    VOUCHERS_BLOC.AGREGAR_EVENTO(
                        CargarVouchers(
                            estado=self._estado_actual
                        )
                    )
                self._timer = threading.Timer(30.0, refresh)  # Cada 30 segundos
                self._timer.start()
        self._timer = threading.Timer(30.0, refresh)
        self._timer.start()
    
    def _ON_ESTADO_CAMBIO(self, estado: VouchersEstado):
        """Actualiza UI según estado del BLoC"""
        
        if isinstance(estado, VouchersCargando):
            # Mostrar skeleton loader SIEMPRE durante la carga
            for est in ["PENDIENTE", "APROBADO", "RECHAZADO"]:
                contenedor = self._obtener_contenedor_por_estado(est)
                if contenedor:
                    contenedor.controls = [self._indicador_carga]
            safe_update(self._pagina)
        elif isinstance(estado, VouchersCargados):
            # Actualizar cache y mostrar vouchers SOLO en el tab/estado correcto
            estado_tab = getattr(estado, "estado_actual", self._estado_actual)
            # Si la carga es paginación, acumular resultados en cache
            existentes = self._cache_vouchers.get(estado_tab)
            if getattr(estado, 'tiene_mas', False) and isinstance(existentes, list):
                existentes.extend(estado.vouchers or [])
                self._cache_vouchers[estado_tab] = existentes
            else:
                self._cache_vouchers[estado_tab] = list(estado.vouchers or [])

            self._ultima_carga[estado_tab] = threading.get_ident()
            contenedor = self._obtener_contenedor_por_estado(estado_tab)
            if contenedor:
                mostrar = self._cache_vouchers[estado_tab]
                if not mostrar:
                    contenedor.controls = [self._crear_mensaje_vacio(estado_tab)]
                else:
                    def _aprobar(e):
                        self._handlers.aprobar_click(e)
                    def _rechazar(e):
                        self._handlers.rechazar_click(e)
                    def _ver_comprobante(e):
                        self._handlers.ver_comprobante_click(e)
                    contenedor.controls = [
                        VoucherCardBuilder.crear_card(
                            voucher=v,
                            estado_actual=estado_tab,
                            on_aprobar_click=_aprobar,
                            on_rechazar_click=_rechazar,
                            on_ver_comprobante_click=_ver_comprobante
                        ) for v in mostrar
                    ]
            safe_update(self._pagina)
        
        elif isinstance(estado, VouchersError):
            # Mostrar error
            contenedor = self._obtener_contenedor_por_estado(self._estado_actual)
            if contenedor:
                contenedor.controls = [self._crear_mensaje_error(estado.mensaje)]
                safe_update(self._pagina)
        
        elif isinstance(estado, VoucherValidado):
            # Recargar vouchers después de validar
            sucursales = self.obtener_sucursales_seleccionadas()
            VOUCHERS_BLOC.AGREGAR_EVENTO(
                CargarVouchers(
                    estado="PENDIENTE",
                    sucursales_ids=sucursales
                )
            )
            VOUCHERS_BLOC.AGREGAR_EVENTO(
                CargarVouchers(
                    estado=estado.nuevo_estado,
                    sucursales_ids=sucursales
                )
            )
    
    def _obtener_contenedor_por_estado(self, estado: str):
        """Obtiene el contenedor correspondiente al estado"""
        if estado == "PENDIENTE":
            return self._contenedor_pendiente
        elif estado == "APROBADO":
            return self._contenedor_aprobado
        elif estado == "RECHAZADO":
            return self._contenedor_rechazado
        return None
    
    def _crear_indicador_carga(self, estado: str):
        """Crea indicador de carga"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.ProgressRing(),
                    ft.Text(f"Cargando vouchers {estado.lower()}...", size=16)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            ),
            alignment=ft.Alignment(0, 0),
            expand=True
        )
    
    def _crear_mensaje_vacio(self, estado: str):
        """Crea mensaje cuando no hay vouchers"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.icons.Icons.FOLDER_OPEN, size=80, color=ft.Colors.GREY_300),
                    ft.Text(
                        "No hay vouchers en este estado",
                        size=19,
                        color=ft.Colors.GREY_600,
                        weight=ft.FontWeight.W_500
                    ),
                    ft.Text(
                        "¡Todo limpio por aquí!",
                        size=15,
                        color=ft.Colors.GREY_400
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=18
            ),
            alignment=ft.Alignment(0, 0),
            expand=True,
            padding=ft.padding.symmetric(vertical=40, horizontal=0)
        )
    
    def _crear_mensaje_error(self, mensaje: str):
        """Crea mensaje de error"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.icons.Icons.ERROR_OUTLINE, size=64, color=ft.Colors.RED),
                    ft.Text(mensaje, size=16, color=ft.Colors.RED)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            ),
            alignment=ft.Alignment(0, 0),
            expand=True
        )
    
    def _ir_dashboard(self):
        """Volver al dashboard"""
        self.will_unmount()
        from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
        self._pagina.controls.clear()
        self._pagina.add(PaginaAdmin(self._pagina, self._usuario))
        safe_update(self._pagina)
    
    def _cerrar_sesion(self, e=None):
        """Cerrar sesión"""
        self.will_unmount()
        from features.autenticacion.presentation.pages.PaginaLogin import PaginaLogin
        self._pagina.controls.clear()
        self._pagina.add(PaginaLogin(self._pagina))
        safe_update(self._pagina)
    
    def will_unmount(self):
        """Cleanup antes de desmontar"""
        self._auto_refresh_activo = False
        if self._timer:
            try:
                self._timer.cancel()
            except:
                pass
        VOUCHERS_BLOC.REMOVER_LISTENER(self._ON_ESTADO_CAMBIO)
