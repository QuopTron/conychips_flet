"""
FinanzasPage Refactorizada con LayoutBase Global
"""
import flet as ft
from typing import Optional, List
from core.Constantes import ROLES
from core.decoradores.DecoradorVistas import REQUIERE_ROL
from core.ui.safe_actions import safe_update

from features.admin.presentation.widgets import LayoutBase
from features.finanzas.presentation.bloc import (
    FinanzasBloc, CargarResumenFinanciero, FiltrarPorEstado,
    BuscarPorCodigo, FiltrarVoucherEstado,
    EstadoFinanzas, EstadoFinanzasCargando, EstadoFinanzasCargado, EstadoFinanzasError
)
from features.finanzas.presentation.widgets.stats_finanzas import StatsFinanzas
from features.finanzas.presentation.widgets.tabla_pedidos import TablaPedidos


@REQUIERE_ROL(ROLES.ADMIN)
class FinanzasPage(LayoutBase):
    """Página de finanzas usando layout global"""
    
    def __init__(self, PAGINA: ft.Page, USUARIO):
        # Inicializar layout base
        super().__init__(
            pagina=PAGINA,
            usuario=USUARIO,
            titulo_vista="Finanzas y Reportes",
            mostrar_boton_volver=True,
            index_navegacion=2,  # Finanzas es el 3er item
            on_volver_dashboard=self._ir_dashboard,
            on_cerrar_sesion=self._cerrar_sesion
        )
        
        # BLoC de finanzas
        sucursales = self.obtener_sucursales_seleccionadas()
        self.bloc = FinanzasBloc(sucursales_ids=sucursales)
        
        # Widgets
        self.stats = StatsFinanzas()
        self.tabla = TablaPedidos(on_ver_detalle=self._ver_detalle_pedido)
        
        # Conectar eventos de filtros
        self.tabla.campo_busqueda.on_submit = self._buscar_pedido
        self.tabla.btn_buscar.on_click = self._buscar_pedido
        self.tabla.filtro_estado.on_select = self._filtrar_estado
        self.tabla.filtro_voucher.on_select = self._filtrar_voucher
        
        # Construir UI
        self._construir_contenido()
        
        # Suscribirse a cambios
        self.bloc.subscribirse(self._actualizar_desde_estado)
        self._cargar_inicial()
    
    def _construir_contenido(self):
        """Construye el contenido específico de finanzas"""
        
        # Indicador de carga
        self.indicador_carga = ft.Container(
            content=ft.Column(
                controls=[
                    ft.ProgressRing(),
                    ft.Text("Cargando datos financieros...", size=16)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            ),
            alignment=ft.Alignment(0, 0),
            expand=True
        )
        
        # Contenedor dinámico que ocupa todo el espacio disponible
        self.contenido_dinamico = ft.Column(
            controls=[self.indicador_carga],
            expand=True,
            spacing=5
        )
        
        # Contenedor principal responsive sin padding - 100% expandible
        contenido = ft.Container(
            content=self.contenido_dinamico,
            expand=True,
            padding=0
        )
        
        # Construir layout base con este contenido
        self.construir(contenido)
    
    def _on_sucursales_change(self, sucursales_ids: Optional[List[int]]):
        """Callback cuando cambian las sucursales seleccionadas"""
        # Recrear BLoC con nuevo filtro
        self.bloc.desuscribirse(self._actualizar_desde_estado)
        self.bloc = FinanzasBloc(sucursales_ids=sucursales_ids)
        self.bloc.subscribirse(self._actualizar_desde_estado)
        
        # Recargar datos
        self.bloc.agregar_evento(CargarResumenFinanciero())
    
    def _cargar_inicial(self):
        """Cargar datos iniciales"""
        import threading
        threading.Timer(0.5, lambda: self.bloc.agregar_evento(CargarResumenFinanciero())).start()
    
    def _actualizar_desde_estado(self, estado: EstadoFinanzas):
        """Actualizar UI según estado del BLoC"""
        if isinstance(estado, EstadoFinanzasCargando):
            self.contenido_dinamico.controls = [self.indicador_carga]
            safe_update(self._pagina)
        
        elif isinstance(estado, EstadoFinanzasCargado):
            # Actualizar widgets
            self.stats.actualizar_desde_estado(estado)
            self.tabla.actualizar_pedidos(estado.pedidos)
            
            # Mostrar contenido con stats compactos y tabla 100% responsive
            self.contenido_dinamico.controls = [
                self.stats,
                ft.Container(
                    content=self.tabla,
                    expand=True,
                )
            ]
            self.contenido_dinamico.expand = True
            self.contenido_dinamico.spacing = 3
            safe_update(self._pagina)
        
        elif isinstance(estado, EstadoFinanzasError):
            self.contenido_dinamico.controls = [
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.Icons.ERROR_OUTLINE, size=64, color=ft.Colors.RED),
                        ft.Text(estado.mensaje, size=16)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20),
                    alignment=ft.Alignment(0, 0),
                    expand=True
                )
            ]
            safe_update(self._pagina)
    
    def _buscar_pedido(self, e):
        """Buscar pedido por código"""
        codigo = self.tabla.campo_busqueda.value
        if codigo and codigo.strip():
            self.bloc.agregar_evento(BuscarPorCodigo(codigo=codigo.strip()))
        else:
            self.bloc.agregar_evento(CargarResumenFinanciero())
    
    def _filtrar_estado(self, e):
        """Filtrar por estado del pedido"""
        estado = e.control.value
        if estado == "TODOS" or not estado:
            self.bloc.agregar_evento(FiltrarPorEstado(estado=None))
        else:
            self.bloc.agregar_evento(FiltrarPorEstado(estado=estado))
    
    def _filtrar_voucher(self, e):
        """Filtrar por estado del voucher"""
        voucher_estado = e.control.value
        self.bloc.agregar_evento(FiltrarVoucherEstado(voucher_estado=voucher_estado))
    
    def _ver_detalle_pedido(self, pedido_id):
        """Ver detalle de un pedido"""
        # TODO: Implementar popup de detalle
        print(f"Ver detalle del pedido {pedido_id}")
    
    def _ir_dashboard(self):
        """Volver al dashboard"""
        from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
        self._pagina.controls.clear()
        self._pagina.add(PaginaAdmin(self._pagina, self._usuario))
        safe_update(self._pagina)
    
    def _cerrar_sesion(self, e=None):
        """Cerrar sesión"""
        from features.autenticacion.presentation.pages.PaginaLogin import PaginaLogin
        self._pagina.controls.clear()
        self._pagina.add(PaginaLogin(self._pagina))
        safe_update(self._pagina)
    
    def will_unmount(self):
        """Cleanup antes de desmontar"""
        self.bloc.desuscribirse(self._actualizar_desde_estado)
