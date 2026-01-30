"""Página de Gestión de Usuarios - Refactorizada con BLoC y LayoutBase"""
import flet as ft
from core.Constantes import COLORES, TAMANOS, ICONOS, ROLES
from core.decoradores.DecoradorVistas import REQUIERE_ROL
from core.ui.safe_actions import safe_update
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_SUCURSAL
from features.admin.presentation.widgets import LayoutBase

from ..bloc import (
    UsuariosBloc,
    CargarUsuarios,
    CrearUsuario,
    ActualizarUsuario,
    CambiarEstadoUsuario,
    CambiarRolUsuario,
    ResetearContrasena,
    UsuariosCargando,
    UsuariosCargados,
    UsuarioCreado,
    UsuarioActualizado,
    UsuarioError
)

from ..widgets.TablaUsuarios import TablaUsuarios
from ..widgets.DialogosUsuario import DialogoUsuario, DialogoCambiarRol, DialogoResetearPassword
from ...data.repositories.RepositorioUsuariosImpl import REPOSITORIO_USUARIOS


@REQUIERE_ROL(ROLES.SUPERADMIN, ROLES.ADMIN)
class PaginaGestionUsuarios(LayoutBase):
    """Página principal de gestión de usuarios"""
    
    def __init__(self, pagina: ft.Page, usuario):
        # Inicializar layout base
        super().__init__(
            pagina=pagina,
            usuario=usuario,
            titulo_vista="Gestión de Usuarios",
            mostrar_boton_volver=True,
            index_navegacion=3,  # Usuarios es el 4to item
            on_volver_dashboard=self._VOLVER,
            on_cerrar_sesion=self._SALIR
        )
        
        self._bloc = UsuariosBloc(REPOSITORIO_USUARIOS)
        
        # Filtros
        self._filtro_rol = None
        self._filtro_estado = None
        
        # Componentes
        self._tabla = None
        self._loading = None
        
        self._CONSTRUIR_UI()
        self._bloc.AGREGAR_LISTENER(self._ON_ESTADO_CAMBIO)
        
        # Cargar datos iniciales
        self._CARGAR_USUARIOS()
    
    def _CONSTRUIR_UI(self):
        """Construye la interfaz"""
        # Barra de acciones
        acciones = ft.Row([
            ft.Container(expand=True),
            ft.Button(
                "Nuevo Usuario",
                icon=ft.icons.Icons.PERSON_ADD,
                on_click=self._ABRIR_DIALOGO_NUEVO,
                bgcolor=COLORES.PRIMARIO,
                color=ft.Colors.WHITE
            ),
            ft.IconButton(
                icon=ft.icons.Icons.REFRESH,
                tooltip="Recargar",
                on_click=lambda e: self._CARGAR_USUARIOS(),
                icon_color=COLORES.PRIMARIO
            )
        ], alignment=ft.MainAxisAlignment.END)
        
        # Filtros
        roles_opciones = [ft.dropdown.Option("TODOS", "Todos los Roles")]
        try:
            roles = REPOSITORIO_USUARIOS.OBTENER_ROLES_DISPONIBLES()
            for rol in roles:
                roles_opciones.append(ft.dropdown.Option(
                    rol.NOMBRE,
                    rol.NOMBRE.replace("_", " ").title()
                ))
        except:
            pass
        
        self._filtro_rol = ft.Dropdown(
            label="Filtrar por Rol",
            options=roles_opciones,
            value="TODOS",
            width=200,
            on_select=lambda e: self._CARGAR_USUARIOS()
        )
        
        self._filtro_estado = ft.Dropdown(
            label="Estado",
            options=[
                ft.dropdown.Option("TODOS", "Todos"),
                ft.dropdown.Option("ACTIVOS", "Activos"),
                ft.dropdown.Option("INACTIVOS", "Inactivos"),
            ],
            value="TODOS",
            width=150,
            on_select=lambda e: self._CARGAR_USUARIOS()
        )
        
        filtros = ft.Container(
            content=ft.ResponsiveRow([
                ft.Container(self._filtro_rol, col={"xs": 12, "sm": 6, "md": 3}),
                ft.Container(self._filtro_estado, col={"xs": 12, "sm": 6, "md": 3})
            ], spacing=6, run_spacing=6),
            bgcolor=ft.Colors.BLUE_50,
            border_radius=4,
            padding=6,
            border=ft.border.all(1, ft.Colors.BLUE_200)
        )
        
        # Loading indicator
        self._loading = ft.ProgressRing(visible=False)
        
        # Tabla
        rol_actual = ""
        if self._usuario.ROLES:
            rol_actual = self._usuario.ROLES[0].NOMBRE if hasattr(self._usuario.ROLES[0], 'NOMBRE') else self._usuario.ROLES[0]
        
        self._tabla = TablaUsuarios(
            on_editar=self._ABRIR_DIALOGO_EDITAR,
            on_cambiar_estado=self._CAMBIAR_ESTADO_USUARIO,
            on_cambiar_rol=self._ABRIR_DIALOGO_CAMBIAR_ROL,
            on_resetear_password=self._ABRIR_DIALOGO_RESETEAR_PASSWORD,
            usuario_actual_rol=rol_actual
        )
        
        # Contenido principal
        contenido = ft.Container(
            content=ft.Column([
                acciones,
                filtros,
                ft.Container(
                    content=self._loading,
                    alignment=ft.alignment.center,
                    height=30
                ),
                ft.Container(
                    content=self._tabla,
                    expand=True,
                )
            ], 
            spacing=4,
            expand=True
            ),
            padding=0,
            expand=True
        )
        
        # Usar LayoutBase.construir()
        self.construir(contenido)
    
    def _ON_ESTADO_CAMBIO(self, estado):
        """Maneja cambios de estado del BLoC"""
        if isinstance(estado, UsuariosCargando):
            self._loading.visible = True
            safe_update(self._pagina)
        
        elif isinstance(estado, UsuariosCargados):
            self._loading.visible = False
            self._tabla.ACTUALIZAR_DATOS(estado.usuarios)
            safe_update(self._pagina)
        
        elif isinstance(estado, (UsuarioCreado, UsuarioActualizado)):
            self._loading.visible = False
            self._MOSTRAR_SNACKBAR(estado.mensaje, es_error=False)
            self._CERRAR_DIALOGO()
            self._CARGAR_USUARIOS()  # Recargar lista
        
        elif isinstance(estado, UsuarioError):
            self._loading.visible = False
            self._MOSTRAR_SNACKBAR(estado.mensaje, es_error=True)
            safe_update(self._pagina)
    
    def _CARGAR_USUARIOS(self):
        """Carga la lista de usuarios con filtros"""
        rol_filtro = None if self._filtro_rol.value == "TODOS" else self._filtro_rol.value
        
        estado_filtro = None
        if self._filtro_estado.value == "ACTIVOS":
            estado_filtro = True
        elif self._filtro_estado.value == "INACTIVOS":
            estado_filtro = False
        
        # Filtrar por sucursal si es admin
        sucursal_id = None
        rol_usuario = self._usuario.ROLES[0].NOMBRE if hasattr(self._usuario.ROLES[0], 'NOMBRE') else self._usuario.ROLES[0]
        if rol_usuario == "ADMIN":
            sucursal_id = self._usuario.SUCURSAL_ID
        
        self._bloc.AGREGAR_EVENTO(CargarUsuarios(
            rol_filtro=rol_filtro,
            estado_filtro=estado_filtro,
            sucursal_id=sucursal_id
        ))
    
    def _ABRIR_DIALOGO_NUEVO(self, e):
        """Abre el diálogo para crear usuario"""
        try:
            roles = REPOSITORIO_USUARIOS.OBTENER_ROLES_DISPONIBLES()
            sucursales = self._OBTENER_SUCURSALES()
            
            dialogo = DialogoUsuario(
                on_guardar=self._CREAR_USUARIO,
                on_cancelar=self._CERRAR_DIALOGO,
                roles_disponibles=roles,
                sucursales=sucursales,
                es_edicion=False
            )
            
            self._pagina.dialog = dialogo
            dialogo.open = True
            safe_update(self._pagina)
        except Exception as ex:
            self._MOSTRAR_SNACKBAR(f"Error: {ex}", es_error=True)
    
    def _ABRIR_DIALOGO_EDITAR(self, usuario):
        """Abre el diálogo para editar usuario"""
        try:
            roles = REPOSITORIO_USUARIOS.OBTENER_ROLES_DISPONIBLES()
            sucursales = self._OBTENER_SUCURSALES()
            
            dialogo = DialogoUsuario(
                on_guardar=lambda datos: self._ACTUALIZAR_USUARIO(usuario.ID, datos),
                on_cancelar=self._CERRAR_DIALOGO,
                usuario=usuario,
                roles_disponibles=roles,
                sucursales=sucursales,
                es_edicion=True
            )
            
            self._pagina.dialog = dialogo
            dialogo.open = True
            safe_update(self._pagina)
        except Exception as ex:
            self._MOSTRAR_SNACKBAR(f"Error: {ex}", es_error=True)
    
    def _ABRIR_DIALOGO_CAMBIAR_ROL(self, usuario):
        """Abre diálogo para cambiar rol"""
        try:
            roles = REPOSITORIO_USUARIOS.OBTENER_ROLES_DISPONIBLES()
            
            dialogo = DialogoCambiarRol(
                usuario=usuario,
                roles_disponibles=roles,
                on_guardar=lambda nuevo_rol: self._CAMBIAR_ROL(usuario.ID, nuevo_rol),
                on_cancelar=self._CERRAR_DIALOGO
            )
            
            self._pagina.dialog = dialogo
            dialogo.open = True
            safe_update(self._pagina)
        except Exception as ex:
            self._MOSTRAR_SNACKBAR(f"Error: {ex}", es_error=True)
    
    def _ABRIR_DIALOGO_RESETEAR_PASSWORD(self, usuario):
        """Abre diálogo para resetear contraseña"""
        dialogo = DialogoResetearPassword(
            usuario=usuario,
            on_guardar=lambda nueva: self._RESETEAR_PASSWORD(usuario.ID, nueva),
            on_cancelar=self._CERRAR_DIALOGO
        )
        
        self._pagina.dialog = dialogo
        dialogo.open = True
        safe_update(self._pagina)
    
    def _CREAR_USUARIO(self, datos):
        """Crea un nuevo usuario"""
        self._bloc.AGREGAR_EVENTO(CrearUsuario(
            nombre_usuario=datos["nombre_usuario"],
            email=datos["email"],
            contrasena=datos["contrasena"],
            nombre_completo=datos["nombre_completo"],
            rol=datos["rol"],
            sucursal_id=datos["sucursal_id"],
            activo=datos["activo"]
        ))
    
    def _ACTUALIZAR_USUARIO(self, usuario_id, datos):
        """Actualiza un usuario existente"""
        self._bloc.AGREGAR_EVENTO(ActualizarUsuario(
            usuario_id=usuario_id,
            datos=datos
        ))
    
    def _CAMBIAR_ESTADO_USUARIO(self, usuario):
        """Cambia el estado activo/inactivo"""
        nuevo_estado = not usuario.ACTIVO
        self._bloc.AGREGAR_EVENTO(CambiarEstadoUsuario(
            usuario_id=usuario.ID,
            activo=nuevo_estado
        ))
    
    def _CAMBIAR_ROL(self, usuario_id, nuevo_rol):
        """Cambia el rol de un usuario"""
        self._bloc.AGREGAR_EVENTO(CambiarRolUsuario(
            usuario_id=usuario_id,
            nuevo_rol=nuevo_rol
        ))
    
    def _RESETEAR_PASSWORD(self, usuario_id, nueva_contrasena):
        """Resetea la contraseña"""
        self._bloc.AGREGAR_EVENTO(ResetearContrasena(
            usuario_id=usuario_id,
            nueva_contrasena=nueva_contrasena
        ))
    
    def _OBTENER_SUCURSALES(self):
        """Obtiene lista de sucursales"""
        sesion = OBTENER_SESION()
        try:
            return sesion.query(MODELO_SUCURSAL).all()
        finally:
            sesion.close()
    
    def _CERRAR_DIALOGO(self):
        """Cierra el diálogo actual"""
        if self._pagina.dialog:
            self._pagina.dialog.open = False
            safe_update(self._pagina)
    
    def _MOSTRAR_SNACKBAR(self, mensaje, es_error=False):
        """Muestra mensaje de notificación"""
        self._pagina.snack_bar = ft.SnackBar(
            content=ft.Text(mensaje),
            bgcolor=COLORES.PELIGRO if es_error else COLORES.EXITO
        )
        self._pagina.snack_bar.open = True
        safe_update(self._pagina)
    
    def _VOLVER(self, e=None):
        """Vuelve al dashboard"""
        from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
        
        self._bloc.DISPOSE()
        self._pagina.controls.clear()
        self._pagina.controls.append(PaginaAdmin(self._pagina, self._usuario))
        safe_update(self._pagina)
    
    def _SALIR(self, e=None):
        """Cerrar sesión"""
        from features.autenticacion.presentation.pages.PaginaLogin import PaginaLogin
        
        self._bloc.DISPOSE()
        self._pagina.controls.clear()
        self._pagina.add(PaginaLogin(self._pagina))
        safe_update(self._pagina)
    
    def DID_UNMOUNT(self):
        """Limpieza al desmontar"""
        self._bloc.DISPOSE()
