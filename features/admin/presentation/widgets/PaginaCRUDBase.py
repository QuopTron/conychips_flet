"""
Página Base CRUD - Componente base para todas las páginas de gestión
Elimina completamente el código repetido
"""

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


class PaginaCRUDBase(ft.Column):
    """
    Clase base para todas las páginas CRUD de admin
    
    ELIMINA:
    - Código repetido de navegación
    - Lógica duplicada de CRUD
    - Diálogos repetidos
    - Manejo de estados duplicado
    
    USO:
    class MiPagina(PaginaCRUDBase):
        def _OBTENER_MODELO(self):
            return MODELO_PRODUCTO
        
        def _OBTENER_CAMPOS_TABLA(self):
            return ["NOMBRE", "PRECIO"]
        
        def _OBTENER_COLUMNAS_TABLA(self):
            return ["Nombre", "Precio"]
    """
    
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
        self._LISTA = ft.Column(spacing=TAMANOS.ESPACIADO_MD, scroll=ft.ScrollMode.AUTO)
        self._DATOS_CACHE = []
        
        self.expand = True
        self._CONSTRUIR_UI()
        self._CARGAR_DATOS_INICIAL()
    
    # ========================================================================
    # MÉTODOS ABSTRACTOS - Implementar en cada página
    # ========================================================================
    
    @abstractmethod
    def _OBTENER_MODELO(self):
        """Retorna el modelo de BD a usar"""
        pass
    
    @abstractmethod
    def _OBTENER_CAMPOS_TABLA(self) -> List[str]:
        """Retorna lista de campos a mostrar en tabla"""
        pass
    
    @abstractmethod
    def _OBTENER_COLUMNAS_TABLA(self) -> List[str]:
        """Retorna nombres de columnas para mostrar"""
        pass
    
    @abstractmethod
    def _CREAR_FORMULARIO(self, item: Any = None) -> List[ft.Control]:
        """Crea campos del formulario (nuevo o editar)"""
        pass
    
    @abstractmethod
    def _EXTRAER_DATOS_FORMULARIO(self, campos: List[ft.Control]) -> Dict:
        """Extrae datos del formulario para guardar"""
        pass
    
    # ========================================================================
    # MÉTODOS CON IMPLEMENTACIÓN POR DEFECTO (Override opcional)
    # ========================================================================
    
    def _FILTRAR_DATOS(self, datos: List[Any]) -> List[Any]:
        """Filtra datos si es necesario. Override para filtros personalizados"""
        return datos
    
    def _VALIDAR_DATOS(self, datos: Dict) -> tuple[bool, str]:
        """Valida datos antes de guardar. Override para validaciones personalizadas"""
        return True, ""
    
    def _DESPUES_GUARDAR(self, exito: bool, mensaje: str):
        """Callback después de guardar. Override para acciones adicionales"""
        if exito:
            Notificador.EXITO(self._PAGINA, mensaje)
        else:
            Notificador.ERROR(self._PAGINA, mensaje)
    
    def _OBTENER_TITULO_FORMULARIO(self, es_edicion: bool) -> str:
        """Retorna título del formulario"""
        return f"{'Editar' if es_edicion else 'Nuevo'} {self._TITULO}"
    
    # ========================================================================
    # IMPLEMENTACIÓN ESTÁNDAR (NO TOCAR - Funciona para todas las páginas)
    # ========================================================================
    
    def _CONSTRUIR_UI(self):
        """Construye la interfaz completa"""
        header = ft.Row(
            [
                ft.Icon(self._ICONO, size=TAMANOS.ICONO_LG, color=COLORES.PRIMARIO),
                ft.Text(
                    self._TITULO,
                    size=TAMANOS.TEXTO_3XL,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Container(expand=True),
                BotonesNavegacion.BOTON_NUEVO(
                    on_click=self._ABRIR_FORMULARIO_NUEVO,
                    texto=f"Nuevo"
                ),
                BotonesNavegacion.BOTON_MENU(on_click=self._IR_MENU),
                BotonesNavegacion.BOTON_SALIR(on_click=self._SALIR),
            ],
            spacing=TAMANOS.ESPACIADO_MD
        )
        
        self.controls = [
            ft.Container(
                content=ft.Column(
                    [header, self._LISTA],
                    spacing=TAMANOS.ESPACIADO_LG
                ),
                padding=TAMANOS.PADDING_XL,
                expand=True
            )
        ]
    
    def _CARGAR_DATOS_INICIAL(self):
        """Carga datos iniciales"""
        self._MOSTRAR_CARGANDO()
        datos = GestorCRUD.CARGAR_DATOS(self._OBTENER_MODELO())
        datos = self._FILTRAR_DATOS(datos)
        self._DATOS_CACHE = datos
        self._ACTUALIZAR_LISTA(datos)
    
    def _MOSTRAR_CARGANDO(self):
        """Muestra indicador de carga"""
        self._LISTA.controls = [CargadorPagina()]
        if hasattr(self._PAGINA, 'update'):
            self._PAGINA.update()
    
    def _ACTUALIZAR_LISTA(self, datos: List[Any]):
        """Actualiza la lista de items"""
        self._LISTA.controls.clear()
        
        if not datos:
            self._LISTA.controls.append(
                ft.Container(
                    content=ft.Text(
                        "No hay registros",
                        size=TAMANOS.TEXTO_LG,
                        color=COLORES.TEXTO_SECUNDARIO
                    ),
                    alignment=ft.alignment.center,
                    padding=TAMANOS.PADDING_XL
                )
            )
        else:
            # Usar TablaCRUD para mostrar datos
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
            self._PAGINA.update()
    
    def _ABRIR_FORMULARIO_NUEVO(self, e):
        """Abre formulario para crear nuevo item"""
        self._ABRIR_FORMULARIO(None)
    
    def _ABRIR_FORMULARIO_EDITAR(self, item: Any):
        """Abre formulario para editar item"""
        self._ABRIR_FORMULARIO(item)
    
    def _ABRIR_FORMULARIO(self, item: Any = None):
        """Abre formulario genérico (nuevo o editar)"""
        es_edicion = item is not None
        campos = self._CREAR_FORMULARIO(item)
        
        def guardar(e):
            datos = self._EXTRAER_DATOS_FORMULARIO(campos)
            
            # Validar
            valido, mensaje_error = self._VALIDAR_DATOS(datos)
            if not valido:
                Notificador.ERROR(self._PAGINA, mensaje_error)
                return
            
            # Guardar
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
        self._PAGINA.update()
    
    def _CONFIRMAR_ELIMINAR(self, item: Any):
        """Confirma eliminación de item"""
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
        """Cierra diálogo actual"""
        if self._PAGINA.dialog:
            self._PAGINA.dialog.open = False
            self._PAGINA.update()
    
    def _IR_MENU(self, e):
        """Navega al menú principal"""
        from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
        self._PAGINA.controls.clear()
        self._PAGINA.controls.append(PaginaAdmin(self._PAGINA, self._USUARIO))
        self._PAGINA.update()
    
    def _SALIR(self, e):
        """Cierra sesión"""
        from features.autenticacion.presentation.pages.PaginaLogin import PaginaLogin
        self._PAGINA.controls.clear()
        self._PAGINA.controls.append(PaginaLogin(self._PAGINA))
        self._PAGINA.update()
