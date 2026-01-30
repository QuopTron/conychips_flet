import flet as ft
from datetime import datetime, timedelta
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_AUDITORIA
from core.Constantes import COLORES, TAMANOS, ICONOS, ROLES
from core.decoradores.DecoradorVistas import REQUIERE_ROL
from features.admin.presentation.widgets import LayoutBase
from core.ui.safe_actions import safe_update
from core.decoradores.DecoradorPermisosUI import requiere_rol_ui
from features.admin.presentation.widgets.ComponentesGlobales import Notificador

@REQUIERE_ROL(ROLES.SUPERADMIN)
class AuditoriaPage(LayoutBase):
    
    def __init__(self, PAGINA: ft.Page, USUARIO):
        # Inicializar layout base
        super().__init__(
            pagina=PAGINA,
            usuario=USUARIO,
            titulo_vista="Auditoría del Sistema",
            mostrar_boton_volver=True,
            index_navegacion=4,  # Auditoría es el 5to item
            on_volver_dashboard=self._IR_MENU,
            on_cerrar_sesion=self._SALIR
        )
        
        self._FILTRO = "TODOS"
        self._FECHA_INICIO = datetime.now() - timedelta(days=7)
        self._FECHA_FIN = datetime.now()
        
        self._CONSTRUIR_UI()
        self._CARGAR_DATOS()
    
    def _CONSTRUIR_UI(self):
        filtros = ft.Container(
            content=ft.ResponsiveRow([
                ft.Container(
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
                    ),
                    col={"xs": 12, "sm": 6, "md": 3}
                ),
                ft.Container(
                    ft.Button(
                        "Última Semana",
                        icon=ft.icons.Icons.CALENDAR_TODAY,
                        on_click=lambda e: self._APLICAR_RANGO(7)
                    ),
                    col={"xs": 6, "sm": 4, "md": 2}
                ),
                ft.Container(
                    ft.Button(
                        "Último Mes",
                        icon=ft.icons.Icons.CALENDAR_MONTH,
                        on_click=lambda e: self._APLICAR_RANGO(30)
                    ),
                    col={"xs": 6, "sm": 4, "md": 2}
                ),
                ft.Container(
                    ft.Button(
                        "Exportar",
                        icon=ft.icons.Icons.DOWNLOAD,
                        on_click=self._EXPORTAR_AUDITORIA
                    ),
                    col={"xs": 12, "sm": 4, "md": 2}
                ),
            ], spacing=6, run_spacing=6),
            bgcolor=ft.Colors.BLUE_50,
            border_radius=4,
            padding=6,
            border=ft.border.all(1, ft.Colors.BLUE_200)
        )
        
        self._tabla = ft.Column(spacing=3, scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        
        contenido = ft.Container(
            content=ft.Column([filtros, self._tabla], expand=True, spacing=4),
            padding=0,
            expand=True
        )
        
        # Usar LayoutBase.construir()
        self.construir(contenido)
    
    def _CARGAR_DATOS(self):
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
        self._tabla.controls.clear()
        
        if not registros:
            self._tabla.controls.append(
                ft.Text("No hay registros en el período seleccionado", 
                       size=16, color=COLORES.TEXTO_SECUNDARIO)
            )
        else:
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
                border=ft.Border.all(1, COLORES.BORDE),
                heading_row_color=COLORES.FONDO_SECUNDARIO,
            )
            
            self._tabla.controls.append(
                ft.Container(
                    content=tabla,
                    border=ft.Border.all(1, COLORES.BORDE),
                    border_radius=TAMANOS.RADIO_MD,
                    padding=TAMANOS.PADDING_MD
                )
            )
        
        safe_update(self._PAGINA)
    
    def _OBTENER_COLOR_EVENTO(self, tipo_evento):
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
        self._FILTRO = e.control.value
        self._CARGAR_DATOS()
    
    def _APLICAR_RANGO(self, dias):
        self._FECHA_INICIO = datetime.now() - timedelta(days=dias)
        self._FECHA_FIN = datetime.now()
        self._CARGAR_DATOS()
    
    @requiere_rol_ui(ROLES.SUPERADMIN, ROLES.ADMIN)
    def _EXPORTAR_AUDITORIA(self, e):
        Notificador.INFO(self._PAGINA, "Exportación en desarrollo...")
    
    def _IR_MENU(self, e=None):
        from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
        self._PAGINA.controls.clear()
        self._PAGINA.add(PaginaAdmin(self._PAGINA, self._USUARIO))
        safe_update(self._PAGINA)
    
    def _SALIR(self, e=None):
        from features.autenticacion.presentation.pages.PaginaLogin import PaginaLogin
        self._PAGINA.controls.clear()
        self._PAGINA.add(PaginaLogin(self._PAGINA))
        safe_update(self._PAGINA)
