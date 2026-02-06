"""
UsuariosPage - Gestión moderna de usuarios con diseño similar a SucursalesPage
"""
import flet as ft
from typing import Optional, List
from datetime import datetime

from core.Constantes import COLORES, ROLES
from core.decoradores.DecoradorVistas import REQUIERE_ROL
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_USUARIO, MODELO_ROL, MODELO_SUCURSAL
from features.admin.presentation.widgets import LayoutBase
import bcrypt


@REQUIERE_ROL(ROLES.ADMIN)
class UsuariosPage(LayoutBase):
    """Página de gestión de usuarios con diseño moderno"""
    
    def __init__(self, PAGINA: ft.Page, USUARIO):
        super().__init__(
            pagina=PAGINA,
            usuario=USUARIO,
            titulo_vista="👥 Usuarios",
            mostrar_boton_volver=True,
            index_navegacion=3,
            on_volver_dashboard=self._ir_dashboard,
            on_cerrar_sesion=self._cerrar_sesion
        )
        
        self._usuarios: List = []
        self._filtro_rol = "TODOS"
        self._filtro_estado = "TODOS"
        self._filtro_conexion = "TODOS"  # CONECTADOS, DESCONECTADOS, TODOS
        self._overlay_crear = None
        self._overlay_editar = None
        
        self._CONSTRUIR_UI()
        self._cargar_usuarios()
    
    def _CONSTRUIR_UI(self):
        """Construye la interfaz de usuarios con diseño moderno"""
        
        # Chips de filtros por estado de conexión
        def crear_chip_conexion(texto, valor, color_seleccionado=ft.Colors.BLUE_100):
            es_seleccionado = self._filtro_conexion == valor
            return ft.ElevatedButton(
                content=ft.Text(texto),
                on_click=lambda e: self._aplicar_filtro_conexion(valor),
                bgcolor=color_seleccionado if es_seleccionado else ft.Colors.GREY_200,
                color=ft.Colors.BLACK if es_seleccionado else ft.Colors.GREY_700,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=20),
                    padding=ft.padding.symmetric(horizontal=16, vertical=10)
                )
            )
        
        self._chips_conexion = ft.Row([
            crear_chip_conexion("🌍 Todos", "TODOS"),
            crear_chip_conexion("🟢 En línea", "CONECTADOS", ft.Colors.GREEN_100),
            crear_chip_conexion("⚫ Desconectados", "DESCONECTADOS", ft.Colors.GREY_300)
        ], spacing=12, scroll=ft.ScrollMode.ADAPTIVE)
        
        # Chips de filtros por estado
        def crear_chip_estado(texto, valor, color_seleccionado=ft.Colors.BLUE_100):
            es_seleccionado = self._filtro_estado == valor
            return ft.ElevatedButton(
                content=ft.Text(texto),
                on_click=lambda e: self._aplicar_filtro_estado(valor),
                bgcolor=color_seleccionado if es_seleccionado else ft.Colors.GREY_200,
                color=ft.Colors.BLACK if es_seleccionado else ft.Colors.GREY_700,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=20),
                    padding=ft.padding.symmetric(horizontal=16, vertical=10)
                )
            )
        
        self._chips_estado = ft.Row([
            crear_chip_estado("📋 Todos", "TODOS"),
            crear_chip_estado("✅ Activos", "ACTIVOS", ft.Colors.GREEN_100),
            crear_chip_estado("❌ Inactivos", "INACTIVOS", ft.Colors.RED_100)
        ], spacing=12, scroll=ft.ScrollMode.ADAPTIVE)
        
        # Chips de filtros por rol
        def crear_chip_rol(texto, valor, color_seleccionado=ft.Colors.BLUE_100):
            es_seleccionado = self._filtro_rol == valor
            return ft.ElevatedButton(
                content=ft.Text(texto),
                on_click=lambda e: self._aplicar_filtro_rol(valor),
                bgcolor=color_seleccionado if es_seleccionado else ft.Colors.GREY_200,
                color=ft.Colors.BLACK if es_seleccionado else ft.Colors.GREY_700,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=20),
                    padding=ft.padding.symmetric(horizontal=16, vertical=10)
                )
            )
        
        self._chips_rol = ft.Row([
            crear_chip_rol("👥 Todos", "TODOS"),
            crear_chip_rol("👑 SuperAdmin", "SUPERADMIN", ft.Colors.PURPLE_100),
            crear_chip_rol("🔧 Admin", "ADMIN", ft.Colors.BLUE_100),
            crear_chip_rol("✅ Gestora Calidad", "GESTORA_CALIDAD", ft.Colors.ORANGE_100)
        ], spacing=12, scroll=ft.ScrollMode.ADAPTIVE)
        
        # Contenedor de usuarios
        self._contenedor_usuarios = ft.Column(
            spacing=16,
            scroll=ft.ScrollMode.ADAPTIVE
        )
        
        # Construir layout con filtros y contenedor
        contenido = ft.Container(
            content=ft.Column([
                # Header con botón nuevo
                ft.Row([
                    ft.Text("Gestión de Usuarios", size=24, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon(ft.icons.Icons.PERSON_ADD, size=20),
                            ft.Text("Nuevo Usuario", weight=ft.FontWeight.W_600)
                        ], spacing=8),
                        on_click=lambda e: self._mostrar_overlay_crear(),
                        bgcolor=ft.Colors.BLUE_700,
                        color=ft.Colors.WHITE,
                        style=ft.ButtonStyle(
                            padding=ft.padding.symmetric(horizontal=20, vertical=12),
                            shape=ft.RoundedRectangleBorder(radius=10)
                        )
                    )
                ]),
                
                # Filtros en cards
                ft.Container(
                    content=ft.Column([
                        ft.Text("🌐 Estado de Conexión", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_700),
                        self._chips_conexion,
                        ft.Divider(height=12),
                        ft.Text("📊 Estado", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_700),
                        self._chips_estado,
                        ft.Divider(height=12),
                        ft.Text("🎭 Rol", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_700),
                        self._chips_rol
                    ], spacing=10),
                    padding=ft.padding.all(16),
                    border_radius=12,
                    bgcolor=ft.Colors.WHITE,
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=8,
                        color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                        offset=ft.Offset(0, 2)
                    )
                ),
                
                # Grid de usuarios
                ft.Container(
                    content=self._contenedor_usuarios,
                    expand=True
                )
            ], spacing=20),
            padding=ft.padding.all(20),
            expand=True
        )
        
        self.construir(contenido)
    
    def _aplicar_filtro_conexion(self, filtro):
        """Aplica filtro por estado de conexión"""
        self._filtro_conexion = filtro
        self._actualizar_chips_conexion()
        self._cargar_usuarios()
    
    def _aplicar_filtro_estado(self, filtro):
        """Aplica filtro por estado activo/inactivo"""
        self._filtro_estado = filtro
        self._actualizar_chips_estado()
        self._cargar_usuarios()
    
    def _aplicar_filtro_rol(self, filtro):
        """Aplica filtro por rol"""
        self._filtro_rol = filtro
        self._actualizar_chips_rol()
        self._cargar_usuarios()
    
    def _actualizar_chips_conexion(self):
        """Actualiza el color de los chips de conexión según selección"""
        for i, chip in enumerate(self._chips_conexion.controls):
            texto = chip.text
            if "Todos" in texto:
                es_seleccionado = self._filtro_conexion == "TODOS"
                chip.bgcolor = ft.Colors.BLUE_100 if es_seleccionado else ft.Colors.GREY_200
            elif "En línea" in texto:
                es_seleccionado = self._filtro_conexion == "CONECTADOS"
                chip.bgcolor = ft.Colors.GREEN_100 if es_seleccionado else ft.Colors.GREY_200
            elif "Desconectados" in texto:
                es_seleccionado = self._filtro_conexion == "DESCONECTADOS"
                chip.bgcolor = ft.Colors.GREY_300 if es_seleccionado else ft.Colors.GREY_200
            chip.color = ft.Colors.BLACK if es_seleccionado else ft.Colors.GREY_700
        self._pagina.update()
    
    def _actualizar_chips_estado(self):
        """Actualiza el color de los chips de estado según selección"""
        for chip in self._chips_estado.controls:
            texto = chip.text
            if "Todos" in texto:
                es_seleccionado = self._filtro_estado == "TODOS"
                chip.bgcolor = ft.Colors.BLUE_100 if es_seleccionado else ft.Colors.GREY_200
            elif "Activos" in texto:
                es_seleccionado = self._filtro_estado == "ACTIVOS"
                chip.bgcolor = ft.Colors.GREEN_100 if es_seleccionado else ft.Colors.GREY_200
            elif "Inactivos" in texto:
                es_seleccionado = self._filtro_estado == "INACTIVOS"
                chip.bgcolor = ft.Colors.RED_100 if es_seleccionado else ft.Colors.GREY_200
            chip.color = ft.Colors.BLACK if es_seleccionado else ft.Colors.GREY_700
        self._pagina.update()
    
    def _actualizar_chips_rol(self):
        """Actualiza el color de los chips de rol según selección"""
        for chip in self._chips_rol.controls:
            texto = chip.text
            if "Todos" in texto:
                es_seleccionado = self._filtro_rol == "TODOS"
                chip.bgcolor = ft.Colors.BLUE_100 if es_seleccionado else ft.Colors.GREY_200
            elif "SuperAdmin" in texto:
                es_seleccionado = self._filtro_rol == "SUPERADMIN"
                chip.bgcolor = ft.Colors.PURPLE_100 if es_seleccionado else ft.Colors.GREY_200
            elif "Admin" in texto:
                es_seleccionado = self._filtro_rol == "ADMIN"
                chip.bgcolor = ft.Colors.BLUE_100 if es_seleccionado else ft.Colors.GREY_200
            elif "Gestora" in texto or "Calidad" in texto:
                es_seleccionado = self._filtro_rol == "GESTORA_CALIDAD"
                chip.bgcolor = ft.Colors.ORANGE_100 if es_seleccionado else ft.Colors.GREY_200
            chip.color = ft.Colors.BLACK if es_seleccionado else ft.Colors.GREY_700
        self._pagina.update()
    
    def _cargar_usuarios(self):
        """Carga usuarios desde la BD con filtros"""
        with OBTENER_SESION() as sesion:
            query = sesion.query(MODELO_USUARIO)
            
            # Aplicar filtros
            if self._filtro_estado == "ACTIVOS":
                query = query.filter_by(ACTIVO=True)
            elif self._filtro_estado == "INACTIVOS":
                query = query.filter_by(ACTIVO=False)
            
            if self._filtro_rol != "TODOS":
                query = query.join(MODELO_USUARIO.ROLES).filter(MODELO_ROL.NOMBRE == self._filtro_rol)
            
            # TODO: filtro de conexión requiere tabla de sesiones activas
            
            self._usuarios = query.all()
        
        self._actualizar_ui()
    
    def _actualizar_ui(self):
        """Actualiza la UI con los usuarios filtrados"""
        self._contenedor_usuarios.controls.clear()
        
        if not self._usuarios:
            self._contenedor_usuarios.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.Icons.PEOPLE_OUTLINE, size=80, color=ft.Colors.GREY_400),
                        ft.Text("No hay usuarios", size=18, color=ft.Colors.GREY_600)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
                    alignment=ft.Alignment(0, 0),
                    padding=ft.padding.all(60)
                )
            )
        else:
            for usuario in self._usuarios:
                self._contenedor_usuarios.controls.append(
                    self._crear_card_usuario(usuario)
                )
        
        self._pagina.update()
    
    def _crear_card_usuario(self, usuario):
        """Crea card moderna para un usuario"""
        # Obtener rol
        rol_nombre = usuario.ROLES[0].NOMBRE if usuario.ROLES else "SIN ROL"
        
        # Colores por rol
        colores_rol = {
            "SUPERADMIN": ft.Colors.PURPLE_700,
            "ADMIN": ft.Colors.BLUE_700,
            "GESTORA_CALIDAD": ft.Colors.ORANGE_700
        }
        color_rol = colores_rol.get(rol_nombre, ft.Colors.GREY_700)
        
        # Estado
        estado_color = ft.Colors.GREEN_600 if usuario.ACTIVO else ft.Colors.RED_600
        estado_texto = "✅ Activo" if usuario.ACTIVO else "❌ Inactivo"
        
        # TODO: Estado de conexión real desde WebSocket
        conectado = False  # Placeholder
        conexion_badge = ft.Container(
            content=ft.Icon(
                ft.icons.Icons.CIRCLE,
                size=12,
                color=ft.Colors.GREEN_500 if conectado else ft.Colors.GREY_500
            ),
            tooltip="En línea" if conectado else "Desconectado"
        )
        
        return ft.Container(
            content=ft.Column([
                # Header del card
                ft.Row([
                    # Avatar + info
                    ft.Row([
                        ft.Container(
                            content=ft.Text(
                                usuario.NOMBRE_USUARIO[0].upper(),
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE
                            ),
                            width=56,
                            height=56,
                            border_radius=28,
                            bgcolor=color_rol,
                            alignment=ft.Alignment(0, 0)
                        ),
                        ft.Column([
                            ft.Row([
                                ft.Text(
                                    usuario.NOMBRE_USUARIO,
                                    size=18,
                                    weight=ft.FontWeight.BOLD
                                ),
                                conexion_badge
                            ], spacing=8),
                            ft.Text(
                                usuario.EMAIL,
                                size=13,
                                color=ft.Colors.GREY_600
                            ),
                            ft.Row([
                                ft.Container(
                                    content=ft.Text(
                                        rol_nombre,
                                        size=11,
                                        weight=ft.FontWeight.W_500,
                                        color=ft.Colors.WHITE
                                    ),
                                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                    border_radius=6,
                                    bgcolor=color_rol
                                ),
                                ft.Container(
                                    content=ft.Text(
                                        estado_texto,
                                        size=11,
                                        weight=ft.FontWeight.W_500,
                                        color=ft.Colors.WHITE
                                    ),
                                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                    border_radius=6,
                                    bgcolor=estado_color
                                )
                            ], spacing=8)
                        ], spacing=4, expand=True)
                    ], spacing=16, expand=True),
                    
                    # Acciones
                    ft.PopupMenuButton(
                        icon=ft.icons.Icons.MORE_VERT,
                        icon_color=ft.Colors.GREY_600,
                        items=[
                            ft.PopupMenuItem(
                                content=ft.Text("Editar información"),
                                icon=ft.icons.Icons.EDIT,
                                on_click=lambda e, u=usuario: self._mostrar_overlay_editar(u)
                            ),
                            ft.PopupMenuItem(
                                content=ft.Text("Cambiar estado"),
                                icon=ft.icons.Icons.SWAP_HORIZ,
                                on_click=lambda e, u=usuario: self._cambiar_estado(u)
                            ),
                            ft.PopupMenuItem(),
                            ft.PopupMenuItem(
                                content=ft.Text("Resetear contraseña"),
                                icon=ft.icons.Icons.LOCK_RESET,
                                on_click=lambda e, u=usuario: self._resetear_password(u)
                            )
                        ]
                    )
                ], spacing=16)
            ], spacing=12),
            padding=ft.padding.all(20),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 2)
            ),
            animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT)
        )
    
    def _mostrar_overlay_crear(self):
        """Overlay para crear usuario"""
        # TODO: Implementar overlay de creación
        self._pagina.snack_bar = ft.SnackBar(
            content=ft.Text("Función de crear usuario - Por implementar")
        )
        self._pagina.snack_bar.open = True
        self._pagina.update()
    
    def _mostrar_overlay_editar(self, usuario):
        """Overlay para editar usuario"""
        # TODO: Implementar overlay de edición
        self._pagina.snack_bar = ft.SnackBar(
            content=ft.Text(f"Editar usuario: {usuario.NOMBRE_USUARIO} - Por implementar")
        )
        self._pagina.snack_bar.open = True
        self._pagina.update()
    
    def _cambiar_estado(self, usuario):
        """Cambia estado activo/inactivo"""
        with OBTENER_SESION() as sesion:
            u = sesion.query(MODELO_USUARIO).filter_by(ID=usuario.ID).first()
            u.ACTIVO = not u.ACTIVO
            sesion.commit()
        
        self._cargar_usuarios()
        self._pagina.snack_bar = ft.SnackBar(
            content=ft.Text(f"✅ Usuario {'activado' if usuario.ACTIVO else 'desactivado'}"),
            bgcolor=ft.Colors.GREEN_600
        )
        self._pagina.snack_bar.open = True
        self._pagina.update()
    
    def _resetear_password(self, usuario):
        """Resetea la contraseña de un usuario"""
        # TODO: Implementar diálogo de reset de contraseña
        self._pagina.snack_bar = ft.SnackBar(
            content=ft.Text(f"Resetear contraseña: {usuario.NOMBRE_USUARIO} - Por implementar")
        )
        self._pagina.snack_bar.open = True
        self._pagina.update()
    
    def _ir_dashboard(self, e=None):
        """Vuelve al dashboard"""
        from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
        self._pagina.controls.clear()
        self._pagina.add(PaginaAdmin(self._pagina, self._usuario))
        self._pagina.update()
    
    def _cerrar_sesion(self, e=None):
        """Cierra sesión"""
        from features.autenticacion.presentation.pages.PaginaLogin import PaginaLogin
        self._pagina.controls.clear()
        self._pagina.add(PaginaLogin(self._pagina))
        self._pagina.update()
