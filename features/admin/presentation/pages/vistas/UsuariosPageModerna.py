"""
UsuariosPageModerna - Gestión completa de usuarios con diseño moderno y logs de auditoría
"""
import flet as ft
from typing import Optional, List
from datetime import datetime, timedelta
import bcrypt
from sqlalchemy.orm import joinedload

from core.Constantes import COLORES, ROLES
from core.decoradores.DecoradorVistas import REQUIERE_ROL
from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION, 
    MODELO_USUARIO, 
    MODELO_ROL, 
    MODELO_SUCURSAL,
    MODELO_AUDITORIA
)
from features.admin.presentation.widgets import LayoutBase


@REQUIERE_ROL(ROLES.ADMIN)
class UsuariosPageModerna(LayoutBase):
    """Página moderna de gestión de usuarios con logs de auditoría"""
    
    def __init__(self, PAGINA: ft.Page, USUARIO):
        super().__init__(
            pagina=PAGINA,
            usuario=USUARIO,
            titulo_vista="👥 Gestión de Usuarios",
            mostrar_boton_volver=True,
            index_navegacion=3,
            on_volver_dashboard=self._ir_dashboard,
            on_cerrar_sesion=self._cerrar_sesion
        )
        
        self._usuarios: List = []
        self._roles_disponibles: List = []
        self._sucursales_disponibles: List = []
        self._filtro_rol = "TODOS"
        self._filtro_estado = "TODOS"
        
        self._cargar_datos_auxiliares()
        self._CONSTRUIR_UI()
        self._cargar_usuarios()
    
    def _cargar_datos_auxiliares(self):
        """Carga roles y sucursales disponibles"""
        with OBTENER_SESION() as sesion:
            self._roles_disponibles = sesion.query(MODELO_ROL).filter_by(ACTIVO=True).all()
            self._sucursales_disponibles = sesion.query(MODELO_SUCURSAL).filter_by(ELIMINADA=False).all()
    
    def _CONSTRUIR_UI(self):
        """Construye la interfaz moderna de usuarios"""
        
        # DataTable de usuarios
        self._tabla_usuarios = ft.DataTable(
            columns=[
                ft.DataColumn(label=ft.Text("Usuario", weight=ft.FontWeight.BOLD, size=13)),
                ft.DataColumn(label=ft.Text("Email", weight=ft.FontWeight.BOLD, size=13)),
                ft.DataColumn(label=ft.Text("Rol", weight=ft.FontWeight.BOLD, size=13)),
                ft.DataColumn(label=ft.Text("Estado", weight=ft.FontWeight.BOLD, size=13)),
                ft.DataColumn(label=ft.Text("Última Conexión", weight=ft.FontWeight.BOLD, size=13)),
                ft.DataColumn(label=ft.Text("Acciones", weight=ft.FontWeight.BOLD, size=13)),
            ],
            rows=[],
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=10,
            horizontal_lines=ft.border.BorderSide(1, ft.Colors.GREY_200),
            heading_row_color={ft.ControlState.DEFAULT: ft.Colors.BLUE_50},
            data_row_max_height=float("inf"),
            column_spacing=20,
        )
        
        # Contenedor scrollable para la tabla
        self._contenedor_usuarios = ft.Column(
            controls=[self._tabla_usuarios],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
            spacing=16
        )
        
        # Chips de filtro por rol
        self._chips_rol = []
        filtros_rol = [
            ("TODOS", ft.icons.Icons.PEOPLE, "📊", ft.Colors.GREY_300),
            ("SUPERADMIN", ft.icons.Icons.ADMIN_PANEL_SETTINGS, "👑", ft.Colors.PURPLE_100),
            ("ADMIN", ft.icons.Icons.MANAGE_ACCOUNTS, "🔧", ft.Colors.BLUE_100),
            ("GESTORA_CALIDAD", ft.icons.Icons.VERIFIED_USER, "✅", ft.Colors.ORANGE_100),
            ("ATENCION", ft.icons.Icons.SUPPORT_AGENT, "🎯", ft.Colors.GREEN_100),
            ("COCINERO", ft.icons.Icons.RESTAURANT, "👨‍🍳", ft.Colors.RED_100),
            ("MOTORIZADO", ft.icons.Icons.TWO_WHEELER, "🏍️", ft.Colors.CYAN_100),
        ]
        
        for rol, icono, emoji, color_bg in filtros_rol:
            chip = self._crear_filtro_chip(rol, emoji, rol == "TODOS", color_bg)
            self._chips_rol.append(chip)
        
        filtros_rol_row = ft.Row(
            controls=self._chips_rol,
            spacing=10,
            wrap=True
        )
        
        # Chips de filtro por estado
        self._chips_estado = []
        filtros_estado = [
            ("TODOS", "📋 Todos", ft.Colors.GREY_300),
            ("ACTIVOS", "✅ Activos", ft.Colors.GREEN_100),
            ("INACTIVOS", "❌ Inactivos", ft.Colors.RED_100),
        ]
        
        for estado, texto, color_bg in filtros_estado:
            chip = self._crear_filtro_chip_estado(estado, texto, estado == "TODOS", color_bg)
            self._chips_estado.append(chip)
        
        filtros_estado_row = ft.Row(
            controls=self._chips_estado,
            spacing=10
        )
        
        # Botones de acción
        btn_crear = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.Icons.PERSON_ADD, size=20, color=ft.Colors.WHITE),
                ft.Text("Nuevo Usuario", size=14, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)
            ], spacing=8),
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            border_radius=12,
            bgcolor=ft.Colors.BLUE_700,
            on_click=lambda e: self._mostrar_overlay_crear(),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.3, ft.Colors.BLUE_700),
                offset=ft.Offset(0, 2)
            )
        )
        
        # Botón de logs (solo ADMIN y SUPERADMIN)
        btn_logs = None
        if self._usuario.TIENE_ROL(ROLES.ADMIN) or self._usuario.TIENE_ROL(ROLES.SUPERADMIN):
            btn_logs = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.icons.Icons.HISTORY, size=18, color=ft.Colors.ORANGE_700),
                    ft.Text("Ver Logs", size=13, weight=ft.FontWeight.W_500, color=ft.Colors.ORANGE_700)
                ], spacing=6),
                padding=ft.padding.symmetric(horizontal=16, vertical=10),
                border_radius=10,
                border=ft.border.all(2, ft.Colors.ORANGE_300),
                on_click=lambda e: self._mostrar_logs_auditoria(),
                tooltip="Ver logs de auditoría de usuarios"
            )
        
        # Header con estadísticas
        header = ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Row([
                        ft.Icon(ft.icons.Icons.PEOPLE, size=32, color=ft.Colors.BLUE_700),
                        ft.Text("Gestión de Usuarios", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_900)
                    ], spacing=12),
                    ft.Text(
                        "Administra usuarios, roles y permisos del sistema",
                        size=13,
                        color=ft.Colors.GREY_600
                    )
                ], spacing=6, expand=True),
                ft.Row([
                    btn_logs if btn_logs else ft.Container(width=0),
                    btn_crear
                ], spacing=12)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.only(bottom=16)
        )
        
        # Contenido principal
        contenido = ft.Container(
            content=ft.Column([
                header,
                ft.Text("Filtrar por Rol:", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_700),
                filtros_rol_row,
                ft.Container(height=8),
                ft.Text("Filtrar por Estado:", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_700),
                filtros_estado_row,
                ft.Container(height=8),
                self._contenedor_usuarios
            ], spacing=0, expand=True),
            expand=True,
            padding=24
        )
        
        self.construir(contenido)
    
    def _crear_filtro_chip(self, valor, emoji, seleccionado, color_bg):
        """Crea un chip de filtro de rol"""
        return ft.Container(
            content=ft.Text(
                f"{emoji} {valor.title()}",
                size=13,
                weight=ft.FontWeight.W_600 if seleccionado else ft.FontWeight.W_400,
                color=ft.Colors.GREY_900 if seleccionado else ft.Colors.GREY_700
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            border_radius=20,
            bgcolor=color_bg if seleccionado else ft.Colors.GREY_200,
            border=ft.border.all(2, ft.Colors.BLUE_400 if seleccionado else ft.Colors.TRANSPARENT),
            on_click=lambda e, v=valor: self._aplicar_filtro_rol(v),
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT)
        )
    
    def _crear_filtro_chip_estado(self, valor, texto, seleccionado, color_bg):
        """Crea un chip de filtro de estado"""
        return ft.Container(
            content=ft.Text(
                texto,
                size=13,
                weight=ft.FontWeight.W_600 if seleccionado else ft.FontWeight.W_400,
                color=ft.Colors.GREY_900 if seleccionado else ft.Colors.GREY_700
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            border_radius=20,
            bgcolor=color_bg if seleccionado else ft.Colors.GREY_200,
            border=ft.border.all(2, ft.Colors.GREEN_400 if seleccionado else ft.Colors.TRANSPARENT),
            on_click=lambda e, v=valor: self._aplicar_filtro_estado(v),
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT)
        )
    
    def _aplicar_filtro_rol(self, valor):
        """Aplica filtro por rol"""
        self._filtro_rol = valor
        self._actualizar_chips_rol()
        self._cargar_usuarios()
    
    def _aplicar_filtro_estado(self, valor):
        """Aplica filtro por estado"""
        self._filtro_estado = valor
        self._actualizar_chips_estado()
        self._cargar_usuarios()
    
    def _actualizar_chips_rol(self):
        """Actualiza visualmente los chips de rol"""
        filtros_rol_config = [
            ("TODOS", ft.Colors.GREY_300),
            ("SUPERADMIN", ft.Colors.PURPLE_100),
            ("ADMIN", ft.Colors.BLUE_100),
            ("GESTORA_CALIDAD", ft.Colors.ORANGE_100),
            ("ATENCION", ft.Colors.GREEN_100),
            ("COCINERO", ft.Colors.RED_100),
            ("MOTORIZADO", ft.Colors.CYAN_100),
        ]
        
        for i, (rol, color_bg) in enumerate(filtros_rol_config):
            if i < len(self._chips_rol):
                chip = self._chips_rol[i]
                seleccionado = self._filtro_rol == rol
                chip.bgcolor = color_bg if seleccionado else ft.Colors.GREY_200
                chip.border = ft.border.all(2, ft.Colors.BLUE_400 if seleccionado else ft.Colors.TRANSPARENT)
                if chip.content:
                    chip.content.weight = ft.FontWeight.W_600 if seleccionado else ft.FontWeight.W_400
        
        self._pagina.update()
    
    def _actualizar_chips_estado(self):
        """Actualiza visualmente los chips de estado"""
        filtros_estado_config = [
            ("TODOS", ft.Colors.GREY_300),
            ("ACTIVOS", ft.Colors.GREEN_100),
            ("INACTIVOS", ft.Colors.RED_100),
        ]
        
        for i, (estado, color_bg) in enumerate(filtros_estado_config):
            if i < len(self._chips_estado):
                chip = self._chips_estado[i]
                seleccionado = self._filtro_estado == estado
                chip.bgcolor = color_bg if seleccionado else ft.Colors.GREY_200
                chip.border = ft.border.all(2, ft.Colors.GREEN_400 if seleccionado else ft.Colors.TRANSPARENT)
                if chip.content:
                    chip.content.weight = ft.FontWeight.W_600 if seleccionado else ft.FontWeight.W_400
        
        self._pagina.update()
    
    def _cargar_usuarios(self):
        """Carga usuarios desde la BD con filtros"""
        with OBTENER_SESION() as sesion:
            # Hacer eager loading de ROLES para evitar DetachedInstanceError
            query = sesion.query(MODELO_USUARIO).options(joinedload(MODELO_USUARIO.ROLES))
            
            # Filtro por estado
            if self._filtro_estado == "ACTIVOS":
                query = query.filter_by(ACTIVO=True)
            elif self._filtro_estado == "INACTIVOS":
                query = query.filter_by(ACTIVO=False)
            
            usuarios = query.order_by(MODELO_USUARIO.FECHA_CREACION.desc()).all()
            
            # Filtro por rol (aplicado en Python porque es many-to-many)
            if self._filtro_rol != "TODOS":
                self._usuarios = [u for u in usuarios if any(r.NOMBRE == self._filtro_rol for r in u.ROLES)]
            else:
                self._usuarios = usuarios
        
        self._actualizar_ui()
    
    def _actualizar_ui(self):
        """Actualiza la tabla de usuarios"""
        self._tabla_usuarios.rows.clear()
        
        if not self._usuarios:
            # Fila vacía con mensaje
            self._tabla_usuarios.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.PEOPLE_OUTLINE, size=40, color=ft.Colors.GREY_400),
                            ft.Text(
                                "No hay usuarios" + (f" con filtro '{self._filtro_rol}' / '{self._filtro_estado}'" if self._filtro_rol != "TODOS" or self._filtro_estado != "TODOS" else ""),
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREY_600,
                                size=13
                            ),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                    )),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                ])
            )
        else:
            for usuario in self._usuarios:
                self._tabla_usuarios.rows.append(self._crear_fila_usuario(usuario))
        
        self._pagina.update()
    
    def _crear_fila_usuario(self, usuario) -> ft.DataRow:
        """Crea una fila de DataTable para un usuario"""
        # Obtener rol principal
        rol_principal = usuario.ROLES[0].NOMBRE if usuario.ROLES else "SIN ROL"
        
        # Configuración de colores por rol
        roles_config = {
            "SUPERADMIN": {"color": ft.Colors.PURPLE_700, "bg": ft.Colors.PURPLE_50, "emoji": "👑"},
            "ADMIN": {"color": ft.Colors.BLUE_700, "bg": ft.Colors.BLUE_50, "emoji": "🔧"},
            "GESTORA_CALIDAD": {"color": ft.Colors.ORANGE_700, "bg": ft.Colors.ORANGE_50, "emoji": "✅"},
            "ATENCION": {"color": ft.Colors.GREEN_700, "bg": ft.Colors.GREEN_50, "emoji": "🎯"},
            "COCINERO": {"color": ft.Colors.RED_700, "bg": ft.Colors.RED_50, "emoji": "👨‍🍳"},
            "MOTORIZADO": {"color": ft.Colors.CYAN_700, "bg": ft.Colors.CYAN_50, "emoji": "🏍️"},
        }
        
        config = roles_config.get(rol_principal, {
            "color": ft.Colors.GREY_700,
            "bg": ft.Colors.GREY_50,
            "emoji": "👤"
        })
        
        # Badge de rol
        rol_badge = ft.Container(
            content=ft.Text(
                f"{config['emoji']} {rol_principal}",
                size=11,
                weight=ft.FontWeight.BOLD,
                color=config["color"]
            ),
            padding=ft.Padding(8, 4, 8, 4),
            border_radius=12,
            bgcolor=config["bg"]
        )
        
        # Badge de estado
        estado_badge = ft.Container(
            content=ft.Row([
                ft.Icon(
                    ft.Icons.CHECK_CIRCLE if usuario.ACTIVO else ft.Icons.CANCEL,
                    size=14,
                    color=ft.Colors.GREEN_700 if usuario.ACTIVO else ft.Colors.RED_700
                ),
                ft.Text(
                    "Activo" if usuario.ACTIVO else "Inactivo",
                    size=11,
                    weight=ft.FontWeight.W_600,
                    color=ft.Colors.GREEN_700 if usuario.ACTIVO else ft.Colors.RED_700
                )
            ], spacing=4),
            padding=ft.Padding(8, 4, 8, 4),
            border_radius=12,
            bgcolor=ft.Colors.GREEN_50 if usuario.ACTIVO else ft.Colors.RED_50
        )
        
        # Última conexión
        ultima_conexion = usuario.ULTIMA_CONEXION.strftime('%d/%m/%Y %H:%M') if usuario.ULTIMA_CONEXION else 'Nunca'
        
        # Botones de acción
        acciones = ft.Row([
            ft.IconButton(
                icon=ft.Icons.INFO,
                tooltip="Ver detalles",
                icon_color=ft.Colors.BLUE_600,
                icon_size=20,
                on_click=lambda _, u=usuario: self._ver_detalles_usuario(u),
            ),
            ft.IconButton(
                icon=ft.Icons.EDIT,
                tooltip="Editar",
                icon_color=ft.Colors.ORANGE_600,
                icon_size=20,
                on_click=lambda _, u=usuario: self._mostrar_overlay_editar(u),
            ),
            ft.IconButton(
                icon=ft.Icons.ADMIN_PANEL_SETTINGS,
                tooltip="Cambiar rol",
                icon_color=ft.Colors.PURPLE_600,
                icon_size=20,
                on_click=lambda _, u=usuario: self._cambiar_rol(u),
            ),
            ft.IconButton(
                icon=ft.Icons.LOCK_RESET,
                tooltip="Resetear contraseña",
                icon_color=ft.Colors.GREY_600,
                icon_size=20,
                on_click=lambda _, u=usuario: self._resetear_contrasena(u),
            ),
            ft.IconButton(
                icon=ft.Icons.BLOCK if usuario.ACTIVO else ft.Icons.CHECK_CIRCLE,
                tooltip="Desactivar" if usuario.ACTIVO else "Activar",
                icon_color=ft.Colors.ORANGE_600 if usuario.ACTIVO else ft.Colors.GREEN_600,
                icon_size=20,
                on_click=lambda _, u=usuario: self._cambiar_estado(u),
            ),
        ], spacing=0)
        
        # Color de fila según estado
        row_color = None if usuario.ACTIVO else {ft.ControlState.DEFAULT: ft.Colors.GREY_100}
        
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Row([
                    ft.Container(
                        content=ft.Text(config["emoji"], size=18),
                        width=32,
                        height=32,
                        border_radius=16,
                        bgcolor=config["bg"],
                        alignment=ft.Alignment(0, 0)
                    ),
                    ft.Text(usuario.NOMBRE_USUARIO, weight=ft.FontWeight.BOLD, size=13),
                ], spacing=8)),
                ft.DataCell(ft.Text(usuario.EMAIL, size=12, color=ft.Colors.GREY_700)),
                ft.DataCell(rol_badge),
                ft.DataCell(estado_badge),
                ft.DataCell(ft.Text(ultima_conexion, size=12, color=ft.Colors.GREY_600)),
                ft.DataCell(acciones),
            ],
            color=row_color
        )
    
    def _ver_detalles_usuario(self, usuario):
        """Muestra overlay con detalles completos del usuario en una tabla"""
        # Obtener roles del usuario
        roles_texto = ", ".join([r.NOMBRE for r in usuario.ROLES]) if usuario.ROLES else "Sin roles"
        
        # Crear tabla de información
        tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Campo", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Valor", weight=ft.FontWeight.BOLD)),
            ],
            rows=[
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("ID", size=12)),
                    ft.DataCell(ft.Text(str(usuario.ID), size=12))
                ]),
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("Usuario", size=12)),
                    ft.DataCell(ft.Text(usuario.NOMBRE_USUARIO, size=12, weight=ft.FontWeight.BOLD))
                ]),
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("Email", size=12)),
                    ft.DataCell(ft.Text(usuario.EMAIL, size=12))
                ]),
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("Roles", size=12)),
                    ft.DataCell(ft.Text(roles_texto, size=12))
                ]),
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("Estado", size=12)),
                    ft.DataCell(ft.Row([
                        ft.Icon(
                            ft.icons.Icons.CHECK_CIRCLE if usuario.ACTIVO else ft.icons.Icons.CANCEL,
                            size=16,
                            color=ft.Colors.GREEN_700 if usuario.ACTIVO else ft.Colors.RED_700
                        ),
                        ft.Text(
                            "Activo" if usuario.ACTIVO else "Inactivo",
                            size=12,
                            color=ft.Colors.GREEN_700 if usuario.ACTIVO else ft.Colors.RED_700
                        )
                    ], spacing=4))
                ]),
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("Verificado", size=12)),
                    ft.DataCell(ft.Text("Sí" if usuario.VERIFICADO else "No", size=12))
                ]),
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("Fecha Creación", size=12)),
                    ft.DataCell(ft.Text(
                        usuario.FECHA_CREACION.strftime("%d/%m/%Y %H:%M") if usuario.FECHA_CREACION else "N/A",
                        size=12
                    ))
                ]),
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("Última Conexión", size=12)),
                    ft.DataCell(ft.Text(
                        usuario.ULTIMA_CONEXION.strftime("%d/%m/%Y %H:%M") if usuario.ULTIMA_CONEXION else "Nunca",
                        size=12
                    ))
                ]),
            ],
            border=ft.border.all(1, ft.Colors.GREY_300),
            heading_row_color=ft.Colors.BLUE_50,
            border_radius=8,
        )
        
        overlay = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.icons.Icons.PERSON, color=ft.Colors.BLUE_700, size=28),
                ft.Text(f"Detalles de {usuario.NOMBRE_USUARIO}", size=20, weight=ft.FontWeight.BOLD)
            ], spacing=12),
            content=ft.Container(
                content=ft.Column([
                    tabla
                ], scroll=ft.ScrollMode.ADAPTIVE),
                width=600,
                height=400

            ),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda e: setattr(overlay, 'open', False) or self._pagina.update())
            ]
        )
        
        self._pagina.overlay.append(overlay)
        overlay.open = True
        self._pagina.update()
    
    def _mostrar_overlay_crear(self):
        """Muestra overlay para crear nuevo usuario"""
        # Campos del formulario
        nombre_usuario_field = ft.TextField(
            label="Nombre de usuario",
            hint_text="Ej: jperez",
            prefix_icon=ft.icons.Icons.PERSON,
            border_radius=10,
            filled=True,
            bgcolor=ft.Colors.GREY_50
        )
        
        email_field = ft.TextField(
            label="Email",
            hint_text="Ej: jperez@empresa.com",
            prefix_icon=ft.icons.Icons.EMAIL,
            border_radius=10,
            filled=True,
            bgcolor=ft.Colors.GREY_50,
            keyboard_type=ft.KeyboardType.EMAIL
        )
        
        contrasena_field = ft.TextField(
            label="Contraseña",
            hint_text="Mínimo 6 caracteres",
            prefix_icon=ft.icons.Icons.LOCK,
            border_radius=10,
            filled=True,
            bgcolor=ft.Colors.GREY_50,
            password=True,
            can_reveal_password=True
        )
        
        # Dropdown de roles
        rol_dropdown = ft.Dropdown(
            label="Rol",
            hint_text="Selecciona un rol",
            border_radius=10,
            filled=True,
            bgcolor=ft.Colors.GREY_50,
            options=[ft.dropdown.Option(r.NOMBRE, r.NOMBRE) for r in self._roles_disponibles]
        )
        
        # Dropdown de sucursales
        sucursal_dropdown = ft.Dropdown(
            label="Sucursal (opcional)",
            hint_text="Selecciona una sucursal",
            border_radius=10,
            filled=True,
            bgcolor=ft.Colors.GREY_50,
            options=[ft.dropdown.Option(str(s.ID), s.NOMBRE) for s in self._sucursales_disponibles]
        )
        
        # Switch de activo
        activo_switch = ft.Switch(
            label="Usuario activo",
            value=True
        )
        
        def guardar(e):
            # Validaciones
            if not nombre_usuario_field.value or not email_field.value or not contrasena_field.value or not rol_dropdown.value:
                self._pagina.snack_bar = ft.SnackBar(
                    content=ft.Row([
                        ft.Icon(ft.icons.Icons.ERROR, color=ft.Colors.WHITE),
                        ft.Text("⚠️ Completa todos los campos obligatorios", color=ft.Colors.WHITE)
                    ], spacing=8),
                    bgcolor=ft.Colors.RED_600
                )
                self._pagina.snack_bar.open = True
                self._pagina.update()
                return
            
            if len(contrasena_field.value) < 6:
                self._pagina.snack_bar = ft.SnackBar(
                    content=ft.Text("⚠️ La contraseña debe tener mínimo 6 caracteres"),
                    bgcolor=ft.Colors.RED_600
                )
                self._pagina.snack_bar.open = True
                self._pagina.update()
                return
            
            try:
                with OBTENER_SESION() as sesion:
                    # Verificar si usuario ya existe
                    existe = sesion.query(MODELO_USUARIO).filter(
                        (MODELO_USUARIO.NOMBRE_USUARIO == nombre_usuario_field.value) |
                        (MODELO_USUARIO.EMAIL == email_field.value)
                    ).first()
                    
                    if existe:
                        self._pagina.snack_bar = ft.SnackBar(
                            content=ft.Text("❌ Usuario o email ya existe"),
                            bgcolor=ft.Colors.RED_600
                        )
                        self._pagina.snack_bar.open = True
                        self._pagina.update()
                        return
                    
                    # Hashear contraseña
                    contrasena_hash = bcrypt.hashpw(contrasena_field.value.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    
                    # Crear usuario
                    nuevo_usuario = MODELO_USUARIO(
                        NOMBRE_USUARIO=nombre_usuario_field.value,
                        EMAIL=email_field.value,
                        CONTRASENA_HASH=contrasena_hash,
                        HUELLA_DISPOSITIVO="admin-created",
                        ACTIVO=activo_switch.value,
                        VERIFICADO=True
                    )
                    sesion.add(nuevo_usuario)
                    sesion.flush()  # Para obtener el ID
                    
                    # Asignar rol
                    rol = sesion.query(MODELO_ROL).filter_by(NOMBRE=rol_dropdown.value).first()
                    if rol:
                        nuevo_usuario.ROLES.append(rol)
                    
                    sesion.commit()
                    
                    # Registrar en auditoría
                    auditoria = MODELO_AUDITORIA(
                        USUARIO_ID=self._usuario.ID,
                        ACCION="USUARIO_CREADO",
                        ENTIDAD="USUARIO",
                        ENTIDAD_ID=nuevo_usuario.ID,
                        DETALLE=f"Usuario '{nuevo_usuario.NOMBRE_USUARIO}' creado con rol '{rol_dropdown.value}'"
                    )
                    sesion.add(auditoria)
                    sesion.commit()
                
                overlay.open = False
                self._cargar_usuarios()
                
                self._pagina.snack_bar = ft.SnackBar(
                    content=ft.Row([
                        ft.Icon(ft.icons.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE),
                        ft.Text(f"✅ Usuario '{nombre_usuario_field.value}' creado exitosamente", color=ft.Colors.WHITE)
                    ], spacing=8),
                    bgcolor=ft.Colors.GREEN_600
                )
                self._pagina.snack_bar.open = True
                self._pagina.update()
                
            except Exception as ex:
                self._pagina.snack_bar = ft.SnackBar(
                    content=ft.Text(f"❌ Error al crear usuario: {str(ex)}"),
                    bgcolor=ft.Colors.RED_600
                )
                self._pagina.snack_bar.open = True
                self._pagina.update()
        
        overlay = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.icons.Icons.PERSON_ADD, color=ft.Colors.BLUE_700, size=28),
                ft.Text("Crear Nuevo Usuario", size=20, weight=ft.FontWeight.BOLD)
            ], spacing=12),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Complete la información del nuevo usuario", size=13, color=ft.Colors.GREY_600),
                    ft.Divider(height=20),
                    nombre_usuario_field,
                    email_field,
                    contrasena_field,
                    rol_dropdown,
                    sucursal_dropdown,
                    activo_switch
                ], tight=True, spacing=16, scroll=ft.ScrollMode.ADAPTIVE),
                width=500,
                height=500
            ),
            actions=[
                ft.TextButton(
                    content=ft.Row([
                        ft.Icon(ft.icons.Icons.CLOSE, size=18),
                        ft.Text("Cancelar")
                    ], spacing=6),
                    on_click=lambda e: setattr(overlay, 'open', False) or self._pagina.update()
                ),
                ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.icons.Icons.SAVE, size=18),
                        ft.Text("Crear Usuario", weight=ft.FontWeight.W_600)
                    ], spacing=6),
                    on_click=guardar,
                    bgcolor=ft.Colors.BLUE_700,
                    color=ft.Colors.WHITE,
                    style=ft.ButtonStyle(
                        padding=ft.padding.symmetric(horizontal=20, vertical=12),
                        shape=ft.RoundedRectangleBorder(radius=10)
                    )
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        self._pagina.overlay.append(overlay)
        overlay.open = True
        self._pagina.update()
    
    def _mostrar_overlay_editar(self, usuario):
        """Muestra overlay para editar usuario"""
        # Pre-llenar campos
        email_field = ft.TextField(
            label="Email",
            value=usuario.EMAIL,
            prefix_icon=ft.icons.Icons.EMAIL,
            border_radius=10,
            filled=True,
            bgcolor=ft.Colors.GREY_50
        )
        
        activo_switch = ft.Switch(
            label="Usuario activo",
            value=usuario.ACTIVO
        )
        
        def guardar(e):
            if not email_field.value:
                self._pagina.snack_bar = ft.SnackBar(
                    content=ft.Text("⚠️ El email es obligatorio"),
                    bgcolor=ft.Colors.RED_600
                )
                self._pagina.snack_bar.open = True
                self._pagina.update()
                return
            
            try:
                with OBTENER_SESION() as sesion:
                    u = sesion.query(MODELO_USUARIO).filter_by(ID=usuario.ID).first()
                    u.EMAIL = email_field.value
                    u.ACTIVO = activo_switch.value
                    sesion.commit()
                    
                    # Auditoría
                    auditoria = MODELO_AUDITORIA(
                        USUARIO_ID=self._usuario.ID,
                        ACCION="USUARIO_ACTUALIZADO",
                        ENTIDAD="USUARIO",
                        ENTIDAD_ID=usuario.ID,
                        DETALLE=f"Usuario '{usuario.NOMBRE_USUARIO}' actualizado"
                    )
                    sesion.add(auditoria)
                    sesion.commit()
                
                overlay.open = False
                self._cargar_usuarios()
                
                self._pagina.snack_bar = ft.SnackBar(
                    content=ft.Text("✅ Usuario actualizado correctamente"),
                    bgcolor=ft.Colors.GREEN_600
                )
                self._pagina.snack_bar.open = True
                self._pagina.update()
                
            except Exception as ex:
                self._pagina.snack_bar = ft.SnackBar(
                    content=ft.Text(f"❌ Error: {str(ex)}"),
                    bgcolor=ft.Colors.RED_600
                )
                self._pagina.snack_bar.open = True
                self._pagina.update()
        
        overlay = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.icons.Icons.EDIT, color=ft.Colors.ORANGE_700, size=28),
                ft.Text(f"Editar: {usuario.NOMBRE_USUARIO}", size=20, weight=ft.FontWeight.BOLD)
            ], spacing=12),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Modifica la información del usuario", size=13, color=ft.Colors.GREY_600),
                    ft.Divider(height=20),
                    ft.Text(f"Usuario: {usuario.NOMBRE_USUARIO}", weight=ft.FontWeight.BOLD),
                    email_field,
                    activo_switch
                ], tight=True, spacing=16),
                width=450
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: setattr(overlay, 'open', False) or self._pagina.update()),
                ft.ElevatedButton(
                    content=ft.Text("Guardar Cambios"),
                    on_click=guardar,
                    bgcolor=ft.Colors.ORANGE_700,
                    color=ft.Colors.WHITE
                )
            ]
        )
        
        self._pagina.overlay.append(overlay)
        overlay.open = True
        self._pagina.update()
    
    def _cambiar_rol(self, usuario):
        """Muestra overlay para cambiar rol del usuario"""
        # Obtener roles actuales del usuario
        roles_actuales = [r.NOMBRE for r in usuario.ROLES]
        
        # Checkboxes para cada rol
        rol_checks = {}
        rol_controls = []
        
        for rol in self._roles_disponibles:
            check = ft.Checkbox(
                label=f"{rol.NOMBRE} - {rol.DESCRIPCION or 'Sin descripción'}",
                value=rol.NOMBRE in roles_actuales
            )
            rol_checks[rol.NOMBRE] = check
            rol_controls.append(check)
        
        def guardar(e):
            try:
                with OBTENER_SESION() as sesion:
                    u = sesion.query(MODELO_USUARIO).filter_by(ID=usuario.ID).first()
                    
                    # Limpiar roles actuales
                    u.ROLES.clear()
                    
                    # Agregar roles seleccionados
                    roles_nuevos = []
                    for nombre_rol, check in rol_checks.items():
                        if check.value:
                            rol = sesion.query(MODELO_ROL).filter_by(NOMBRE=nombre_rol).first()
                            if rol:
                                u.ROLES.append(rol)
                                roles_nuevos.append(nombre_rol)
                    
                    sesion.commit()
                    
                    # Auditoría
                    auditoria = MODELO_AUDITORIA(
                        USUARIO_ID=self._usuario.ID,
                        ACCION="USUARIO_CAMBIO_ROL",
                        ENTIDAD="USUARIO",
                        ENTIDAD_ID=usuario.ID,
                        DETALLE=f"Roles de '{usuario.NOMBRE_USUARIO}' cambiados a: {', '.join(roles_nuevos)}"
                    )
                    sesion.add(auditoria)
                    sesion.commit()
                
                overlay.open = False
                self._cargar_usuarios()
                
                self._pagina.snack_bar = ft.SnackBar(
                    content=ft.Text("✅ Roles actualizados correctamente"),
                    bgcolor=ft.Colors.GREEN_600
                )
                self._pagina.snack_bar.open = True
                self._pagina.update()
                
            except Exception as ex:
                self._pagina.snack_bar = ft.SnackBar(
                    content=ft.Text(f"❌ Error: {str(ex)}"),
                    bgcolor=ft.Colors.RED_600
                )
                self._pagina.snack_bar.open = True
                self._pagina.update()
        
        overlay = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.icons.Icons.ADMIN_PANEL_SETTINGS, color=ft.Colors.PURPLE_700, size=28),
                ft.Text(f"Cambiar Roles: {usuario.NOMBRE_USUARIO}", size=18, weight=ft.FontWeight.BOLD)
            ], spacing=12),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Selecciona los roles para este usuario", size=13, color=ft.Colors.GREY_600),
                    ft.Divider(height=20),
                    ft.Container(
                        content=ft.Column(rol_controls, spacing=12),
                        padding=ft.padding.all(10),
                        border_radius=10,
                        bgcolor=ft.Colors.BLUE_50
                    )
                ], tight=True, spacing=16, scroll=ft.ScrollMode.ADAPTIVE),
                width=500,
                height=400
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: setattr(overlay, 'open', False) or self._pagina.update()),
                ft.ElevatedButton(
                    content=ft.Text("Guardar Roles"),
                    on_click=guardar,
                    bgcolor=ft.Colors.PURPLE_700,
                    color=ft.Colors.WHITE
                )
            ]
        )
        
        self._pagina.overlay.append(overlay)
        overlay.open = True
        self._pagina.update()
    
    def _resetear_contrasena(self, usuario):
        """Muestra overlay para resetear contraseña"""
        nueva_contrasena_field = ft.TextField(
            label="Nueva contraseña",
            hint_text="Mínimo 6 caracteres",
            prefix_icon=ft.icons.Icons.LOCK,
            border_radius=10,
            filled=True,
            bgcolor=ft.Colors.GREY_50,
            password=True,
            can_reveal_password=True
        )
        
        confirmar_contrasena_field = ft.TextField(
            label="Confirmar contraseña",
            prefix_icon=ft.icons.Icons.LOCK_RESET,
            border_radius=10,
            filled=True,
            bgcolor=ft.Colors.GREY_50,
            password=True,
            can_reveal_password=True
        )
        
        def guardar(e):
            if not nueva_contrasena_field.value or not confirmar_contrasena_field.value:
                self._pagina.snack_bar = ft.SnackBar(
                    content=ft.Text("⚠️ Completa ambos campos"),
                    bgcolor=ft.Colors.RED_600
                )
                self._pagina.snack_bar.open = True
                self._pagina.update()
                return
            
            if nueva_contrasena_field.value != confirmar_contrasena_field.value:
                self._pagina.snack_bar = ft.SnackBar(
                    content=ft.Text("⚠️ Las contraseñas no coinciden"),
                    bgcolor=ft.Colors.RED_600
                )
                self._pagina.snack_bar.open = True
                self._pagina.update()
                return
            
            if len(nueva_contrasena_field.value) < 6:
                self._pagina.snack_bar = ft.SnackBar(
                    content=ft.Text("⚠️ La contraseña debe tener mínimo 6 caracteres"),
                    bgcolor=ft.Colors.RED_600
                )
                self._pagina.snack_bar.open = True
                self._pagina.update()
                return
            
            try:
                # Hashear nueva contraseña
                contrasena_hash = bcrypt.hashpw(nueva_contrasena_field.value.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                with OBTENER_SESION() as sesion:
                    u = sesion.query(MODELO_USUARIO).filter_by(ID=usuario.ID).first()
                    u.CONTRASENA_HASH = contrasena_hash
                    sesion.commit()
                    
                    # Auditoría
                    auditoria = MODELO_AUDITORIA(
                        USUARIO_ID=self._usuario.ID,
                        ACCION="USUARIO_RESET_CONTRASENA",
                        ENTIDAD="USUARIO",
                        ENTIDAD_ID=usuario.ID,
                        DETALLE=f"Contraseña reseteada para '{usuario.NOMBRE_USUARIO}'"
                    )
                    sesion.add(auditoria)
                    sesion.commit()
                
                overlay.open = False
                
                self._pagina.snack_bar = ft.SnackBar(
                    content=ft.Text(f"✅ Contraseña reseteada para '{usuario.NOMBRE_USUARIO}'"),
                    bgcolor=ft.Colors.GREEN_600
                )
                self._pagina.snack_bar.open = True
                self._pagina.update()
                
            except Exception as ex:
                self._pagina.snack_bar = ft.SnackBar(
                    content=ft.Text(f"❌ Error: {str(ex)}"),
                    bgcolor=ft.Colors.RED_600
                )
                self._pagina.snack_bar.open = True
                self._pagina.update()
        
        overlay = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.icons.Icons.LOCK_RESET, color=ft.Colors.RED_700, size=28),
                ft.Text(f"Resetear Contraseña: {usuario.NOMBRE_USUARIO}", size=18, weight=ft.FontWeight.BOLD)
            ], spacing=12),
            content=ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.icons.Icons.WARNING, color=ft.Colors.ORANGE_700),
                            ft.Text("Se cambiará la contraseña del usuario", size=13, color=ft.Colors.GREY_700)
                        ], spacing=8),
                        padding=ft.padding.all(12),
                        border_radius=8,
                        bgcolor=ft.Colors.ORANGE_50
                    ),
                    ft.Divider(height=20),
                    nueva_contrasena_field,
                    confirmar_contrasena_field
                ], tight=True, spacing=16),
                width=450
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: setattr(overlay, 'open', False) or self._pagina.update()),
                ft.ElevatedButton(
                    content=ft.Text("Resetear Contraseña"),
                    on_click=guardar,
                    bgcolor=ft.Colors.RED_700,
                    color=ft.Colors.WHITE
                )
            ]
        )
        
        self._pagina.overlay.append(overlay)
        overlay.open = True
        self._pagina.update()
    
    def _cambiar_estado(self, usuario):
        """Cambia el estado activo/inactivo del usuario"""
        nuevo_estado = not usuario.ACTIVO
        
        with OBTENER_SESION() as sesion:
            u = sesion.query(MODELO_USUARIO).filter_by(ID=usuario.ID).first()
            u.ACTIVO = nuevo_estado
            sesion.commit()
            
            # Registrar en auditoría
            auditoria = MODELO_AUDITORIA(
                USUARIO_ID=self._usuario.ID,
                ACCION="USUARIO_CAMBIO_ESTADO",
                ENTIDAD="USUARIO",
                ENTIDAD_ID=usuario.ID,
                DETALLE=f"Usuario '{usuario.NOMBRE_USUARIO}' {'activado' if nuevo_estado else 'desactivado'}"
            )
            sesion.add(auditoria)
            sesion.commit()
        
        self._cargar_usuarios()
        
        self._pagina.snack_bar = ft.SnackBar(
            content=ft.Text(
                f"✅ Usuario '{usuario.NOMBRE_USUARIO}' {'activado' if nuevo_estado else 'desactivado'}",
                color=ft.Colors.WHITE
            ),
            bgcolor=ft.Colors.GREEN_700 if nuevo_estado else ft.Colors.ORANGE_700
        )
        self._pagina.snack_bar.open = True
        self._pagina.update()
    
    def _mostrar_logs_auditoria(self):
        """Muestra overlay con logs de auditoría de usuarios"""
        with OBTENER_SESION() as sesion:
            # Últimos 50 logs relacionados con usuarios
            logs = sesion.query(MODELO_AUDITORIA).filter(
                MODELO_AUDITORIA.ACCION.like("%USUARIO%")
            ).order_by(MODELO_AUDITORIA.FECHA.desc()).limit(50).all()
            
            # Crear lista de tuplas con la información necesaria (dentro de la sesión)
            logs_data = []
            for log in logs:
                # Color según tipo de acción
                color_accion = ft.Colors.BLUE_700
                if "CREADO" in log.ACCION:
                    color_accion = ft.Colors.GREEN_700
                elif "ELIMINADO" in log.ACCION or "DESACTIVADO" in log.ACCION:
                    color_accion = ft.Colors.RED_700
                elif "ACTUALIZADO" in log.ACCION or "CAMBIO" in log.ACCION:
                    color_accion = ft.Colors.ORANGE_700
                
                # Obtener nombre del usuario que realizó la acción (dentro de la sesión)
                usuario_accion = sesion.query(MODELO_USUARIO).filter_by(ID=log.USUARIO_ID).first()
                nombre_usuario = usuario_accion.NOMBRE_USUARIO if usuario_accion else "Sistema"
                
                # Guardar toda la info necesaria
                logs_data.append({
                    'fecha': log.FECHA.strftime("%d/%m/%Y\n%H:%M:%S") if log.FECHA else "N/A",
                    'accion': log.ACCION.replace("USUARIO_", "").replace("_", " "),
                    'color': color_accion,
                    'usuario': nombre_usuario,
                    'detalle': log.DETALLE or "-"
                })
        
        # Ahora trabajamos con los datos fuera de la sesión
        if not logs_data:
            overlay = ft.AlertDialog(
                title=ft.Text("📋 Logs de Auditoría"),
                content=ft.Text("No hay registros de auditoría de usuarios."),
                actions=[ft.TextButton("Cerrar", on_click=lambda e: setattr(overlay, 'open', False) or self._pagina.update())]
            )
        else:
            # Crear tabla de logs con los datos extraídos
            filas = []
            for log_data in logs_data:
                filas.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(
                                log_data['fecha'],
                                size=11
                            )),
                            ft.DataCell(ft.Container(
                                content=ft.Text(
                                    log_data['accion'],
                                    size=11,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE
                                ),
                                padding=6,
                                border_radius=6,
                                bgcolor=log_data['color']
                            )),
                            ft.DataCell(ft.Text(log_data['usuario'], size=11)),
                            ft.DataCell(ft.Text(
                                log_data['detalle'],
                                size=11,
                                max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS
                            ))
                        ]
                    )
                )
            
            tabla = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Fecha/Hora", weight=ft.FontWeight.BOLD, size=12)),
                    ft.DataColumn(ft.Text("Acción", weight=ft.FontWeight.BOLD, size=12)),
                    ft.DataColumn(ft.Text("Usuario", weight=ft.FontWeight.BOLD, size=12)),
                    ft.DataColumn(ft.Text("Detalles", weight=ft.FontWeight.BOLD, size=12)),
                ],
                rows=filas,
                border=ft.border.all(1, ft.Colors.GREY_300),
                heading_row_color=ft.Colors.ORANGE_50,
                border_radius=8,
                horizontal_lines=ft.BorderSide(1, ft.Colors.GREY_200),
            )
            
            overlay = ft.AlertDialog(
                title=ft.Row([
                    ft.Icon(ft.icons.Icons.HISTORY, color=ft.Colors.ORANGE_700, size=28),
                    ft.Text("📋 Logs de Auditoría de Usuarios", size=20, weight=ft.FontWeight.BOLD)
                ], spacing=12),
                content=ft.Container(
                    content=ft.Column([
                        ft.Text(
                            f"Mostrando los últimos {len(logs_data)} registros",
                            size=13,
                            color=ft.Colors.GREY_600,
                            italic=True
                        ),
                        ft.Divider(height=20),
                        ft.Container(
                            content=ft.Column([tabla], scroll=ft.ScrollMode.ADAPTIVE),
                            height=500
                        )
                    ]),
                    width=900
                ),
                actions=[
                    ft.TextButton("Cerrar", on_click=lambda e: setattr(overlay, 'open', False) or self._pagina.update())
                ]
            )
        
        self._pagina.overlay.append(overlay)
        overlay.open = True
        self._pagina.update()
    
    def _ir_dashboard(self):
        """Vuelve al dashboard"""
        from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
        self._pagina.controls.clear()
        self._pagina.add(PaginaAdmin(self._pagina, self._usuario))
        self._pagina.update()
    
    def _cerrar_sesion(self):
        """Cierra sesión"""
        self._pagina.controls.clear()
        from main import crear_login_page
        self._pagina.add(crear_login_page(self._pagina))
        self._pagina.update()
