"""
VouchersPage Refactorizada con LayoutBase Global
"""
import flet as ft
from typing import Optional, List
import threading
import sys

from core.Constantes import COLORES, TAMANOS, ICONOS, ROLES
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
            titulo_vista="🧾 Vouchers",
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
        
        # Forzar actualización inicial con el estado actual del BLoC
        print(f"[DEBUG INIT] Forzando actualización inicial con estado actual del BLoC")
        estado_actual = VOUCHERS_BLOC._estado
        if estado_actual:
            print(f"[DEBUG INIT] Estado actual del BLoC: {type(estado_actual).__name__}")
            self._ON_ESTADO_CAMBIO(estado_actual)
        else:
            print(f"[DEBUG INIT] No hay estado actual en el BLoC")
        
        # Cargar los 3 estados de forma escalonada (con delay entre cada uno)
        # para evitar competencia de threads y tener datos en todos los tabs
        sucursales = self.obtener_sucursales_seleccionadas()
        
        def cargar_estado(estado, delay=0):
            def _cargar():
                if sucursales:
                    for sucursal_id in sucursales:
                        VOUCHERS_BLOC.AGREGAR_EVENTO(CargarVouchers(estado=estado, sucursal_id=sucursal_id))
                else:
                    VOUCHERS_BLOC.AGREGAR_EVENTO(CargarVouchers(estado=estado))
            
            if delay > 0:
                threading.Timer(delay, _cargar).start()
            else:
                _cargar()
        
        # Cargar en secuencia: PENDIENTE (0s), APROBADO (0.3s), RECHAZADO (0.6s)
        cargar_estado("PENDIENTE", delay=0)
        cargar_estado("APROBADO", delay=0.3)
        cargar_estado("RECHAZADO", delay=0.6)
    
    def _on_sucursales_change(self, sucursales_ids: Optional[List[int]]):
        """OVERRIDE: Callback cuando cambian las sucursales"""
        # Recargar solo el estado actual
        if sucursales_ids:
            for sucursal_id in sucursales_ids:
                VOUCHERS_BLOC.AGREGAR_EVENTO(CargarVouchers(estado=self._estado_actual, sucursal_id=sucursal_id))
        else:
            VOUCHERS_BLOC.AGREGAR_EVENTO(CargarVouchers(estado=self._estado_actual))
    
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
        
        # Contenedores para cada estado (cada uno con su propio indicador)
        self._contenedor_pendiente = ft.Column(
            controls=[],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
            spacing=4
        )
        
        self._contenedor_aprobado = ft.Column(
            controls=[],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
            spacing=4
        )
        
        self._contenedor_rechazado = ft.Column(
            controls=[],
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

        # Botón de configuración de tiempo de bloqueo
        btn_config = ft.IconButton(
            icon=ft.Icons.SETTINGS,
            icon_color=ft.Colors.BLUE_700,
            tooltip="Configurar tiempo de bloqueo",
            on_click=self._abrir_config_tiempo_bloqueo
        )

        # Barra de tabs con botón de config
        self._tab_bar = ft.Row([
            _tab("Pendientes", ft.icons.Icons.PENDING_ACTIONS, 0),
            _tab("Aprobados", ft.icons.Icons.CHECK_CIRCLE, 1),
            _tab("Rechazados", ft.icons.Icons.CANCEL, 2),
            ft.Container(expand=True),  # Espaciador
            btn_config,
        ], spacing=0, alignment=ft.MainAxisAlignment.START)

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
            # Mostrar skeleton loader SOLO en el estado que se está cargando
            estado_cargando = getattr(estado, "estado_actual", self._estado_actual)
            contenedor = self._obtener_contenedor_por_estado(estado_cargando)
            if contenedor:
                # Crear nuevo indicador para evitar problemas de reutilización
                contenedor.controls = [self._crear_indicador_carga(estado_cargando)]
                safe_update(self._pagina)
            
            # TIMEOUT: Si después de 5 segundos aún no hay datos, mostrar error
            def verificar_timeout():
                import time
                time.sleep(5)
                # Verificar si sigue en cargando (no hay datos en cache)
                if self._cache_vouchers.get(estado_cargando) is None:
                    print(f"⚠️ TIMEOUT: No se recibieron datos para {estado_cargando} en 5s")
                    contenedor = self._obtener_contenedor_por_estado(estado_cargando)
                    if contenedor:
                        contenedor.controls = [self._crear_mensaje_error(
                            f"Tiempo de espera agotado. Reintentando..."
                        )]
                        safe_update(self._pagina)
                        # Reintentar carga
                        VOUCHERS_BLOC.AGREGAR_EVENTO(CargarVouchers(estado=estado_cargando))
            
            threading.Thread(target=verificar_timeout, daemon=True).start()
            
        elif isinstance(estado, VouchersCargados):
            print(f"[DEBUG UI] VouchersCargados recibido - {len(estado.vouchers)} vouchers")
            # Actualizar cache y mostrar vouchers SOLO en el tab/estado correcto
            estado_tab = getattr(estado, "estado_actual", self._estado_actual)
            print(f"[DEBUG UI] estado_tab={estado_tab}, _estado_actual={self._estado_actual}")
            # Si la carga es paginación, acumular resultados en cache
            existentes = self._cache_vouchers.get(estado_tab)
            if getattr(estado, 'tiene_mas', False) and isinstance(existentes, list):
                existentes.extend(estado.vouchers or [])
                self._cache_vouchers[estado_tab] = existentes
            else:
                self._cache_vouchers[estado_tab] = list(estado.vouchers or [])

            self._ultima_carga[estado_tab] = threading.get_ident()
            contenedor = self._obtener_contenedor_por_estado(estado_tab)
            print(f"[DEBUG UI] contenedor obtenido: {contenedor is not None}")
            if contenedor:
                mostrar = self._cache_vouchers[estado_tab]
                print(f"[DEBUG UI] vouchers a mostrar: {len(mostrar) if mostrar else 0}")
                if not mostrar:
                    print(f"[DEBUG UI] Sin vouchers, mostrando mensaje vacío")
                    contenedor.controls = [self._crear_mensaje_vacio(estado_tab)]
                else:
                    print(f"[DEBUG UI] Creando {len(mostrar)} cards...")
                    def _aprobar(e):
                        self._handlers.aprobar_click(e)
                    def _rechazar(e):
                        self._handlers.rechazar_click(e)
                    def _ver_comprobante(e):
                        self._handlers.ver_comprobante_click(e)
                    def _ver_detalles(e):
                        self._handlers.ver_detalles_pedido(e)
                    
                    try:
                        contenedor.controls = [
                            VoucherCardBuilder.crear_card(
                                voucher=v,
                                estado_actual=estado_tab,
                                on_aprobar_click=_aprobar,
                                on_rechazar_click=_rechazar,
                                on_ver_comprobante_click=_ver_comprobante,
                                on_ver_detalles_click=_ver_detalles
                            ) for v in mostrar
                        ]
                        print(f"[DEBUG UI] Cards creadas exitosamente")
                    except Exception as ex:
                        print(f"[ERROR] Error creando cards: {ex}")
                        import traceback
                        traceback.print_exc()
                        contenedor.controls = [ft.Text(f"Error: {ex}", color=ft.Colors.ERROR)]
            
            # Usar run_task para actualizar desde thread secundario
            print(f"[DEBUG UI] Programando actualización para {len(self._cache_vouchers.get(estado_tab, []))} vouchers en estado {estado_tab}")
            
            async def actualizar_ui():
                try:
                    print(f"[DEBUG UI] async actualizar_ui ejecutándose...")
                    safe_update(self._pagina)
                    print(f"[DEBUG UI] safe_update completado OK")
                except Exception as ex:
                    print(f"[ERROR] actualizar_ui: {ex}")
                    import traceback
                    traceback.print_exc()
            
            try:
                self._pagina.run_task(actualizar_ui)
                print(f"[DEBUG UI] run_task() llamado exitosamente")
            except Exception as ex:
                print(f"[ERROR] run_task falló: {ex}")
                import traceback
                traceback.print_exc()
        
        elif isinstance(estado, VouchersError):
            # Mostrar error
            contenedor = self._obtener_contenedor_por_estado(self._estado_actual)
            if contenedor:
                contenedor.controls = [self._crear_mensaje_error(estado.mensaje)]
                
                # Usar run_task para actualizar desde thread secundario
                async def actualizar_ui_error():
                    try:
                        safe_update(self._pagina)
                    except Exception as ex:
                        print(f"[ERROR] actualizar_ui_error: {ex}")
                
                self._pagina.run_task(actualizar_ui_error)
        
        elif isinstance(estado, VoucherValidado):
            # Recargar los 3 estados para ver el cambio inmediato en todos los tabs
            # Escalonado para evitar race conditions
            sucursales = self.obtener_sucursales_seleccionadas()
            
            def cargar_estado(est, delay=0):
                def _cargar():
                    if sucursales:
                        for sucursal_id in sucursales:
                            VOUCHERS_BLOC.AGREGAR_EVENTO(
                                CargarVouchers(estado=est, sucursal_id=sucursal_id)
                            )
                    else:
                        VOUCHERS_BLOC.AGREGAR_EVENTO(
                            CargarVouchers(estado=est)
                        )
                
                if delay > 0:
                    threading.Timer(delay, _cargar).start()
                else:
                    _cargar()
            
            # Recargar en secuencia para evitar bucles
            cargar_estado("PENDIENTE", delay=0)
            cargar_estado("APROBADO", delay=0.2)
            cargar_estado("RECHAZADO", delay=0.4)
    
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
    
    def _abrir_config_tiempo_bloqueo(self, e):
        """Abre el diálogo de configuración de tiempo de bloqueo"""
        from core.configuracion.ServicioConfiguracion import ServicioConfiguracion
        
        # Obtener valor actual
        tiempo_actual = ServicioConfiguracion.obtener_valor("vouchers.tiempo_bloqueo_minutos", default=5)
        
        # Campo de entrada
        tf_tiempo = ft.TextField(
            label="Tiempo de bloqueo (minutos)",
            value=str(tiempo_actual),
            keyboard_type=ft.KeyboardType.NUMBER,
            width=300
        )
        
        def guardar_config(evento):
            try:
                nuevo_tiempo = int(tf_tiempo.value)
                if nuevo_tiempo <= 0:
                    dlg.snack = ft.SnackBar(ft.Text("El tiempo debe ser mayor a 0", color=ft.Colors.WHITE), bgcolor=ft.Colors.RED)
                    dlg.snack.open = True
                    self._pagina.update()
                    return
                
                # Guardar en configuración
                resultado = ServicioConfiguracion.actualizar_valor(
                    "vouchers.tiempo_bloqueo_minutos",
                    nuevo_tiempo,
                    usuario_id=self._usuario.ID
                )
                
                if resultado:
                    dlg.snack = ft.SnackBar(
                        ft.Text(f"⏱️ Tiempo de bloqueo actualizado a {nuevo_tiempo} minutos", color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.GREEN
                    )
                    dlg.snack.open = True
                    dlg.open = False
                    self._pagina.update()
                else:
                    dlg.snack = ft.SnackBar(
                        ft.Text("Error al guardar la configuración", color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.RED
                    )
                    dlg.snack.open = True
                    self._pagina.update()
            except ValueError:
                dlg.snack = ft.SnackBar(
                    ft.Text("Por favor ingresa un número válido", color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.RED
                )
                dlg.snack.open = True
                self._pagina.update()
        
        # Diálogo
        dlg = ft.AlertDialog(
            title=ft.Text("⏱️ Tiempo de Bloqueo de Vouchers"),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "Configura cuántos minutos se bloquean los vouchers después de ser procesados",
                        size=14,
                        color=ft.Colors.GREY_700
                    ),
                    ft.Divider(height=20),
                    tf_tiempo,
                    ft.Container(height=10),
                    ft.Text(
                        "💡 Ejemplo: Si estableces 5 minutos, los vouchers no podrán ser editados durante 5 minutos después de su aprobación o rechazo.",
                        size=12,
                        color=ft.Colors.GREY_600,
                        italic=True
                    )
                ], spacing=0),
                width=350
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: dlg.close()),
                ft.ElevatedButton("Guardar", on_click=guardar_config),
            ],
            modal=True
        )
        
        self._pagina.dialog = dlg
        dlg.open = True
        self._pagina.update()
    
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
