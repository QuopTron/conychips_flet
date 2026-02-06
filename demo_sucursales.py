#!/usr/bin/env python
"""Demostración de las mejoras en SucursalesPage"""
import flet as ft

def main(page: ft.Page):
    page.title = "Demo: SucursalesPage Mejorada"
    page.padding = 20
    page.bgcolor = ft.Colors.GREY_100
    
    # Demostración de card moderna
    demo_card = ft.Container(
        content=ft.Column([
            # Header mejorado
            ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Stack([
                            ft.Container(
                                width=60, height=60, border_radius=30,
                                bgcolor=ft.Colors.GREEN_50,
                            ),
                            ft.Container(
                                content=ft.Icon(ft.icons.STORE_ROUNDED, size=28, color=ft.Colors.GREEN_600),
                                width=60, height=60, alignment=ft.alignment.center
                            ),
                        ]),
                        animate_scale=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT)
                    ),
                    ft.Column([
                        ft.Text("Sucursal Centro", size=18, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=ft.Row([
                                ft.Text("✅", size=14),
                                ft.Text("ACTIVA", size=13, weight=ft.FontWeight.W_600, color=ft.Colors.GREEN_600)
                            ], spacing=4),
                            padding=ft.padding.symmetric(horizontal=10, vertical=4),
                            border_radius=12, bgcolor=ft.Colors.GREEN_50
                        ),
                        ft.Text("Operando normalmente", size=11, color=ft.Colors.GREY_500, italic=True)
                    ], spacing=4, expand=True)
                ], spacing=14),
                padding=ft.padding.only(bottom=12)
            ),
            ft.Divider(height=1, color=ft.Colors.GREY_200),
            # Info mejorada
            ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Icon(ft.icons.LOCATION_ON_ROUNDED, size=18, color=ft.Colors.PURPLE_600),
                                width=32, height=32, border_radius=8,
                                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.PURPLE_600),
                                alignment=ft.alignment.center
                            ),
                            ft.Column([
                                ft.Text("Dirección", size=11, color=ft.Colors.GREY_500, weight=ft.FontWeight.W_500),
                                ft.Text("Av. Principal 123, Lima", size=13, color=ft.Colors.GREY_900)
                            ], spacing=2, expand=True)
                        ], spacing=10),
                        padding=ft.padding.all(8), border_radius=10, bgcolor=ft.Colors.GREY_50
                    ),
                    ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Icon(ft.icons.PHONE_ROUNDED, size=18, color=ft.Colors.BLUE_600),
                                width=32, height=32, border_radius=8,
                                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLUE_600),
                                alignment=ft.alignment.center
                            ),
                            ft.Column([
                                ft.Text("Teléfono", size=11, color=ft.Colors.GREY_500, weight=ft.FontWeight.W_500),
                                ft.Text("987654321", size=13, color=ft.Colors.GREY_900)
                            ], spacing=2, expand=True)
                        ], spacing=10),
                        padding=ft.padding.all(8), border_radius=10, bgcolor=ft.Colors.GREY_50
                    ),
                ], spacing=10),
                padding=ft.padding.only(top=12)
            )
        ], spacing=0),
        padding=20, border_radius=16, bgcolor=ft.Colors.WHITE,
        border=ft.border.all(1, ft.Colors.GREY_200),
        shadow=ft.BoxShadow(
            spread_radius=1, blur_radius=12,
            color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
            offset=ft.Offset(0, 4)
        ),
        width=400
    )
    
    # Lista de mejoras
    mejoras = ft.Container(
        content=ft.Column([
            ft.Text("✨ Mejoras Implementadas", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
            ft.Divider(),
            ft.Column([
                ft.Row([ft.Icon(ft.icons.CHECK_CIRCLE, color=ft.Colors.GREEN_600, size=20), ft.Text("Cards con diseño moderno y animaciones hover", size=14)], spacing=8),
                ft.Row([ft.Icon(ft.icons.CHECK_CIRCLE, color=ft.Colors.GREEN_600, size=20), ft.Text("Chips de filtro interactivos con emojis", size=14)], spacing=8),
                ft.Row([ft.Icon(ft.icons.CHECK_CIRCLE, color=ft.Colors.GREEN_600, size=20), ft.Text("Overlays mejorados para crear/editar", size=14)], spacing=8),
                ft.Row([ft.Icon(ft.icons.CHECK_CIRCLE, color=ft.Colors.GREEN_600, size=20), ft.Text("Menú de cambio de estado visual", size=14)], spacing=8),
                ft.Row([ft.Icon(ft.icons.CHECK_CIRCLE, color=ft.Colors.GREEN_600, size=20), ft.Text("Confirmación de eliminación con warnings", size=14)], spacing=8),
                ft.Row([ft.Icon(ft.icons.CHECK_CIRCLE, color=ft.Colors.GREEN_600, size=20), ft.Text("Iconos con colores distintivos por campo", size=14)], spacing=8),
                ft.Row([ft.Icon(ft.icons.CHECK_CIRCLE, color=ft.Colors.GREEN_600, size=20), ft.Text("Sombras y efectos de profundidad", size=14)], spacing=8),
                ft.Row([ft.Icon(ft.icons.CHECK_CIRCLE, color=ft.Colors.GREEN_600, size=20), ft.Text("VouchersPage con título correcto", size=14)], spacing=8),
            ], spacing=12)
        ], spacing=16),
        padding=20, border_radius=12, bgcolor=ft.Colors.WHITE,
        shadow=ft.BoxShadow(spread_radius=0, blur_radius=8, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
        width=500
    )
    
    page.add(
        ft.Column([
            ft.Text("🏪 SucursalesPage - Demostración", size=32, weight=ft.FontWeight.BOLD),
            ft.Row([demo_card, mejoras], spacing=30, alignment=ft.MainAxisAlignment.CENTER)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=30)
    )

if __name__ == "__main__":
    ft.app(target=main)
