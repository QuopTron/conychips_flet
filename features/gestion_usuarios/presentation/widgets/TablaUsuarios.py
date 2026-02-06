"""Tabla de usuarios - Similar al diseño de vouchers"""
import flet as ft
from core.Constantes import COLORES, TAMANOS, ICONOS, ROLES
from typing import Callable, Optional


class TablaUsuarios(ft.Column):
    """Componente de tabla para mostrar usuarios"""
    
    def __init__(
        self,
        on_editar: Callable = None,
        on_cambiar_estado: Callable = None,
        on_cambiar_rol: Callable = None,
        on_resetear_password: Callable = None,
        usuario_actual_rol: str = None
    ):
        super().__init__()
        
        self.on_editar = on_editar
        self.on_cambiar_estado = on_cambiar_estado
        self.on_cambiar_rol = on_cambiar_rol
        self.on_resetear_password = on_resetear_password
        self.usuario_actual_rol = usuario_actual_rol
        
        self._tabla_container = ft.Column(
            spacing=3,
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True
        )
        
        self.controls = [self._tabla_container]
        self.expand = True
        self.spacing = 0
    
    def ACTUALIZAR_DATOS(self, usuarios: list):
        """Actualiza la tabla con nuevos datos"""
        self._tabla_container.controls.clear()
        
        if not usuarios:
            self._tabla_container.controls.append(
                ft.Container(
                    content=ft.Text(
                        "No hay usuarios para mostrar",
                        size=TAMANOS.TEXTO_LG,
                        color=COLORES.TEXTO_SECUNDARIO
                    ),
                    padding=TAMANOS.PADDING_XL,
                    alignment=ft.Alignment(0, 0)
                )
            )
            return
        
        # Crear tabla
        filas = []
        for usuario in usuarios:
            filas.append(self._CREAR_FILA_USUARIO(usuario))
        
        tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD, size=12)),
                ft.DataColumn(ft.Text("Usuario", weight=ft.FontWeight.BOLD, size=12)),
                ft.DataColumn(ft.Text("Nombre Completo", weight=ft.FontWeight.BOLD, size=12)),
                ft.DataColumn(ft.Text("Email", weight=ft.FontWeight.BOLD, size=12)),
                ft.DataColumn(ft.Text("Rol", weight=ft.FontWeight.BOLD, size=12)),
                ft.DataColumn(ft.Text("Sucursal", weight=ft.FontWeight.BOLD, size=12)),
                ft.DataColumn(ft.Text("Estado", weight=ft.FontWeight.BOLD, size=12)),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD, size=12)),
            ],
            rows=filas,
            border=ft.Border.all(1, ft.Colors.GREY_300),
            border_radius=8,
            vertical_lines=ft.BorderSide(0.5, ft.Colors.GREY_200),
            horizontal_lines=ft.BorderSide(0.5, ft.Colors.GREY_200),
            heading_row_color=ft.Colors.BLUE_50,
            heading_row_height=40,
            data_row_min_height=36,
            data_row_max_height=36,
            column_spacing=8,
        )
        
        self._tabla_container.controls.append(
            ft.Container(
                content=ft.Row(
                    [tabla],
                    scroll=ft.ScrollMode.ADAPTIVE,
                    expand=True,
                ),
                bgcolor=ft.Colors.WHITE,
                border_radius=4,
                padding=0,
                expand=True,
                border=ft.Border.all(1, ft.Colors.BLUE_200)
            )
        )
    
    def _CREAR_FILA_USUARIO(self, usuario) -> ft.DataRow:
        """Crea una fila para un usuario"""
        
        # Obtener datos
        if usuario.ROLES:
            rol_nombre = usuario.ROLES[0].NOMBRE if hasattr(usuario.ROLES[0], 'NOMBRE') else usuario.ROLES[0]
        else:
            rol_nombre = "Sin Rol"
        rol_label = rol_nombre.replace("_", " ").title()
        sucursal_nombre = usuario.SUCURSAL.NOMBRE if usuario.SUCURSAL else "Sin Sucursal"
        
        # Color del rol
        rol_color = COLORES.PRIMARIO
        if rol_nombre == "SUPERADMIN":
            rol_color = COLORES.PELIGRO
        elif rol_nombre == "ADMINISTRADOR":
            rol_color = COLORES.ADVERTENCIA
        elif rol_nombre == "SUPERVISOR":
            rol_color = COLORES.INFO
        
        # Estado
        estado_activo = usuario.ACTIVO
        estado_texto = "✓ Activo" if estado_activo else "✗ Inactivo"
        estado_color = COLORES.EXITO if estado_activo else COLORES.GRIS_OSCURO
        
        # Acciones basadas en permisos
        acciones = self._CREAR_ACCIONES(usuario, rol_nombre)
        
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(str(usuario.ID), size=11)),
                ft.DataCell(ft.Text(
                    usuario.NOMBRE_USUARIO,
                    weight=ft.FontWeight.W_500,
                    size=11
                )),
                ft.DataCell(ft.Text(
                    usuario.NOMBRE_COMPLETO or "-",
                    size=11
                )),
                ft.DataCell(ft.Text(
                    usuario.EMAIL or "-",
                    size=11
                )),
                ft.DataCell(ft.Container(
                    content=ft.Text(
                        rol_label,
                        color=ft.Colors.WHITE,
                        size=10,
                        weight=ft.FontWeight.BOLD
                    ),
                    bgcolor=rol_color,
                    padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                    border_radius=4
                )),
                ft.DataCell(ft.Text(
                    sucursal_nombre,
                    size=11
                )),
                ft.DataCell(ft.Text(
                    estado_texto,
                    color=estado_color,
                    weight=ft.FontWeight.BOLD,
                    size=11
                )),
                ft.DataCell(acciones),
            ]
        )
    
    def _CREAR_ACCIONES(self, usuario, rol_nombre: str) -> ft.Row:
        """Crea botones de acción según permisos"""
        botones = []
        
        # SUPERADMIN puede editar a todos
        # ADMIN puede editar solo a usuarios de su sucursal y roles menores
        puede_editar = self.usuario_actual_rol == "SUPERADMIN"
        if self.usuario_actual_rol == "ADMIN":
            puede_editar = rol_nombre not in ["SUPERADMIN", "ADMIN"]
        
        if puede_editar and self.on_editar:
            botones.append(ft.IconButton(
                icon=ft.icons.Icons.EDIT,
                tooltip="Editar Usuario",
                icon_color=COLORES.INFO,
                icon_size=20,
                on_click=lambda e, u=usuario: self.on_editar(u)
            ))
        
        # Cambiar estado (activar/desactivar)
        if puede_editar and self.on_cambiar_estado:
            icono_estado = ft.icons.Icons.CHECK_CIRCLE if not usuario.ACTIVO else ft.icons.Icons.BLOCK
            tooltip_estado = "Activar" if not usuario.ACTIVO else "Desactivar"
            color_estado = COLORES.EXITO if not usuario.ACTIVO else COLORES.ADVERTENCIA
            
            botones.append(ft.IconButton(
                icon=icono_estado,
                tooltip=tooltip_estado,
                icon_color=color_estado,
                icon_size=20,
                on_click=lambda e, u=usuario: self.on_cambiar_estado(u)
            ))
        
        # Cambiar rol (solo SUPERADMIN)
        if self.usuario_actual_rol == "SUPERADMIN" and self.on_cambiar_rol:
            botones.append(ft.IconButton(
                icon=ft.icons.Icons.ADMIN_PANEL_SETTINGS,
                tooltip="Cambiar Rol",
                icon_color=COLORES.PRIMARIO,
                icon_size=20,
                on_click=lambda e, u=usuario: self.on_cambiar_rol(u)
            ))
        
        # Resetear contraseña
        if puede_editar and self.on_resetear_password:
            botones.append(ft.IconButton(
                icon=ft.icons.Icons.LOCK_RESET,
                tooltip="Resetear Contraseña",
                icon_color=COLORES.ADVERTENCIA_OSCURO,
                icon_size=20,
                on_click=lambda e, u=usuario: self.on_resetear_password(u)
            ))
        
        return ft.Row(
            controls=botones,
            spacing=5,
            tight=True
        )
