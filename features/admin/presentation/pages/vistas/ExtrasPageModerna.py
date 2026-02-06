"""
ExtrasPageModerna - CRUD completo de extras con diseño moderno
Similar a ProductosPageModerna con todas las funcionalidades
"""
import flet as ft
from typing import Optional, List, Dict, Any
from datetime import datetime

from core.Constantes import COLORES, TAMANOS, ICONOS, ROLES
from core.decoradores.DecoradorVistas import REQUIERE_ROL
from core.ui.safe_actions import safe_update
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_EXTRA, MODELO_PRODUCTO

from features.admin.presentation.widgets import LayoutBase


@REQUIERE_ROL(ROLES.ADMIN)
class ExtrasPageModerna(LayoutBase):
    """Página moderna de gestión de extras con CRUD completo"""
    
    def __init__(self, pagina: ft.Page, usuario):
        self._extras_cache: List[Dict] = []
        self._filtro_busqueda: str = ""
        self._filtro_estado: str = "TODOS"  # TODOS, ACTIVOS, INACTIVOS
        
        # Componentes UI
        self._campo_busqueda: Optional[ft.TextField] = None
        self._contenedor_extras: Optional[ft.Column] = None
        self._contenedor_principal: Optional[ft.Container] = None
        
        # Overlays
        self._overlay_crear: Optional[ft.AlertDialog] = None
        self._overlay_editar: Optional[ft.AlertDialog] = None
        self._overlay_detalle: Optional[ft.AlertDialog] = None
        self._overlay_productos: Optional[ft.AlertDialog] = None
        
        # Inicializar LayoutBase
        super().__init__(
            pagina=pagina,
            usuario=usuario,
            titulo_vista="➕ Gestión de Extras",
            mostrar_boton_volver=True,
            index_navegacion=0,
            on_volver_dashboard=self._volver_dashboard,
            on_cerrar_sesion=self._cerrar_sesion
        )
        
        # Construir interfaz
        contenido = self._construir_contenido()
        self.construir(contenido)
        
        # Cargar datos iniciales
        self._cargar_extras()
    
    def _construir_contenido(self) -> ft.Container:
        """Construye el contenido principal de la página"""
        # Header con búsqueda y botón crear
        self._campo_busqueda = ft.TextField(
            hint_text="Buscar extras por nombre...",
            prefix_icon=ft.icons.Icons.SEARCH,
            expand=True,
            on_change=self._on_buscar,
            border_radius=8,
            filled=True,
            bgcolor=ft.Colors.WHITE,
        )
        
        btn_crear = ft.FilledButton(
            content=ft.Row([
                ft.Icon(ft.icons.Icons.ADD, size=20),
                ft.Text("Crear Extra", size=14, weight=ft.FontWeight.BOLD),
            ], spacing=8, tight=True),
            on_click=self._mostrar_crear,
            style=ft.ButtonStyle(
                bgcolor=COLORES.EXITO,
                color=ft.Colors.WHITE,
                padding=ft.Padding(16, 12, 16, 12),
            ),
        )
        
        btn_refresh = ft.IconButton(
            icon=ft.icons.Icons.REFRESH,
            on_click=lambda _: self._cargar_extras(),
            tooltip="Actualizar",
            icon_color=COLORES.PRIMARIO,
        )
        
        header = ft.Container(
            content=ft.Row([
                self._campo_busqueda,
                btn_refresh,
                btn_crear,
            ], spacing=12),
            padding=ft.Padding(0, 0, 0, 20),
        )
        
        # Filtros de estado
        filtros = self._crear_filtros()
        
        # DataTable de extras
        self._tabla_extras = ft.DataTable(
            columns=[
                ft.DataColumn(label=ft.Text("Nombre", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Descripción", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Precio", weight=ft.FontWeight.BOLD), numeric=True),
                ft.DataColumn(label=ft.Text("Estado", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, COLORES.BORDE),
            border_radius=10,
            heading_row_color=ft.Colors.BLUE_50,
            heading_row_height=55,
            data_row_min_height=55,
            data_row_max_height=float("inf"),
            column_spacing=25,
            horizontal_margin=15,
            divider_thickness=1,
            horizontal_lines=ft.border.BorderSide(1, ft.Colors.GREY_200),
        )
        
        # Contenedor scrollable
        self._contenedor_extras = ft.Container(
            content=ft.Column([self._tabla_extras], scroll=ft.ScrollMode.AUTO, expand=True),
            expand=True,
            padding=10
        )
        
        # Contenedor principal
        self._contenedor_principal = ft.Container(
            content=ft.Column([
                header,
                filtros,
                ft.Divider(height=1, color=COLORES.BORDE),
                self._contenedor_extras,
            ], spacing=16, scroll=ft.ScrollMode.AUTO),
            padding=ft.Padding(20, 20, 20, 20),
            expand=True,
        )
        
        return self._contenedor_principal
    
    def _crear_filtros(self) -> ft.Row:
        """Crea los chips de filtro por estado"""
        def crear_chip(estado: str, label: str, icono, color):
            return ft.Container(
                content=ft.Row([
                    ft.Icon(icono, size=18, color=ft.Colors.WHITE if self._filtro_estado == estado else color),
                    ft.Text(
                        label,
                        size=14,
                        weight=ft.FontWeight.BOLD if self._filtro_estado == estado else ft.FontWeight.NORMAL,
                        color=ft.Colors.WHITE if self._filtro_estado == estado else color,
                    ),
                ], spacing=8, tight=True),
                padding=ft.Padding(12, 8, 12, 8),
                border_radius=20,
                bgcolor=color if self._filtro_estado == estado else ft.Colors.with_opacity(0.1, color),
                on_click=lambda _, e=estado: self._cambiar_filtro(e),
                ink=True,
            )
        
        return ft.Row([
            ft.Text("Filtros:", size=14, weight=ft.FontWeight.BOLD, color=COLORES.TEXTO),
            crear_chip("TODOS", "Todos", ft.icons.Icons.SELECT_ALL, ft.Colors.BLUE),
            crear_chip("ACTIVOS", "Activos", ft.icons.Icons.CHECK_CIRCLE, ft.Colors.GREEN),
            crear_chip("INACTIVOS", "Inactivos", ft.icons.Icons.CANCEL, ft.Colors.RED),
        ], spacing=12, wrap=True)
    
    def _cambiar_filtro(self, nuevo_filtro: str):
        """Cambia el filtro de estado actual"""
        self._filtro_estado = nuevo_filtro
        self._aplicar_filtros()
        self.construir()  # Reconstruir para actualizar los chips seleccionados
    
    def _on_buscar(self, e):
        """Handler del campo de búsqueda"""
        self._filtro_busqueda = e.control.value.lower()
        self._aplicar_filtros()
    
    def _aplicar_filtros(self):
        """Aplica los filtros de búsqueda y estado"""
        extras_filtrados = self._extras_cache.copy()
        
        # Filtro de búsqueda
        if self._filtro_busqueda:
            extras_filtrados = [
                e for e in extras_filtrados
                if self._filtro_busqueda in e["NOMBRE"].lower() or
                   (e["DESCRIPCION"] and self._filtro_busqueda in e["DESCRIPCION"].lower())
            ]
        
        # Filtro de estado
        if self._filtro_estado == "ACTIVOS":
            extras_filtrados = [e for e in extras_filtrados if e["ACTIVO"]]
        elif self._filtro_estado == "INACTIVOS":
            extras_filtrados = [e for e in extras_filtrados if not e["ACTIVO"]]
        
        self._actualizar_lista_extras(extras_filtrados)
    
    def _cargar_extras(self):
        """Carga todos los extras desde la base de datos"""
        with OBTENER_SESION() as sesion:
            try:
                extras_db = sesion.query(MODELO_EXTRA).order_by(MODELO_EXTRA.FECHA_CREACION.desc()).all()
                self._extras_cache = [{
                    "ID": e.ID,
                    "NOMBRE": e.NOMBRE,
                    "DESCRIPCION": e.DESCRIPCION,
                    "PRECIO_ADICIONAL": e.PRECIO_ADICIONAL,
                    "ACTIVO": e.ACTIVO,
                    "FECHA_CREACION": e.FECHA_CREACION,
                } for e in extras_db]
                
                self._aplicar_filtros()
                
            except Exception as ex:
                print(f"[ERROR] Cargando extras: {ex}")
                self._mostrar_error("Error al cargar extras")
    
    def _actualizar_lista_extras(self, extras: List[Dict]):
        """Actualiza la tabla de extras"""
        if not self._tabla_extras:
            return
        
        self._tabla_extras.rows.clear()
        
        if not extras:
            # Fila vacía con mensaje
            self._tabla_extras.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.icons.Icons.ADD_CIRCLE_OUTLINE, size=40, color=ft.Colors.GREY_400),
                            ft.Text("No hay extras", weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                    )),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                ])
            )
        else:
            for extra in extras:
                self._tabla_extras.rows.append(self._crear_fila_extra(extra))
        
        safe_update(self._pagina)
    
    def _crear_fila_extra(self, extra: Dict) -> ft.DataRow:
        """Crea una fila de DataTable para un extra"""
        # Badge de estado
        estado_cell = ft.Container(
            content=ft.Text(
                "ACTIVO" if extra["ACTIVO"] else "INACTIVO",
                size=11,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE,
            ),
            padding=ft.Padding(8, 4, 8, 4),
            border_radius=12,
            bgcolor=COLORES.EXITO if extra["ACTIVO"] else COLORES.PELIGRO,
        )
        
        # Precio formateado
        precio_cell = ft.Container(
            content=ft.Text(
                f"S/ {extra['PRECIO_ADICIONAL'] / 100:.2f}",
                size=14,
                weight=ft.FontWeight.BOLD,
                color=COLORES.EXITO,
            ),
            padding=ft.Padding(8, 4, 8, 4),
            border_radius=8,
            bgcolor=ft.Colors.GREEN_50,
        )
        
        # Botones de acción
        acciones = ft.Row([
            ft.IconButton(
                icon=ft.icons.Icons.VISIBILITY,
                tooltip="Ver detalles",
                icon_color=COLORES.INFO,
                icon_size=20,
                on_click=lambda _, e=extra: self._mostrar_detalle(e),
            ),
            ft.IconButton(
                icon=ft.icons.Icons.EDIT,
                tooltip="Editar",
                icon_color=COLORES.ADVERTENCIA,
                icon_size=20,
                on_click=lambda _, e=extra: self._mostrar_editar(e),
            ),
            ft.IconButton(
                icon=ft.icons.Icons.SHOPPING_BAG,
                tooltip="Ver productos",
                icon_color=COLORES.PRIMARIO,
                icon_size=20,
                on_click=lambda _, e=extra: self._mostrar_productos(e),
            ),
            ft.IconButton(
                icon=ft.icons.Icons.TOGGLE_ON if extra["ACTIVO"] else ft.icons.Icons.TOGGLE_OFF,
                tooltip="Desactivar" if extra["ACTIVO"] else "Activar",
                icon_color=COLORES.EXITO if extra["ACTIVO"] else ft.Colors.GREY_400,
                icon_size=20,
                on_click=lambda _, e=extra: self._toggle_estado(e),
            ),
        ], spacing=0)
        
        # Color de fila según estado
        row_color = None if extra["ACTIVO"] else {ft.ControlState.DEFAULT: ft.Colors.GREY_100}
        
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Row([
                    ft.Icon(ft.icons.Icons.ADD_CIRCLE, size=20, color=COLORES.PRIMARIO),
                    ft.Text(extra["NOMBRE"], weight=ft.FontWeight.BOLD, size=13),
                ], spacing=8)),
                ft.DataCell(ft.Text(
                    extra["DESCRIPCION"] or "Sin descripción",
                    size=12,
                    color=COLORES.TEXTO_SECUNDARIO,
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS,
                )),
                ft.DataCell(precio_cell),
                ft.DataCell(estado_cell),
                ft.DataCell(acciones),
            ],
            color=row_color
        )
    
    def _mostrar_crear(self, e):
        """Muestra el overlay para crear un nuevo extra"""
        campo_nombre = ft.TextField(
            label="Nombre del extra",
            hint_text="Ej: Queso extra, Tocino, etc.",
            prefix_icon=ft.icons.Icons.ADD_CIRCLE,
            autofocus=True,
        )
        
        campo_descripcion = ft.TextField(
            label="Descripción",
            hint_text="Descripción del extra (opcional)",
            prefix_icon=ft.icons.Icons.DESCRIPTION,
            multiline=True,
            max_lines=3,
        )
        
        campo_precio = ft.TextField(
            label="Precio adicional (Bs.)",
            hint_text="0.00",
            prefix_icon=ft.icons.Icons.ATTACH_MONEY,
            keyboard_type=ft.KeyboardType.NUMBER,
            value="0",
        )
        
        def guardar(e):
            if not campo_nombre.value:
                campo_nombre.error_text = "El nombre es obligatorio"
                safe_update(self._pagina)
                return
            
            try:
                precio_bs = float(campo_precio.value or 0)
                precio_centavos = int(precio_bs * 100)
                
                with OBTENER_SESION() as sesion:
                    nuevo_extra = MODELO_EXTRA(
                        NOMBRE=campo_nombre.value,
                        DESCRIPCION=campo_descripcion.value or None,
                        PRECIO_ADICIONAL=precio_centavos,
                        ACTIVO=True,
                    )
                    sesion.add(nuevo_extra)
                    sesion.commit()
                
                self._pagina.overlay.clear()
                self._cargar_extras()
                self._mostrar_exito("Extra creado exitosamente")
                
            except ValueError:
                campo_precio.error_text = "Precio inválido"
                safe_update(self._pagina)
            except Exception as ex:
                print(f"[ERROR] Creando extra: {ex}")
                self._mostrar_error(f"Error al crear extra: {str(ex)}")
        
        self._overlay_crear = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.icons.Icons.ADD_CIRCLE, color=COLORES.EXITO, size=28),
                ft.Text("Crear Nuevo Extra", size=20, weight=ft.FontWeight.BOLD),
            ], spacing=12),
            content=ft.Column([
                campo_nombre,
                campo_descripcion,
                campo_precio,
            ], tight=True, spacing=16),
            actions=[
                ft.TextButton(
                    content=ft.Row([
                        ft.Icon(ft.icons.Icons.CLOSE, size=18),
                        ft.Text("Cancelar"),
                    ], spacing=8),
                    on_click=lambda _: self._cerrar_overlays(),
                ),
                ft.FilledButton(
                    content=ft.Row([
                        ft.Icon(ft.icons.Icons.SAVE, size=18),
                        ft.Text("Guardar"),
                    ], spacing=8),
                    on_click=guardar,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self._overlay_crear.open = True
        self._pagina.overlay.append(self._overlay_crear)
        safe_update(self._pagina)
    
    def _mostrar_editar(self, extra: Dict):
        """Muestra el overlay para editar un extra"""
        campo_nombre = ft.TextField(
            label="Nombre del extra",
            prefix_icon=ft.icons.Icons.ADD_CIRCLE,
            value=extra["NOMBRE"],
            autofocus=True,
        )
        
        campo_descripcion = ft.TextField(
            label="Descripción",
            prefix_icon=ft.icons.Icons.DESCRIPTION,
            multiline=True,
            max_lines=3,
            value=extra["DESCRIPCION"] or "",
        )
        
        campo_precio = ft.TextField(
            label="Precio adicional (Bs.)",
            prefix_icon=ft.icons.Icons.ATTACH_MONEY,
            keyboard_type=ft.KeyboardType.NUMBER,
            value=str(extra["PRECIO_ADICIONAL"] / 100),
        )
        
        def guardar(e):
            if not campo_nombre.value:
                campo_nombre.error_text = "El nombre es obligatorio"
                safe_update(self._pagina)
                return
            
            try:
                precio_bs = float(campo_precio.value or 0)
                precio_centavos = int(precio_bs * 100)
                
                with OBTENER_SESION() as sesion:
                    extra_db = sesion.query(MODELO_EXTRA).filter_by(ID=extra["ID"]).first()
                    if extra_db:
                        extra_db.NOMBRE = campo_nombre.value
                        extra_db.DESCRIPCION = campo_descripcion.value or None
                        extra_db.PRECIO_ADICIONAL = precio_centavos
                        sesion.commit()
                
                self._pagina.overlay.clear()
                self._cargar_extras()
                self._mostrar_exito("Extra actualizado exitosamente")
                
            except ValueError:
                campo_precio.error_text = "Precio inválido"
                safe_update(self._pagina)
            except Exception as ex:
                print(f"[ERROR] Actualizando extra: {ex}")
                self._mostrar_error(f"Error al actualizar extra: {str(ex)}")
        
        self._overlay_editar = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.icons.Icons.EDIT, color=COLORES.ADVERTENCIA, size=28),
                ft.Text("Editar Extra", size=20, weight=ft.FontWeight.BOLD),
            ], spacing=12),
            content=ft.Column([
                campo_nombre,
                campo_descripcion,
                campo_precio,
            ], tight=True, spacing=16),
            actions=[
                ft.TextButton(
                    content=ft.Row([
                        ft.Icon(ft.icons.Icons.CLOSE, size=18),
                        ft.Text("Cancelar"),
                    ], spacing=8),
                    on_click=lambda _: self._cerrar_overlays(),
                ),
                ft.FilledButton(
                    content=ft.Row([
                        ft.Icon(ft.icons.Icons.SAVE, size=18),
                        ft.Text("Guardar"),
                    ], spacing=8),
                    on_click=guardar,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self._overlay_editar.open = True
        self._pagina.overlay.append(self._overlay_editar)
        safe_update(self._pagina)
    
    def _mostrar_detalle(self, extra: Dict):
        """Muestra el overlay con detalles del extra"""
        fecha_creacion = extra["FECHA_CREACION"].strftime("%d/%m/%Y %H:%M") if extra["FECHA_CREACION"] else "N/A"
        
        self._overlay_detalle = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.icons.Icons.INFO, color=COLORES.INFO, size=28),
                ft.Text("Detalles del Extra", size=20, weight=ft.FontWeight.BOLD),
            ], spacing=12),
            content=ft.Column([
                ft.ListTile(
                    leading=ft.Icon(ft.icons.Icons.ADD_CIRCLE, color=COLORES.PRIMARIO),
                    title=ft.Text("Nombre", weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(extra["NOMBRE"]),
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.icons.Icons.DESCRIPTION, color=COLORES.INFO),
                    title=ft.Text("Descripción", weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(extra["DESCRIPCION"] or "Sin descripción"),
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.icons.Icons.ATTACH_MONEY, color=COLORES.EXITO),
                    title=ft.Text("Precio adicional", weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(f"S/ {extra['PRECIO_ADICIONAL'] / 100:.2f}"),
                ),
                ft.ListTile(
                    leading=ft.Icon(
                        ft.icons.Icons.CHECK_CIRCLE if extra["ACTIVO"] else ft.icons.Icons.CANCEL,
                        color=COLORES.EXITO if extra["ACTIVO"] else COLORES.PELIGRO,
                    ),
                    title=ft.Text("Estado", weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text("ACTIVO" if extra["ACTIVO"] else "INACTIVO"),
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.icons.Icons.CALENDAR_TODAY, color=COLORES.TEXTO_SECUNDARIO),
                    title=ft.Text("Fecha de creación", weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(fecha_creacion),
                ),
            ], tight=True, spacing=0),
            actions=[
                ft.TextButton(
                    content=ft.Row([
                        ft.Icon(ft.icons.Icons.CLOSE, size=18),
                        ft.Text("Cerrar"),
                    ], spacing=8),
                    on_click=lambda _: self._cerrar_overlays(),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self._overlay_detalle.open = True
        self._pagina.overlay.append(self._overlay_detalle)
        safe_update(self._pagina)
    
    def _mostrar_productos(self, extra: Dict):
        """Muestra el overlay con los productos que tienen este extra"""
        with OBTENER_SESION() as sesion:
            try:
                extra_db = sesion.query(MODELO_EXTRA).filter_by(ID=extra["ID"]).first()
                if not extra_db:
                    self._mostrar_error("Extra no encontrado")
                    return
                
                productos = extra_db.PRODUCTOS
                
                if not productos:
                    contenido = ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.icons.Icons.INVENTORY_2, size=48, color=ft.Colors.GREY_400),
                            ft.Text("No hay productos con este extra", color=ft.Colors.GREY_600),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                        padding=ft.Padding(20, 20, 20, 20),
                    )
                else:
                    lista_productos = ft.Column([
                        ft.ListTile(
                            leading=ft.Icon(ft.icons.Icons.INVENTORY_2, color=COLORES.PRIMARIO),
                            title=ft.Text(p.NOMBRE, weight=ft.FontWeight.W_500),
                            subtitle=ft.Text(f"S/ {p.PRECIO / 100:.2f}"),
                        ) for p in productos
                    ], spacing=0, scroll=ft.ScrollMode.AUTO)
                    
                    contenido = ft.Container(
                        content=lista_productos,
                        height=300,
                    )
                
                self._overlay_productos = ft.AlertDialog(
                    title=ft.Row([
                        ft.Icon(ft.icons.Icons.SHOPPING_BAG, color=COLORES.PRIMARIO, size=28),
                        ft.Text(f"Productos con '{extra['NOMBRE']}'", size=18, weight=ft.FontWeight.BOLD),
                    ], spacing=12),
                    content=contenido,
                    actions=[
                        ft.TextButton(
                            content=ft.Row([
                                ft.Icon(ft.icons.Icons.CLOSE, size=18),
                                ft.Text("Cerrar"),
                            ], spacing=8),
                            on_click=lambda _: self._cerrar_overlays(),
                        ),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                
                self._overlay_productos.open = True
                self._pagina.overlay.append(self._overlay_productos)
                safe_update(self._pagina)
                
            except Exception as ex:
                print(f"[ERROR] Cargando productos del extra: {ex}")
                self._mostrar_error("Error al cargar productos")
    
    def _toggle_estado(self, extra: Dict):
        """Activa/desactiva un extra"""
        nuevo_estado = not extra["ACTIVO"]
        
        with OBTENER_SESION() as sesion:
            try:
                extra_db = sesion.query(MODELO_EXTRA).filter_by(ID=extra["ID"]).first()
                if extra_db:
                    extra_db.ACTIVO = nuevo_estado
                    sesion.commit()
                    
                    self._cargar_extras()
                    mensaje = "Extra activado" if nuevo_estado else "Extra desactivado"
                    self._mostrar_exito(mensaje)
            except Exception as ex:
                print(f"[ERROR] Cambiando estado del extra: {ex}")
                self._mostrar_error("Error al cambiar estado")
    
    def _cerrar_overlays(self):
        """Cierra todos los overlays abiertos"""
        self._pagina.overlay.clear()
        safe_update(self._pagina)
    
    def _mostrar_exito(self, mensaje: str):
        """Muestra un snackbar de éxito"""
        self._pagina.snack_bar = ft.SnackBar(
            content=ft.Row([
                ft.Icon(ft.icons.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE),
                ft.Text(mensaje, color=ft.Colors.WHITE),
            ], spacing=12),
            bgcolor=COLORES.EXITO,
        )
        self._pagina.snack_bar.open = True
        safe_update(self._pagina)
    
    def _mostrar_error(self, mensaje: str):
        """Muestra un snackbar de error"""
        self._pagina.snack_bar = ft.SnackBar(
            content=ft.Row([
                ft.Icon(ft.icons.Icons.ERROR, color=ft.Colors.WHITE),
                ft.Text(mensaje, color=ft.Colors.WHITE),
            ], spacing=12),
            bgcolor=COLORES.PELIGRO,
        )
        self._pagina.snack_bar.open = True
        safe_update(self._pagina)
    
    def _volver_dashboard(self):
        """Vuelve al dashboard"""
        from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
        self._pagina.controls.clear()
        self._pagina.add(PaginaAdmin(self._pagina, self._usuario))
        safe_update(self._pagina)
    
    def _cerrar_sesion(self):
        """Cierra la sesión del usuario"""
        from features.autenticacion.presentation.pages.PaginaLogin import PaginaLogin
        self._pagina.controls.clear()
        self._pagina.add(PaginaLogin(self._pagina))
        safe_update(self._pagina)
