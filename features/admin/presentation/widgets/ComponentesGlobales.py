"""
Componentes Globales Compartidos - Admin
Widgets reutilizables para todas las páginas de administración
REFACTORIZADO: Componentes DRY para eliminar código duplicado
"""

import flet as ft
from typing import Callable, List, Optional, Any
from core.Constantes import COLORES, TAMANOS, ICONOS
from core.base_datos.ConfiguracionBD import OBTENER_SESION


class HeaderAdmin(ft.Row):
    """
    Header estándar para páginas de admin
    Reutilizable con título y botones personalizables
    """
    
    def __init__(
        self,
        titulo: str,
        icono: str = ICONOS.ADMIN,
        mostrar_volver: bool = True,
        on_volver: Optional[Callable] = None,
        mostrar_salir: bool = True,
        on_salir: Optional[Callable] = None,
        botones_adicionales: List[ft.Control] = None,
    ):
        super().__init__()
        
        self.spacing = TAMANOS.ESPACIADO_MD
        
        controles = [
            ft.Icon(icono, size=TAMANOS.ICONO_LG, color=COLORES.PRIMARIO),
            ft.Text(
                titulo,
                size=TAMANOS.TEXTO_3XL,
                weight=ft.FontWeight.BOLD,
                color=COLORES.TEXTO
            ),
            ft.Container(expand=True),
        ]
        
        # Botones adicionales personalizados
        if botones_adicionales:
            controles.extend(botones_adicionales)
        
        # Botón volver
        if mostrar_volver and on_volver:
            controles.append(
                ft.ElevatedButton(
                    "Volver",
                    icon=ft.Icons.ARROW_BACK,
                    on_click=on_volver,
                    bgcolor=COLORES.SECUNDARIO,
                    color=COLORES.TEXTO_BLANCO
                )
            )
        
        # Botón salir
        if mostrar_salir and on_salir:
            controles.append(
                ft.ElevatedButton(
                    "Salir",
                    icon=ICONOS.CERRAR_SESION,
                    on_click=on_salir,
                    bgcolor=COLORES.PELIGRO,
                    color=COLORES.TEXTO_BLANCO
                )
            )
        
        self.controls = controles


class BarraBusqueda(ft.Row):
    """
    Barra de búsqueda estándar con filtros
    """
    
    def __init__(
        self,
        placeholder: str = "Buscar...",
        on_search: Optional[Callable] = None,
        mostrar_filtros: bool = False,
        filtros: List[ft.Control] = None,
    ):
        super().__init__()
        
        self.spacing = TAMANOS.ESPACIADO_MD
        self.wrap = True
        
        self.campo_busqueda = ft.TextField(
            hint_text=placeholder,
            prefix_icon=ft.Icons.SEARCH,
            border_radius=TAMANOS.RADIO_MD,
            on_change=on_search if on_search else None,
            expand=True,
        )
        
        controles = [self.campo_busqueda]
        
        if mostrar_filtros and filtros:
            controles.extend(filtros)
        
        self.controls = controles
    
    def OBTENER_TEXTO(self) -> str:
        """Obtiene el texto de búsqueda"""
        return self.campo_busqueda.value or ""


class TablaGenerica(ft.Container):
    """
    Tabla genérica con paginación y acciones
    """
    
    def __init__(
        self,
        columnas: List[ft.DataColumn],
        filas_iniciales: List[ft.DataRow] = None,
        altura: int = 500,
    ):
        super().__init__()
        
        self.tabla = ft.DataTable(
            columns=columnas,
            rows=filas_iniciales or [],
            border=ft.border.all(1, COLORES.BORDE),
            border_radius=TAMANOS.RADIO_MD,
            vertical_lines=ft.BorderSide(1, COLORES.BORDE),
            horizontal_lines=ft.BorderSide(1, COLORES.BORDE),
            heading_row_color=COLORES.FONDO,
            heading_row_height=60,
            data_row_min_height=50,
            data_row_max_height=80,
        )
        
        self.content = ft.Column(
            [
                ft.Container(
                    content=ft.Row(
                        [self.tabla],
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    height=altura,
                )
            ],
            spacing=TAMANOS.ESPACIADO_SM,
        )
        
        self.padding = TAMANOS.PADDING_MD
        self.bgcolor = COLORES.FONDO_BLANCO
        self.border_radius = TAMANOS.RADIO_MD
        self.border = ft.border.all(1, COLORES.BORDE)
    
    def ACTUALIZAR_FILAS(self, nuevas_filas: List[ft.DataRow]):
        """Actualiza las filas de la tabla"""
        self.tabla.rows = nuevas_filas
        if hasattr(self, 'update'):
            self.update()


class BotonAccion(ft.ElevatedButton):
    """
    Botón de acción estándar
    """
    
    def __init__(
        self,
        texto: str,
        icono: str,
        on_click: Callable,
        color: str = COLORES.PRIMARIO,
        tipo: str = "normal"  # normal, success, danger, warning
    ):
        # Determinar color según tipo
        colores_tipo = {
            "normal": COLORES.PRIMARIO,
            "success": COLORES.EXITO,
            "danger": COLORES.PELIGRO,
            "warning": COLORES.ADVERTENCIA,
            "info": COLORES.INFO,
        }
        
        bgcolor = colores_tipo.get(tipo, color)
        
        super().__init__(
            text=texto,
            icon=icono,
            on_click=on_click,
            bgcolor=bgcolor,
            color=COLORES.TEXTO_BLANCO,
        )


class DialogoConfirmacion:
    """
    Diálogo de confirmación reutilizable
    """
    
    @staticmethod
    def MOSTRAR(
        page: ft.Page,
        titulo: str,
        mensaje: str,
        on_confirmar: Callable,
        tipo: str = "warning"  # info, warning, danger
    ):
        iconos_tipo = {
            "info": ft.Icons.INFO_OUTLINED,
            "warning": ft.Icons.WARNING_AMBER_OUTLINED,
            "danger": ft.Icons.ERROR_OUTLINE,
        }
        
        colores_tipo = {
            "info": COLORES.INFO,
            "warning": COLORES.ADVERTENCIA,
            "danger": COLORES.PELIGRO,
        }
        
        def cerrar_dialogo(e):
            page.dialog.open = False
            page.update()
        
        def confirmar(e):
            page.dialog.open = False
            page.update()
            on_confirmar(e)
        
        dlg = ft.AlertDialog(
            title=ft.Row(
                [
                    ft.Icon(iconos_tipo.get(tipo, ft.Icons.INFO_OUTLINED), color=colores_tipo.get(tipo, COLORES.INFO)),
                    ft.Text(titulo, color=COLORES.TEXTO),
                ],
                spacing=TAMANOS.ESPACIADO_SM,
            ),
            content=ft.Text(mensaje, color=COLORES.TEXTO),
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar_dialogo),
                ft.ElevatedButton(
                    "Confirmar",
                    on_click=confirmar,
                    bgcolor=colores_tipo.get(tipo, COLORES.INFO),
                    color=COLORES.TEXTO_BLANCO
                ),
            ],
        )
        
        page.dialog = dlg
        dlg.open = True
        page.update()


class FormularioGenerico(ft.Container):
    """
    Formulario genérico con campos dinámicos
    """
    
    def __init__(
        self,
        campos: List[ft.Control],
        on_guardar: Callable,
        on_cancelar: Optional[Callable] = None,
        titulo: str = "Formulario",
    ):
        super().__init__()
        
        botones = [
            ft.ElevatedButton(
                "Guardar",
                icon=ft.Icons.SAVE,
                on_click=on_guardar,
                bgcolor=COLORES.EXITO,
                color=COLORES.TEXTO_BLANCO
            ),
        ]
        
        if on_cancelar:
            botones.insert(0, ft.TextButton("Cancelar", on_click=on_cancelar))
        
        self.content = ft.Column(
            [
                ft.Text(
                    titulo,
                    size=TAMANOS.TEXTO_XL,
                    weight=ft.FontWeight.BOLD,
                    color=COLORES.TEXTO
                ),
                ft.Divider(height=1, color=COLORES.BORDE),
                *campos,
                ft.Divider(height=1, color=COLORES.BORDE),
                ft.Row(
                    botones,
                    alignment=ft.MainAxisAlignment.END,
                    spacing=TAMANOS.ESPACIADO_MD,
                ),
            ],
            spacing=TAMANOS.ESPACIADO_MD,
        )
        
        self.padding = TAMANOS.PADDING_LG
        self.bgcolor = COLORES.FONDO_BLANCO
        self.border_radius = TAMANOS.RADIO_MD
        self.border = ft.border.all(1, COLORES.BORDE)


class Notificador:
    """
    Sistema de notificaciones unificado
    """
    
    @staticmethod
    def EXITO(page: ft.Page, mensaje: str):
        snackbar = ft.SnackBar(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=COLORES.TEXTO_BLANCO),
                    ft.Text(mensaje, color=COLORES.TEXTO_BLANCO),
                ],
                spacing=TAMANOS.ESPACIADO_SM,
            ),
            bgcolor=COLORES.EXITO,
        )
        page.overlay.append(snackbar)
        snackbar.open = True
        page.update()
    
    @staticmethod
    def ERROR(page: ft.Page, mensaje: str):
        snackbar = ft.SnackBar(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.ERROR, color=COLORES.TEXTO_BLANCO),
                    ft.Text(mensaje, color=COLORES.TEXTO_BLANCO),
                ],
                spacing=TAMANOS.ESPACIADO_SM,
            ),
            bgcolor=COLORES.PELIGRO,
        )
        page.overlay.append(snackbar)
        snackbar.open = True
        page.update()
    
    @staticmethod
    def INFO(page: ft.Page, mensaje: str):
        snackbar = ft.SnackBar(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.INFO, color=COLORES.TEXTO_BLANCO),
                    ft.Text(mensaje, color=COLORES.TEXTO_BLANCO),
                ],
                spacing=TAMANOS.ESPACIADO_SM,
            ),
            bgcolor=COLORES.INFO,
        )
        page.overlay.append(snackbar)
        snackbar.open = True
        page.update()
    
    @staticmethod
    def ADVERTENCIA(page: ft.Page, mensaje: str):
        snackbar = ft.SnackBar(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.WARNING, color=COLORES.TEXTO_BLANCO),
                    ft.Text(mensaje, color=COLORES.TEXTO_BLANCO),
                ],
                spacing=TAMANOS.ESPACIADO_SM,
            ),
            bgcolor=COLORES.ADVERTENCIA,
        )
        page.overlay.append(snackbar)
        snackbar.open = True
        page.update()


class CargadorPagina(ft.Container):
    """
    Indicador de carga para páginas
    """
    
    def __init__(self, mensaje: str = "Cargando..."):
        super().__init__()
        
        self.content = ft.Column(
            [
                ft.ProgressRing(),
                ft.Text(mensaje, size=TAMANOS.TEXTO_MD, color=COLORES.TEXTO_SECUNDARIO),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=TAMANOS.ESPACIADO_MD,
        )
        
        self.alignment = ft.alignment.center
        self.expand = True
        self.padding = TAMANOS.PADDING_XL


class ContenedorPagina(ft.Container):
    """
    Contenedor estándar para páginas de admin
    """
    
    def __init__(self, contenido: ft.Control):
        super().__init__()
        
        self.content = contenido
        self.padding = TAMANOS.PADDING_XL
        self.expand = True
        self.bgcolor = COLORES.FONDO


# ============================================================================
# COMPONENTES CRUD - Elimina código duplicado en todas las páginas
# ============================================================================

class GestorCRUD:
    """
    Gestor genérico de operaciones CRUD
    Elimina código repetido en todas las páginas admin
    """
    
    @staticmethod
    def CARGAR_DATOS(modelo, filtro: Optional[dict] = None):
        """Carga datos de cualquier modelo con filtros opcionales"""
        try:
            sesion = OBTENER_SESION()
            query = sesion.query(modelo)
            
            if filtro:
                query = query.filter_by(**filtro)
            
            datos = query.all()
            sesion.close()
            return datos
        except Exception as e:
            print(f"Error cargando datos: {e}")
            return []
    
    @staticmethod
    def CREAR(modelo, datos: dict):
        """Crea nuevo registro en cualquier modelo"""
        try:
            sesion = OBTENER_SESION()
            nuevo = modelo(**datos)
            sesion.add(nuevo)
            sesion.commit()
            sesion.close()
            return True, "Creado exitosamente"
        except Exception as e:
            return False, f"Error al crear: {str(e)}"
    
    @staticmethod
    def ACTUALIZAR(modelo, id_registro: int, datos: dict):
        """Actualiza registro existente"""
        try:
            sesion = OBTENER_SESION()
            registro = sesion.query(modelo).filter_by(ID=id_registro).first()
            
            if not registro:
                sesion.close()
                return False, "Registro no encontrado"
            
            for clave, valor in datos.items():
                if hasattr(registro, clave):
                    setattr(registro, clave, valor)
            
            sesion.commit()
            sesion.close()
            return True, "Actualizado exitosamente"
        except Exception as e:
            return False, f"Error al actualizar: {str(e)}"
    
    @staticmethod
    def ELIMINAR(modelo, id_registro: int):
        """Elimina registro"""
        try:
            sesion = OBTENER_SESION()
            registro = sesion.query(modelo).filter_by(ID=id_registro).first()
            
            if registro:
                sesion.delete(registro)
                sesion.commit()
            
            sesion.close()
            return True, "Eliminado exitosamente"
        except Exception as e:
            return False, f"Error al eliminar: {str(e)}"


class FormularioCRUD:
    """
    Constructor de formularios CRUD genéricos
    Elimina código repetido en popups de crear/editar
    """
    
    @staticmethod
    def CREAR_CAMPO(
        label: str,
        valor: str = "",
        tipo: str = "text",
        icono: str = None,
        multiline: bool = False,
        max_lines: int = 1
    ) -> ft.TextField:
        """Crea campo de formulario estandarizado"""
        return ft.TextField(
            label=label,
            value=valor,
            prefix_icon=icono,
            password=tipo == "password",
            can_reveal_password=tipo == "password",
            multiline=multiline,
            max_lines=max_lines,
            keyboard_type=ft.KeyboardType.NUMBER if tipo == "number" else ft.KeyboardType.TEXT
        )
    
    @staticmethod
    def CREAR_DROPDOWN(
        label: str,
        opciones: List[tuple],  # [(texto, valor), ...]
        valor_actual: Any = None,
        icono: str = None
    ) -> ft.Dropdown:
        """Crea dropdown estandarizado"""
        return ft.Dropdown(
            label=label,
            value=valor_actual,
            options=[ft.dropdown.Option(text=txt, key=str(val)) for txt, val in opciones],
            prefix_icon=icono
        )
    
    @staticmethod
    def CREAR_SWITCH(
        label: str,
        valor: bool = True
    ) -> ft.Switch:
        """Crea switch estandarizado"""
        return ft.Switch(
            label=label,
            value=valor
        )
    
    @staticmethod
    def CONSTRUIR_DIALOGO(
        titulo: str,
        campos: List[ft.Control],
        on_guardar: Callable,
        on_cancelar: Callable,
        es_edicion: bool = False
    ) -> ft.AlertDialog:
        """Construye diálogo CRUD completo"""
        return ft.AlertDialog(
            title=ft.Text(titulo, color=COLORES.TEXTO),
            content=ft.Container(
                content=ft.Column(
                    campos,
                    tight=True,
                    spacing=TAMANOS.ESPACIADO_MD,
                    scroll=ft.ScrollMode.AUTO
                ),
                width=400,
                height=min(len(campos) * 80, 500)
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=on_cancelar),
                ft.ElevatedButton(
                    "Actualizar" if es_edicion else "Guardar",
                    icon=ft.Icons.SAVE,
                    on_click=on_guardar,
                    bgcolor=COLORES.INFO if es_edicion else COLORES.PRIMARIO,
                    color=COLORES.TEXTO_BLANCO
                )
            ]
        )


class TablaCRUD(ft.DataTable):
    """
    Tabla CRUD genérica con acciones estándar
    Elimina código repetido de tablas
    """
    
    def __init__(
        self,
        columnas: List[str],
        datos: List[Any],
        campos_mostrar: List[str],
        on_editar: Optional[Callable] = None,
        on_eliminar: Optional[Callable] = None,
        mostrar_id: bool = True
    ):
        # Construir columnas
        cols = []
        if mostrar_id:
            cols.append(ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)))
        
        for col in columnas:
            cols.append(ft.DataColumn(ft.Text(col, weight=ft.FontWeight.BOLD)))
        
        cols.append(ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD)))
        
        # Construir filas
        rows = []
        for item in datos:
            cells = []
            
            if mostrar_id:
                cells.append(ft.DataCell(ft.Text(str(item.ID))))
            
            for campo in campos_mostrar:
                valor = getattr(item, campo, "-")
                cells.append(ft.DataCell(ft.Text(str(valor) if valor else "-")))
            
            # Acciones
            acciones = ft.Row([])
            if on_editar:
                acciones.controls.append(
                    ft.IconButton(
                        icon=ft.Icons.EDIT,
                        tooltip="Editar",
                        icon_color=COLORES.INFO,
                        on_click=lambda e, i=item: on_editar(i)
                    )
                )
            if on_eliminar:
                acciones.controls.append(
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        tooltip="Eliminar",
                        icon_color=COLORES.PELIGRO,
                        on_click=lambda e, i=item: on_eliminar(i)
                    )
                )
            
            cells.append(ft.DataCell(acciones))
            rows.append(ft.DataRow(cells=cells))
        
        super().__init__(
            columns=cols,
            rows=rows,
            border=ft.border.all(1, COLORES.BORDE),
            border_radius=TAMANOS.RADIO_MD,
            vertical_lines=ft.BorderSide(1, COLORES.BORDE),
            heading_row_color=COLORES.PRIMARIO_CLARO
        )


class BotonesNavegacion:
    """
    Botones de navegación estandarizados
    Elimina código repetido de navegación
    """
    
    @staticmethod
    def BOTON_VOLVER(on_click: Callable) -> ft.ElevatedButton:
        """Botón volver estándar"""
        return ft.ElevatedButton(
            "← Volver",
            icon=ft.Icons.ARROW_BACK,
            on_click=on_click,
            bgcolor=COLORES.SECUNDARIO,
            color=COLORES.TEXTO_BLANCO
        )
    
    @staticmethod
    def BOTON_MENU(on_click: Callable) -> ft.ElevatedButton:
        """Botón menú estándar"""
        return ft.ElevatedButton(
            "Menú",
            icon=ICONOS.DASHBOARD,
            on_click=on_click,
            bgcolor=COLORES.PRIMARIO,
            color=COLORES.TEXTO_BLANCO
        )
    
    @staticmethod
    def BOTON_SALIR(on_click: Callable) -> ft.ElevatedButton:
        """Botón salir estándar"""
        return ft.ElevatedButton(
            "Salir",
            icon=ICONOS.CERRAR_SESION,
            on_click=on_click,
            bgcolor=COLORES.PELIGRO,
            color=COLORES.TEXTO_BLANCO
        )
    
    @staticmethod
    def BOTON_NUEVO(on_click: Callable, texto: str = "Nuevo") -> ft.ElevatedButton:
        """Botón nuevo estándar"""
        return ft.ElevatedButton(
            f"➕ {texto}",
            icon=ICONOS.AGREGAR,
            on_click=on_click,
            bgcolor=COLORES.EXITO,
            color=COLORES.TEXTO_BLANCO
        )

        self.bgcolor = COLORES.FONDO
