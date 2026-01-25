"""
Componente de Navbar reutilizable para todas las vistas de administración
"""
import flet as ft
from core.Constantes import COLORES, TAMANOS, ICONOS, ROLES
from typing import Callable, Optional


class NavbarAdmin(ft.Container):
    """Navbar persistente para vistas de administración"""
    
    def __init__(
        self,
        pagina: ft.Page,
        usuario,
        titulo: str = "Dashboard Admin",
        on_volver_inicio: Optional[Callable] = None,
        mostrar_boton_volver: bool = False
    ):
        super().__init__()
        self._pagina = pagina
        self._usuario = usuario
        self._titulo = titulo
        self._on_volver_inicio = on_volver_inicio
        self._mostrar_boton_volver = mostrar_boton_volver
        
        self._construir()
    
    def _construir(self):
        """Construye el navbar con todos los controles"""
        controles = [
            ft.Icon(
                ICONOS.ADMIN,
                size=TAMANOS.ICONO_LG,
                color=COLORES.PRIMARIO
            ),
            ft.Text(
                self._titulo,
                size=TAMANOS.TEXTO_2XL,
                weight=ft.FontWeight.BOLD,
                color=COLORES.TEXTO
            ),
        ]
        
        # Botón volver si está en una subvista
        if self._mostrar_boton_volver and self._on_volver_inicio:
            controles.append(
                ft.ElevatedButton(
                    "← Volver al Dashboard",
                    icon=ft.Icons.HOME,
                    on_click=lambda e: self._on_volver_inicio(),
                    bgcolor=COLORES.INFO,
                    color=COLORES.TEXTO_BLANCO
                )
            )
        
        controles.extend([
            ft.Container(expand=True),  # Espaciador
            ft.Text(
                f"👤 {self._usuario.NOMBRE_USUARIO}",
                size=TAMANOS.TEXTO_MD,
                color=COLORES.TEXTO_SECUNDARIO
            ),
            ft.ElevatedButton(
                "Menú",
                icon=ICONOS.DASHBOARD,
                on_click=self._ir_menu,
                bgcolor=COLORES.PRIMARIO,
                color=COLORES.TEXTO_BLANCO
            ),
            ft.ElevatedButton(
                "Salir",
                icon=ICONOS.CERRAR_SESION,
                on_click=self._salir,
                bgcolor=COLORES.PELIGRO,
                color=COLORES.TEXTO_BLANCO
            ),
        ])
        
        self.content = ft.Row(
            controls=controles,
            spacing=TAMANOS.ESPACIADO_MD,
            alignment=ft.MainAxisAlignment.START,
        )
        self.padding = TAMANOS.PADDING_MD
        self.bgcolor = COLORES.FONDO_BLANCO
        self.border = ft.border.only(bottom=ft.BorderSide(2, COLORES.PRIMARIO))
    
    def _ir_menu(self, e):
        """Volver al dashboard principal"""
        if self._on_volver_inicio:
            self._on_volver_inicio()
        else:
            from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
            self._pagina.controls.clear()
            self._pagina.controls.append(PaginaAdmin(self._pagina, self._usuario))
            self._pagina.update()
    
    def _salir(self, e):
        """Cerrar sesión"""
        from features.autenticacion.presentation.pages.PaginaLogin import PaginaLogin
        self._pagina.controls.clear()
        self._pagina.controls.append(PaginaLogin(self._pagina))
        self._pagina.update()
    
    def actualizar_titulo(self, nuevo_titulo: str):
        """Actualiza el título del navbar"""
        self._titulo = nuevo_titulo
        self.content.controls[1].value = nuevo_titulo
        self.update()
