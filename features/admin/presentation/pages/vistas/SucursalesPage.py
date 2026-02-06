"""
SucursalesPage - Gestión moderna de sucursales con CRUD completo
"""
import flet as ft
from typing import Optional, List
from datetime import datetime

from core.Constantes import COLORES, ROLES
from core.decoradores.DecoradorVistas import REQUIERE_ROL
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_SUCURSAL
from features.admin.presentation.widgets import LayoutBase


@REQUIERE_ROL(ROLES.ADMIN)
class SucursalesPage(LayoutBase):
    """Página de gestión de sucursales con diseño moderno"""
    
    def __init__(self, PAGINA: ft.Page, USUARIO):
        super().__init__(
            pagina=PAGINA,
            usuario=USUARIO,
            titulo_vista="🏪 Sucursales",
            mostrar_boton_volver=True,
            index_navegacion=2,
            on_volver_dashboard=self._ir_dashboard,
            on_cerrar_sesion=self._cerrar_sesion
        )
        
        self._sucursales: List = []
        self._filtro_estado = "TODAS"
        self._overlay_crear = None
        self._overlay_editar = None
        
        self._CONSTRUIR_UI()
        self._cargar_sucursales()
    
    def _CONSTRUIR_UI(self):
        """Construye la interfaz de sucursales con diseño moderno"""
        
        # DataTable de sucursales
        self._tabla_sucursales = ft.DataTable(
            columns=[
                ft.DataColumn(label=ft.Text("Nombre", weight=ft.FontWeight.BOLD, size=13)),
                ft.DataColumn(label=ft.Text("Dirección", weight=ft.FontWeight.BOLD, size=13)),
                ft.DataColumn(label=ft.Text("Teléfono", weight=ft.FontWeight.BOLD, size=13)),
                ft.DataColumn(label=ft.Text("Horario", weight=ft.FontWeight.BOLD, size=13)),
                ft.DataColumn(label=ft.Text("Estado", weight=ft.FontWeight.BOLD, size=13)),
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
        self._contenedor_sucursales = ft.Column(
            controls=[self._tabla_sucursales],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
            spacing=16
        )
        
        # Chips de filtro modernos
        self._filtro_chips = []
        filtros_config = [
            ("TODAS", ft.icons.Icons.APPS, "📊"),
            ("ACTIVA", ft.icons.Icons.CHECK_CIRCLE, "✅"),
            ("MANTENIMIENTO", ft.icons.Icons.BUILD, "🔧"),
            ("VACACIONES", ft.icons.Icons.BEACH_ACCESS, "🏖️"),
            ("CERRADA", ft.icons.Icons.CANCEL, "❌"),
        ]
        
        for estado, icono, emoji in filtros_config:
            chip = self._crear_filtro_chip_moderno(estado, icono, emoji, estado == "TODAS")
            self._filtro_chips.append(chip)
        
        filtros = ft.Row(
            controls=self._filtro_chips,
            spacing=10,
            wrap=True
        )
        
        # Botón crear sucursal con estilo moderno
        btn_crear = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.Icons.ADD, size=20, color=ft.Colors.WHITE),
                ft.Text("Nueva Sucursal", size=14, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)
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
            ),
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            on_hover=lambda e: self._animar_boton_crear(e)
        )
        
        # Botón para ver eliminadas (solo SUPERADMIN)
        btn_ver_eliminadas = None
        if self._usuario.TIENE_ROL(ROLES.SUPERADMIN):
            btn_ver_eliminadas = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.icons.Icons.RESTORE_FROM_TRASH, size=18, color=ft.Colors.ORANGE_700),
                    ft.Text("Ver Eliminadas", size=13, weight=ft.FontWeight.W_500, color=ft.Colors.ORANGE_700)
                ], spacing=6),
                padding=ft.padding.symmetric(horizontal=16, vertical=10),
                border_radius=10,
                border=ft.border.all(2, ft.Colors.ORANGE_300),
                on_click=lambda e: self._ver_sucursales_eliminadas(),
                tooltip="Ver y restaurar sucursales eliminadas"
            )
        
        # Header con estadísticas
        header = ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Row([
                        ft.Icon(ft.icons.Icons.STORE, size=32, color=ft.Colors.BLUE_700),
                        ft.Text("Gestión de Sucursales", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_900)
                    ], spacing=12),
                    ft.Text(
                        "Administra tus sucursales, horarios y estados operativos",
                        size=13,
                        color=ft.Colors.GREY_600
                    )
                ], spacing=6, expand=True),
                ft.Row([
                    btn_ver_eliminadas if btn_ver_eliminadas else ft.Container(width=0),
                    btn_crear
                ], spacing=12)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.only(bottom=16)
        )
        
        contenido = ft.Container(
            content=ft.Column([
                header,
                filtros,
                ft.Container(height=8),  # Espaciador
                self._contenedor_sucursales
            ], spacing=0, expand=True),
            expand=True,
            padding=24
        )
        
        self.construir(contenido)
    
    def _animar_boton_crear(self, e):
        """Anima el botón de crear al hacer hover"""
        if e.data == "true":  # Mouse enter
            e.control.scale = 1.05
            e.control.shadow = ft.BoxShadow(
                spread_radius=0,
                blur_radius=12,
                color=ft.Colors.with_opacity(0.4, ft.Colors.BLUE_700),
                offset=ft.Offset(0, 4)
            )
        else:  # Mouse leave
            e.control.scale = 1.0
            e.control.shadow = ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.3, ft.Colors.BLUE_700),
                offset=ft.Offset(0, 2)
            )
        e.control.update()

    
    def _crear_filtro_chip(self, estado: str, icono, seleccionado: bool):
        """Crea un chip de filtro (método legacy)"""
        def on_click(e):
            self._filtro_estado = estado
            self._cargar_sucursales()
        
        return ft.Container(
            content=ft.Row([
                ft.Icon(icono, size=18, color=ft.Colors.WHITE if seleccionado else ft.Colors.BLUE_700),
                ft.Text(estado, size=13, weight=ft.FontWeight.W_500, 
                       color=ft.Colors.WHITE if seleccionado else ft.Colors.BLUE_700)
            ], spacing=6),
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            border_radius=20,
            bgcolor=ft.Colors.BLUE_700 if seleccionado else ft.Colors.BLUE_50,
            on_click=on_click
        )
    
    def _crear_filtro_chip_moderno(self, estado: str, icono, emoji: str, seleccionado: bool):
        """Crea un chip de filtro con diseño moderno y animaciones"""
        def on_click(e):
            self._filtro_estado = estado
            # Actualizar estado de todos los chips
            for idx, chip in enumerate(self._filtro_chips):
                es_seleccionado = (idx == self._filtro_chips.index(e.control))
                if es_seleccionado:
                    chip.bgcolor = ft.Colors.BLUE_700
                    chip.border = ft.border.all(2, ft.Colors.BLUE_700)
                    chip.content.controls[0].color = ft.Colors.WHITE  # emoji/icono
                    chip.content.controls[1].color = ft.Colors.WHITE  # texto
                else:
                    chip.bgcolor = ft.Colors.WHITE
                    chip.border = ft.border.all(1, ft.Colors.GREY_300)
                    chip.content.controls[0].color = ft.Colors.GREY_700
                    chip.content.controls[1].color = ft.Colors.GREY_700
                chip.update()
            self._cargar_sucursales()
        
        return ft.Container(
            content=ft.Row([
                ft.Text(emoji, size=16),
                ft.Text(
                    estado.capitalize() if estado != "TODAS" else estado,
                    size=13,
                    weight=ft.FontWeight.W_600,
                    color=ft.Colors.WHITE if seleccionado else ft.Colors.GREY_700
                )
            ], spacing=6),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            border_radius=20,
            bgcolor=ft.Colors.BLUE_700 if seleccionado else ft.Colors.WHITE,
            border=ft.border.all(2 if seleccionado else 1, ft.Colors.BLUE_700 if seleccionado else ft.Colors.GREY_300),
            on_click=on_click,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=4 if seleccionado else 2,
                color=ft.Colors.with_opacity(0.2 if seleccionado else 0.1, ft.Colors.BLUE_700),
                offset=ft.Offset(0, 2)
            ) if seleccionado else None
        )

    
    def _cargar_sucursales(self):
        """Carga sucursales desde la BD (excluye eliminadas)"""
        with OBTENER_SESION() as sesion:
            # Filtrar solo sucursales NO eliminadas
            query = sesion.query(MODELO_SUCURSAL).filter_by(ELIMINADA=False)
            
            if self._filtro_estado != "TODAS":
                query = query.filter_by(ESTADO=self._filtro_estado)
            
            self._sucursales = query.order_by(MODELO_SUCURSAL.FECHA_CREACION.desc()).all()
        
        self._actualizar_ui()
    
    def _actualizar_ui(self):
        """Actualiza la tabla de sucursales"""
        self._tabla_sucursales.rows.clear()
        
        if not self._sucursales:
            # Fila vacía con mensaje
            self._tabla_sucursales.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.STORE, size=40, color=ft.Colors.GREY_400),
                            ft.Text(
                                "No hay sucursales" + (f" en estado {self._filtro_estado}" if self._filtro_estado != "TODAS" else ""),
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
            for sucursal in self._sucursales:
                self._tabla_sucursales.rows.append(self._crear_fila_sucursal(sucursal))
        
        self._pagina.update()
    
    def _crear_fila_sucursal(self, sucursal) -> ft.DataRow:
        """Crea una fila de DataTable para una sucursal"""
        # Configuración de estado
        estado_config = {
            "ACTIVA": {"color": ft.Colors.GREEN_600, "bg": ft.Colors.GREEN_50, "emoji": "✅"},
            "MANTENIMIENTO": {"color": ft.Colors.ORANGE_600, "bg": ft.Colors.ORANGE_50, "emoji": "🔧"},
            "VACACIONES": {"color": ft.Colors.BLUE_600, "bg": ft.Colors.BLUE_50, "emoji": "🏖️"},
            "CERRADA": {"color": ft.Colors.RED_600, "bg": ft.Colors.RED_50, "emoji": "❌"},
        }
        config = estado_config.get(sucursal.ESTADO, {
            "color": ft.Colors.GREY_600, "bg": ft.Colors.GREY_50, "emoji": "❓"
        })
        
        # Badge de estado
        estado_badge = ft.Container(
            content=ft.Row([
                ft.Text(config["emoji"], size=14),
                ft.Text(
                    sucursal.ESTADO,
                    size=11,
                    weight=ft.FontWeight.BOLD,
                    color=config["color"]
                )
            ], spacing=4),
            padding=ft.Padding(8, 4, 8, 4),
            border_radius=12,
            bgcolor=config["bg"]
        )
        
        # Botones de acción
        acciones = ft.Row([
            ft.IconButton(
                icon=ft.Icons.EDIT,
                tooltip="Editar",
                icon_color=ft.Colors.ORANGE_600,
                icon_size=20,
                on_click=lambda _, s=sucursal: self._mostrar_overlay_editar(s),
            ),
            ft.IconButton(
                icon=ft.Icons.SWAP_HORIZ,
                tooltip="Cambiar estado",
                icon_color=ft.Colors.BLUE_600,
                icon_size=20,
                on_click=lambda _, s=sucursal: self._mostrar_menu_estado(s),
            ),
            ft.IconButton(
                icon=ft.Icons.DELETE,
                tooltip="Eliminar",
                icon_color=ft.Colors.RED_600,
                icon_size=20,
                on_click=lambda _, s=sucursal: self._confirmar_eliminar(s),
            ),
        ], spacing=0)
        
        # Color de fila según estado
        row_color_map = {
            "ACTIVA": None,
            "MANTENIMIENTO": {ft.ControlState.DEFAULT: ft.Colors.ORANGE_50},
            "VACACIONES": {ft.ControlState.DEFAULT: ft.Colors.BLUE_50},
            "CERRADA": {ft.ControlState.DEFAULT: ft.Colors.RED_50},
        }
        row_color = row_color_map.get(sucursal.ESTADO)
        
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.STORE, size=18, color=config["color"]),
                        width=32,
                        height=32,
                        border_radius=8,
                        bgcolor=config["bg"],
                        alignment=ft.Alignment(0, 0)
                    ),
                    ft.Text(sucursal.NOMBRE, weight=ft.FontWeight.BOLD, size=13),
                ], spacing=8)),
                ft.DataCell(ft.Text(
                    sucursal.DIRECCION or "No especificada",
                    size=12,
                    color=ft.Colors.GREY_700,
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS
                )),
                ft.DataCell(ft.Text(sucursal.TELEFONO or "-", size=12, color=ft.Colors.GREY_600)),
                ft.DataCell(ft.Text(
                    sucursal.HORARIO or "-",
                    size=12,
                    color=ft.Colors.GREY_600,
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS
                )),
                ft.DataCell(estado_badge),
                ft.DataCell(acciones),
            ],
            color=row_color
        )
    
    def _crear_card_sucursal_legacy(self, sucursal):
        """Crea un card para una sucursal con diseño moderno"""
        # Configuración de estado con gradientes y estilos
        estado_config = {
            "ACTIVA": {
                "icono": ft.icons.Icons.CHECK_CIRCLE,
                "color": ft.Colors.GREEN_600,
                "bg_color": ft.Colors.GREEN_50,
                "emoji": "✅",
                "descripcion": "Operando normalmente"
            },
            "MANTENIMIENTO": {
                "icono": ft.icons.Icons.BUILD,
                "color": ft.Colors.ORANGE_600,
                "bg_color": ft.Colors.ORANGE_50,
                "emoji": "🔧",
                "descripcion": "En mantenimiento"
            },
            "VACACIONES": {
                "icono": ft.icons.Icons.BEACH_ACCESS,
                "color": ft.Colors.BLUE_600,
                "bg_color": ft.Colors.BLUE_50,
                "emoji": "🏖️",
                "descripcion": "Temporalmente cerrada"
            },
            "CERRADA": {
                "icono": ft.icons.Icons.CANCEL,
                "color": ft.Colors.RED_600,
                "bg_color": ft.Colors.RED_50,
                "emoji": "❌",
                "descripcion": "Fuera de servicio"
            }
        }
        config = estado_config.get(sucursal.ESTADO, {
            "icono": ft.icons.Icons.HELP_OUTLINE,
            "color": ft.Colors.GREY_600,
            "bg_color": ft.Colors.GREY_50,
            "emoji": "❓",
            "descripcion": "Estado desconocido"
        })
        
        return ft.Container(
            content=ft.Column([
                # Header con gradiente sutil
                ft.Container(
                    content=ft.Row([
                        # Icono principal con animación
                        ft.Container(
                            content=ft.Stack([
                                ft.Container(
                                    width=60,
                                    height=60,
                                    border_radius=30,
                                    bgcolor=config["bg_color"],
                                ),
                                ft.Container(
                                    content=ft.Icon(ft.icons.Icons.STORE, size=28, color=config["color"]),
                                    width=60,
                                    height=60,
                                    alignment=ft.alignment.Alignment(0, 0)
                                ),
                            ]),
                            animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_OUT)
                        ),
                        
                        # Info principal
                        ft.Column([
                            ft.Text(
                                sucursal.NOMBRE,
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREY_900
                            ),
                            ft.Container(
                                content=ft.Row([
                                    ft.Text(config["emoji"], size=14),
                                    ft.Text(
                                        sucursal.ESTADO,
                                        size=13,
                                        weight=ft.FontWeight.W_600,
                                        color=config["color"]
                                    ),
                                ], spacing=4),
                                padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                border_radius=12,
                                bgcolor=config["bg_color"]
                            ),
                            ft.Text(
                                config["descripcion"],
                                size=11,
                                color=ft.Colors.GREY_500,
                                italic=True
                            )
                        ], spacing=4, expand=True),
                        
                        # Menú de acciones
                        ft.PopupMenuButton(
                            icon=ft.icons.Icons.MORE_VERT,
                            icon_color=ft.Colors.GREY_600,
                            items=[
                                ft.PopupMenuItem(
                                    content=ft.Text("Editar información"),
                                    icon=ft.icons.Icons.EDIT,
                                    on_click=lambda e, s=sucursal: self._mostrar_overlay_editar(s)
                                ),
                                ft.PopupMenuItem(
                                    content=ft.Text("Cambiar estado"),
                                    icon=ft.icons.Icons.SWAP_HORIZ,
                                    on_click=lambda e, s=sucursal: self._mostrar_menu_estado(s)
                                ),
                                ft.PopupMenuItem(),
                                ft.PopupMenuItem(
                                    content=ft.Text("Eliminar"),
                                    icon=ft.icons.Icons.DELETE,
                                    on_click=lambda e, s=sucursal: self._confirmar_eliminar(s)
                                )
                            ]
                        )
                    ], spacing=14),
                    padding=ft.padding.only(bottom=12)
                ),
                
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                
                # Información detallada con iconos modernos
                ft.Container(
                    content=ft.Column([
                        self._crear_info_row_moderna(
                            ft.icons.Icons.LOCATION_ON,
                            "Dirección",
                            sucursal.DIRECCION or "No especificada",
                            ft.Colors.PURPLE_600
                        ),
                        self._crear_info_row_moderna(
                            ft.icons.Icons.PHONE,
                            "Teléfono",
                            sucursal.TELEFONO or "No especificado",
                            ft.Colors.BLUE_600
                        ),
                        self._crear_info_row_moderna(
                            ft.icons.Icons.ACCESS_TIME,
                            "Horario",
                            sucursal.HORARIO or "No especificado",
                            ft.Colors.ORANGE_600
                        ),
                        self._crear_info_row_moderna(
                            ft.icons.Icons.CALENDAR_TODAY,
                            "Creada",
                            sucursal.FECHA_CREACION.strftime("%d/%m/%Y %H:%M") if sucursal.FECHA_CREACION else "N/A",
                            ft.Colors.GREEN_600
                        )
                    ], spacing=10),
                    padding=ft.padding.only(top=12)
                )
            ], spacing=0),
            padding=20,
            border_radius=16,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, ft.Colors.GREY_200),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=12,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 4)
            ),
            animate=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
            on_hover=lambda e: self._animar_hover_card(e)
        )
    
    def _crear_info_row(self, icono, label, valor):
        """Crea una fila de información (método legacy, usar _crear_info_row_moderna)"""
        return ft.Row([
            ft.Icon(icono, size=16, color=ft.Colors.GREY_600),
            ft.Text(f"{label}:", size=13, color=ft.Colors.GREY_700, weight=ft.FontWeight.W_500),
            ft.Text(valor, size=13, color=ft.Colors.GREY_900, expand=True)
        ], spacing=8)
    
    def _crear_info_row_moderna(self, icono, label, valor, color_icono):
        """Crea una fila de información con diseño moderno"""
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(icono, size=18, color=color_icono),
                    width=32,
                    height=32,
                    border_radius=8,
                    bgcolor=ft.Colors.with_opacity(0.1, color_icono),
                    alignment=ft.alignment.Alignment(0, 0)
                ),
                ft.Column([
                    ft.Text(
                        label,
                        size=11,
                        color=ft.Colors.GREY_500,
                        weight=ft.FontWeight.W_500
                    ),
                    ft.Text(
                        valor,
                        size=13,
                        color=ft.Colors.GREY_900,
                        weight=ft.FontWeight.W_400
                    )
                ], spacing=2, expand=True)
            ], spacing=10),
            padding=ft.padding.all(8),
            border_radius=10,
            bgcolor=ft.Colors.GREY_50
        )
    
    def _animar_hover_card(self, e):
        """Animación al pasar el mouse sobre la card"""
        if e.data == "true":  # Mouse enter
            e.control.shadow = ft.BoxShadow(
                spread_radius=2,
                blur_radius=16,
                color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
                offset=ft.Offset(0, 6)
            )
        else:  # Mouse leave
            e.control.shadow = ft.BoxShadow(
                spread_radius=1,
                blur_radius=12,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 4)
            )
        e.control.update()

    
    def _mostrar_overlay_crear(self):
        """Muestra overlay moderno para crear sucursal"""
        nombre_field = ft.TextField(
            label="Nombre de la sucursal",
            hint_text="Ej: Sucursal Centro",
            prefix_icon=ft.icons.Icons.STORE,
            border_radius=10,
            filled=True,
            bgcolor=ft.Colors.GREY_50
        )
        direccion_field = ft.TextField(
            label="Dirección completa",
            hint_text="Ej: Av. Principal 123, Lima",
            prefix_icon=ft.icons.Icons.LOCATION_ON,
            border_radius=10,
            filled=True,
            bgcolor=ft.Colors.GREY_50,
            multiline=True,
            min_lines=2,
            max_lines=3
        )
        telefono_field = ft.TextField(
            label="Teléfono de contacto",
            hint_text="Ej: 987654321",
            prefix_icon=ft.icons.Icons.PHONE,
            border_radius=10,
            filled=True,
            bgcolor=ft.Colors.GREY_50
        )
        horario_field = ft.TextField(
            label="Horario de atención",
            hint_text="Ej: Lun-Vie 8am-6pm, Sáb 9am-1pm",
            prefix_icon=ft.icons.Icons.ACCESS_TIME,
            border_radius=10,
            filled=True,
            bgcolor=ft.Colors.GREY_50,
            multiline=True,
            min_lines=2,
            max_lines=3
        )
        estado_dropdown = ft.Dropdown(
            label="Estado inicial",
            value="ACTIVA",
            border_radius=10,
            filled=True,
            bgcolor=ft.Colors.GREY_50,
            options=[
                ft.dropdown.Option("ACTIVA", "✅ ACTIVA - Operando normalmente"),
                ft.dropdown.Option("MANTENIMIENTO", "🔧 MANTENIMIENTO - En reparaciones"),
                ft.dropdown.Option("VACACIONES", "🏖️ VACACIONES - Cerrada temporalmente"),
                ft.dropdown.Option("CERRADA", "❌ CERRADA - Fuera de servicio")
            ]
        )
        
        def guardar(e):
            if not nombre_field.value or not direccion_field.value:
                self._pagina.snack_bar = ft.SnackBar(
                    content=ft.Row([
                        ft.Icon(ft.icons.Icons.ERROR, color=ft.Colors.WHITE),
                        ft.Text("⚠️ Nombre y dirección son obligatorios", color=ft.Colors.WHITE)
                    ], spacing=8),
                    bgcolor=ft.Colors.RED_600
                )
                self._pagina.snack_bar.open = True
                self._pagina.update()
                return
            
            with OBTENER_SESION() as sesion:
                nueva = MODELO_SUCURSAL(
                    NOMBRE=nombre_field.value,
                    DIRECCION=direccion_field.value,
                    TELEFONO=telefono_field.value,
                    HORARIO=horario_field.value,
                    ESTADO=estado_dropdown.value,
                    ACTIVA=estado_dropdown.value == "ACTIVA"
                )
                sesion.add(nueva)
                sesion.commit()
            
            self._overlay_crear.open = False
            self._cargar_sucursales()
            
            # Recargar dropdown de sucursales en navbar
            if hasattr(self, '_navbar') and self._navbar:
                self._navbar.recargar_sucursales()
            
            self._pagina.snack_bar = ft.SnackBar(
                content=ft.Row([
                    ft.Icon(ft.icons.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE),
                    ft.Text(f"✅ Sucursal '{nombre_field.value}' creada exitosamente", color=ft.Colors.WHITE)
                ], spacing=8),
                bgcolor=ft.Colors.GREEN_600
            )
            self._pagina.snack_bar.open = True
            self._pagina.update()
        
        self._overlay_crear = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.icons.Icons.ADD_BUSINESS, color=ft.Colors.BLUE_700, size=28),
                ft.Text("Nueva Sucursal", size=20, weight=ft.FontWeight.BOLD)
            ], spacing=12),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Complete la información de la nueva sucursal", size=13, color=ft.Colors.GREY_600),
                    ft.Divider(height=20),
                    nombre_field,
                    direccion_field,
                    telefono_field,
                    horario_field,
                    estado_dropdown
                ], tight=True, spacing=16),
                width=500
            ),
            actions=[
                ft.TextButton(
                    content=ft.Row([
                        ft.Icon(ft.icons.Icons.CLOSE, size=18),
                        ft.Text("Cancelar")
                    ], spacing=6),
                    on_click=lambda e: setattr(self._overlay_crear, 'open', False) or self._pagina.update()
                ),
                ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.icons.Icons.CHECK, size=18),
                        ft.Text("Crear Sucursal", weight=ft.FontWeight.W_600)
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
        
        self._pagina.overlay.append(self._overlay_crear)
        self._overlay_crear.open = True
        self._pagina.update()
    
    def _mostrar_overlay_editar(self, sucursal):
        """Muestra overlay moderno para editar sucursal"""
        nombre_field = ft.TextField(
            label="Nombre de la sucursal",
            value=sucursal.NOMBRE,
            prefix_icon=ft.icons.Icons.STORE,
            border_radius=10,
            filled=True,
            bgcolor=ft.Colors.GREY_50
        )
        direccion_field = ft.TextField(
            label="Dirección completa",
            value=sucursal.DIRECCION,
            prefix_icon=ft.icons.Icons.LOCATION_ON,
            border_radius=10,
            filled=True,
            bgcolor=ft.Colors.GREY_50,
            multiline=True,
            min_lines=2,
            max_lines=3
        )
        telefono_field = ft.TextField(
            label="Teléfono de contacto",
            value=sucursal.TELEFONO or "",
            prefix_icon=ft.icons.Icons.PHONE,
            border_radius=10,
            filled=True,
            bgcolor=ft.Colors.GREY_50
        )
        horario_field = ft.TextField(
            label="Horario de atención",
            value=sucursal.HORARIO or "",
            prefix_icon=ft.icons.Icons.ACCESS_TIME,
            border_radius=10,
            filled=True,
            bgcolor=ft.Colors.GREY_50,
            multiline=True,
            min_lines=2,
            max_lines=3
        )
        
        def guardar(e):
            with OBTENER_SESION() as sesion:
                s = sesion.query(MODELO_SUCURSAL).filter_by(ID=sucursal.ID).first()
                s.NOMBRE = nombre_field.value
                s.DIRECCION = direccion_field.value
                s.TELEFONO = telefono_field.value
                s.HORARIO = horario_field.value
                sesion.commit()
            
            self._overlay_editar.open = False
            self._cargar_sucursales()
            
            # Recargar dropdown de sucursales en navbar
            if hasattr(self, '_navbar') and self._navbar:
                self._navbar.recargar_sucursales()
            
            self._pagina.snack_bar = ft.SnackBar(
                content=ft.Row([
                    ft.Icon(ft.icons.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE),
                    ft.Text("✅ Sucursal actualizada correctamente", color=ft.Colors.WHITE)
                ], spacing=8),
                bgcolor=ft.Colors.GREEN_600
            )
            self._pagina.snack_bar.open = True
            self._pagina.update()
        
        self._overlay_editar = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.icons.Icons.EDIT, color=ft.Colors.ORANGE_700, size=28),
                ft.Text("Editar Sucursal", size=20, weight=ft.FontWeight.BOLD)
            ], spacing=12),
            content=ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.icons.Icons.INFO, size=16, color=ft.Colors.BLUE_700),
                            ft.Text(
                                f"Modificando: {sucursal.NOMBRE}",
                                size=13,
                                color=ft.Colors.BLUE_700,
                                weight=ft.FontWeight.W_500
                            )
                        ], spacing=8),
                        padding=ft.padding.all(12),
                        border_radius=8,
                        bgcolor=ft.Colors.BLUE_50
                    ),
                    ft.Divider(height=20),
                    nombre_field,
                    direccion_field,
                    telefono_field,
                    horario_field
                ], tight=True, spacing=16),
                width=500
            ),
            actions=[
                ft.TextButton(
                    content=ft.Row([
                        ft.Icon(ft.icons.Icons.CLOSE, size=18),
                        ft.Text("Cancelar")
                    ], spacing=6),
                    on_click=lambda e: setattr(self._overlay_editar, 'open', False) or self._pagina.update()
                ),
                ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.icons.Icons.SAVE, size=18),
                        ft.Text("Guardar Cambios", weight=ft.FontWeight.W_600)
                    ], spacing=6),
                    on_click=guardar,
                    bgcolor=ft.Colors.ORANGE_700,
                    color=ft.Colors.WHITE,
                    style=ft.ButtonStyle(
                        padding=ft.padding.symmetric(horizontal=20, vertical=12),
                        shape=ft.RoundedRectangleBorder(radius=10)
                    )
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        self._pagina.overlay.append(self._overlay_editar)
        self._overlay_editar.open = True
        self._pagina.update()
    
    def _mostrar_menu_estado(self, sucursal):
        """Muestra menú moderno para cambiar estado de sucursal"""
        def cambiar_estado(nuevo_estado):
            with OBTENER_SESION() as sesion:
                s = sesion.query(MODELO_SUCURSAL).filter_by(ID=sucursal.ID).first()
                s.ESTADO = nuevo_estado
                s.ACTIVA = nuevo_estado == "ACTIVA"
                sesion.commit()
            
            overlay.open = False
            self._cargar_sucursales()
            
            # Recargar dropdown de sucursales en navbar
            if hasattr(self, '_navbar') and self._navbar:
                self._navbar.recargar_sucursales()
            
            estados_emoji = {
                "ACTIVA": "✅",
                "MANTENIMIENTO": "🔧",
                "VACACIONES": "🏖️",
                "CERRADA": "❌"
            }
            
            self._pagina.snack_bar = ft.SnackBar(
                content=ft.Row([
                    ft.Icon(ft.icons.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE),
                    ft.Text(
                        f"{estados_emoji.get(nuevo_estado, '✓')} Estado cambiado a {nuevo_estado}",
                        color=ft.Colors.WHITE
                    )
                ], spacing=8),
                bgcolor=ft.Colors.GREEN_600
            )
            self._pagina.snack_bar.open = True
            self._pagina.update()
        
        def crear_boton_estado(estado, icono, color, emoji, descripcion):
            return ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(icono, size=24, color=color),
                        width=48,
                        height=48,
                        border_radius=24,
                        bgcolor=ft.Colors.with_opacity(0.1, color),
                        alignment=ft.alignment.Alignment(0, 0)
                    ),
                    ft.Column([
                        ft.Row([
                            ft.Text(emoji, size=14),
                            ft.Text(estado, size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_900)
                        ], spacing=6),
                        ft.Text(descripcion, size=12, color=ft.Colors.GREY_600)
                    ], spacing=2, expand=True)
                ], spacing=14),
                padding=ft.padding.all(14),
                border_radius=12,
                bgcolor=ft.Colors.WHITE,
                border=ft.border.all(2, ft.Colors.with_opacity(0.3, color)),
                on_click=lambda e: cambiar_estado(estado),
                animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
                on_hover=lambda e: self._animar_hover_boton_estado(e, color)
            )
        
        overlay = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.icons.Icons.SWAP_HORIZ, color=ft.Colors.BLUE_700, size=28),
                ft.Column([
                    ft.Text("Cambiar Estado", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Sucursal: {sucursal.NOMBRE}", size=13, color=ft.Colors.GREY_600)
                ], spacing=2, expand=True)
            ], spacing=12),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "Selecciona el nuevo estado operativo para esta sucursal:",
                        size=13,
                        color=ft.Colors.GREY_600
                    ),
                    ft.Divider(height=20),
                    crear_boton_estado(
                        "ACTIVA",
                        ft.icons.Icons.CHECK_CIRCLE,
                        ft.Colors.GREEN_600,
                        "✅",
                        "Operando normalmente"
                    ),
                    crear_boton_estado(
                        "MANTENIMIENTO",
                        ft.icons.Icons.BUILD,
                        ft.Colors.ORANGE_600,
                        "🔧",
                        "En reparación o actualización"
                    ),
                    crear_boton_estado(
                        "VACACIONES",
                        ft.icons.Icons.BEACH_ACCESS,
                        ft.Colors.BLUE_600,
                        "🏖️",
                        "Cerrada temporalmente"
                    ),
                    crear_boton_estado(
                        "CERRADA",
                        ft.icons.Icons.CANCEL,
                        ft.Colors.RED_600,
                        "❌",
                        "Fuera de servicio"
                    )
                ], tight=True, spacing=12),
                width=450
            ),
            actions=[
                ft.TextButton(
                    content=ft.Row([
                        ft.Icon(ft.icons.Icons.CLOSE, size=18),
                        ft.Text("Cancelar")
                    ], spacing=6),
                    on_click=lambda e: setattr(overlay, 'open', False) or self._pagina.update()
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        self._pagina.overlay.append(overlay)
        overlay.open = True
        self._pagina.update()
    
    def _animar_hover_boton_estado(self, e, color):
        """Anima botones de estado al hacer hover"""
        if e.data == "true":  # Mouse enter
            e.control.bgcolor = ft.Colors.with_opacity(0.05, color)
            e.control.border = ft.border.all(2, color)
        else:  # Mouse leave
            e.control.bgcolor = ft.Colors.WHITE
            e.control.border = ft.border.all(2, ft.Colors.with_opacity(0.3, color))
        e.control.update()
    
    def _confirmar_eliminar(self, sucursal):
        """Confirma eliminación lógica de sucursal con diseño moderno"""
        def eliminar(e):
            with OBTENER_SESION() as sesion:
                s = sesion.query(MODELO_SUCURSAL).filter_by(ID=sucursal.ID).first()
                # Eliminación lógica en lugar de física
                s.ELIMINADA = True
                s.ACTIVA = False
                s.FECHA_ELIMINACION = datetime.now()
                s.USUARIO_ELIMINO_ID = self._usuario.ID
                sesion.commit()
            
            overlay.open = False
            self._cargar_sucursales()
            
            # Recargar dropdown de sucursales en navbar
            if hasattr(self, '_navbar') and self._navbar:
                self._navbar.recargar_sucursales()
            
            self._pagina.snack_bar = ft.SnackBar(
                content=ft.Row([
                    ft.Icon(ft.icons.Icons.DELETE, color=ft.Colors.WHITE),
                    ft.Text(f"🗑️ Sucursal '{sucursal.NOMBRE}' eliminada (puede restaurarse)", color=ft.Colors.WHITE)
                ], spacing=8),
                bgcolor=ft.Colors.ORANGE_700
            )
            self._pagina.snack_bar.open = True
            self._pagina.update()
        
        overlay = ft.AlertDialog(
            title=ft.Row([
                ft.Container(
                    content=ft.Icon(ft.icons.Icons.WARNING, size=32, color=ft.Colors.ORANGE_700),
                    width=48,
                    height=48,
                    border_radius=24,
                    bgcolor=ft.Colors.ORANGE_50,
                    alignment=ft.alignment.Alignment(0, 0)
                ),
                ft.Text("Confirmar Eliminación", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_900)
            ], spacing=12),
            content=ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.icons.Icons.STORE, size=20, color=ft.Colors.BLUE_700),
                                ft.Text(
                                    sucursal.NOMBRE,
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.BLUE_700
                                )
                            ], spacing=8),
                            ft.Text(
                                sucursal.DIRECCION or "Sin dirección",
                                size=13,
                                color=ft.Colors.GREY_600
                            )
                        ], spacing=6),
                        padding=ft.padding.all(14),
                        border_radius=10,
                        bgcolor=ft.Colors.BLUE_50,
                        border=ft.border.all(1, ft.Colors.BLUE_200)
                    ),
                    ft.Divider(height=20),
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.icons.Icons.INFO, size=18, color=ft.Colors.ORANGE_700),
                                ft.Text(
                                    "¿Estás seguro?",
                                    size=15,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.GREY_900
                                )
                            ], spacing=8),
                            ft.Text(
                                "Esta acción marcará la sucursal como eliminada. Los datos se preservarán.",
                                size=13,
                                color=ft.Colors.GREY_700
                            ),
                            ft.Text(
                                "✅ La sucursal puede ser restaurada por un SUPERADMIN si es necesario.",
                                size=12,
                                color=ft.Colors.GREEN_700,
                                italic=True
                            )
                        ], spacing=8),
                        padding=ft.padding.all(14),
                        border_radius=10,
                        bgcolor=ft.Colors.ORANGE_50,
                        border=ft.border.all(1, ft.Colors.ORANGE_200)
                    )
                ], spacing=16),
                width=450
            ),
            actions=[
                ft.TextButton(
                    content=ft.Row([
                        ft.Icon(ft.icons.Icons.CLOSE, size=18),
                        ft.Text("Cancelar", weight=ft.FontWeight.W_500)
                    ], spacing=6),
                    on_click=lambda e: setattr(overlay, 'open', False) or self._pagina.update()
                ),
                ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.icons.Icons.DELETE_FOREVER, size=18),
                        ft.Text("Eliminar Sucursal", weight=ft.FontWeight.BOLD)
                    ], spacing=6),
                    on_click=eliminar,
                    bgcolor=ft.Colors.RED_700,
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
    
    def _ver_sucursales_eliminadas(self):
        """Muestra lista de sucursales eliminadas (solo SUPERADMIN)"""
        # Verificar que sea SUPERADMIN
        if not self._usuario.TIENE_ROL(ROLES.SUPERADMIN):
            self._pagina.snack_bar = ft.SnackBar(
                content=ft.Text("❌ Solo SUPERADMIN puede ver sucursales eliminadas"),
                bgcolor=ft.Colors.RED_700
            )
            self._pagina.snack_bar.open = True
            self._pagina.update()
            return
        
        with OBTENER_SESION() as sesion:
            eliminadas = sesion.query(MODELO_SUCURSAL).filter_by(ELIMINADA=True).all()
        
        if not eliminadas:
            overlay = ft.AlertDialog(
                title=ft.Text("🗑️ Sucursales Eliminadas"),
                content=ft.Text("No hay sucursales eliminadas en este momento."),
                actions=[
                    ft.TextButton("Cerrar", on_click=lambda e: setattr(overlay, 'open', False) or self._pagina.update())
                ]
            )
        else:
            # Crear lista de sucursales eliminadas
            lista_eliminadas = ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(s.NOMBRE, weight=ft.FontWeight.BOLD),
                            ft.Text(s.DIRECCION or "Sin dirección", size=12, color=ft.Colors.GREY_600),
                            ft.Text(
                                f"Eliminada: {s.FECHA_ELIMINACION.strftime('%d/%m/%Y %H:%M') if s.FECHA_ELIMINACION else 'N/A'}",
                                size=11,
                                color=ft.Colors.RED_400,
                                italic=True
                            )
                        ], expand=True),
                        ft.IconButton(
                            icon=ft.icons.Icons.RESTORE,
                            tooltip="Restaurar sucursal",
                            icon_color=ft.Colors.GREEN_700,
                            on_click=lambda e, suc=s: self._restaurar_sucursal(suc)
                        )
                    ]),
                    padding=10,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=8,
                    bgcolor=ft.Colors.RED_50
                )
                for s in eliminadas
            ], spacing=8, scroll=ft.ScrollMode.ADAPTIVE, height=400)
            
            overlay = ft.AlertDialog(
                title=ft.Row([
                    ft.Icon(ft.icons.Icons.RESTORE_FROM_TRASH, color=ft.Colors.ORANGE_700),
                    ft.Text("🗑️ Sucursales Eliminadas", size=18, weight=ft.FontWeight.BOLD)
                ], spacing=10),
                content=ft.Container(
                    content=lista_eliminadas,
                    width=500
                ),
                actions=[
                    ft.TextButton(
                        "Cerrar",
                        on_click=lambda e: setattr(overlay, 'open', False) or self._pagina.update()
                    )
                ]
            )
        
        self._pagina.overlay.append(overlay)
        overlay.open = True
        self._pagina.update()
    
    def _restaurar_sucursal(self, sucursal):
        """Restaura una sucursal eliminada (solo SUPERADMIN)"""
        if not self._usuario.TIENE_ROL(ROLES.SUPERADMIN):
            return
        
        with OBTENER_SESION() as sesion:
            s = sesion.query(MODELO_SUCURSAL).filter_by(ID=sucursal.ID).first()
            s.ELIMINADA = False
            s.FECHA_ELIMINACION = None
            s.USUARIO_ELIMINO_ID = None
            s.ACTIVA = True  # Restaurar como activa
            s.ESTADO = "ACTIVA"
            sesion.commit()
        
        # Cerrar overlay y recargar
        for overlay in self._pagina.overlay:
            if hasattr(overlay, 'open'):
                overlay.open = False
        
        self._cargar_sucursales()
        
        # Recargar navbar
        if hasattr(self, '_navbar') and self._navbar:
            self._navbar.recargar_sucursales()
        
        self._pagina.snack_bar = ft.SnackBar(
            content=ft.Row([
                ft.Icon(ft.icons.Icons.RESTORE, color=ft.Colors.WHITE),
                ft.Text(f"✅ Sucursal '{sucursal.NOMBRE}' restaurada exitosamente", color=ft.Colors.WHITE)
            ], spacing=8),
            bgcolor=ft.Colors.GREEN_700
        )
        self._pagina.snack_bar.open = True
        self._pagina.update()
    
    def _ir_dashboard(self):
        """Vuelve al dashboard"""
        from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
        self._pagina.controls.clear()
        self._pagina.add(PaginaAdmin(self._pagina, self._usuario))
        self._pagina.update()
    
    def _cerrar_sesion(self):
        """Cierra sesión"""
        # Limpiar y volver al login
        self._pagina.controls.clear()
        # Import local para evitar circular
        from main import crear_login_page
        self._pagina.add(crear_login_page(self._pagina))
        self._pagina.update()
