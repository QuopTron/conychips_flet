import flet as ft
from functools import wraps
from typing import Callable

from core.Constantes import ROLES, ERRORES_AUTENTICACION
from features.autenticacion.domain.entities.Usuario import Usuario


def REQUIERE_ROL(*ROLES_PERMITIDOS):
    
    def DECORADOR(CLASE_VISTA):
        
        INIT_ORIGINAL = CLASE_VISTA.__init__
        
        @wraps(INIT_ORIGINAL)
        def NUEVO_INIT(self, PAGINA: ft.Page, USUARIO: Usuario, *args, **kwargs):
            
            TIENE_PERMISO = any(USUARIO.TIENE_ROL(rol) for rol in ROLES_PERMITIDOS)
            
            if not TIENE_PERMISO:
                self._MOSTRAR_ERROR_ACCESO(PAGINA, USUARIO)
                return
            
            INIT_ORIGINAL(self, PAGINA, USUARIO, *args, **kwargs)
        
        CLASE_VISTA.__init__ = NUEVO_INIT
        
        def _MOSTRAR_ERROR_ACCESO(self, PAGINA: ft.Page, USUARIO: Usuario):
            from features.autenticacion.presentation.pages.PaginaLogin import PaginaLogin
            
            PAGINA.controls.clear()
            PAGINA.add(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(
                                ft.Icons.BLOCK,
                                size=80,
                                color=ft.Colors.RED_600
                            ),
                            ft.Text(
                                "Acceso Denegado",
                                size=32,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.RED_600
                            ),
                            ft.Text(
                                ERRORES_AUTENTICACION.PERMISOS_INSUFICIENTES,
                                size=16,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.ElevatedButton(
                                "Volver al Inicio",
                                on_click=lambda e: self._VOLVER_LOGIN(PAGINA),
                                bgcolor=ft.Colors.BLUE_600,
                                color=ft.Colors.WHITE,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=20,
                    ),
                    alignment=ft.alignment.center,
                    expand=True,
                )
            )
            PAGINA.update()
        
        def _VOLVER_LOGIN(self, PAGINA: ft.Page):
            from features.autenticacion.presentation.pages.PaginaLogin import PaginaLogin
            PAGINA.controls.clear()
            PAGINA.add(PaginaLogin(PAGINA))
            PAGINA.update()
        
        CLASE_VISTA._MOSTRAR_ERROR_ACCESO = _MOSTRAR_ERROR_ACCESO
        CLASE_VISTA._VOLVER_LOGIN = _VOLVER_LOGIN
        
        return CLASE_VISTA
    
    return DECORADOR


def REQUIERE_PERMISO(*PERMISOS_REQUERIDOS):
    
    def DECORADOR(CLASE_VISTA):
        
        INIT_ORIGINAL = CLASE_VISTA.__init__
        
        @wraps(INIT_ORIGINAL)
        def NUEVO_INIT(self, PAGINA: ft.Page, USUARIO: Usuario, *args, **kwargs):
            
            if USUARIO.TIENE_ROL(ROLES.SUPERADMIN):
                INIT_ORIGINAL(self, PAGINA, USUARIO, *args, **kwargs)
                return
            
            TIENE_PERMISO = any(USUARIO.TIENE_PERMISO(permiso) for permiso in PERMISOS_REQUERIDOS)
            
            if not TIENE_PERMISO:
                self._MOSTRAR_ERROR_ACCESO(PAGINA, USUARIO)
                return
            
            INIT_ORIGINAL(self, PAGINA, USUARIO, *args, **kwargs)
        
        CLASE_VISTA.__init__ = NUEVO_INIT
        
        def _MOSTRAR_ERROR_ACCESO(self, PAGINA: ft.Page, USUARIO: Usuario):
            from features.autenticacion.presentation.pages.PaginaLogin import PaginaLogin
            
            PAGINA.controls.clear()
            PAGINA.add(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(
                                ft.Icons.LOCK,
                                size=80,
                                color=ft.Colors.ORANGE_600
                            ),
                            ft.Text(
                                "Permiso Requerido",
                                size=32,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.ORANGE_600
                            ),
                            ft.Text(
                                ERRORES_AUTENTICACION.PERMISOS_INSUFICIENTES,
                                size=16,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                f"Se requiere uno de estos permisos: {', '.join(PERMISOS_REQUERIDOS)}",
                                size=14,
                                color=ft.Colors.GREY_600,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.ElevatedButton(
                                "Volver al Inicio",
                                on_click=lambda e: self._VOLVER_LOGIN(PAGINA),
                                bgcolor=ft.Colors.BLUE_600,
                                color=ft.Colors.WHITE,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=20,
                    ),
                    alignment=ft.alignment.center,
                    expand=True,
                )
            )
            PAGINA.update()
        
        def _VOLVER_LOGIN(self, PAGINA: ft.Page):
            from features.autenticacion.presentation.pages.PaginaLogin import PaginaLogin
            PAGINA.controls.clear()
            PAGINA.add(PaginaLogin(PAGINA))
            PAGINA.update()
        
        CLASE_VISTA._MOSTRAR_ERROR_ACCESO = _MOSTRAR_ERROR_ACCESO
        CLASE_VISTA._VOLVER_LOGIN = _VOLVER_LOGIN
        
        return CLASE_VISTA
    
    return DECORADOR
