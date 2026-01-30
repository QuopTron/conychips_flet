import flet as ft
from features.admin.presentation.widgets.VistaBase import VistaBase
from features.admin.presentation.bloc.UsuariosBloc import (
    USUARIOS_BLOC,
    CargarUsuarios,
    CrearUsuario,
    ActualizarUsuario,
    EliminarUsuario,
    UsuariosCargando,
    UsuariosCargados,
    UsuarioError,
    UsuarioCreado,
    UsuarioActualizado,
    UsuarioEliminado
)
from features.admin.presentation.widgets.ComponentesGlobales import (
    HeaderAdmin,
    TablaGenerica,
    FormularioGenerico,
    DialogoConfirmacion,
    Notificador
)
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_ROL
from core.Constantes import COLORES, TAMANOS, ICONOS
import bcrypt

class VistaUsuarios(VistaBase):
    
    def __init__(self, pagina: ft.Page, usuario, on_volver_inicio):
        super().__init__(
            pagina=pagina,
            usuario=usuario,
            titulo="Gestión de Usuarios",
            on_volver_inicio=on_volver_inicio,
            mostrar_boton_volver=True
        )
        self._tabla_usuarios = None
        self._roles_cache = []
        
        USUARIOS_BLOC.AGREGAR_LISTENER(self._ON_ESTADO_CAMBIO)
        
        self._cargar_vista()
        
        USUARIOS_BLOC.AGREGAR_EVENTO(CargarUsuarios())
    
    
    def _ON_ESTADO_CAMBIO(self, estado):
        if isinstance(estado, UsuariosCargando):
            pass
        
        elif isinstance(estado, UsuariosCargados):
            self._actualizar_tabla(estado.usuarios)
        
        elif isinstance(estado, UsuarioError):
            Notificador.ERROR(self, estado.mensaje)
        
        elif isinstance(estado, UsuarioCreado):
            self.cerrar_dialogo()
            Notificador.EXITO(self, estado.mensaje)
        
        elif isinstance(estado, UsuarioActualizado):
            self.cerrar_dialogo()
            Notificador.EXITO(self, estado.mensaje)
        
        elif isinstance(estado, UsuarioEliminado):
            self.cerrar_dialogo()
            Notificador.EXITO(self, estado.mensaje)
    
    def _cargar_vista(self):
        header = HeaderAdmin(
            self,
            titulo="Gestión de Usuarios",
            botones_personalizados=[
                ft.Button(
                    "➕ Nuevo Usuario",
                    icon=ICONOS.USUARIOS,
                    on_click=self._abrir_popup_crear,
                    bgcolor=COLORES.PRIMARIO,
                    color=COLORES.TEXTO_BLANCO,
                )
            ]
        )
        
        self._tabla_usuarios = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Nombre Usuario", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Email", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Rol", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Estado", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.Border.all(1, COLORES.BORDE),
            border_radius=TAMANOS.RADIO_MD,
            vertical_lines=ft.BorderSide(1, COLORES.BORDE),
            heading_row_color=COLORES.PRIMARIO_CLARO,
        )
        
        self.establecer_contenido([
            header,
            ft.Container(
                content=self._tabla_usuarios,
                bgcolor=COLORES.FONDO_BLANCO,
                border_radius=TAMANOS.RADIO_MD,
                padding=TAMANOS.PADDING_MD,
            )
        ])
    
    def _actualizar_tabla(self, usuarios):
        self._tabla_usuarios.rows.clear()
        
        for usuario in usuarios:
            rol_nombre = usuario.ROLES[0].NOMBRE if usuario.ROLES else "Sin rol"
            estado = "✓ Activo" if usuario.ACTIVO else "✗ Inactivo"
            
            self._tabla_usuarios.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(usuario.ID))),
                        ft.DataCell(ft.Text(usuario.NOMBRE_USUARIO)),
                        ft.DataCell(ft.Text(usuario.EMAIL)),
                        ft.DataCell(ft.Text(rol_nombre)),
                        ft.DataCell(ft.Text(
                            estado,
                            color=COLORES.EXITO if usuario.ACTIVO else COLORES.PELIGRO
                        )),
                        ft.DataCell(ft.Row([
                            ft.IconButton(
                                icon=ft.icons.Icons.Icons.EDIT,
                                tooltip="Editar",
                                icon_color=COLORES.INFO,
                                on_click=lambda e, u=usuario: self._abrir_popup_editar(u)
                            ),
                            ft.IconButton(
                                icon=ft.icons.Icons.Icons.DELETE,
                                tooltip="Eliminar",
                                icon_color=COLORES.PELIGRO,
                                on_click=lambda e, u=usuario: self._confirmar_eliminar(u)
                            ),
                        ])),
                    ]
                )
            )
        
        self.actualizar_ui()
    
    def _cargar_roles(self):
        if not self._roles_cache:
            sesion = OBTENER_SESION()
            self._roles_cache = sesion.query(MODELO_ROL).all()
            sesion.close()
        return self._roles_cache
    
    
    def _abrir_popup_crear(self, e):
        roles = self._cargar_roles()
        
        campo_nombre = ft.TextField(
            label="Nombre de Usuario",
            hint_text="ejm: juanperez",
            prefix_icon=ft.icons.Icons.Icons.PERSON
        )
        campo_email = ft.TextField(
            label="Email",
            hint_text="ejm: usuario@ejemplo.com",
            prefix_icon=ft.icons.Icons.Icons.EMAIL
        )
        campo_password = ft.TextField(
            label="Contraseña",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.icons.Icons.Icons.LOCK
        )
        
        campo_rol = ft.Dropdown(
            label="Rol",
            hint_text="Selecciona un rol",
            options=[ft.dropdown.Option(r.NOMBRE, key=str(r.ID)) for r in roles],
            prefix_icon=ft.icons.Icons.Icons.BADGE
        )
        
        switch_activo = ft.Switch(
            label="Usuario Activo",
            value=True
        )
        
        def guardar(e):
            if not campo_nombre.value or not campo_email.value or not campo_password.value:
                Notificador.ADVERTENCIA(self, "Completa todos los campos")
                return
            
            if not campo_rol.value:
                Notificador.ADVERTENCIA(self, "Selecciona un rol")
                return
            
            try:
                rol_id = int([opt for opt in campo_rol.options if opt.text == campo_rol.value][0].key)
                
                USUARIOS_BLOC.AGREGAR_EVENTO(
                    CrearUsuario(
                        email=campo_email.value,
                        nombre_usuario=campo_nombre.value,
                        contrasena=campo_password.value,
                        rol_id=rol_id
                    )
                )
                
            except Exception as ex:
                Notificador.ERROR(self, f"Error: {str(ex)}")
        
        dialogo = ft.AlertDialog(
            title=ft.Text("➕ Nuevo Usuario", color=COLORES.TEXTO),
            content=ft.Container(
                content=ft.Column([
                    campo_nombre,
                    campo_email,
                    campo_password,
                    campo_rol,
                    switch_activo
                ], tight=True, spacing=TAMANOS.ESPACIADO_MD),
                width=400
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.cerrar_dialogo()),
                ft.Button(
                    "Guardar",
                    icon=ft.icons.Icons.Icons.SAVE,
                    on_click=guardar,
                    bgcolor=COLORES.PRIMARIO,
                    color=COLORES.TEXTO_BLANCO
                )
            ]
        )
        
        self.mostrar_dialogo(dialogo)
    
    
    def _abrir_popup_editar(self, usuario):
        roles = self._cargar_roles()
        rol_actual = usuario.ROLES[0].NOMBRE if usuario.ROLES else None
        
        campo_nombre = ft.TextField(
            label="Nombre de Usuario",
            value=usuario.NOMBRE_USUARIO,
            prefix_icon=ft.icons.Icons.Icons.PERSON
        )
        campo_email = ft.TextField(
            label="Email",
            value=usuario.EMAIL,
            prefix_icon=ft.icons.Icons.Icons.EMAIL
        )
        campo_password = ft.TextField(
            label="Nueva Contraseña (dejar vacío para mantener actual)",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.icons.Icons.Icons.LOCK
        )
        
        campo_rol = ft.Dropdown(
            label="Rol",
            value=rol_actual,
            options=[ft.dropdown.Option(r.NOMBRE, key=str(r.ID)) for r in roles],
            prefix_icon=ft.icons.Icons.Icons.BADGE
        )
        
        switch_activo = ft.Switch(
            label="Usuario Activo",
            value=usuario.ACTIVO
        )
        
        def guardar(e):
            try:
                datos = {
                    "NOMBRE_USUARIO": campo_nombre.value,
                    "EMAIL": campo_email.value,
                    "ACTIVO": switch_activo.value
                }
                
                if campo_password.value:
                    salt = bcrypt.gensalt(rounds=12)
                    hash_pw = bcrypt.hashpw(campo_password.value.encode('utf-8'), salt).decode('utf-8')
                    datos["CONTRASENA_HASH"] = hash_pw
                
                USUARIOS_BLOC.AGREGAR_EVENTO(
                    ActualizarUsuario(
                        usuario_id=usuario.ID,
                        datos=datos
                    )
                )
                
            except Exception as ex:
                Notificador.ERROR(self, f"Error: {str(ex)}")
        
        dialogo = ft.AlertDialog(
            title=ft.Text(f"✏️ Editar Usuario: {usuario.NOMBRE_USUARIO}", color=COLORES.TEXTO),
            content=ft.Container(
                content=ft.Column([
                    campo_nombre,
                    campo_email,
                    campo_password,
                    campo_rol,
                    switch_activo
                ], tight=True, spacing=TAMANOS.ESPACIADO_MD),
                width=400
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.cerrar_dialogo()),
                ft.Button(
                    "Actualizar",
                    icon=ft.icons.Icons.Icons.SAVE,
                    on_click=guardar,
                    bgcolor=COLORES.INFO,
                    color=COLORES.TEXTO_BLANCO
                )
            ]
        )
        
        self.mostrar_dialogo(dialogo)
    
    def _confirmar_eliminar(self, usuario):
        def eliminar(e):
            try:
                USUARIOS_BLOC.AGREGAR_EVENTO(
                    EliminarUsuario(usuario_id=usuario.ID)
                )
            except Exception as ex:
                Notificador.ERROR(self, f"Error: {str(ex)}")
        
        dialogo = ft.AlertDialog(
            title=ft.Text("⚠️ Confirmar Eliminación", color=COLORES.PELIGRO),
            content=ft.Text(
                f"¿Estás seguro de eliminar al usuario '{usuario.NOMBRE_USUARIO}'?\n\n"
                "Esta acción no se puede deshacer.",
                size=TAMANOS.TEXTO_MD
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.cerrar_dialogo()),
                ft.Button(
                    "Eliminar",
                    icon=ft.icons.Icons.Icons.DELETE_FOREVER,
                    on_click=eliminar,
                    bgcolor=COLORES.PELIGRO,
                    color=COLORES.TEXTO_BLANCO
                )
            ]
        )
        
        self.mostrar_dialogo(dialogo)
    
    def __del__(self):
        try:
            USUARIOS_BLOC.REMOVER_LISTENER(self._ON_ESTADO_CAMBIO)
        except:
            pass

