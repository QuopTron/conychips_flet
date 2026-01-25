"""
Página de visualización de auditoría del sistema.
Solo lectura - No es CRUD.
Arquitectura: Clean Architecture + Hexagonal
"""
import flet as ft
from datetime import datetime, timedelta
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_AUDITORIA
from core.Constantes import COLORES, TAMANOS, ICONOS, ROLES
from core.decoradores.DecoradorVistas import REQUIERE_ROL
from features.admin.presentation.widgets.ComponentesGlobales import (
    HeaderAdmin, TablaGenerica, BarraBusqueda, ContenedorPagina, Notificador
)


@REQUIERE_ROL(ROLES.SUPERADMIN)
class AuditoriaPage(ft.Column):
    """Vista de solo lectura de logs de auditoría."""
    
    def __init__(self, PAGINA: ft.Page, USUARIO):
        super().__init__()
        self._PAGINA = PAGINA
        self._USUARIO = USUARIO
        self._FILTRO = "TODOS"
        self._FECHA_INICIO = datetime.now() - timedelta(days=7)
        self._FECHA_FIN = datetime.now()
        
        self.expand = True
        self._CONSTRUIR_UI()
        self._CARGAR_DATOS()
    
    def _CONSTRUIR_UI(self):
        """Construye la interfaz de usuario."""
        # Header
        header = HeaderAdmin(
            titulo="Auditoría del Sistema",
            icono=ICONOS.AUDITORIA,
            on_menu=self._IR_MENU,
            on_salir=self._SALIR
        )
        
        # Filtros
        filtros = ft.Row(
            controls=[
                ft.Dropdown(
                    label="Tipo de Evento",
                    options=[
                        ft.dropdown.Option("TODOS", "Todos"),
                        ft.dropdown.Option("LOGIN", "Inicios de Sesión"),
                        ft.dropdown.Option("LOGOUT", "Cierres de Sesión"),
                        ft.dropdown.Option("CREAR", "Creaciones"),
                        ft.dropdown.Option("EDITAR", "Modificaciones"),
                        ft.dropdown.Option("ELIMINAR", "Eliminaciones"),
                        ft.dropdown.Option("ERROR", "Errores"),
                    ],
                    value=self._FILTRO,
                    on_change=self._CAMBIAR_FILTRO,
                    width=200
                ),
                ft.ElevatedButton(
                    "Última Semana",
                    icon=ICONOS.CALENDARIO,
                    on_click=lambda e: self._APLICAR_RANGO(7)
                ),
                ft.ElevatedButton(
                    "Último Mes",
                    icon=ICONOS.CALENDARIO,
                    on_click=lambda e: self._APLICAR_RANGO(30)
                ),
                ft.ElevatedButton(
                    "Exportar",
                    icon=ICONOS.DESCARGAR,
                    on_click=self._EXPORTAR_AUDITORIA
                ),
            ],
            spacing=TAMANOS.ESPACIADO_MD
        )
        
        # Tabla de resultados
        self._tabla = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
        
        # Contenedor principal
        contenido = ContenedorPagina(
            controles=[header, filtros, self._tabla]
        )
        
        self.controls = [contenido]
    
    def _CARGAR_DATOS(self):
        """Carga los registros de auditoría."""
        try:
            sesion = OBTENER_SESION()
            query = sesion.query(MODELO_AUDITORIA).filter(
                MODELO_AUDITORIA.FECHA >= self._FECHA_INICIO,
                MODELO_AUDITORIA.FECHA <= self._FECHA_FIN
            )
            
            if self._FILTRO != "TODOS":
                query = query.filter(MODELO_AUDITORIA.TIPO_EVENTO == self._FILTRO)
            
            registros = query.order_by(MODELO_AUDITORIA.FECHA.desc()).limit(500).all()
            
            self._ACTUALIZAR_TABLA(registros)
            
        except Exception as e:
            Notificador.ERROR(self._PAGINA, f"Error al cargar auditoría: {str(e)}")
    
    def _ACTUALIZAR_TABLA(self, registros):
        """Actualiza la tabla con los registros."""
        self._tabla.controls.clear()
        
        if not registros:
            self._tabla.controls.append(
                ft.Text("No hay registros en el período seleccionado", 
                       size=16, color=COLORES.TEXTO_SECUNDARIO)
            )
        else:
            # Crear tabla
            filas = []
            for reg in registros:
                color_evento = self._OBTENER_COLOR_EVENTO(reg.TIPO_EVENTO)
                filas.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(reg.FECHA.strftime("%d/%m/%Y %H:%M:%S"))),
                            ft.DataCell(ft.Container(
                                content=ft.Text(reg.TIPO_EVENTO, color=COLORES.TEXTO_BLANCO),
                                bgcolor=color_evento,
                                padding=5,
                                border_radius=5
                            )),
                            ft.DataCell(ft.Text(reg.USUARIO or "Sistema")),
                            ft.DataCell(ft.Text(reg.ACCION or "-")),
                            ft.DataCell(ft.Text(reg.DETALLES or "-", max_lines=2)),
                        ]
                    )
                )
            
            tabla = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Fecha y Hora", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Evento", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Usuario", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Acción", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Detalles", weight=ft.FontWeight.BOLD)),
                ],
                rows=filas,
                border=ft.border.all(1, COLORES.BORDE),
                heading_row_color=COLORES.FONDO_SECUNDARIO,
            )
            
            self._tabla.controls.append(
                ft.Container(
                    content=tabla,
                    border=ft.border.all(1, COLORES.BORDE),
                    border_radius=TAMANOS.RADIO_MD,
                    padding=TAMANOS.PADDING_MD
                )
            )
        
        self._PAGINA.update()
    
    def _OBTENER_COLOR_EVENTO(self, tipo_evento):
        """Retorna color según tipo de evento."""
        colores_eventos = {
            "LOGIN": COLORES.EXITO,
            "LOGOUT": COLORES.INFO,
            "CREAR": COLORES.PRIMARIO,
            "EDITAR": COLORES.ADVERTENCIA,
            "ELIMINAR": COLORES.PELIGRO,
            "ERROR": COLORES.PELIGRO,
        }
        return colores_eventos.get(tipo_evento, COLORES.SECUNDARIO)
    
    def _CAMBIAR_FILTRO(self, e):
        """Cambia el filtro de eventos."""
        self._FILTRO = e.control.value
        self._CARGAR_DATOS()
    
    def _APLICAR_RANGO(self, dias):
        """Aplica rango de fechas."""
        self._FECHA_INICIO = datetime.now() - timedelta(days=dias)
        self._FECHA_FIN = datetime.now()
        self._CARGAR_DATOS()
    
    def _EXPORTAR_AUDITORIA(self, e):
        """Exporta auditoría a CSV."""
        Notificador.INFO(self._PAGINA, "Exportación en desarrollo...")
    
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
