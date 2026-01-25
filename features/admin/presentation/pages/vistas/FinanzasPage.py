"""
Página de visualización de finanzas y reportes.
Dashboard de métricas financieras.
Arquitectura: Clean Architecture + Hexagonal
"""
import flet as ft
from datetime import datetime, timedelta
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_PEDIDO, MODELO_CAJA
from core.Constantes import COLORES, TAMANOS, ICONOS, ROLES
from core.decoradores.DecoradorVistas import REQUIERE_ROL
from features.admin.presentation.widgets.ComponentesGlobales import (
    HeaderAdmin, ContenedorPagina, Notificador
)
from features.admin.presentation.widgets.CardEstadistica import CardEstadistica


@REQUIERE_ROL(ROLES.ADMINISTRADOR)
class FinanzasPage(ft.Column):
    """Dashboard de finanzas y reportes financieros."""
    
    def __init__(self, PAGINA: ft.Page, USUARIO):
        super().__init__()
        self._PAGINA = PAGINA
        self._USUARIO = USUARIO
        self._PERIODO = "HOY"
        
        self.expand = True
        self._CONSTRUIR_UI()
        self._CARGAR_METRICAS()
    
    def _CONSTRUIR_UI(self):
        """Construye interfaz del dashboard."""
        # Header
        header = HeaderAdmin(
            titulo="Finanzas y Reportes",
            icono=ICONOS.FINANZAS,
            on_menu=self._IR_MENU,
            on_salir=self._SALIR
        )
        
        # Selector de período
        selector_periodo = ft.Row(
            controls=[
                ft.Text("Período:", weight=ft.FontWeight.BOLD),
                ft.SegmentedButton(
                    selected={"HOY"},
                    allow_empty_selection=False,
                    segments=[
                        ft.Segment(value="HOY", label=ft.Text("Hoy")),
                        ft.Segment(value="SEMANA", label=ft.Text("Esta Semana")),
                        ft.Segment(value="MES", label=ft.Text("Este Mes")),
                        ft.Segment(value="ANO", label=ft.Text("Este Año")),
                    ],
                    on_change=self._CAMBIAR_PERIODO
                ),
            ],
            spacing=TAMANOS.ESPACIADO_MD
        )
        
        # Cards de métricas
        self._cards_metricas = ft.Row(
            controls=[],
            spacing=TAMANOS.ESPACIADO_LG,
            wrap=True
        )
        
        # Gráficos y tablas
        self._seccion_graficos = ft.Column(
            controls=[],
            spacing=TAMANOS.ESPACIADO_LG
        )
        
        # Contenedor principal
        contenido = ContenedorPagina(
            controles=[
                header,
                selector_periodo,
                self._cards_metricas,
                self._seccion_graficos
            ]
        )
        
        self.controls = [contenido]
    
    def _CARGAR_METRICAS(self):
        """Carga y calcula métricas financieras."""
        try:
            sesion = OBTENER_SESION()
            fecha_inicio, fecha_fin = self._OBTENER_RANGO_FECHAS()
            
            # Calcular ingresos de pedidos
            ingresos_query = sesion.query(MODELO_PEDIDO).filter(
                MODELO_PEDIDO.FECHA >= fecha_inicio,
                MODELO_PEDIDO.FECHA <= fecha_fin,
                MODELO_PEDIDO.ESTADO == "COMPLETADO"
            )
            total_ingresos = sum([p.TOTAL for p in ingresos_query.all()])
            cantidad_pedidos = ingresos_query.count()
            
            # Calcular movimientos de caja
            egresos_query = sesion.query(MODELO_CAJA).filter(
                MODELO_CAJA.FECHA >= fecha_inicio,
                MODELO_CAJA.FECHA <= fecha_fin,
                MODELO_CAJA.TIPO_MOVIMIENTO.in_(["EGRESO", "RETIRO"])
            )
            total_egresos = sum([c.MONTO for c in egresos_query.all()])
            
            # Calcular utilidad neta
            utilidad_neta = total_ingresos - total_egresos
            
            # Ticket promedio
            ticket_promedio = total_ingresos / cantidad_pedidos if cantidad_pedidos > 0 else 0
            
            # Actualizar cards
            self._ACTUALIZAR_CARDS({
                "ingresos": total_ingresos,
                "egresos": total_egresos,
                "utilidad": utilidad_neta,
                "pedidos": cantidad_pedidos,
                "ticket_promedio": ticket_promedio
            })
            
        except Exception as e:
            Notificador.ERROR(self._PAGINA, f"Error al cargar métricas: {str(e)}")
    
    def _ACTUALIZAR_CARDS(self, metricas):
        """Actualiza cards de métricas."""
        self._cards_metricas.controls.clear()
        
        cards = [
            CardEstadistica(
                titulo="Ingresos Totales",
                valor=f"S/. {metricas['ingresos']:.2f}",
                icono=ICONOS.DINERO,
                color=COLORES.EXITO
            ),
            CardEstadistica(
                titulo="Egresos Totales",
                valor=f"S/. {metricas['egresos']:.2f}",
                icono=ICONOS.EGRESO,
                color=COLORES.PELIGRO
            ),
            CardEstadistica(
                titulo="Utilidad Neta",
                valor=f"S/. {metricas['utilidad']:.2f}",
                icono=ICONOS.GRAFICO,
                color=COLORES.PRIMARIO if metricas['utilidad'] >= 0 else COLORES.ADVERTENCIA
            ),
            CardEstadistica(
                titulo="Pedidos",
                valor=str(metricas['pedidos']),
                icono=ICONOS.PEDIDOS,
                color=COLORES.INFO
            ),
            CardEstadistica(
                titulo="Ticket Promedio",
                valor=f"S/. {metricas['ticket_promedio']:.2f}",
                icono=ICONOS.ESTADISTICA,
                color=COLORES.SECUNDARIO
            ),
        ]
        
        self._cards_metricas.controls.extend(cards)
        self._PAGINA.update()
    
    def _OBTENER_RANGO_FECHAS(self):
        """Obtiene rango de fechas según período seleccionado."""
        hoy = datetime.now()
        
        if self._PERIODO == "HOY":
            inicio = hoy.replace(hour=0, minute=0, second=0)
            fin = hoy
        elif self._PERIODO == "SEMANA":
            inicio = hoy - timedelta(days=hoy.weekday())
            fin = hoy
        elif self._PERIODO == "MES":
            inicio = hoy.replace(day=1, hour=0, minute=0, second=0)
            fin = hoy
        elif self._PERIODO == "ANO":
            inicio = hoy.replace(month=1, day=1, hour=0, minute=0, second=0)
            fin = hoy
        else:
            inicio = hoy.replace(hour=0, minute=0, second=0)
            fin = hoy
        
        return inicio, fin
    
    def _CAMBIAR_PERIODO(self, e):
        """Cambia el período de visualización."""
        self._PERIODO = list(e.control.selected)[0]
        self._CARGAR_METRICAS()
    
    def _IR_MENU(self, e=None):
        """Retorna al menú principal."""
        from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
        self._PAGINA.controls.clear()
        self._PAGINA.add(PaginaAdmin(self._PAGINA, self._USUARIO))
        self._PAGINA.update()
    
    def _SALIR(self, e=None):
        """Cierra sesión."""
        from features.autenticacion.presentation.pages.PaginaLogin import PaginaLogin
        self._PAGINA.controls.clear()
        self._PAGINA.add(PaginaLogin(self._PAGINA))
        self._PAGINA.update()
