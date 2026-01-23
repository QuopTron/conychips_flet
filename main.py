import flet as ft
import os
import sys
import traceback
import asyncio
from features.autenticacion.presentation.pages.PaginaLogin import PaginaLogin
from core.base_datos.ConfiguracionBD import INICIALIZAR_BASE_DATOS

os.environ['NO_AT_BRIDGE'] = '1'

def main(page: ft.Page):
    

    page.title = "Cony Chips"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.window.min_width = 400
    page.window.min_height = 600
    page.window.width = 1200
    page.window.height = 800
    page.window.resizable = True

    try:
        # Programar inicialización de BD en el loop actual (no usar asyncio.run dentro de Flet)
        asyncio.create_task(INICIALIZAR_BASE_DATOS())
        print("Inicializando base de datos en background...")
    except Exception as e:
        print(f"Error iniciando BD: {e}")
    

    try:
        print("Cargando página de Login")

        login = PaginaLogin(page)
        page.controls = [login]
        page.update() 

        print("Login cargado correctamente")

    except Exception as e:
        print(f"Error crítico cargando login:")
        traceback.print_exc()

        page.controls = [
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.ERROR_OUTLINED, size=80, color=ft.Colors.RED_400),
                    ft.Text("Error de Inicialización", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Detalle: {str(e)[:100]}...", size=14, color=ft.Colors.RED_600),
                    ft.Container(height=20),
                    ft.Text("Revisa la consola para más detalles", size=12, color=ft.Colors.GREY_600),
                    ft.Container(height=10),
                    ft.Button(
                        "Ver Error Completo",
                        on_click=lambda e: print(f"\n{'='*60}\n{traceback.format_exc()}\n{'='*60}\n"),
                        icon=ft.Icons.BUG_REPORT
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15),
                alignment=ft.Alignment(0, 0),
                expand=True,
                bgcolor=ft.Colors.RED_50
            )
        ]
        page.update()

if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"Flet versión: {ft.__version__}")
    print(f"Python versión: {sys.version}")
    print(f"Iniciando aplicación Cony Chips CLI...")
    print(f"{'='*60}\n")
    
    ft.run(main)
