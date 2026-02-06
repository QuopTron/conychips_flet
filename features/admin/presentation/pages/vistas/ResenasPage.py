import flet as ft
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_RESENA_ATENCION
from core.Constantes import COLORES, TAMANOS, ICONOS, ROLES
from core.decoradores.DecoradorVistas import REQUIERE_ROL
from features.admin.presentation.widgets.ComponentesGlobales import (
    HeaderAdmin, ContenedorPagina, Notificador
)
from core.ui.safe_actions import safe_update

@REQUIERE_ROL(ROLES.ADMIN)
class ResenasPage(ft.Column):
    
    def __init__(self, PAGINA: ft.Page, USUARIO):
        super().__init__()
        self._PAGINA = PAGINA
        self._USUARIO = USUARIO
        self._FILTRO = "TODAS"
        
        self.expand = True
        self._CONSTRUIR_UI()
        self._CARGAR_RESENAS()
    
    def _CONSTRUIR_UI(self):
        header = HeaderAdmin(
            titulo="Reseñas de Clientes",
            icono=ICONOS.ESTRELLA,
            on_menu=self._IR_MENU,
            on_salir=self._SALIR
        )
        
        # Dropdown con manejo correcto para Flet 0.8.0
        self._dropdown_filtro = ft.Dropdown(
            label="Calificación",
            options=[
                ft.dropdown.Option("TODAS", "Todas"),
                ft.dropdown.Option("5", "⭐⭐⭐⭐⭐ (5)"),
                ft.dropdown.Option("4", "⭐⭐⭐⭐ (4)"),
                ft.dropdown.Option("3", "⭐⭐⭐ (3)"),
                ft.dropdown.Option("2", "⭐⭐ (2)"),
                ft.dropdown.Option("1", "⭐ (1)"),
            ],
            value=self._FILTRO,
        )
        self._dropdown_filtro.on_select = self._CAMBIAR_FILTRO
        
        filtros = ft.Container(
            content=ft.ResponsiveRow([
                ft.Container(
                    self._dropdown_filtro,
                    col={"xs": 12, "sm": 6, "md": 3}
                ),
                ft.Container(
                    ft.Button(
                        "Actualizar",
                        icon=ft.icons.Icons.REFRESH,
                        on_click=lambda e: self._CARGAR_RESENAS()
                    ),
                    col={"xs": 12, "sm": 6, "md": 2}
                ),
            ], spacing=6, run_spacing=6),
            bgcolor=ft.Colors.BLUE_50,
            border_radius=4,
            padding=6,
            border=ft.Border.all(1, ft.Colors.BLUE_200)
        )
        
        self._lista = ft.Column(spacing=4, scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        
        contenido = ft.Container(
            content=ft.Column([header, filtros, self._lista], spacing=4, expand=True),
            padding=0,
            expand=True
        )
        
        self.controls = [contenido]
    
    def _CARGAR_RESENAS(self):
        try:
            sesion = OBTENER_SESION()
            query = sesion.query(MODELO_RESENA_ATENCION)
            
            if self._FILTRO != "TODAS":
                query = query.filter(MODELO_RESENA_ATENCION.CALIFICACION == int(self._FILTRO))
            
            resenas = query.order_by(MODELO_RESENA_ATENCION.FECHA.desc()).limit(50).all()
            
            self._ACTUALIZAR_LISTA(resenas)
            
        except Exception as e:
            Notificador.ERROR(self._PAGINA, f"Error al cargar reseñas: {str(e)}")
    
    def _ACTUALIZAR_LISTA(self, resenas):
        self._lista.controls.clear()
        
        if not resenas:
            self._lista.controls.append(
                ft.Text("No hay reseñas", size=16, color=COLORES.TEXTO_SECUNDARIO)
            )
        else:
            for resena in resenas:
                estrellas = "⭐" * resena.CALIFICACION
                
                # Obtener nombre del usuario
                nombre_usuario = "Cliente Anónimo"
                if resena.USUARIO:
                    nombre_usuario = resena.USUARIO.NOMBRE_USUARIO
                
                card = ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Column([
                                    ft.Text(nombre_usuario, 
                                           weight=ft.FontWeight.BOLD),
                                    ft.Text(
                                        resena.FECHA.strftime("%d/%m/%Y %H:%M"),
                                        size=12,
                                        color=COLORES.TEXTO_SECUNDARIO
                                    ),
                                ]),
                                ft.Container(expand=True),
                                ft.Text(estrellas, size=20),
                            ]),
                            ft.Divider(),
                            ft.Text(
                                resena.COMENTARIO or "Sin comentario",
                                size=14,
                                max_lines=None
                            ),
                        ], spacing=10),
                        padding=TAMANOS.PADDING_MD,
                    ),
                    elevation=2
                )
                self._lista.controls.append(card)
        
        safe_update(self._PAGINA)
    
    def _CAMBIAR_FILTRO(self, e):
        self._FILTRO = e.control.value
        self._CARGAR_RESENAS()
    
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
