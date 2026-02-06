"""
Layout Base Global
Todas las vistas heredan de este layout
"""
import flet as ft
from typing import Callable, Optional, List
from core.Constantes import COLORES
from core.ui.safe_actions import safe_update
from .NavbarGlobal import NavbarGlobal
from .BottomNavigation import BottomNavigation
from core.chat.ChatFlotante import ChatFlotante
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_USUARIO


class LayoutBase(ft.Column):
    """
    Layout base para todas las vistas administrativas
    Incluye: Header global + Contenido + Bottom Navigation
    """
    
    def __init__(
        self,
        pagina: ft.Page,
        usuario,
        titulo_vista: str = "Vista",
        mostrar_boton_volver: bool = True,
        index_navegacion: int = 0,
        on_volver_dashboard: Optional[Callable] = None,
        on_cerrar_sesion: Optional[Callable] = None
    ):
        super().__init__()
        self._pagina = pagina
        self._usuario = usuario
        self._titulo_vista = titulo_vista
        self._mostrar_boton_volver = mostrar_boton_volver
        self._index_navegacion = index_navegacion
        self._on_volver_dashboard = on_volver_dashboard
        self._on_cerrar_sesion = on_cerrar_sesion
        
        # Componentes globales
        self._navbar = None
        self._bottom_nav = None
        self._contenido_container = None
        
        # Soporte para gestos
        self._gesture_detector = None
        
        # Chat flotante
        sesion = OBTENER_SESION()
        usuario_db = sesion.query(MODELO_USUARIO).get(usuario.ID)
        rol_usuario = usuario_db.ROLES[0].NOMBRE if usuario_db and usuario_db.ROLES else "ADMIN"
        sesion.close()
        
        self._chat_flotante = ChatFlotante(
            pagina=pagina,
            usuario_id=usuario.ID,
            usuario_rol=rol_usuario
        )
        
        self.spacing = 0
        self.expand = True
        self.controls = []  # Inicializar controles vacíos
    
    def construir(self, contenido: ft.Control):
        """Construye el layout con el contenido de la vista"""
        print(f"🟢 LayoutBase.construir() - INICIO con contenido tipo: {type(contenido).__name__}")
        
        # Navbar superior con filtro de sucursales, título dinámico y botón volver integrado
        print("🟢 LayoutBase - Creando NavbarGlobal")
        self._navbar = NavbarGlobal(
            pagina=self._pagina,
            usuario=self._usuario,
            titulo_vista=self._titulo_vista,
            mostrar_boton_volver=self._mostrar_boton_volver,
            on_volver=self._on_volver_dashboard,
            on_cambio_sucursales=self._manejar_cambio_sucursales,
            on_cerrar_sesion=self._cerrar_sesion
        )
        
        # Ya no necesitamos header separado - todo está en el navbar
        header_vista = ft.Container(height=0)
        
        # Contenedor del contenido
        self._contenido_container = ft.Container(
            content=contenido,
            expand=True,
            padding=0,
            bgcolor=COLORES.FONDO
        )
        
        # Bottom navigation
        self._bottom_nav = BottomNavigation(
            pagina=self._pagina,
            usuario=self._usuario,
            on_navigate=self._navegar_a,
            selected_index=self._index_navegacion
        )
        
        # Contenedor principal con contenido que se expande
        contenido_principal = ft.Column(
            controls=[
                self._navbar,
                header_vista,
                self._contenido_container
            ],
            spacing=0,
            expand=True
        )
        
        # Layout completo con bottom nav fijo y chat flotante
        print("🟢 LayoutBase - Asignando self.controls con Stack")
        layout_con_nav = ft.Column(
            controls=[
                contenido_principal,
                self._bottom_nav
            ],
            spacing=0,
            expand=True
        )
        
        # Envolver en Stack para agregar chat flotante encima
        self.controls = [
            ft.Stack(
                controls=[
                    layout_con_nav,
                    self._chat_flotante
                ],
                expand=True
            )
        ]
        print(f"🟢 LayoutBase - self.controls asignado con Stack + ChatFlotante")
        
        # Forzar actualización si la página existe
        if self._pagina:
            try:
                print("🟢 LayoutBase - Actualizando página")
                self._pagina.update()
                print("🟢 LayoutBase - Página actualizada exitosamente")
            except Exception as ex:
                print(f"❌ LayoutBase - Error actualizando página: {ex}")
        
        print("🟢 LayoutBase.construir() - FIN")
    
    def _crear_boton_volver(self):
        """Crea solo el botón volver si es necesario"""
        if self._on_volver_dashboard:
            return ft.Container(
                content=ft.IconButton(
                    icon=ft.icons.Icons.ARROW_BACK,
                    tooltip="Volver al Dashboard",
                    on_click=lambda e: self._on_volver_dashboard(),
                    icon_color=COLORES.PRIMARIO,
                    icon_size=22
                ),
                padding=ft.padding.only(left=10, top=5, bottom=5)
            )
        return ft.Container(height=0)
    
    def _manejar_cambio_sucursales(self, sucursales_ids: Optional[List[int]]):
        """
        Wrapper para el callback de cambio de sucursales
        Llama al método de la clase hija si existe
        """
        if hasattr(self, '_on_sucursales_change') and callable(self._on_sucursales_change):
            self._on_sucursales_change(sucursales_ids)
    
    def _on_sucursales_change(self, sucursales_ids: Optional[List[int]]):
        """
        Callback cuando cambian las sucursales seleccionadas
        Las vistas hijas deben sobrescribir este método
        """
        pass
    
    def _on_swipe(self, e: ft.DragEndEvent):
        """Detecta gestos de swipe horizontal"""
        if not hasattr(e, 'primary_velocity'):
            return
        
        velocity = e.primary_velocity
        
        # Swipe derecha → Vista anterior
        if velocity > 500:
            if self._index_navegacion > 0:
                self._index_navegacion -= 1
                route = self._bottom_nav._items[self._index_navegacion].route
                self._navegar_a(route)
        
        # Swipe izquierda → Vista siguiente
        elif velocity < -500:
            if self._index_navegacion < len(self._bottom_nav._items) - 1:
                self._index_navegacion += 1
                route = self._bottom_nav._items[self._index_navegacion].route
                self._navegar_a(route)
    
    def _navegar_a(self, route: str):
        """Navega a una ruta específica"""
        if route == "mas":
            self._mostrar_menu_mas()
        elif route == "dashboard":
            self._ir_dashboard()
        elif route == "usuarios":
            self._ir_a_usuarios()
        elif route == "productos":
            self._ir_a_productos()
        elif route == "pedidos":
            self._ir_a_pedidos()
        elif route == "finanzas":
            self._ir_a_finanzas()
        elif route == "vouchers":
            self._ir_a_vouchers()
    
    def _mostrar_menu_mas(self):
        """Muestra bottom sheet con más opciones"""
        rol = self._usuario.ROLES[0].NOMBRE if hasattr(self._usuario.ROLES[0], 'NOMBRE') else self._usuario.ROLES[0]
        
        opciones = [
            ("Extras", ft.icons.Icons.ADD_CIRCLE),
            ("Ofertas", ft.icons.Icons.LOCAL_OFFER),
            ("Horarios", ft.icons.Icons.SCHEDULE),
            ("Insumos", ft.icons.Icons.INVENTORY_2),
            ("Proveedores", ft.icons.Icons.LOCAL_SHIPPING),
            ("Caja", ft.icons.Icons.POINT_OF_SALE),
            ("Reseñas", ft.icons.Icons.STAR_RATE),
        ]
        
        if rol == "SUPERADMIN":
            opciones.extend([
                ("Sucursales", ft.icons.Icons.STORE),
                ("Roles", ft.icons.Icons.ADMIN_PANEL_SETTINGS),
                ("Auditoría", ft.icons.Icons.HISTORY),
            ])
        
        def navegar_a(texto):
            def handler(e):
                cerrar(e)
                # Navegar según la opción
                if texto == "Extras":
                    self._ir_a_extras()
                elif texto == "Ofertas":
                    self._ir_a_ofertas()
                elif texto == "Horarios":
                    self._ir_a_horarios()
                elif texto == "Insumos":
                    self._ir_a_insumos()
                elif texto == "Proveedores":
                    self._ir_a_proveedores()
                elif texto == "Caja":
                    self._ir_a_caja()
                elif texto == "Reseñas":
                    self._ir_a_resenas()
                elif texto == "Sucursales":
                    self._ir_a_sucursales()
                elif texto == "Roles":
                    self._ir_a_roles()
                elif texto == "Auditoría":
                    self._ir_a_auditoria()
            return handler
        
        def cerrar(e):
            bs.open = False
            self._pagina.update()
        
        # Crear botones
        botones = []
        for texto, icono in opciones:
            botones.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(icono, size=20),
                        ft.Text(texto, size=14, weight=ft.FontWeight.W_500)
                    ], spacing=10),
                    padding=15,
                    ink=True,
                    on_click=navegar_a(texto),
                    border_radius=8
                )
            )
        
        # Crear bottom sheet
        bs = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Row([
                            ft.Text("Más Opciones", size=20, weight=ft.FontWeight.BOLD),
                            ft.Container(expand=True),
                            ft.IconButton(icon=ft.icons.Icons.CLOSE, on_click=cerrar)
                        ]),
                        padding=ft.padding.only(left=20, top=15, right=10, bottom=10)
                    ),
                    ft.Divider(height=1),
                    ft.Container(
                        content=ft.Column(
                            botones,
                            spacing=5,
                            scroll=ft.ScrollMode.AUTO,
                        ),
                        padding=10,
                        height=350
                    )
                ], tight=True, spacing=0),
                bgcolor=ft.Colors.WHITE,
                border_radius=ft.border_radius.only(top_left=20, top_right=20)
            ),
            open=True,
            on_dismiss=cerrar
        )
        
        self._pagina.overlay.append(bs)
        self._pagina.update()
    
    def _ir_a_productos(self):
        """Navega a productos (versión moderna)"""
        from features.productos.presentation.pages.ProductosPageModerna import ProductosPageModerna
        self._pagina.controls.clear()
        self._pagina.add(ProductosPageModerna(self._pagina, self._usuario))
        safe_update(self._pagina)
    
    def _ir_a_pedidos(self):
        """Navega a pedidos (Vouchers/Comprobantes)"""
        from features.admin.presentation.pages.vistas.VouchersPage import VouchersPage
        self._pagina.controls.clear()
        self._pagina.add(VouchersPage(self._pagina, self._usuario))
        safe_update(self._pagina)
    
    def _ir_dashboard(self):
        """Navega al dashboard"""
        from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
        self._pagina.controls.clear()
        self._pagina.add(PaginaAdmin(self._pagina, self._usuario))
        safe_update(self._pagina)
    
    def _ir_a_vouchers(self):
        """Navega a vouchers"""
        from features.admin.presentation.pages.vistas.VouchersPage import VouchersPage
        self._pagina.controls.clear()
        self._pagina.add(VouchersPage(self._pagina, self._usuario))
        safe_update(self._pagina)
    
    def _ir_a_finanzas(self):
        """Navega a finanzas"""
        from features.admin.presentation.pages.vistas.FinanzasPage import FinanzasPage
        self._pagina.controls.clear()
        self._pagina.add(FinanzasPage(self._pagina, self._usuario))
        safe_update(self._pagina)
    
    def _ir_a_usuarios(self):
        """Navega a usuarios con UI moderna"""
        from features.admin.presentation.pages.vistas.UsuariosPageModerna import UsuariosPageModerna
        self._pagina.controls.clear()
        self._pagina.add(UsuariosPageModerna(self._pagina, self._usuario))
        safe_update(self._pagina)
    
    def _ir_a_auditoria(self):
        """Navega a auditoría"""
        from features.admin.presentation.pages.vistas.AuditoriaPageModerna import AuditoriaPageModerna
        self._pagina.controls.clear()
        self._pagina.add(AuditoriaPageModerna(self._pagina, self._usuario))
        safe_update(self._pagina)
    
    def _ir_a_extras(self):
        """Navega a extras"""
        from features.admin.presentation.pages.vistas.ExtrasPageModerna import ExtrasPageModerna
        self._pagina.controls.clear()
        self._pagina.add(ExtrasPageModerna(self._pagina, self._usuario))
        safe_update(self._pagina)
    
    def _ir_a_ofertas(self):
        """Navega a ofertas"""
        from features.admin.presentation.pages.vistas.OfertasPageModerna import OfertasPageModerna
        self._pagina.controls.clear()
        self._pagina.add(OfertasPageModerna(self._pagina, self._usuario))
        safe_update(self._pagina)
    
    def _ir_a_horarios(self):
        """Navega a horarios"""
        from features.admin.presentation.pages.vistas.HorariosPageModerna import HorariosPageModerna
        self._pagina.controls.clear()
        self._pagina.add(HorariosPageModerna(self._pagina, self._usuario))
        safe_update(self._pagina)
    
    def _ir_a_insumos(self):
        """Navega a insumos"""
        from features.admin.presentation.pages.vistas.InsumosPageModerna import InsumosPageModerna
        self._pagina.controls.clear()
        self._pagina.add(InsumosPageModerna(self._pagina, self._usuario))
        safe_update(self._pagina)
    
    def _ir_a_proveedores(self):
        """Navega a proveedores"""
        from features.admin.presentation.pages.vistas.ProveedoresPageModerna import ProveedoresPageModerna
        self._pagina.controls.clear()
        self._pagina.add(ProveedoresPageModerna(self._pagina, self._usuario))
        safe_update(self._pagina)
    
    def _ir_a_caja(self):
        """Navega a caja - versión moderna"""
        from features.admin.presentation.pages.vistas.CajasPageModerna import CajasPageModerna
        self._pagina.controls.clear()
        self._pagina.add(CajasPageModerna(self._pagina, self._usuario))
        safe_update(self._pagina)
    
    def _ir_a_resenas(self):
        """Navega a reseñas"""
        from features.admin.presentation.pages.vistas.ResenasPage import ResenasPage
        self._pagina.controls.clear()
        self._pagina.add(ResenasPage(self._pagina, self._usuario))
        safe_update(self._pagina)
    
    def _ir_a_sucursales(self):
        """Navega a sucursales"""
        from features.admin.presentation.pages.vistas.SucursalesPage import SucursalesPage
        self._pagina.controls.clear()
        self._pagina.add(SucursalesPage(self._pagina, self._usuario))
        safe_update(self._pagina)
    
    def _ir_a_roles(self):
        """Navega a roles (versión moderna)"""
        from features.admin.presentation.pages.gestion.RolesPage import RolesPage
        self._pagina.controls.clear()
        self._pagina.add(RolesPage(self._pagina, self._usuario))
        safe_update(self._pagina)
    
    def _cerrar_sesion(self):
        """Cierra la sesión"""
        if self._on_cerrar_sesion:
            self._on_cerrar_sesion()
        else:
            from features.autenticacion.presentation.pages.PaginaLogin import PaginaLogin
            self._pagina.controls.clear()
            self._pagina.add(PaginaLogin(self._pagina))
            safe_update(self._pagina)
    
    def actualizar_contenido(self, nuevo_contenido: ft.Control):
        """Actualiza el contenido de la vista"""
        self._contenido_container.content = nuevo_contenido
        safe_update(self._pagina)
    
    def obtener_sucursales_seleccionadas(self) -> Optional[List[int]]:
        """Retorna las sucursales actualmente seleccionadas"""
        if self._navbar:
            return self._navbar.obtener_sucursales_seleccionadas()
        return None
