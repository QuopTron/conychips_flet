import flet as ft
from datetime import datetime

from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION,
    MODELO_PEDIDO,
    MODELO_SUCURSAL,
    MODELO_USUARIO,
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
class PaginaPedidos(ft.Column):

    def __init__(self, PAGINA: ft.Page, USUARIO: Usuario):
        super().__init__()
        self._PAGINA = PAGINA
        self._USUARIO = USUARIO
        self._LISTA = ft.Column(spacing=TAMANOS.ESPACIADO_MD)
        self._FILTRO_ESTADO = None
        self._FILTRO_SUCURSAL = None
        self._CONSTRUIR()

    def _CONSTRUIR(self):
        sesion = OBTENER_SESION()
        sucursales = sesion.query(MODELO_SUCURSAL).all()
        sesion.close()

        opciones_sucursales = [ft.dropdown.Option("", "Todas las sucursales")]
        opciones_sucursales.extend([
            ft.dropdown.Option(str(s.ID), s.NOMBRE) for s in sucursales
        ])

        self._DROPDOWN_ESTADO = ft.Dropdown(
            label="Filtrar por Estado",
            value="",
            width=200,
            options=[
                ft.dropdown.Option("", "Todos los estados"),
                ft.dropdown.Option("Pendiente", "Pendiente"),
                ft.dropdown.Option("En preparación", "En preparación"),
                ft.dropdown.Option("Listo", "Listo"),
                ft.dropdown.Option("Entregado", "Entregado"),
            ],
            on_select=self._APLICAR_FILTROS,
        )

        self._DROPDOWN_SUCURSAL = ft.Dropdown(
            label="Filtrar por Sucursal",
            value="",
            width=250,
            options=opciones_sucursales,
            on_select=self._APLICAR_FILTROS,
        )

        HEADER = ft.Row(
            controls=[
                ft.Icon(ICONOS.PEDIDOS,
                    size=TAMANOS.ICONO_LG,
                    color=COLORES.EXITO
                ),
                ft.Text(
                    "Gestión de Pedidos",
                    size=TAMANOS.TEXTO_3XL,
                    weight=ft.FontWeight.BOLD,
                    color=COLORES.TEXTO
                ),
                ft.Container(expand=True),
                self._DROPDOWN_ESTADO,
                self._DROPDOWN_SUCURSAL,
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

    def _APLICAR_FILTROS(self, e):
        self._FILTRO_ESTADO = self._DROPDOWN_ESTADO.value if self._DROPDOWN_ESTADO.value else None
        self._FILTRO_SUCURSAL = int(self._DROPDOWN_SUCURSAL.value) if self._DROPDOWN_SUCURSAL.value else None
        self._CARGAR_DATOS()

    def _CARGAR_DATOS(self):
        self._LISTA.controls.clear()
        
        sesion = OBTENER_SESION()
        query = sesion.query(MODELO_PEDIDO)
        
        if self._FILTRO_ESTADO:
            query = query.filter_by(ESTADO=self._FILTRO_ESTADO)
        
        if self._FILTRO_SUCURSAL:
            query = query.filter_by(SUCURSAL_ID=self._FILTRO_SUCURSAL)
        
        pedidos = query.all()
        sesion.close()

        if not pedidos:
            self._LISTA.controls.append(
                ft.Container(
                    content=ft.Text(
                        "No hay pedidos registrados",
                        size=TAMANOS.TEXTO_LG,
                        color=COLORES.TEXTO_SECUNDARIO,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    alignment=ft.Alignment(0, 0),
                    padding=TAMANOS.PADDING_2XL,
                )
            )
        else:
            for p in pedidos:
                self._LISTA.controls.append(self._CREAR_CARD(p))

        if hasattr(self, "update"):
            self.update()

    def _CREAR_CARD(self, PEDIDO):
        sesion = OBTENER_SESION()
        sucursal = sesion.query(MODELO_SUCURSAL).filter_by(ID=PEDIDO.SUCURSAL_ID).first()
        cliente = sesion.query(MODELO_USUARIO).filter_by(ID=PEDIDO.CLIENTE_ID).first()
        nombre_sucursal = sucursal.NOMBRE if sucursal else "N/A"
        nombre_cliente = cliente.NOMBRE if cliente else "N/A"
        sesion.close()

        color_estado = COLORES.ADVERTENCIA
        if PEDIDO.ESTADO == "Pendiente":
            color_estado = COLORES.ADVERTENCIA
        elif PEDIDO.ESTADO == "En preparación":
            color_estado = COLORES.INFO
        elif PEDIDO.ESTADO == "Listo":
            color_estado = COLORES.PRIMARIO
        elif PEDIDO.ESTADO == "Entregado":
            color_estado = COLORES.EXITO
        
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ICONOS.PEDIDOS,
                        size=TAMANOS.ICONO_XL,
                        color=COLORES.EXITO
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(
                                f"Pedido #{PEDIDO.ID}",
                                size=TAMANOS.TEXTO_LG,
                                weight=ft.FontWeight.BOLD,
                                color=COLORES.TEXTO
                            ),
                            ft.Text(
                                f"Cliente: {nombre_cliente} | Sucursal: {nombre_sucursal}",
                                size=TAMANOS.TEXTO_SM,
                                color=COLORES.TEXTO_SECUNDARIO
                            ),
                            ft.Row(
                                controls=[
                                    ft.Container(
                                        content=ft.Text(
                                            PEDIDO.ESTADO,
                                            size=TAMANOS.TEXTO_XS,
                                            color=COLORES.TEXTO_BLANCO,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        bgcolor=color_estado,
                                        padding=5,
                                        border_radius=TAMANOS.RADIO_SM,
                                    ),
                                    ft.Text(
                                        f"Total: ${PEDIDO.TOTAL:.2f}",
                                        size=TAMANOS.TEXTO_SM,
                                        color=COLORES.EXITO,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        f"Fecha: {PEDIDO.FECHA_PEDIDO if PEDIDO.FECHA_PEDIDO else 'N/A'}",
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
                                icon=ft.icons.Icons.Icons.VISIBILITY,
                                icon_color=COLORES.INFO,
                                tooltip="Ver detalles",
                                on_click=lambda e, p=PEDIDO: self._VER_DETALLES(p),
                            ),
                            ft.IconButton(
                                icon=ft.icons.Icons.Icons.ARROW_FORWARD,
                                icon_color=COLORES.PRIMARIO,
                                tooltip="Cambiar estado",
                                on_click=lambda e, p=PEDIDO: self._CAMBIAR_ESTADO(p),
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

    def _VER_DETALLES(self, PEDIDO):
        sesion = OBTENER_SESION()
        sucursal = sesion.query(MODELO_SUCURSAL).filter_by(ID=PEDIDO.SUCURSAL_ID).first()
        cliente = sesion.query(MODELO_USUARIO).filter_by(ID=PEDIDO.CLIENTE_ID).first()
        nombre_sucursal = sucursal.NOMBRE if sucursal else "N/A"
        nombre_cliente = cliente.NOMBRE if cliente else "N/A"
        sesion.close()

        DLG = ft.AlertDialog(
            title=ft.Text(
                f"Detalles del Pedido #{PEDIDO.ID}",
                color=COLORES.TEXTO
            ),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(f"Cliente: {nombre_cliente}", color=COLORES.TEXTO),
                        ft.Text(f"Sucursal: {nombre_sucursal}", color=COLORES.TEXTO),
                        ft.Text(f"Estado: {PEDIDO.ESTADO}", color=COLORES.TEXTO),
                        ft.Text(f"Total: ${PEDIDO.TOTAL:.2f}", color=COLORES.EXITO, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Fecha: {PEDIDO.FECHA_PEDIDO if PEDIDO.FECHA_PEDIDO else 'N/A'}", color=COLORES.TEXTO),
                        ft.Text(f"Notas: {PEDIDO.NOTAS if hasattr(PEDIDO, 'NOTAS') and PEDIDO.NOTAS else 'Sin notas'}", color=COLORES.TEXTO_SECUNDARIO),
                    ],
                    spacing=TAMANOS.ESPACIADO_MD,
                    tight=True,
                ),
                width=400,
            ),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda e: self._CERRAR_DIALOGO()),
            ],
        )

        self._PAGINA.dialog = DLG
        DLG.open = True
        self._PAGINA.update()

    def _CAMBIAR_ESTADO(self, PEDIDO):
        estados = {
            "Pendiente": "En preparación",
            "En preparación": "Listo",
            "Listo": "Entregado",
            "Entregado": "Entregado",
        }

        nuevo_estado = estados.get(PEDIDO.ESTADO, "Pendiente")

        if PEDIDO.ESTADO == "Entregado":
            self._MOSTRAR_ERROR("El pedido ya está entregado")
            return

        def CONFIRMAR(e):
            sesion = OBTENER_SESION()
            pedido = sesion.query(MODELO_PEDIDO).filter_by(ID=PEDIDO.ID).first()
            
            if pedido:
                pedido.ESTADO = nuevo_estado
                sesion.commit()
            
            sesion.close()
            self._CERRAR_DIALOGO()
            self._CARGAR_DATOS()
            self._MOSTRAR_EXITO(f"Estado actualizado a: {nuevo_estado}")

        DLG = ft.AlertDialog(
            title=ft.Text("Cambiar Estado", color=COLORES.PRIMARIO),
            content=ft.Text(
                f"¿Cambiar estado de '{PEDIDO.ESTADO}' a '{nuevo_estado}'?",
                color=COLORES.TEXTO
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self._CERRAR_DIALOGO()),
                ft.Button(
                    "Confirmar",
                    icon=ft.icons.Icons.Icons.CHECK,
                    on_click=CONFIRMAR,
                    bgcolor=COLORES.PRIMARIO,
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
