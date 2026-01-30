import flet as ft
from datetime import datetime

from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION,
    MODELO_HORARIO,
    MODELO_SUCURSAL,
)
from core.Constantes import (
    COLORES,
    TAMANOS,
    ICONOS,
    ERRORES_VALIDACION,
    MENSAJES_EXITO,
)
from core.Constantes import ROLES
from features.autenticacion.domain.entities.Usuario import Usuario
from core.decoradores.DecoradorVistas import REQUIERE_ROL

@REQUIERE_ROL(ROLES.SUPERADMIN, ROLES.ADMIN)
class PaginaHorarios(ft.Column):

    def __init__(self, PAGINA: ft.Page, USUARIO: Usuario):
        super().__init__()
        self._PAGINA = PAGINA
        self._USUARIO = USUARIO
        self._LISTA = ft.Column(spacing=TAMANOS.ESPACIADO_MD)
        self._CONSTRUIR()

    def _CONSTRUIR(self):
        HEADER = ft.Row(
            controls=[
                ft.Icon(ft.icons.Icons.SCHEDULE,
                    size=TAMANOS.ICONO_LG,
                    color=COLORES.INFO
                ),
                ft.Text(
                    "Gestión de Horarios",
                    size=TAMANOS.TEXTO_3XL,
                    weight=ft.FontWeight.BOLD,
                    color=COLORES.TEXTO
                ),
                ft.Container(expand=True),
                ft.Button(
                    "Menú",
                    icon=ICONOS.DASHBOARD,
                    on_click=self._IR_MENU,
                    bgcolor=COLORES.PRIMARIO,
                    color=COLORES.TEXTO_BLANCO
                ),
                ft.Button(
                    "Salir",
                    icon=ICONOS.CERRAR_SESION,
                    on_click=self._SALIR,
                    bgcolor=COLORES.PELIGRO,
                    color=COLORES.TEXTO_BLANCO
                ),
                ft.Button(
                    "Nuevo Horario",
                    icon=ICONOS.AGREGAR,
                    on_click=self._NUEVA,
                    bgcolor=COLORES.EXITO,
                    color=COLORES.TEXTO_BLANCO
                ),
            ],
            spacing=TAMANOS.ESPACIADO_MD,
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

    def _CARGAR_DATOS(self):
        self._LISTA.controls.clear()
        
        sesion = OBTENER_SESION()
        horarios = sesion.query(MODELO_HORARIO).all()
        sesion.close()

        if not horarios:
            self._LISTA.controls.append(
                ft.Container(
                    content=ft.Text(
                        "No hay horarios registrados",
                        size=TAMANOS.TEXTO_LG,
                        color=COLORES.TEXTO_SECUNDARIO,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    alignment=ft.Alignment(0, 0),
                    padding=TAMANOS.PADDING_2XL,
                )
            )
        else:
            for h in horarios:
                self._LISTA.controls.append(self._CREAR_CARD(h))

        if hasattr(self, "update"):
            self.update()

    def _CREAR_CARD(self, HORARIO):
        sesion = OBTENER_SESION()
        sucursal = sesion.query(MODELO_SUCURSAL).filter_by(ID=HORARIO.SUCURSAL_ID).first()
        nombre_sucursal = sucursal.NOMBRE if sucursal else "N/A"
        sesion.close()
        
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.icons.Icons.SCHEDULE,
                        size=TAMANOS.ICONO_XL,
                        color=COLORES.INFO
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(
                                HORARIO.NOMBRE,
                                size=TAMANOS.TEXTO_LG,
                                weight=ft.FontWeight.BOLD,
                                color=COLORES.TEXTO
                            ),
                            ft.Text(
                                f"Día: {HORARIO.DIA_SEMANA}",
                                size=TAMANOS.TEXTO_SM,
                                color=COLORES.TEXTO_SECUNDARIO
                            ),
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        f"Apertura: {HORARIO.HORA_APERTURA}",
                                        size=TAMANOS.TEXTO_SM,
                                        color=COLORES.INFO,
                                    ),
                                    ft.Text(
                                        f"Cierre: {HORARIO.HORA_CIERRE}",
                                        size=TAMANOS.TEXTO_SM,
                                        color=COLORES.INFO,
                                    ),
                                    ft.Text(
                                        f"Sucursal: {nombre_sucursal}",
                                        size=TAMANOS.TEXTO_XS,
                                        color=COLORES.TEXTO_SECUNDARIO,
                                    ),
                                ],
                                spacing=TAMANOS.ESPACIADO_MD,
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
                                on_click=lambda e, h=HORARIO: self._EDITAR(h),
                            ),
                            ft.IconButton(
                                icon=ICONOS.ELIMINAR,
                                icon_color=COLORES.PELIGRO,
                                tooltip="Eliminar",
                                on_click=lambda e, h=HORARIO: self._ELIMINAR(h),
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
            border=ft.Border.all(1, COLORES.BORDE),
        )

    def _NUEVA(self, e):
        self._ABRIR_FORMULARIO(None)

    def _EDITAR(self, HORARIO):
        self._ABRIR_FORMULARIO(HORARIO)

    def _ABRIR_FORMULARIO(self, HORARIO):
        ES_EDICION = HORARIO is not None

        sesion = OBTENER_SESION()
        sucursales = sesion.query(MODELO_SUCURSAL).all()
        sesion.close()

        opciones_sucursales = [
            ft.dropdown.Option(str(s.ID), s.NOMBRE) for s in sucursales
        ]

        CAMPO_NOMBRE = ft.TextField(
            label="Nombre",
            value=HORARIO.NOMBRE if ES_EDICION else "",
            width=TAMANOS.ANCHO_INPUT,
        )
        
        CAMPO_DIA_SEMANA = ft.Dropdown(
            label="Día de la Semana",
            value=HORARIO.DIA_SEMANA if ES_EDICION else "Lunes",
            width=TAMANOS.ANCHO_INPUT,
            options=[
                ft.dropdown.Option("Lunes", "Lunes"),
                ft.dropdown.Option("Martes", "Martes"),
                ft.dropdown.Option("Miércoles", "Miércoles"),
                ft.dropdown.Option("Jueves", "Jueves"),
                ft.dropdown.Option("Viernes", "Viernes"),
                ft.dropdown.Option("Sábado", "Sábado"),
                ft.dropdown.Option("Domingo", "Domingo"),
            ],
        )
        
        CAMPO_HORA_APERTURA = ft.TextField(
            label="Hora Apertura (HH:MM)",
            value=HORARIO.HORA_APERTURA if ES_EDICION else "",
            width=TAMANOS.ANCHO_INPUT,
        )
        
        CAMPO_HORA_CIERRE = ft.TextField(
            label="Hora Cierre (HH:MM)",
            value=HORARIO.HORA_CIERRE if ES_EDICION else "",
            width=TAMANOS.ANCHO_INPUT,
        )
        
        CAMPO_SUCURSAL_ID = ft.Dropdown(
            label="Sucursal",
            value=str(HORARIO.SUCURSAL_ID) if ES_EDICION else (str(sucursales[0].ID) if sucursales else ""),
            width=TAMANOS.ANCHO_INPUT,
            options=opciones_sucursales,
        )

        def GUARDAR(e):
            if not CAMPO_NOMBRE.value:
                self._MOSTRAR_ERROR(ERRORES_VALIDACION.CAMPO_REQUERIDO)
                return

            if not CAMPO_SUCURSAL_ID.value:
                self._MOSTRAR_ERROR("Debe seleccionar una sucursal")
                return

            try:
                sucursal_id = int(CAMPO_SUCURSAL_ID.value)
            except ValueError:
                self._MOSTRAR_ERROR("Sucursal inválida")
                return

            sesion = OBTENER_SESION()
            
            if ES_EDICION:
                horario = sesion.query(MODELO_HORARIO).filter_by(ID=HORARIO.ID).first()
                horario.NOMBRE = CAMPO_NOMBRE.value
                horario.DIA_SEMANA = CAMPO_DIA_SEMANA.value
                horario.HORA_APERTURA = CAMPO_HORA_APERTURA.value
                horario.HORA_CIERRE = CAMPO_HORA_CIERRE.value
                horario.SUCURSAL_ID = sucursal_id
            else:
                nuevo = MODELO_HORARIO(
                    NOMBRE=CAMPO_NOMBRE.value,
                    DIA_SEMANA=CAMPO_DIA_SEMANA.value,
                    HORA_APERTURA=CAMPO_HORA_APERTURA.value,
                    HORA_CIERRE=CAMPO_HORA_CIERRE.value,
                    SUCURSAL_ID=sucursal_id,
                )
                sesion.add(nuevo)

            sesion.commit()
            sesion.close()
            
            self._CERRAR_DIALOGO()
            self._CARGAR_DATOS()
            self._MOSTRAR_EXITO(MENSAJES_EXITO.GUARDADO_EXITOSO)

        DLG = ft.AlertDialog(
            title=ft.Text(
                "Editar Horario" if ES_EDICION else "Nuevo Horario",
                color=COLORES.TEXTO
            ),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        CAMPO_NOMBRE,
                        CAMPO_DIA_SEMANA,
                        CAMPO_HORA_APERTURA,
                        CAMPO_HORA_CIERRE,
                        CAMPO_SUCURSAL_ID,
                    ],
                    spacing=TAMANOS.ESPACIADO_MD,
                    tight=True,
                ),
                width=400,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self._CERRAR_DIALOGO()),
                ft.Button(
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

    def _ELIMINAR(self, HORARIO):
        def CONFIRMAR(e):
            sesion = OBTENER_SESION()
            horario = sesion.query(MODELO_HORARIO).filter_by(ID=HORARIO.ID).first()
            
            if horario:
                sesion.delete(horario)
                sesion.commit()
            
            sesion.close()
            self._CERRAR_DIALOGO()
            self._CARGAR_DATOS()
            self._MOSTRAR_EXITO(MENSAJES_EXITO.ELIMINADO_EXITOSO)

        DLG = ft.AlertDialog(
            title=ft.Text("Confirmar Eliminación", color=COLORES.PELIGRO),
            content=ft.Text(
                f"¿Estás seguro que deseas eliminar el horario '{HORARIO.NOMBRE}'?",
                color=COLORES.TEXTO
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self._CERRAR_DIALOGO()),
                ft.Button(
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
