"""
Script de prueba para el login con fondo animado de emojis.
"""
import flet as ft
from core.ui.fondo_animado import FondoAnimadoLogin
from core.ui.colores import (
    PRIMARIO,
    SECUNDARIO,
    obtener_gradiente_primario,
    obtener_sombra_elevada,
)
from core.ui.animaciones import animar_hover


def main(page: ft.Page):
    page.title = "Login Animado - Cony Chips 🍔"
    page.padding = 0
    page.bgcolor = ft.Colors.WHITE
    
    # Crear fondo con emojis cayendo
    ancho_ventana = page.width or 1200
    alto_ventana = page.height or 800
    
    fondo_animado = FondoAnimadoLogin(ancho_ventana, alto_ventana)
    
    # Iniciar animación
    page.run_task(fondo_animado.iniciar_animacion, page)
    
    # Logo con gradiente
    logo = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "🍔",
                    size=60,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Cony Chips",
                    size=48,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Autenticación de doble capa",
                    size=16,
                    color=ft.Colors.with_opacity(0.9, ft.Colors.WHITE),
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        gradient=obtener_gradiente_primario(),
        padding=30,
        border_radius=15,
        margin=ft.margin.only(bottom=30),
    )
    
    # Campos de entrada
    campo_email = ft.TextField(
        label="Email",
        prefix_icon=ft.Icons.EMAIL,
        border_color=PRIMARIO,
        focused_border_color=SECUNDARIO,
        filled=True,
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
        width=400,
    )
    
    campo_password = ft.TextField(
        label="Contraseña",
        prefix_icon=ft.Icons.LOCK,
        password=True,
        can_reveal_password=True,
        border_color=PRIMARIO,
        focused_border_color=SECUNDARIO,
        filled=True,
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
        width=400,
    )
    
    # Botón de login
    boton_login = ft.Button(
        "Entrar",
        icon=ft.Icons.LOGIN,
        width=400,
        height=55,
        bgcolor=PRIMARIO,
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
        ),
    )
    
    # Agregar efecto hover
    animar_hover(
        boton_login,
        PRIMARIO,
        ft.Colors.with_opacity(0.9, PRIMARIO)
    )
    
    # Card de login
    login_card = ft.Container(
        content=ft.Column(
            [
                logo,
                ft.Text(
                    "Iniciar Sesión",
                    size=24,
                    weight=ft.FontWeight.W_500,
                    color=PRIMARIO,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                campo_email,
                campo_password,
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                boton_login,
                ft.TextButton(
                    "¿No tienes cuenta? Regístrate",
                    style=ft.ButtonStyle(color=PRIMARIO),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
        ),
        width=500,
        padding=40,
        bgcolor=ft.Colors.WHITE,
        border_radius=20,
        shadow=obtener_sombra_elevada(),
    )
    
    # Centrar la card sobre el fondo animado
    fondo_animado.controls.append(
        ft.Container(
            content=login_card,
            alignment=ft.Alignment(0, 0),
            expand=True,
        )
    )
    
    page.add(fondo_animado)


if __name__ == "__main__":
    ft.app(target=main)
