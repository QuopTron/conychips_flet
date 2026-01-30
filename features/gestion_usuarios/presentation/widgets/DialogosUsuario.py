"""Diálogos para crear/editar usuarios"""
import flet as ft
from core.Constantes import COLORES, TAMANOS, ICONOS
from typing import Callable, Optional


class DialogoUsuario(ft.AlertDialog):
    """Diálogo para crear o editar un usuario"""
    
    def __init__(
        self,
        on_guardar: Callable,
        on_cancelar: Callable,
        usuario=None,
        roles_disponibles: list = None,
        sucursales: list = None,
        es_edicion: bool = False
    ):
        self.on_guardar = on_guardar
        self.on_cancelar = on_cancelar
        self.usuario = usuario
        self.es_edicion = es_edicion
        
        # Campos del formulario
        self.campo_usuario = ft.TextField(
            label="Nombre de Usuario",
            hint_text="Ej: jperez",
            prefix_icon=ft.icons.Icons.PERSON,
            value=usuario.NOMBRE_USUARIO if usuario else "",
            read_only=es_edicion,  # No se puede cambiar el usuario en edición
            border_color=COLORES.BORDE,
            focused_border_color=COLORES.PRIMARIO
        )
        
        self.campo_email = ft.TextField(
            label="Email",
            hint_text="usuario@ejemplo.com",
            prefix_icon=ft.icons.Icons.EMAIL,
            value=usuario.EMAIL if usuario else "",
            keyboard_type=ft.KeyboardType.EMAIL,
            border_color=COLORES.BORDE,
            focused_border_color=COLORES.PRIMARIO
        )
        
        self.campo_nombre_completo = ft.TextField(
            label="Nombre Completo",
            hint_text="Ej: Juan Pérez",
            prefix_icon=ft.icons.Icons.BADGE,
            value=usuario.NOMBRE_COMPLETO if usuario else "",
            border_color=COLORES.BORDE,
            focused_border_color=COLORES.PRIMARIO
        )
        
        # Contraseña (solo en creación o si se quiere cambiar)
        self.campo_contrasena = None
        if not es_edicion:
            self.campo_contrasena = ft.TextField(
                label="Contraseña",
                hint_text="Mínimo 8 caracteres",
                prefix_icon=ft.icons.Icons.LOCK,
                password=True,
                can_reveal_password=True,
                border_color=COLORES.BORDE,
                focused_border_color=COLORES.PRIMARIO
            )
        
        # Rol
        opciones_rol = []
        if roles_disponibles:
            for rol in roles_disponibles:
                opciones_rol.append(ft.dropdown.Option(
                    key=rol.NOMBRE,
                    text=rol.NOMBRE.replace("_", " ").title()
                ))
        
        valor_rol = "EMPLEADO"
        if usuario and usuario.ROLES:
            valor_rol = usuario.ROLES[0].NOMBRE if hasattr(usuario.ROLES[0], 'NOMBRE') else usuario.ROLES[0]
        
        self.campo_rol = ft.Dropdown(
            label="Rol",
            options=opciones_rol,
            value=valor_rol,
            prefix_icon=ft.icons.Icons.ADMIN_PANEL_SETTINGS,
            border_color=COLORES.BORDE,
            focused_border_color=COLORES.PRIMARIO
        )
        
        # Sucursal
        opciones_sucursal = []
        if sucursales:
            for sucursal in sucursales:
                opciones_sucursal.append(ft.dropdown.Option(
                    key=str(sucursal.ID),
                    text=sucursal.NOMBRE
                ))
        
        valor_sucursal = str(usuario.SUCURSAL_ID) if (usuario and usuario.SUCURSAL_ID) else None
        
        self.campo_sucursal = ft.Dropdown(
            label="Sucursal",
            options=opciones_sucursal,
            value=valor_sucursal,
            prefix_icon=ft.icons.Icons.STORE,
            border_color=COLORES.BORDE,
            focused_border_color=COLORES.PRIMARIO
        )
        
        # Estado activo
        self.switch_activo = ft.Switch(
            label="Usuario Activo",
            value=usuario.ACTIVO if usuario else True,
            active_color=COLORES.EXITO
        )
        
        # Construir formulario
        campos = [
            self.campo_usuario,
            self.campo_email,
            self.campo_nombre_completo,
        ]
        
        if self.campo_contrasena:
            campos.append(self.campo_contrasena)
        
        campos.extend([
            self.campo_rol,
            self.campo_sucursal,
            ft.Container(
                content=self.switch_activo,
                padding=ft.padding.symmetric(vertical=10)
            )
        ])
        
        super().__init__(
            modal=True,
            title=ft.Text(
                "Editar Usuario" if es_edicion else "Nuevo Usuario",
                size=TAMANOS.TEXTO_XL,
                weight=ft.FontWeight.BOLD,
                color=COLORES.TEXTO
            ),
            content=ft.Container(
                content=ft.Column(
                    controls=campos,
                    spacing=TAMANOS.ESPACIADO_MD,
                    tight=True,
                    scroll=ft.ScrollMode.AUTO
                ),
                width=500,
                padding=TAMANOS.PADDING_MD
            ),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e: self.on_cancelar(),
                    style=ft.ButtonStyle(
                        color=COLORES.TEXTO_SECUNDARIO
                    )
                ),
                ft.Button(
                    "Guardar",
                    icon=ft.icons.Icons.SAVE,
                    on_click=lambda e: self._validar_y_guardar(),
                    bgcolor=COLORES.PRIMARIO,
                    color=ft.Colors.WHITE
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
    
    def _validar_y_guardar(self):
        """Valida los datos y llama al callback de guardar"""
        errores = []
        
        # Validaciones
        if not self.es_edicion and not self.campo_usuario.value:
            errores.append("El nombre de usuario es obligatorio")
        
        if not self.campo_email.value:
            errores.append("El email es obligatorio")
        elif "@" not in self.campo_email.value:
            errores.append("El email no es válido")
        
        if not self.es_edicion and not self.campo_contrasena.value:
            errores.append("La contraseña es obligatoria")
        elif not self.es_edicion and len(self.campo_contrasena.value) < 8:
            errores.append("La contraseña debe tener al menos 8 caracteres")
        
        if not self.campo_nombre_completo.value:
            errores.append("El nombre completo es obligatorio")
        
        if not self.campo_rol.value:
            errores.append("Debe seleccionar un rol")
        
        if not self.campo_sucursal.value:
            errores.append("Debe seleccionar una sucursal")
        
        if errores:
            # Mostrar errores
            self.content.content.controls.insert(0, ft.Container(
                content=ft.Column([
                    ft.Text("⚠️ Errores de validación:", color=COLORES.PELIGRO, weight=ft.FontWeight.BOLD),
                    *[ft.Text(f"• {error}", color=COLORES.PELIGRO, size=TAMANOS.TEXTO_SM) for error in errores]
                ]),
                bgcolor=ft.Colors.RED_50,
                padding=TAMANOS.PADDING_SM,
                border_radius=TAMANOS.RADIO_SM
            ))
            self.update()
            return
        
        # Extraer datos
        datos = {
            "email": self.campo_email.value.strip(),
            "nombre_completo": self.campo_nombre_completo.value.strip(),
            "rol": self.campo_rol.value,
            "sucursal_id": int(self.campo_sucursal.value),
            "activo": self.switch_activo.value
        }
        
        if not self.es_edicion:
            datos["nombre_usuario"] = self.campo_usuario.value.strip().upper()
            datos["contrasena"] = self.campo_contrasena.value
        
        # Llamar callback
        self.on_guardar(datos)


class DialogoCambiarRol(ft.AlertDialog):
    """Diálogo para cambiar el rol de un usuario"""
    
    def __init__(
        self,
        usuario,
        roles_disponibles: list,
        on_guardar: Callable,
        on_cancelar: Callable
    ):
        self.usuario = usuario
        self.on_guardar = on_guardar
        self.on_cancelar = on_cancelar
        
        # Opciones de rol
        opciones = []
        for rol in roles_disponibles:
            opciones.append(ft.dropdown.Option(
                key=rol.NOMBRE,
                text=rol.NOMBRE.replace("_", " ").title()
            ))
        
        rol_actual = ""
        if usuario.ROLES:
            rol_actual = usuario.ROLES[0].NOMBRE if hasattr(usuario.ROLES[0], 'NOMBRE') else usuario.ROLES[0]
        
        self.campo_rol = ft.Dropdown(
            label="Nuevo Rol",
            options=opciones,
            value=rol_actual,
            prefix_icon=ft.icons.Icons.ADMIN_PANEL_SETTINGS,
            border_color=COLORES.BORDE,
            focused_border_color=COLORES.PRIMARIO,
            width=300
        )
        
        super().__init__(
            modal=True,
            title=ft.Text(
                f"Cambiar Rol - {usuario.NOMBRE_USUARIO}",
                size=TAMANOS.TEXTO_LG,
                weight=ft.FontWeight.BOLD
            ),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        f"Rol actual: {rol_actual.replace('_', ' ').title()}",
                        size=TAMANOS.TEXTO_SM,
                        color=COLORES.TEXTO_SECUNDARIO
                    ),
                    ft.Divider(),
                    self.campo_rol
                ]),
                padding=TAMANOS.PADDING_MD
            ),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e: self.on_cancelar()
                ),
                ft.Button(
                    "Guardar",
                    icon=ft.icons.Icons.SAVE,
                    on_click=lambda e: self.on_guardar(self.campo_rol.value),
                    bgcolor=COLORES.PRIMARIO,
                    color=ft.Colors.WHITE
                )
            ]
        )


class DialogoResetearPassword(ft.AlertDialog):
    """Diálogo para resetear contraseña"""
    
    def __init__(
        self,
        usuario,
        on_guardar: Callable,
        on_cancelar: Callable
    ):
        self.usuario = usuario
        self.on_guardar = on_guardar
        self.on_cancelar = on_cancelar
        
        self.campo_nueva = ft.TextField(
            label="Nueva Contraseña",
            hint_text="Mínimo 8 caracteres",
            prefix_icon=ft.icons.Icons.LOCK,
            password=True,
            can_reveal_password=True,
            border_color=COLORES.BORDE,
            focused_border_color=COLORES.PRIMARIO
        )
        
        self.campo_confirmar = ft.TextField(
            label="Confirmar Contraseña",
            hint_text="Repetir contraseña",
            prefix_icon=ft.icons.Icons.LOCK_OUTLINE,
            password=True,
            can_reveal_password=True,
            border_color=COLORES.BORDE,
            focused_border_color=COLORES.PRIMARIO
        )
        
        super().__init__(
            modal=True,
            title=ft.Text(
                f"Resetear Contraseña - {usuario.NOMBRE_USUARIO}",
                size=TAMANOS.TEXTO_LG,
                weight=ft.FontWeight.BOLD
            ),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "⚠️ Esta acción no se puede deshacer",
                        color=COLORES.ADVERTENCIA,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Divider(),
                    self.campo_nueva,
                    self.campo_confirmar
                ]),
                padding=TAMANOS.PADDING_MD,
                width=400
            ),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e: self.on_cancelar()
                ),
                ft.Button(
                    "Resetear",
                    icon=ft.icons.Icons.LOCK_RESET,
                    on_click=lambda e: self._validar_y_guardar(),
                    bgcolor=COLORES.ADVERTENCIA,
                    color=ft.Colors.WHITE
                )
            ]
        )
    
    def _validar_y_guardar(self):
        """Valida las contraseñas y guarda"""
        if not self.campo_nueva.value:
            self.campo_nueva.error_text = "Contraseña requerida"
            self.update()
            return
        
        if len(self.campo_nueva.value) < 8:
            self.campo_nueva.error_text = "Mínimo 8 caracteres"
            self.update()
            return
        
        if self.campo_nueva.value != self.campo_confirmar.value:
            self.campo_confirmar.error_text = "Las contraseñas no coinciden"
            self.update()
            return
        
        self.on_guardar(self.campo_nueva.value)
