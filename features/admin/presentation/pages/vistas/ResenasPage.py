"""
Página de visualización de reseñas de clientes.
Vista de solo lectura para moderación.
Arquitectura: Clean Architecture + Hexagonal
"""
import flet as ft
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_RESENA
from core.Constantes import COLORES, TAMANOS, ICONOS, ROLES
from core.decoradores.DecoradorVistas import REQUIERE_ROL
from features.admin.presentation.widgets.ComponentesGlobales import (
    HeaderAdmin, ContenedorPagina, Notificador
)


@REQUIERE_ROL(ROLES.SUPERVISOR)
class ResenasPage(ft.Column):
    """Vista de reseñas y valoraciones de clientes."""
    
    def __init__(self, PAGINA: ft.Page, USUARIO):
        super().__init__()
        self._PAGINA = PAGINA
        self._USUARIO = USUARIO
        self._FILTRO = "TODAS"
        
        self.expand = True
        self._CONSTRUIR_UI()
        self._CARGAR_RESENAS()
    
    def _CONSTRUIR_UI(self):
        """Construye interfaz."""
        # Header
        header = HeaderAdmin(
            titulo="Reseñas de Clientes",
            icono=ICONOS.ESTRELLA,
            on_menu=self._IR_MENU,
            on_salir=self._SALIR
        )
        
        # Filtros
        filtros = ft.Row(
            controls=[
                ft.Dropdown(
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
                    on_change=self._CAMBIAR_FILTRO,
                    width=200
                ),
                ft.ElevatedButton(
                    "Actualizar",
                    icon=ICONOS.ACTUALIZAR,
                    on_click=lambda e: self._CARGAR_RESENAS()
                ),
            ],
            spacing=TAMANOS.ESPACIADO_MD
        )
        
        # Lista de reseñas
        self._lista = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
        
        # Contenedor principal
        contenido = ContenedorPagina(
            controles=[header, filtros, self._lista]
        )
        
        self.controls = [contenido]
    
    def _CARGAR_RESENAS(self):
        """Carga reseñas desde BD."""
        try:
            sesion = OBTENER_SESION()
            query = sesion.query(MODELO_RESENA)
            
            if self._FILTRO != "TODAS":
                query = query.filter(MODELO_RESENA.CALIFICACION == int(self._FILTRO))
            
            resenas = query.order_by(MODELO_RESENA.FECHA.desc()).limit(50).all()
            
            self._ACTUALIZAR_LISTA(resenas)
            
        except Exception as e:
            Notificador.ERROR(self._PAGINA, f"Error al cargar reseñas: {str(e)}")
    
    def _ACTUALIZAR_LISTA(self, resenas):
        """Actualiza lista de reseñas."""
        self._lista.controls.clear()
        
        if not resenas:
            self._lista.controls.append(
                ft.Text("No hay reseñas", size=16, color=COLORES.TEXTO_SECUNDARIO)
            )
        else:
            for resena in resenas:
                # Construir estrellas
                estrellas = "⭐" * resena.CALIFICACION
                
                card = ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Column([
                                    ft.Text(resena.CLIENTE or "Cliente Anónimo", 
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
                            # Producto si existe
                            ft.Row([
                                ft.Icon(ICONOS.PRODUCTO, size=16, 
                                       color=COLORES.TEXTO_SECUNDARIO),
                                ft.Text(
                                    resena.PRODUCTO or "Experiencia general",
                                    size=12,
                                    color=COLORES.TEXTO_SECUNDARIO
                                ),
                            ]) if hasattr(resena, 'PRODUCTO') else ft.Container(),
                        ], spacing=10),
                        padding=TAMANOS.PADDING_MD,
                    ),
                    elevation=2
                )
                self._lista.controls.append(card)
        
        self._PAGINA.update()
    
    def _CAMBIAR_FILTRO(self, e):
        """Cambia filtro de calificación."""
        self._FILTRO = e.control.value
        self._CARGAR_RESENAS()
    
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
