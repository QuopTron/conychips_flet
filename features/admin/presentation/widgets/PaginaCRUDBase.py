
import flet as ft
from typing import Callable, List, Optional, Any, Dict
from abc import ABC, abstractmethod

from core.Constantes import COLORES, TAMANOS, ICONOS
from .ComponentesGlobales import (
    HeaderAdmin,
    Notificador,
    TablaCRUD,
    FormularioCRUD,
    BotonesNavegacion,
    GestorCRUD,
    DialogoConfirmacion,
    CargadorPagina
)
from core.decoradores.DecoradorPermisosUI import requiere_rol_ui
from core.Constantes import ROLES
from core.ui.safe_actions import safe_update

class PaginaCRUDBase(ft.Column):
    
    def __init__(
        self,
        PAGINA: ft.Page,
        USUARIO: Any,
        titulo: str,
        icono: str = ICONOS.ADMIN
    ):
        super().__init__()
        self._PAGINA = PAGINA
        self._USUARIO = USUARIO
        self._TITULO = titulo
        self._ICONO = icono
        self._LISTA = ft.Column(spacing=3, scroll=ft.ScrollMode.ADAPTIVE)
        self._DATOS_CACHE = []
        
        self.expand = True
        self._CONSTRUIR_UI()
        self._CARGAR_DATOS_INICIAL()
    
    
    @abstractmethod
    def _OBTENER_MODELO(self):
        pass
    
    @abstractmethod
    def _OBTENER_CAMPOS_TABLA(self) -> List[str]:
        pass
    
    @abstractmethod
    def _OBTENER_COLUMNAS_TABLA(self) -> List[str]:
        pass
    
    @abstractmethod
    def _CREAR_FORMULARIO(self, item: Any = None) -> List[ft.Control]:
        pass
    
    @abstractmethod
    def _EXTRAER_DATOS_FORMULARIO(self, campos: List[ft.Control]) -> Dict:
        pass
    
    
    def _FILTRAR_DATOS(self, datos: List[Any]) -> List[Any]:
        return datos
    
    def _VALIDAR_DATOS(self, datos: Dict) -> tuple[bool, str]:
        return True, ""
    
    def _DESPUES_GUARDAR(self, exito: bool, mensaje: str):
        if exito:
            Notificador.EXITO(self._PAGINA, mensaje)
        else:
            Notificador.ERROR(self._PAGINA, mensaje)
    
    def _OBTENER_TITULO_FORMULARIO(self, es_edicion: bool) -> str:
        return f"{'Editar' if es_edicion else 'Nuevo'} {self._TITULO}"
    
    
    def _CONSTRUIR_UI(self):
        header = ft.Container(
            content=ft.ResponsiveRow([
                ft.Container(
                    ft.Row([
                        ft.Icon(self._ICONO, size=24, color=COLORES.PRIMARIO),
                        ft.Text(
                            self._TITULO,
                            size=20,
                            weight=ft.FontWeight.BOLD
                        ),
                    ], spacing=10),
                    col={"xs": 12, "md": 6}
                ),
                ft.Container(
                    ft.Row([
                        BotonesNavegacion.BOTON_NUEVO(
                            on_click=self._ABRIR_FORMULARIO_NUEVO,
                            texto=f"Nuevo"
                        ),
                        BotonesNavegacion.BOTON_MENU(on_click=self._IR_MENU),
                        BotonesNavegacion.BOTON_SALIR(on_click=self._SALIR),
                    ], spacing=8, alignment=ft.MainAxisAlignment.END),
                    col={"xs": 12, "md": 6}
                ),
            ], spacing=6, run_spacing=6),
            bgcolor=ft.Colors.BLUE_50,
            border_radius=4,
            padding=8,
            border=ft.border.all(1, ft.Colors.BLUE_200)
        )
        
        self.controls = [
            ft.Container(
                content=ft.Column(
                    [header, self._LISTA],
                    spacing=4
                ),
                padding=0,
                expand=True
            )
        ]
    
    def _CARGAR_DATOS_INICIAL(self):
        self._MOSTRAR_CARGANDO()
        # Aplicar filtro por sucursal si el usuario tiene una selección
        try:
            suc_sel = getattr(self._USUARIO, 'SUCURSAL_SELECCIONADA', None)
        except Exception:
            suc_sel = None

        filtro = None
        if suc_sel is not None:
            filtro = {"SUCURSAL_ID": suc_sel}

        datos = GestorCRUD.CARGAR_DATOS(self._OBTENER_MODELO(), filtro=filtro)
        datos = self._FILTRAR_DATOS(datos)
        self._DATOS_CACHE = datos
        self._ACTUALIZAR_LISTA(datos)
    
    def _MOSTRAR_CARGANDO(self):
        self._LISTA.controls = [CargadorPagina()]
        if hasattr(self._PAGINA, 'update'):
            safe_update(self._PAGINA)
    
    def _ACTUALIZAR_LISTA(self, datos: List[Any]):
        self._LISTA.controls.clear()
        
        if not datos:
            self._LISTA.controls.append(
                ft.Container(
                    content=ft.Text(
                        "No hay registros",
                        size=TAMANOS.TEXTO_LG,
                        color=COLORES.TEXTO_SECUNDARIO
                    ),
                    alignment=ft.Alignment(0, 0),
                    padding=TAMANOS.PADDING_XL
                )
            )
        else:
            tabla = TablaCRUD(
                columnas=self._OBTENER_COLUMNAS_TABLA(),
                datos=datos,
                campos_mostrar=self._OBTENER_CAMPOS_TABLA(),
                on_editar=self._ABRIR_FORMULARIO_EDITAR,
                on_eliminar=self._CONFIRMAR_ELIMINAR
            )
            
            self._LISTA.controls.append(
                ft.Container(
                    content=ft.Row(
                        [tabla],
                        scroll=ft.ScrollMode.AUTO
                    ),
                    bgcolor=COLORES.FONDO_BLANCO,
                    border_radius=TAMANOS.RADIO_MD,
                    padding=TAMANOS.PADDING_MD
                )
            )
        
        if hasattr(self._PAGINA, 'update'):
            safe_update(self._PAGINA)
    
    @requiere_rol_ui(ROLES.SUPERADMIN, ROLES.ADMIN)
    def _ABRIR_FORMULARIO_NUEVO(self, e):
        self._ABRIR_FORMULARIO(None)
    
    @requiere_rol_ui(ROLES.SUPERADMIN, ROLES.ADMIN)
    def _ABRIR_FORMULARIO_EDITAR(self, item: Any):
        self._ABRIR_FORMULARIO(item)
    
    def _ABRIR_FORMULARIO(self, item: Any = None):
        es_edicion = item is not None
        campos = self._CREAR_FORMULARIO(item)
        
        def guardar(e):
            datos = self._EXTRAER_DATOS_FORMULARIO(campos)
            
            valido, mensaje_error = self._VALIDAR_DATOS(datos)
            if not valido:
                Notificador.ERROR(self._PAGINA, mensaje_error)
                return
            
            if es_edicion:
                exito, mensaje = GestorCRUD.ACTUALIZAR(
                    self._OBTENER_MODELO(),
                    item.ID,
                    datos
                )
            else:
                exito, mensaje = GestorCRUD.CREAR(
                    self._OBTENER_MODELO(),
                    datos
                )
            
            self._CERRAR_DIALOGO()
            self._DESPUES_GUARDAR(exito, mensaje)
            
            if exito:
                self._CARGAR_DATOS_INICIAL()
        
        dialogo = FormularioCRUD.CONSTRUIR_DIALOGO(
            titulo=self._OBTENER_TITULO_FORMULARIO(es_edicion),
            campos=campos,
            on_guardar=guardar,
            on_cancelar=lambda e: self._CERRAR_DIALOGO(),
            es_edicion=es_edicion
        )
        
        self._PAGINA.dialog = dialogo
        dialogo.open = True
        safe_update(self._PAGINA)
    
    @requiere_rol_ui(ROLES.SUPERADMIN, ROLES.ADMIN)
    def _CONFIRMAR_ELIMINAR(self, item: Any):
        def eliminar(e):
            exito, mensaje = GestorCRUD.ELIMINAR(
                self._OBTENER_MODELO(),
                item.ID
            )
            
            if exito:
                Notificador.EXITO(self._PAGINA, mensaje)
                self._CARGAR_DATOS_INICIAL()
            else:
                Notificador.ERROR(self._PAGINA, mensaje)
        
        DialogoConfirmacion.MOSTRAR(
            page=self._PAGINA,
            titulo="Confirmar Eliminación",
            mensaje=f"¿Estás seguro de eliminar este registro?\nEsta acción no se puede deshacer.",
            on_confirmar=eliminar,
            tipo="danger"
        )
    
    def _CERRAR_DIALOGO(self):
        if self._PAGINA.dialog:
            self._PAGINA.dialog.open = False
            safe_update(self._PAGINA)
    
    def _IR_MENU(self, e):
        from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
        self._PAGINA.controls.clear()
        self._PAGINA.controls.append(PaginaAdmin(self._PAGINA, self._USUARIO))
        safe_update(self._PAGINA)
    
    def _SALIR(self, e):
        from features.autenticacion.presentation.pages.PaginaLogin import PaginaLogin
        self._PAGINA.controls.clear()
        self._PAGINA.controls.append(PaginaLogin(self._PAGINA))
        safe_update(self._PAGINA)
