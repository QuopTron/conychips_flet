"""
Componente base para vistas de administración con navbar y área de contenido
"""
import flet as ft
from features.admin.presentation.widgets.NavbarAdmin import NavbarAdmin
from core.Constantes import COLORES, TAMANOS
from typing import Optional, Callable


class VistaBase(ft.Column):
    """Vista base con navbar persistente y área de contenido"""
    
    def __init__(
        self,
        pagina: ft.Page,
        usuario,
        titulo: str = "Vista Admin",
        on_volver_inicio: Optional[Callable] = None,
        mostrar_boton_volver: bool = False
    ):
        super().__init__()
        self._pagina = pagina
        self._usuario = usuario
        self._titulo = titulo
        
        # Navbar
        self._navbar = NavbarAdmin(
            pagina=pagina,
            usuario=usuario,
            titulo=titulo,
            on_volver_inicio=on_volver_inicio,
            mostrar_boton_volver=mostrar_boton_volver
        )
        
        # Área de contenido (children)
        self._area_contenido = ft.Container(
            content=ft.Column(
                controls=[],
                spacing=TAMANOS.ESPACIADO_LG,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=TAMANOS.PADDING_XL,
            expand=True,
            bgcolor=COLORES.FONDO,
        )
        
        # Construir estructura
        self.controls = [
            self._navbar,
            self._area_contenido
        ]
        self.spacing = 0
        self.expand = True
    
    def establecer_contenido(self, controles: list):
        """Establece los controles del área de contenido"""
        self._area_contenido.content.controls = controles
        self.actualizar_ui()
    
    def agregar_contenido(self, control):
        """Agrega un control al área de contenido"""
        self._area_contenido.content.controls.append(control)
        self.actualizar_ui()
    
    def limpiar_contenido(self):
        """Limpia el área de contenido"""
        self._area_contenido.content.controls.clear()
        self.actualizar_ui()
    
    def actualizar_ui(self):
        """Actualiza la UI de forma segura"""
        if hasattr(self, 'update') and self._pagina:
            self._pagina.update()
    
    def mostrar_dialogo(self, dialogo: ft.AlertDialog):
        """Muestra un diálogo modal"""
        self._pagina.dialog = dialogo
        dialogo.open = True
        self._pagina.update()
    
    def cerrar_dialogo(self):
        """Cierra el diálogo actual"""
        if hasattr(self._pagina, 'dialog') and self._pagina.dialog:
            self._pagina.dialog.open = False
            self._pagina.update()
    
    def mostrar_snackbar(self, mensaje: str, es_error: bool = False):
        """Muestra un snackbar con mensaje"""
        snackbar = ft.SnackBar(
            content=ft.Text(mensaje, color=COLORES.TEXTO_BLANCO),
            bgcolor=COLORES.PELIGRO if es_error else COLORES.EXITO,
        )
        self._pagina.overlay.append(snackbar)
        snackbar.open = True
        self._pagina.update()
