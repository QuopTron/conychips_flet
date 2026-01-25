import flet as ft
from features.autenticacion.domain.entities.Usuario import Usuario
from typing import Optional, List
import json
from core.Constantes import (
    COLORES,
    TAMANOS,
    ICONOS,
    ERRORES_AUTENTICACION,
    ERRORES_VALIDACION,
    MENSAJES_EXITO,
)
from core.decoradores.DecoradorVistas import REQUIERE_ROL
from core.Constantes import ROLES


@REQUIERE_ROL(ROLES.SUPERADMIN)
class PaginaGestionRoles(ft.Column):

    def __init__(self, PAGINA: ft.Page, USUARIO: Usuario, on_volver_dashboard=None):
        super().__init__()
        self._PAGINA = PAGINA
        self._USUARIO = USUARIO
        self._on_volver_dashboard = on_volver_dashboard
        
        self._LISTA_ROLES: Optional[ft.Column] = None
        self._DIALOGO_CREAR_ROL: Optional[ft.AlertDialog] = None
        self._ROLES_ACTUALES: List = []
        
        self._CONSTRUIR()
        self._CARGAR_ROLES()

    def _CONSTRUIR(self):
        
        HEADER = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ICONOS.ADMIN, size=TAMANOS.ICONO_LG, color=COLORES.PRIMARIO),
                    ft.Text(
                        "Gestión de Roles",
                        size=TAMANOS.TEXTO_4XL,
                        weight=ft.FontWeight.BOLD,
                        color=COLORES.PRIMARIO
                    ),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        "← Volver al Dashboard",
                        icon=ft.Icons.HOME,
                        on_click=self._volver_dashboard,
                        bgcolor=COLORES.SECUNDARIO,
                        color=COLORES.TEXTO_BLANCO,
                    ),
                    ft.ElevatedButton(
                        "Nuevo Rol",
                        icon=ICONOS.AGREGAR,
                        on_click=self._MOSTRAR_DIALOGO_CREAR_ROL,
                        bgcolor=COLORES.PRIMARIO,
                        color=COLORES.TEXTO_BLANCO,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=TAMANOS.ESPACIADO_MD,
            ),
            padding=TAMANOS.PADDING_XL,
            bgcolor=COLORES.FONDO_BLANCO,
            border=ft.border.only(bottom=ft.BorderSide(1, COLORES.BORDE)),
        )
        
        self._LISTA_ROLES = ft.Column(
            controls=[],
            spacing=TAMANOS.ESPACIADO_MD,
            scroll=ft.ScrollMode.AUTO,
        )
        
        CONTENEDOR_ROLES = ft.Container(
            content=self._LISTA_ROLES,
            padding=TAMANOS.PADDING_XL,
            expand=True,
        )
        
        self.controls = [
            ft.Container(
                content=ft.Column(
                    controls=[HEADER, CONTENEDOR_ROLES],
                    spacing=0,
                    expand=True,
                ),
                bgcolor=COLORES.FONDO,
                expand=True,
            )
        ]
        self.expand = True

    def _CARGAR_ROLES(self):
        try:
            from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_ROL
            
            with OBTENER_SESION() as sesion:
                roles = sesion.query(MODELO_ROL).order_by(MODELO_ROL.FECHA_CREACION.desc()).all()
                self._ROLES_ACTUALES = roles
                
                self._LISTA_ROLES.controls.clear()
                
                if not roles:
                    self._LISTA_ROLES.controls.append(
                        ft.Container(
                            content=ft.Text(
                                "No hay roles creados aún",
                                size=TAMANOS.TEXTO_LG,
                                color=COLORES.GRIS,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            alignment=ft.alignment.center,
                            padding=40,
                        )
                    )
                else:
                    for rol in roles:
                        self._LISTA_ROLES.controls.append(self._CREAR_CARD_ROL(rol))
                
                if getattr(self, "_PAGINA", None):
                    self._PAGINA.update()
                
        except Exception as e:
            print(f"Error cargando roles: {e}")
            self._MOSTRAR_ERROR(f"Error al cargar roles: {str(e)}")

    def _CREAR_CARD_ROL(self, ROL) -> ft.Container:
        try:
            permisos = json.loads(ROL.PERMISOS) if ROL.PERMISOS else []
        except:
            permisos = []
        
        num_permisos = len(permisos)
        from core.Constantes import ROLES

        es_super_admin = ROL.NOMBRE == ROLES.SUPERADMIN
        
        color_rol = COLORES.SECUNDARIO if es_super_admin else COLORES.PRIMARIO
        
        permisos_text = "*" if "*" in permisos else f"{num_permisos} permisos"
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(
                                ICONOS.ROLES if es_super_admin else ICONOS.PERMISOS,
                                size=TAMANOS.TEXTO_3XL,
                                color=color_rol,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        ROL.NOMBRE,
                                        size=TAMANOS.TEXTO_XL,
                                        weight=ft.FontWeight.BOLD,
                                        color=color_rol,
                                    ),
                                    ft.Text(
                                        ROL.DESCRIPCION or "Sin descripción",
                                        size=TAMANOS.TEXTO_SM,
                                        color=COLORES.GRIS,
                                    ),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                            ft.Container(
                                content=ft.Text(
                                    permisos_text,
                                    size=TAMANOS.TEXTO_SM,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                padding=ft.padding.symmetric(horizontal=TAMANOS.PADDING_MD, vertical=TAMANOS.PADDING_SM),
                                bgcolor=ft.Colors.GREEN_50,
                                border_radius=TAMANOS.RADIO_LG,
                                border=ft.border.all(1, ft.Colors.GREEN_300),
                            ),
                            ft.Container(
                                content=ft.Text(
                                    "Activo" if ROL.ACTIVO else "Inactivo",
                                    size=TAMANOS.TEXTO_SM,
                                ),
                                padding=ft.padding.symmetric(horizontal=TAMANOS.PADDING_MD, vertical=TAMANOS.PADDING_SM),
                                bgcolor=ft.Colors.GREEN_50 if ROL.ACTIVO else ft.Colors.RED_50,
                                border_radius=TAMANOS.RADIO_LG,
                            ),
                        ],
                        spacing=TAMANOS.ESPACIADO_LG,
                    ),
                    ft.Divider(height=1, color=COLORES.BORDE_CLARO),
                    ft.Row(
                        controls=[
                            ft.TextButton(
                                "Ver Permisos",
                                icon=ICONOS.VISIBLE,
                                on_click=lambda e, r=ROL: self._VER_PERMISOS_ROL(r),
                            ),
                            ft.TextButton(
                                "Editar",
                                icon=ICONOS.EDITAR,
                                on_click=lambda e, r=ROL: self._EDITAR_ROL(r),
                                disabled=es_super_admin,
                            ),
                            ft.TextButton(
                                "Eliminar",
                                icon=ICONOS.ELIMINAR,
                                on_click=lambda e, r=ROL: self._ELIMINAR_ROL(r),
                                style=ft.ButtonStyle(color=COLORES.PELIGRO),
                                disabled=es_super_admin,
                            ),
                        ],
                        spacing=TAMANOS.ESPACIADO_MD,
                    ),
                ],
                spacing=TAMANOS.ESPACIADO_MD,
            ),
            padding=TAMANOS.PADDING_XL,
            bgcolor=COLORES.FONDO_BLANCO,
            border_radius=TAMANOS.RADIO_MD,
            border=ft.border.all(1, COLORES.BORDE),
        )

    def _MOSTRAR_DIALOGO_CREAR_ROL(self, e):
        from core.Constantes import PERMISOS_DISPONIBLES
        
        campo_nombre = ft.TextField(
            label="Nombre del Rol",
            hint_text="Ej: cajero, mesero, gerente",
            prefix_icon=ICONOS.PERMISOS,
        )
        
        campo_descripcion = ft.TextField(
            label="Descripción",
            hint_text="Describe las responsabilidades de este rol",
            multiline=True,
            min_lines=2,
            max_lines=3,
        )
        
        permisos_checkboxes = []
        for permiso in PERMISOS_DISPONIBLES:
            permisos_checkboxes.append(
                ft.Checkbox(
                    label=permiso,
                    value=False,
                )
            )
        
        contenedor_permisos = ft.Container(
            content=ft.Column(
                controls=permisos_checkboxes,
                spacing=TAMANOS.ESPACIADO_SM,
                scroll=ft.ScrollMode.AUTO,
                height=300,
            ),
            border=ft.border.all(1, COLORES.BORDE),
            border_radius=TAMANOS.RADIO_SM,
            padding=TAMANOS.ESPACIADO_MD,
        )
        
        def CREAR_ROL_HANDLER(e):
            nombre = campo_nombre.value
            descripcion = campo_descripcion.value
            
            if not nombre:
                self._MOSTRAR_ERROR("El nombre del rol es requerido")
                return
            
            permisos_seleccionados = [
                cb.label for cb in permisos_checkboxes if cb.value
            ]
            
            if not permisos_seleccionados:
                self._MOSTRAR_ERROR("Debes seleccionar al menos un permiso")
                return
            
            self._CREAR_ROL(nombre, descripcion, permisos_seleccionados)
            if self._PAGINA.dialog:
                self._PAGINA.dialog.open = False
                self._PAGINA.update()
        
        self._DIALOGO_CREAR_ROL = ft.AlertDialog(
            modal=True,
            title=ft.Text("Crear Nuevo Rol"),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        campo_nombre,
                        campo_descripcion,
                        ft.Text("Permisos:", weight=ft.FontWeight.BOLD, size=TAMANOS.TEXTO_LG),
                        contenedor_permisos,
                    ],
                    spacing=TAMANOS.ESPACIADO_LG,
                    tight=True,
                ),
                width=500,
                height=600,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self._CERRAR_DIALOGO()),
                ft.ElevatedButton(
                    "Crear Rol",
                    icon=ICONOS.GUARDAR,
                    on_click=CREAR_ROL_HANDLER,
                    bgcolor=COLORES.PRIMARIO,
                    color=COLORES.TEXTO_BLANCO,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self._PAGINA.dialog = self._DIALOGO_CREAR_ROL
        self._DIALOGO_CREAR_ROL.open = True
        self._PAGINA.update()

    def _CERRAR_DIALOGO(self):
        if self._PAGINA.dialog:
            self._PAGINA.dialog.open = False
            self._PAGINA.update()

    def _CREAR_ROL(self, NOMBRE: str, DESCRIPCION: str, PERMISOS: List[str]):
        try:
            from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_ROL
            from datetime import datetime
            
            with OBTENER_SESION() as sesion:
                existe = sesion.query(MODELO_ROL).filter_by(NOMBRE=NOMBRE).first()
                if existe:
                    self._MOSTRAR_ERROR(f"Ya existe un rol con el nombre '{NOMBRE}'")
                    return
                
                nuevo_rol = MODELO_ROL(
                    NOMBRE=NOMBRE.strip().upper(),
                    DESCRIPCION=DESCRIPCION,
                    PERMISOS=json.dumps(PERMISOS),
                    ACTIVO=True,
                    FECHA_CREACION=datetime.utcnow()
                )
                
                sesion.add(nuevo_rol)
                sesion.commit()
                
                self._MOSTRAR_EXITO(f"Rol '{NOMBRE}' creado exitosamente")
                self._CARGAR_ROLES()
                
        except Exception as e:
            print(f"Error creando rol: {e}")
            self._MOSTRAR_ERROR(f"Error al crear rol: {str(e)}")

    def _VER_PERMISOS_ROL(self, ROL):
        try:
            permisos = json.loads(ROL.PERMISOS) if ROL.PERMISOS else []
        except:
            permisos = []
        
        if "*" in permisos:
            permisos_text = "Todos los permisos (*)"
        else:
            permisos_text = "\n".join([f"• {p}" for p in permisos])
        
        dialogo = ft.AlertDialog(
            title=ft.Text(f"Permisos de '{ROL.NOMBRE}'"),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(permisos_text, selectable=True),
                    ],
                    scroll=ft.ScrollMode.AUTO,
                ),
                width=400,
                height=300,
            ),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda e: self._CERRAR_DIALOGO()),
            ],
        )

        self._PAGINA.dialog = dialogo
        dialogo.open = True
        self._PAGINA.update()

    def _EDITAR_ROL(self, ROL):
        self._MOSTRAR_ERROR("Función de edición en desarrollo")

    def _ELIMINAR_ROL(self, ROL):
        def CONFIRMAR_ELIMINACION(e):
            try:
                from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_ROL
                
                with OBTENER_SESION() as sesion:
                    rol_a_eliminar = sesion.query(MODELO_ROL).filter_by(ID=ROL.ID).first()
                    if rol_a_eliminar:
                        sesion.delete(rol_a_eliminar)
                        sesion.commit()
                        self._MOSTRAR_EXITO(f"Rol '{ROL.NOMBRE}' eliminado")
                        self._CARGAR_ROLES()
                
                self._CERRAR_DIALOGO()
                
            except Exception as e:
                print(f"Error eliminando rol: {e}")
                self._MOSTRAR_ERROR(f"Error al eliminar rol: {str(e)}")
        
        dialogo = ft.AlertDialog(
            title=ft.Text("Confirmar Eliminación"),
            content=ft.Text(f"¿Estás seguro de eliminar el rol '{ROL.NOMBRE}'?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self._CERRAR_DIALOGO()),
                ft.ElevatedButton(
                    "Eliminar",
                    on_click=CONFIRMAR_ELIMINACION,
                    bgcolor=COLORES.PELIGRO,
                    color=COLORES.TEXTO_BLANCO,
                ),
            ],
        )

        self._PAGINA.dialog = dialogo
        dialogo.open = True
        self._PAGINA.update()

    def _MOSTRAR_ERROR(self, MENSAJE: str):
        snackbar = ft.SnackBar(
            content=ft.Text(MENSAJE, color=COLORES.TEXTO_BLANCO),
            bgcolor=COLORES.PELIGRO,
        )
        self._PAGINA.overlay.append(snackbar)
        snackbar.open = True
        self._PAGINA.update()

    def _volver_dashboard(self, e):
        """Vuelve al dashboard principal"""
        if self._on_volver_dashboard:
            self._on_volver_dashboard()
        else:
            # Fallback: volver manualmente
            from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
            self._PAGINA.controls.clear()
            self._PAGINA.controls.append(PaginaAdmin(self._PAGINA, self._USUARIO))
            self._PAGINA.update()

    def _MOSTRAR_EXITO(self, MENSAJE: str):
        snackbar = ft.SnackBar(
            content=ft.Text(MENSAJE, color=COLORES.TEXTO_BLANCO),
            bgcolor=COLORES.EXITO,
        )
        self._PAGINA.overlay.append(snackbar)
        snackbar.open = True
        self._PAGINA.update()
