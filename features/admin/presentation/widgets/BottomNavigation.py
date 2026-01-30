"""
Bottom Navigation Bar - Menú inferior global con animaciones
"""
import flet as ft
from core.Constantes import COLORES, ICONOS, ROLES
from typing import Callable, Optional


class BottomNavItem:
    """Item del menú de navegación"""
    def __init__(self, label: str, icon, icon_selected, route: str):
        self.label = label
        self.icon = icon
        self.icon_selected = icon_selected
        self.route = route


class BottomNavigation(ft.Container):
    """Barra de navegación inferior con animaciones parallax"""
    
    def __init__(
        self,
        pagina: ft.Page,
        usuario,
        on_navigate: Callable[[str], None],
        selected_index: int = 0
    ):
        super().__init__()
        self._pagina = pagina
        self._usuario = usuario
        self._on_navigate = on_navigate
        self._selected_index = selected_index
        
        # Items del menú según rol
        self._items = self._obtener_items_menu()
        
        self._construir()
    
    def _obtener_items_menu(self):
        """Obtiene items según el rol del usuario"""
        rol = self._usuario.ROLES[0].NOMBRE if hasattr(self._usuario.ROLES[0], 'NOMBRE') else self._usuario.ROLES[0]
        
        items = [
            BottomNavItem(
                "Dashboard",
                ft.icons.Icons.DASHBOARD_OUTLINED,
                ft.icons.Icons.DASHBOARD,
                "dashboard"
            ),
            BottomNavItem(
                "Usuarios",
                ft.icons.Icons.PEOPLE_OUTLINED,
                ft.icons.Icons.PEOPLE,
                "usuarios"
            ),
            BottomNavItem(
                "Productos",
                ft.icons.Icons.INVENTORY_OUTLINED,
                ft.icons.Icons.INVENTORY,
                "productos"
            ),
            BottomNavItem(
                "Pedidos",
                ft.icons.Icons.SHOPPING_CART_OUTLINED,
                ft.icons.Icons.SHOPPING_CART,
                "pedidos"
            ),
            BottomNavItem(
                "Finanzas",
                ft.icons.Icons.ATTACH_MONEY_OUTLINED,
                ft.icons.Icons.ATTACH_MONEY,
                "finanzas"
            ),
            BottomNavItem(
                "Vouchers",
                ft.icons.Icons.RECEIPT_OUTLINED,
                ft.icons.Icons.RECEIPT,
                "vouchers"
            ),
            BottomNavItem(
                "Más",
                ft.icons.Icons.APPS_OUTLINED,
                ft.icons.Icons.APPS,
                "mas"
            ),
        ]
        
        return items
    
    def _construir(self):
        """Construye la barra de navegación"""
        nav_items = []
        
        for i, item in enumerate(self._items):
            is_selected = i == self._selected_index
            nav_items.append(self._crear_nav_item(item, i, is_selected))
        
        # Layout para desktop
        desktop_nav = ft.Container(
            content=ft.Row(
                controls=nav_items,
                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                spacing=0
            ),
            bgcolor=ft.Colors.WHITE,
            padding=ft.padding.symmetric(vertical=8, horizontal=20),
            border=ft.border.only(top=ft.BorderSide(2, COLORES.BORDE)),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
                offset=ft.Offset(0, -2)
            )
        )
        
        self.content = desktop_nav
        self.height = 70
        self.expand = False
    
    def _crear_nav_item(self, item: BottomNavItem, index: int, is_selected: bool):
        """Crea un item de navegación con animación"""
        
        # Color según estado
        color = COLORES.PRIMARIO if is_selected else COLORES.TEXTO_SECUNDARIO
        bg_color = ft.Colors.BLUE_50 if is_selected else ft.Colors.TRANSPARENT
        
        # Container animado
        container = ft.Container(
            content=ft.Column([
                ft.Icon(
                    item.icon_selected if is_selected else item.icon,
                    size=26,
                    color=color
                ),
                ft.Text(
                    item.label,
                    size=12,
                    weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.W_400,
                    color=color
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4, tight=True),
            bgcolor=bg_color,
            padding=ft.padding.symmetric(horizontal=20, vertical=8),
            border_radius=12,
            ink=True,
            on_click=lambda e, idx=index, route=item.route: self._on_item_click(idx, route),
            on_hover=lambda e, c=None: self._on_item_hover(e, c),
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_OUT)
        )
        
        return container
    
    def _on_item_hover(self, e, container):
        """Efecto parallax al pasar el mouse"""
        if e.data == "true":
            # Mouse enter - elevar
            e.control.scale = 1.1
            e.control.shadow = ft.BoxShadow(
                spread_radius=1,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.2, COLORES.PRIMARIO),
                offset=ft.Offset(0, -3)
            )
        else:
            # Mouse leave - resetear
            e.control.scale = 1.0
            e.control.shadow = None
        
        e.control.update()
    
    def _on_item_click(self, index: int, route: str):
        """Maneja el click en un item"""
        self._selected_index = index
        self._on_navigate(route)
    
    def actualizar_seleccion(self, index: int):
        """Actualiza el item seleccionado"""
        self._selected_index = index
        self._construir()
        self.update()
