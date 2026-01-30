import flet as ft
from core.base_datos.ConfiguracionBD import MODELO_PRODUCTO
from core.Constantes import COLORES, TAMANOS, ICONOS, ROLES
from core.decoradores.DecoradorVistas import REQUIERE_ROL
from features.admin.presentation.bloc.ProductosBloc import (
    PRODUCTOS_BLOC,
    CargarProductos,
    GuardarProducto,
    EliminarProducto,
    ProductosCargando,
    ProductosCargados,
    ProductoError,
    ProductoGuardado
)
from features.admin.presentation.widgets.ComponentesGlobales import (
    Notificador,
    FormularioCRUD,
    BotonesNavegacion
)

@REQUIERE_ROL(ROLES.SUPERADMIN)
class PaginaProductosAdmin(ft.Column):
    def __init__(self, PAGINA: ft.Page, USUARIO):
        super().__init__()
        self._PAGINA = PAGINA
        self._USUARIO = USUARIO
        self._LISTA = ft.Column(spacing=10)
        
        PRODUCTOS_BLOC.AGREGAR_LISTENER(self._ON_ESTADO_CAMBIO)
        
        self._CONSTRUIR()
        
        PRODUCTOS_BLOC.AGREGAR_EVENTO(CargarProductos())
    
    def _ON_ESTADO_CAMBIO(self, estado):
        if isinstance(estado, ProductosCargados):
            self._ACTUALIZAR_LISTA(estado.productos)
        elif isinstance(estado, ProductoError):
            Notificador.ERROR(self, estado.mensaje)
        elif isinstance(estado, ProductoGuardado):
            self._CERRAR_DIALOGO()
            Notificador.EXITO(self, estado.mensaje)

    def _CONSTRUIR(self):
        header = ft.Row(
            controls=[
                ft.Icon(ft.icons.Icons.INVENTORY, size=TAMANOS.ICONO_LG, color=COLORES.PRIMARIO),
                ft.Text("Productos", size=TAMANOS.TEXTO_3XL, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                BotonesNavegacion.BOTON_MENU(self._IR_MENU),
                BotonesNavegacion.BOTON_SALIR(self._SALIR),
                BotonesNavegacion.BOTON_NUEVO(self._NUEVO, "Producto"),
            ],
            spacing=TAMANOS.ESPACIADO_MD,
        )

        self.controls = [
            ft.Container(
                content=ft.Column(
                    controls=[header, self._LISTA],
                    spacing=TAMANOS.ESPACIADO_LG,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=TAMANOS.PADDING_XL,
                expand=True,
                bgcolor=COLORES.FONDO
            )
        ]
        self.expand = True

    def _ACTUALIZAR_LISTA(self, productos):
        self._LISTA.controls.clear()

        for p in productos:
            self._LISTA.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(p.NOMBRE, weight=ft.FontWeight.W_500),
                            ft.Text(p.DESCRIPCION or "", size=TAMANOS.TEXTO_SM, color=COLORES.GRIS),
                            ft.Text(f"{p.PRECIO} Bs", color=COLORES.EXITO, weight=ft.FontWeight.BOLD),
                            ft.Container(expand=True),
                            ft.IconButton(
                                icon=ft.icons.Icons.Icons.EDIT,
                                tooltip="Editar",
                                icon_color=COLORES.INFO,
                                on_click=lambda e, x=p: self._EDITAR(x)
                            ),
                            ft.IconButton(
                                icon=ft.icons.Icons.Icons.DELETE,
                                tooltip="Eliminar",
                                icon_color=COLORES.PELIGRO,
                                on_click=lambda e, x=p: self._ELIMINAR(x)
                            ),
                        ],
                    ),
                    padding=TAMANOS.PADDING_MD,
                    bgcolor=COLORES.FONDO_BLANCO,
                    border_radius=TAMANOS.RADIO_SM,
                    border=ft.Border.all(1, COLORES.BORDE),
                )
            )

        if getattr(self, "_PAGINA", None):
            self._PAGINA.update()

    def _NUEVO(self, e):
        self._ABRIR_FORM()

    def _EDITAR(self, PROD):
        self._ABRIR_FORM(PROD)

    def _ELIMINAR(self, PROD):
        PRODUCTOS_BLOC.AGREGAR_EVENTO(EliminarProducto(producto_id=PROD.ID))

    def _ABRIR_FORM(self, PROD=None):
        campo_nombre = FormularioCRUD.CREAR_CAMPO(
            "Nombre",
            PROD.NOMBRE if PROD else "",
            icono=ft.icons.Icons.INVENTORY
        )
        campo_desc = FormularioCRUD.CREAR_CAMPO(
            "Descripción",
            PROD.DESCRIPCION if PROD else "",
            multiline=True,
            max_lines=3
        )
        campo_precio = FormularioCRUD.CREAR_CAMPO(
            "Precio",
            str(PROD.PRECIO) if PROD else "0",
            tipo="number",
            icono=ft.icons.Icons.ATTACH_MONEY
        )
        campo_img = FormularioCRUD.CREAR_CAMPO(
            "Imagen URL",
            PROD.IMAGEN if PROD else "",
            icono=ft.icons.Icons.IMAGE
        )

        def GUARDAR(e):
            if not campo_nombre.value:
                Notificador.ADVERTENCIA(self, "El nombre es obligatorio")
                return
            
            datos = {
                "NOMBRE": campo_nombre.value.strip(),
                "DESCRIPCION": campo_desc.value.strip(),
                "PRECIO": float(campo_precio.value or 0),
                "IMAGEN": campo_img.value.strip()
            }
            
            if PROD:
                datos["ID"] = PROD.ID
            
            PRODUCTOS_BLOC.AGREGAR_EVENTO(GuardarProducto(datos=datos))

        dlg = FormularioCRUD.CONSTRUIR_DIALOGO(
            titulo="✏️ Editar Producto" if PROD else "➕ Nuevo Producto",
            campos=[campo_nombre, campo_desc, campo_precio, campo_img],
            on_guardar=GUARDAR,
            on_cancelar=lambda e: self._CERRAR_DIALOGO(),
            es_edicion=PROD is not None
        )

        self._PAGINA.dialog = dlg
        dlg.open = True
        self._PAGINA.update()

    def _CERRAR_DIALOGO(self):
        if self._PAGINA.dialog:
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
    
    def __del__(self):
        try:
            PRODUCTOS_BLOC.REMOVER_LISTENER(self._ON_ESTADO_CAMBIO)
        except:
            pass
