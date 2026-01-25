import flet as ft
from datetime import datetime

from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION,
    MODELO_USUARIO,
    MODELO_ROL,
)
from core.Constantes import (
    COLORES,
    TAMANOS,
    ICONOS,
    ROLES,
    ERRORES_VALIDACION,
    ERRORES_AUTENTICACION,
    MENSAJES_EXITO,
)
from features.autenticacion.domain.entities.Usuario import Usuario
from core.decoradores.DecoradorVistas import REQUIERE_ROL
import bcrypt


@REQUIERE_ROL(ROLES.SUPERADMIN)
class PaginaUsuarios(ft.Column):

    def __init__(self, PAGINA: ft.Page, USUARIO: Usuario):
        super().__init__()
        self._PAGINA = PAGINA
        self._USUARIO = USUARIO
        self._LISTA = ft.Column(spacing=TAMANOS.ESPACIADO_MD)
        self._FILTRO_ROL = None
        self._FILTRO_ACTIVO = None
        self._CONSTRUIR()


    def _CONSTRUIR(self):
        self._FILTRO_ROL = ft.Dropdown(
            label="Filtrar por Rol",
            options=[ft.dropdown.Option("TODOS", "Todos")],
            value="TODOS",
            width=200,
            on_change=lambda e: self._CARGAR_DATOS(),
        )
        
        self._FILTRO_ACTIVO = ft.Dropdown(
            label="Estado",
            options=[
                ft.dropdown.Option("TODOS", "Todos"),
                ft.dropdown.Option("ACTIVO", "Activos"),
                ft.dropdown.Option("INACTIVO", "Inactivos"),
            ],
            value="TODOS",
            width=150,
            on_change=lambda e: self._CARGAR_DATOS(),
        )
        
        self._CARGAR_ROLES_FILTRO()

        HEADER = ft.Row(
            controls=[
                ft.Icon(
                    ICONOS.USUARIOS,
                    size=TAMANOS.ICONO_LG,
                    color=COLORES.PRIMARIO
                ),
                ft.Text(
                    "Gestión de Usuarios",
                    size=TAMANOS.TEXTO_3XL,
                    weight=ft.FontWeight.BOLD,
                    color=COLORES.TEXTO
                ),
                ft.Container(expand=True),
                self._FILTRO_ROL,
                self._FILTRO_ACTIVO,
                ft.ElevatedButton(
                    "Menú",
                    icon=ICONOS.DASHBOARD,
                    on_click=self._IR_MENU,
                    bgcolor=COLORES.PRIMARIO,
                    color=COLORES.TEXTO_BLANCO
                ),
                ft.ElevatedButton(
                    "Salir",
                    icon=ICONOS.CERRAR_SESION,
                    on_click=self._SALIR,
                    bgcolor=COLORES.PELIGRO,
                    color=COLORES.TEXTO_BLANCO
                ),
                ft.ElevatedButton(
                    "Nuevo Usuario",
                    icon=ICONOS.AGREGAR,
                    on_click=self._NUEVO,
                    bgcolor=COLORES.EXITO,
                    color=COLORES.TEXTO_BLANCO
                ),
            ],
            spacing=TAMANOS.ESPACIADO_MD,
            wrap=True,
        )

        self.controls = [
            ft.Container(
                content=ft.Column(
                    controls=[
                        HEADER,
                        ft.Divider(height=1, color=COLORES.BORDE),
                        self._LISTA,
                    ],
                    spacing=TAMANOS.ESPACIADO_LG,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=TAMANOS.PADDING_XL,
                expand=True,
                bgcolor=COLORES.FONDO,
            )
        ]
        self.expand = True
        self._CARGAR_DATOS()


    def _CARGAR_ROLES_FILTRO(self):
        sesion = OBTENER_SESION()
        roles = sesion.query(MODELO_ROL).all()
        sesion.close()
        
        for rol in roles:
            self._FILTRO_ROL.options.append(
                ft.dropdown.Option(rol.NOMBRE, rol.NOMBRE)
            )


    def _CARGAR_DATOS(self):
        self._LISTA.controls.clear()
        
        sesion = OBTENER_SESION()
        query = sesion.query(MODELO_USUARIO)
        
        if self._FILTRO_ACTIVO.value == "ACTIVO":
            query = query.filter_by(ACTIVO=True)
        elif self._FILTRO_ACTIVO.value == "INACTIVO":
            query = query.filter_by(ACTIVO=False)
        
        usuarios = query.all()

        # Ensure roles are loaded before closing session to avoid DetachedInstanceError
        for u in usuarios:
            try:
                _ = u.ROLES
            except Exception:
                pass

        if self._FILTRO_ROL.value and self._FILTRO_ROL.value != "TODOS":
            usuarios = [u for u in usuarios if any(getattr(r, 'NOMBRE', None) == self._FILTRO_ROL.value for r in u.ROLES)]

        sesion.close()

        if not usuarios:
            self._LISTA.controls.append(
                ft.Container(
                    content=ft.Text(
                        "No hay usuarios registrados",
                        size=TAMANOS.TEXTO_LG,
                        color=COLORES.TEXTO_SECUNDARIO,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    alignment=ft.alignment.center,
                    padding=TAMANOS.PADDING_2XL,
                )
            )
        else:
            for u in usuarios:
                self._LISTA.controls.append(self._CREAR_CARD(u))

        if getattr(self, "_PAGINA", None):
            self._PAGINA.update()


    def _CREAR_CARD(self, USUARIO_OBJ):
        ROLES_NOMBRES = [r.NOMBRE for r in USUARIO_OBJ.ROLES]
        ROLES_STR = ", ".join(ROLES_NOMBRES) if ROLES_NOMBRES else "Sin rol"
        
        COLOR_ESTADO = COLORES.EXITO if USUARIO_OBJ.ACTIVO else COLORES.PELIGRO
        TEXTO_ESTADO = "ACTIVO" if USUARIO_OBJ.ACTIVO else "INACTIVO"
        
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        ICONOS.USUARIO,
                        size=TAMANOS.ICONO_XL,
                        color=COLORES.PRIMARIO
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(
                                USUARIO_OBJ.NOMBRE_USUARIO,
                                size=TAMANOS.TEXTO_LG,
                                weight=ft.FontWeight.BOLD,
                                color=COLORES.TEXTO
                            ),
                            ft.Text(
                                USUARIO_OBJ.EMAIL,
                                size=TAMANOS.TEXTO_SM,
                                color=COLORES.TEXTO_SECUNDARIO
                            ),
                            ft.Row(
                                controls=[
                                    ft.Container(
                                        content=ft.Text(
                                            ROLES_STR,
                                            size=TAMANOS.TEXTO_SM,
                                            color=COLORES.TEXTO_BLANCO,
                                        ),
                                        padding=ft.padding.symmetric(
                                            horizontal=TAMANOS.PADDING_SM,
                                            vertical=TAMANOS.PADDING_XS
                                        ),
                                        bgcolor=COLORES.SECUNDARIO,
                                        border_radius=TAMANOS.RADIO_SM,
                                    ),
                                    ft.Container(
                                        content=ft.Text(
                                            TEXTO_ESTADO,
                                            size=TAMANOS.TEXTO_SM,
                                            color=COLORES.TEXTO_BLANCO,
                                        ),
                                        padding=ft.padding.symmetric(
                                            horizontal=TAMANOS.PADDING_SM,
                                            vertical=TAMANOS.PADDING_XS
                                        ),
                                        bgcolor=COLOR_ESTADO,
                                        border_radius=TAMANOS.RADIO_SM,
                                    ),
                                ],
                                spacing=TAMANOS.ESPACIADO_SM,
                            ),
                        ],
                        spacing=TAMANOS.ESPACIADO_XS,
                        expand=True,
                    ),
                    ft.Row(
                        controls=[
                            ft.IconButton(
                                icon=ICONOS.EDITAR,
                                icon_color=COLORES.INFO,
                                tooltip="Editar",
                                on_click=lambda e, u=USUARIO_OBJ: self._EDITAR(u),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.BLOCK if USUARIO_OBJ.ACTIVO else ft.Icons.CHECK_CIRCLE,
                                icon_color=COLORES.ADVERTENCIA if USUARIO_OBJ.ACTIVO else COLORES.EXITO,
                                tooltip="Desactivar" if USUARIO_OBJ.ACTIVO else "Activar",
                                on_click=lambda e, u=USUARIO_OBJ: self._TOGGLE_ACTIVO(u),
                            ),
                            ft.IconButton(
                                icon=ICONOS.ELIMINAR,
                                icon_color=COLORES.PELIGRO,
                                tooltip="Eliminar",
                                on_click=lambda e, u=USUARIO_OBJ: self._ELIMINAR(u),
                            ),
                        ],
                        spacing=TAMANOS.ESPACIADO_SM,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=TAMANOS.PADDING_LG,
            bgcolor=COLORES.FONDO_BLANCO,
            border_radius=TAMANOS.RADIO_MD,
            border=ft.border.all(1, COLORES.BORDE),
        )


    def _NUEVO(self, e):
        self._ABRIR_FORMULARIO(None)


    def _EDITAR(self, USUARIO_OBJ):
        self._ABRIR_FORMULARIO(USUARIO_OBJ)


    def _ABRIR_FORMULARIO(self, USUARIO_OBJ):
        ES_EDICION = USUARIO_OBJ is not None

        CAMPO_NOMBRE = ft.TextField(
            label="Nombre de Usuario",
            value=USUARIO_OBJ.NOMBRE_USUARIO if ES_EDICION else "",
            width=TAMANOS.ANCHO_INPUT,
        )
        
        CAMPO_EMAIL = ft.TextField(
            label="Correo Electrónico",
            value=USUARIO_OBJ.EMAIL if ES_EDICION else "",
            width=TAMANOS.ANCHO_INPUT,
        )
        
        CAMPO_CONTRASENA = ft.TextField(
            label="Contraseña" + (" (dejar vacío para no cambiar)" if ES_EDICION else ""),
            password=True,
            can_reveal_password=True,
            width=TAMANOS.ANCHO_INPUT,
        )
        
        sesion = OBTENER_SESION()
        roles = sesion.query(MODELO_ROL).all()
        sesion.close()
        
        OPCIONES_ROLES = [ft.dropdown.Option(r.NOMBRE, r.NOMBRE) for r in roles]
        ROL_ACTUAL = USUARIO_OBJ.ROLES[0].NOMBRE if ES_EDICION and USUARIO_OBJ.ROLES else ""
        
        CAMPO_ROL = ft.Dropdown(
            label="Rol",
            options=OPCIONES_ROLES,
            value=ROL_ACTUAL,
            width=TAMANOS.ANCHO_INPUT,
        )

        def GUARDAR(e):
            if not CAMPO_NOMBRE.value or not CAMPO_EMAIL.value:
                self._MOSTRAR_ERROR(ERRORES_VALIDACION.CAMPO_REQUERIDO)
                return
                
            if not ES_EDICION and not CAMPO_CONTRASENA.value:
                self._MOSTRAR_ERROR("La contraseña es obligatoria para usuarios nuevos")
                return

            sesion = OBTENER_SESION()
            
            if ES_EDICION:
                usuario = sesion.query(MODELO_USUARIO).filter_by(ID=USUARIO_OBJ.ID).first()
                usuario.NOMBRE_USUARIO = CAMPO_NOMBRE.value
                usuario.EMAIL = CAMPO_EMAIL.value
                
                if CAMPO_CONTRASENA.value:
                    SALT = bcrypt.gensalt()
                    HASH = bcrypt.hashpw(CAMPO_CONTRASENA.value.encode(), SALT)
                    usuario.CONTRASENA_HASH = HASH.decode()
                
                if CAMPO_ROL.value:
                    rol = sesion.query(MODELO_ROL).filter_by(NOMBRE=CAMPO_ROL.value).first()
                    if rol:
                        usuario.ROLES.clear()
                        usuario.ROLES.append(rol)
            else:
                SALT = bcrypt.gensalt()
                HASH = bcrypt.hashpw(CAMPO_CONTRASENA.value.encode(), SALT)
                
                nuevo = MODELO_USUARIO(
                    NOMBRE_USUARIO=CAMPO_NOMBRE.value,
                    EMAIL=CAMPO_EMAIL.value,
                    CONTRASENA_HASH=HASH.decode(),
                    HUELLA_DISPOSITIVO="system_created",
                    ACTIVO=True,
                    VERIFICADO=True,
                )
                
                if CAMPO_ROL.value:
                    rol = sesion.query(MODELO_ROL).filter_by(NOMBRE=CAMPO_ROL.value).first()
                    if rol:
                        nuevo.ROLES.append(rol)
                
                sesion.add(nuevo)

            sesion.commit()
            sesion.close()
            
            self._CERRAR_DIALOGO()
            self._CARGAR_DATOS()
            self._MOSTRAR_EXITO(MENSAJES_EXITO.GUARDADO_EXITOSO)

        DLG = ft.AlertDialog(
            title=ft.Text(
                "Editar Usuario" if ES_EDICION else "Nuevo Usuario",
                color=COLORES.TEXTO
            ),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        CAMPO_NOMBRE,
                        CAMPO_EMAIL,
                        CAMPO_CONTRASENA,
                        CAMPO_ROL,
                    ],
                    spacing=TAMANOS.ESPACIADO_MD,
                    tight=True,
                ),
                width=400,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self._CERRAR_DIALOGO()),
                ft.ElevatedButton(
                    "Guardar",
                    icon=ICONOS.GUARDAR,
                    on_click=GUARDAR,
                    bgcolor=COLORES.PRIMARIO,
                    color=COLORES.TEXTO_BLANCO
                ),
            ],
        )

        self._PAGINA.dialog = DLG
        DLG.open = True
        self._PAGINA.update()


    def _TOGGLE_ACTIVO(self, USUARIO_OBJ):
        sesion = OBTENER_SESION()
        usuario = sesion.query(MODELO_USUARIO).filter_by(ID=USUARIO_OBJ.ID).first()
        
        if usuario:
            usuario.ACTIVO = not usuario.ACTIVO
            sesion.commit()
        
        sesion.close()
        self._CARGAR_DATOS()
        self._MOSTRAR_EXITO("Estado actualizado correctamente")


    def _ELIMINAR(self, USUARIO_OBJ):
        if USUARIO_OBJ.ID == self._USUARIO.ID:
            self._MOSTRAR_ERROR("No puedes eliminar tu propia cuenta")
            return

        def CONFIRMAR(e):
            sesion = OBTENER_SESION()
            usuario = sesion.query(MODELO_USUARIO).filter_by(ID=USUARIO_OBJ.ID).first()
            
            if usuario:
                sesion.delete(usuario)
                sesion.commit()
            
            sesion.close()
            self._CERRAR_DIALOGO()
            self._CARGAR_DATOS()
            self._MOSTRAR_EXITO(MENSAJES_EXITO.ELIMINADO_EXITOSO)

        DLG = ft.AlertDialog(
            title=ft.Text("Confirmar Eliminación", color=COLORES.PELIGRO),
            content=ft.Text(
                f"¿Estás seguro que deseas eliminar al usuario '{USUARIO_OBJ.NOMBRE_USUARIO}'?",
                color=COLORES.TEXTO
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self._CERRAR_DIALOGO()),
                ft.ElevatedButton(
                    "Eliminar",
                    icon=ICONOS.ELIMINAR,
                    on_click=CONFIRMAR,
                    bgcolor=COLORES.PELIGRO,
                    color=COLORES.TEXTO_BLANCO
                ),
            ],
        )

        self._PAGINA.dialog = DLG
        DLG.open = True
        self._PAGINA.update()


    def _CERRAR_DIALOGO(self):
        if hasattr(self._PAGINA, "dialog") and self._PAGINA.dialog:
            self._PAGINA.dialog.open = False
            self._PAGINA.update()


    def _IR_MENU(self, e):
        from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
        
        self._PAGINA.controls.clear()
        self._PAGINA.controls.append(PaginaAdmin(self._PAGINA, self._USUARIO))
        self._PAGINA.update()


    def _SALIR(self, e):
        from features.autenticacion.presentation.pages.PaginaLogin import PaginaLogin
        
        self._PAGINA.controls.clear()
        self._PAGINA.controls.append(PaginaLogin(self._PAGINA))
        self._PAGINA.update()


    def _MOSTRAR_ERROR(self, MENSAJE: str):
        snackbar = ft.SnackBar(
            content=ft.Text(MENSAJE, color=COLORES.TEXTO_BLANCO),
            bgcolor=COLORES.PELIGRO,
        )
        self._PAGINA.overlay.append(snackbar)
        snackbar.open = True
        self._PAGINA.update()


    def _MOSTRAR_EXITO(self, MENSAJE: str):
        snackbar = ft.SnackBar(
            content=ft.Text(MENSAJE, color=COLORES.TEXTO_BLANCO),
            bgcolor=COLORES.EXITO,
        )
        self._PAGINA.overlay.append(snackbar)
        snackbar.open = True
        self._PAGINA.update()
