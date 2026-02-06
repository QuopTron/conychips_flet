"""
Página moderna de gestión de ofertas con sistema avanzado
Incluye: Tipos de oferta, sucursales específicas, tiempos personalizados, overlays hermosos
"""
import flet as ft
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import threading
import time
from core.base_datos.ConfiguracionBD import (
    MODELO_OFERTA, MODELO_PRODUCTO, MODELO_SUCURSAL, 
    MODELO_OFERTA_SUCURSAL, OBTENER_SESION
)
from core.ui.safe_actions import safe_update
from features.admin.presentation.widgets.LayoutBase import LayoutBase
from core.realtime.broker_notify import notify
from core.realtime import dispatcher
from core.decoradores.DecoradorPermisosUI import requiere_permiso_ui
from core.Constantes import ROLES


# Tipos de oferta disponibles
TIPOS_OFERTA = [
    ("DESCUENTO", "💰 Descuento", "Descuento porcentual directo"),
    ("2X1", "🎁 2x1", "Dos productos por el precio de uno"),
    ("3X2", "🎉 3x2", "Tres productos por el precio de dos"),
    ("COMBO", "🍔 Combo", "Oferta especial en combo"),
    ("ESPECIAL", "⭐ Especial", "Oferta especial del día"),
    ("FLASH", "⚡ Flash", "Oferta relámpago limitada")
]


class OfertasPageModerna(LayoutBase):
    """Página moderna para gestión de ofertas con configuración avanzada"""

    def __init__(self, pagina: ft.Page, usuario):
        # Caches y filtros
        self._ofertas_cache: List = []
        self._productos_cache: List = []
        self._sucursales_cache: List = []
        self._filtro_estado = "ACTIVAS"
        self._filtro_busqueda = ""
        
        # Componentes UI
        self._lista_ofertas: Optional[ft.Column] = None
        self._campo_busqueda: Optional[ft.TextField] = None
        
        # Overlays
        self._overlay_crear: Optional[ft.AlertDialog] = None
        self._overlay_editar: Optional[ft.AlertDialog] = None
        self._overlay_configurar_sucursales: Optional[ft.AlertDialog] = None
        
        # Timer de expiración
        self._timer_thread: Optional[threading.Thread] = None
        self._timer_running = False
        
        # Estado temporal para creación de oferta
        self._temp_oferta_data: Dict = {}
        self._temp_sucursales_seleccionadas: List = []
        self._temp_oferta_editando: Optional[int] = None
        
        # Inicializar LayoutBase primero
        super().__init__(
            pagina=pagina,
            usuario=usuario,
            titulo_vista="🏷️ Gestión de Ofertas Avanzada",
            mostrar_boton_volver=True,
            index_navegacion=0,
            on_volver_dashboard=self._volver_dashboard,
            on_cerrar_sesion=self._cerrar_sesion
        )
        
        # Guardar referencias para decoradores (después de super para no sobrescribir)
        self.usuario = usuario
        self.pagina = pagina
        
        # Construir interfaz
        contenido = self._construir_contenido()
        self.construir(contenido)
        
        # Registrar websocket handlers
        dispatcher.register("oferta_expirada", self._on_oferta_expirada)
        dispatcher.register("oferta_actualizada", self._on_oferta_actualizada)
        
        # Cargar datos e iniciar timer
        self._cargar_productos()
        self._cargar_sucursales()
        self._cargar_ofertas()
        self._iniciar_timer_expiracion()
    
    def _construir_contenido(self) -> ft.Container:
        """Construye el contenido principal"""
        # Barra de búsqueda
        self._campo_busqueda = ft.TextField(
            hint_text="Buscar por nombre, producto o tipo...",
            prefix_icon=ft.icons.Icons.SEARCH,
            on_change=self._on_buscar,
            expand=True,
            border_radius=10,
            height=50
        )
        
        # Botones de acción - visibles siempre pero controlados por permisos
        puede_crear = self._puede_ejecutar("ofertas.crear")
        
        btn_crear = ft.ElevatedButton(
            "Nueva Oferta",
            icon=ft.icons.Icons.ADD,
            on_click=lambda e: self._intentar_crear(),
            bgcolor=ft.Colors.GREEN_700 if puede_crear else ft.Colors.GREY_400,
            color=ft.Colors.WHITE,
            height=50,
            disabled=not puede_crear,
            tooltip="Nueva Oferta" if puede_crear else "Sin permisos para crear ofertas"
        )
        
        btn_refrescar = ft.IconButton(
            icon=ft.icons.Icons.REFRESH,
            on_click=lambda e: self._cargar_ofertas(),
            tooltip="Refrescar",
            icon_size=30
        )
        
        # Chips de filtro
        filtros = self._crear_filtros()
        
        # DataTable de ofertas (en lugar de lista de cards)
        self._tabla_ofertas = ft.DataTable(
            columns=[
                ft.DataColumn(label=ft.Text("Tipo", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Nombre", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Producto", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Descuento", weight=ft.FontWeight.BOLD), numeric=True),
                ft.DataColumn(label=ft.Text("Estado", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Fechas", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=10,
            heading_row_color=ft.Colors.BLUE_50,
            heading_row_height=60,
            data_row_min_height=60,
            data_row_max_height=float("inf"),
            column_spacing=20,
            horizontal_margin=15,
            divider_thickness=1,
            horizontal_lines=ft.border.BorderSide(1, ft.Colors.GREY_200),
        )
        
        # Contenedor scrollable para la tabla
        self._contenedor_tabla = ft.Container(
            content=ft.Column([
                self._tabla_ofertas
            ], scroll=ft.ScrollMode.AUTO, expand=True),
            expand=True,
            padding=10
        )
        
        return ft.Container(
            content=ft.Column([
                # Header
                ft.Row([
                    self._campo_busqueda,
                    btn_crear,
                    btn_refrescar
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                # Filtros
                filtros,
                
                ft.Divider(height=1, color=ft.Colors.GREY_300),
                
                # Tabla
                self._contenedor_tabla
            ], spacing=15, expand=True),
            padding=20,
            expand=True
        )
    
    def _crear_filtros(self) -> ft.Row:
        """Crea los chips de filtro"""
        return ft.Row([
            ft.Text("Filtrar:", weight=ft.FontWeight.BOLD, size=14),
            ft.Chip(
                label=ft.Text("TODAS"),
                on_click=lambda e: self._cambiar_filtro("TODAS"),
                bgcolor=ft.Colors.BLUE_700 if self._filtro_estado == "TODAS" else ft.Colors.GREY_300
            ),
            ft.Chip(
                label=ft.Text("ACTIVAS"),
                on_click=lambda e: self._cambiar_filtro("ACTIVAS"),
                bgcolor=ft.Colors.GREEN_700 if self._filtro_estado == "ACTIVAS" else ft.Colors.GREY_300
            ),
            ft.Chip(
                label=ft.Text("EXPIRADAS"),
                on_click=lambda e: self._cambiar_filtro("EXPIRADAS"),
                bgcolor=ft.Colors.RED_700 if self._filtro_estado == "EXPIRADAS" else ft.Colors.GREY_300
            )
        ], spacing=10)
    
    def _cambiar_filtro(self, nuevo_filtro: str):
        """Cambia el filtro activo"""
        self._filtro_estado = nuevo_filtro
        self._aplicar_filtros()
        safe_update(self._pagina)
    
    def _on_buscar(self, e):
        """Búsqueda en tiempo real"""
        self._filtro_busqueda = e.control.value.lower()
        self._aplicar_filtros()
    
    def _aplicar_filtros(self):
        """Aplica los filtros"""
        ofertas_filtradas = self._ofertas_cache.copy()
        
        # Filtrar por búsqueda
        if self._filtro_busqueda:
            ofertas_filtradas = [
                o for o in ofertas_filtradas
                if self._filtro_busqueda in o.NOMBRE.lower() or
                   self._filtro_busqueda in o.PRODUCTO.NOMBRE.lower() or
                   self._filtro_busqueda in o.TIPO.lower()
            ]
        
        # Filtrar por estado
        ahora = datetime.now()
        if self._filtro_estado == "ACTIVAS":
            ofertas_filtradas = [
                o for o in ofertas_filtradas
                if o.ACTIVA and (not o.FECHA_FIN or o.FECHA_FIN > ahora)
            ]
        elif self._filtro_estado == "EXPIRADAS":
            ofertas_filtradas = [
                o for o in ofertas_filtradas
                if not o.ACTIVA or (o.FECHA_FIN and o.FECHA_FIN <= ahora)
            ]
        
        self._actualizar_lista_ofertas(ofertas_filtradas)
    
    def _cargar_productos(self):
        """Carga productos disponibles"""
        with OBTENER_SESION() as sesion:
            self._productos_cache = sesion.query(MODELO_PRODUCTO).filter_by(DISPONIBLE=True).all()
    
    def _cargar_sucursales(self):
        """Carga sucursales activas"""
        with OBTENER_SESION() as sesion:
            self._sucursales_cache = sesion.query(MODELO_SUCURSAL).filter_by(ACTIVA=True, ELIMINADA=False).all()
    
    def _cargar_ofertas(self):
        """Carga ofertas con relaciones (solo no eliminadas)"""
        from sqlalchemy.orm import joinedload
        
        with OBTENER_SESION() as sesion:
            self._ofertas_cache = sesion.query(MODELO_OFERTA).options(
                joinedload(MODELO_OFERTA.PRODUCTO),
                joinedload(MODELO_OFERTA.SUCURSALES).joinedload(MODELO_OFERTA_SUCURSAL.SUCURSAL)
            ).filter_by(ELIMINADO=False).all()
        
        self._aplicar_filtros()
    
    def _actualizar_lista_ofertas(self, ofertas: List):
        """Actualiza la tabla de ofertas"""
        if not self._tabla_ofertas:
            return
        
        self._tabla_ofertas.rows.clear()
        
        if not ofertas:
            # Mostrar mensaje vacío
            self._tabla_ofertas.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Container(
                            content=ft.Column([
                                ft.Icon(ft.icons.Icons.LOCAL_OFFER_OUTLINED, size=40, color=ft.Colors.GREY_400),
                                ft.Text("No hay ofertas", weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                        )),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text("")),
                    ]
                )
            )
        else:
            for oferta in ofertas:
                self._tabla_ofertas.rows.append(self._crear_fila_oferta(oferta))
        
        safe_update(self._pagina)
    
    def _crear_fila_oferta(self, oferta) -> ft.DataRow:
        """Crea una fila de DataTable para la oferta"""
        ahora = datetime.now()
        expirada = oferta.FECHA_FIN and oferta.FECHA_FIN <= ahora
        activa = oferta.ACTIVA and not expirada
        
        # Info del tipo
        tipo_info = next((t for t in TIPOS_OFERTA if t[0] == oferta.TIPO), TIPOS_OFERTA[0])
        
        # Badge de estado
        if activa:
            estado_cell = ft.Container(
                content=ft.Text("ACTIVA", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                bgcolor=ft.Colors.GREEN_700,
                padding=ft.Padding(8, 4, 8, 4),
                border_radius=12
            )
        elif expirada:
            estado_cell = ft.Container(
                content=ft.Text("EXPIRADA", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED_700,
                padding=ft.Padding(8, 4, 8, 4),
                border_radius=12
            )
        else:
            estado_cell = ft.Container(
                content=ft.Text("INACTIVA", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                bgcolor=ft.Colors.GREY_600,
                padding=ft.Padding(8, 4, 8, 4),
                border_radius=12
            )
        
        # Precio con descuento
        precio_original = oferta.PRODUCTO.PRECIO / 100
        precio_final = precio_original * (1 - oferta.DESCUENTO_PORCENTAJE / 100)
        
        # Fechas
        fecha_inicio_str = oferta.FECHA_INICIO.strftime('%d/%m/%Y')
        fecha_fin_str = oferta.FECHA_FIN.strftime('%d/%m/%Y') if oferta.FECHA_FIN else "Sin límite"
        
        # Tiempo restante
        tiempo_restante = ""
        if activa and oferta.FECHA_FIN:
            delta = oferta.FECHA_FIN - ahora
            if delta.days > 0:
                tiempo_restante = f"({delta.days}d)"
            elif delta.seconds > 3600:
                tiempo_restante = f"({delta.seconds // 3600}h)"
            else:
                tiempo_restante = f"({delta.seconds // 60}m)"
        
        # Permisos
        puede_ver = self._puede_ejecutar("ofertas.ver")
        puede_editar = self._puede_ejecutar("ofertas.editar")
        puede_eliminar = self._puede_ejecutar("ofertas.eliminar")
        
        # Botones de acción
        acciones = ft.Row([
            ft.IconButton(
                icon=ft.icons.Icons.INFO_OUTLINE,
                tooltip="Ver detalles",
                icon_color=ft.Colors.BLUE_700 if puede_ver else ft.Colors.GREY_400,
                icon_size=20,
                on_click=lambda e, o=oferta: self._intentar_ver_detalle(o),
                disabled=not puede_ver
            ),
            ft.IconButton(
                icon=ft.icons.Icons.EDIT,
                tooltip="Editar",
                icon_color=ft.Colors.ORANGE_700 if puede_editar else ft.Colors.GREY_400,
                icon_size=20,
                on_click=lambda e, o=oferta: self._intentar_editar(o),
                disabled=expirada or not puede_editar
            ),
            ft.IconButton(
                icon=ft.icons.Icons.TOGGLE_ON if activa else ft.icons.Icons.TOGGLE_OFF,
                tooltip="Activar/Desactivar",
                icon_color=ft.Colors.GREEN_700 if activa else ft.Colors.GREY_400,
                icon_size=20,
                on_click=lambda e, o=oferta: self._intentar_toggle_estado(o),
                disabled=expirada or not puede_editar
            ),
            ft.IconButton(
                icon=ft.icons.Icons.DELETE_OUTLINE,
                tooltip="Eliminar",
                icon_color=ft.Colors.RED_700 if puede_eliminar else ft.Colors.GREY_400,
                icon_size=20,
                on_click=lambda e, o=oferta: self._intentar_eliminar(o),
                disabled=not puede_eliminar
            )
        ], spacing=0)
        
        # Color de fila según estado
        row_color = None
        if expirada:
            row_color = {ft.ControlState.DEFAULT: ft.Colors.RED_50}
        elif not activa:
            row_color = {ft.ControlState.DEFAULT: ft.Colors.GREY_100}
        
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Container(
                    content=ft.Text(tipo_info[1], size=20),
                    tooltip=tipo_info[2]
                )),
                ft.DataCell(ft.Column([
                    ft.Text(oferta.NOMBRE, weight=ft.FontWeight.BOLD, size=13),
                    ft.Text(f"ID: {oferta.ID}", size=10, color=ft.Colors.GREY_500)
                ], spacing=2)),
                ft.DataCell(ft.Column([
                    ft.Text(oferta.PRODUCTO.NOMBRE, size=12),
                    ft.Text(f"${precio_original:.2f} → ${precio_final:.2f}", size=11, color=ft.Colors.GREEN_700, weight=ft.FontWeight.BOLD)
                ], spacing=2)),
                ft.DataCell(ft.Container(
                    content=ft.Text(f"{oferta.DESCUENTO_PORCENTAJE}%", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700),
                    bgcolor=ft.Colors.GREEN_50,
                    padding=ft.Padding(8, 4, 8, 4),
                    border_radius=8
                )),
                ft.DataCell(estado_cell),
                ft.DataCell(ft.Column([
                    ft.Text(f"📅 {fecha_inicio_str}", size=11),
                    ft.Text(f"🏁 {fecha_fin_str} {tiempo_restante}", size=11, color=ft.Colors.RED_700 if expirada else None)
                ], spacing=2)),
                ft.DataCell(acciones),
            ],
            color=row_color
        )
    
    def _puede_ejecutar(self, permiso: str) -> bool:
        """Verifica si el usuario tiene permiso para ejecutar acción"""
        try:
            # SUPERADMIN puede todo
            if hasattr(self.usuario, 'TIENE_ROL') and self.usuario.TIENE_ROL(ROLES.SUPERADMIN):
                return True
            # Verificar permiso específico
            if hasattr(self.usuario, 'TIENE_PERMISO'):
                return self.usuario.TIENE_PERMISO(permiso)
            return False
        except:
            return False
    
    def _intentar_crear(self):
        """Wrapper que verifica permisos antes de crear"""
        if self._puede_ejecutar("ofertas.crear"):
            self._mostrar_crear()
        else:
            self._mostrar_advertencia("No tienes permisos para crear ofertas")
    
    def _intentar_ver_detalle(self, oferta):
        """Wrapper que verifica permisos antes de ver detalles"""
        if self._puede_ejecutar("ofertas.ver"):
            self._mostrar_detalle(oferta)
        else:
            self._mostrar_advertencia("No tienes permisos para ver detalles")
    
    def _intentar_editar(self, oferta):
        """Wrapper que verifica permisos antes de editar"""
        if self._puede_ejecutar("ofertas.editar"):
            self._mostrar_editar(oferta)
        else:
            self._mostrar_advertencia("No tienes permisos para editar ofertas")
    
    def _intentar_toggle_estado(self, oferta):
        """Wrapper que verifica permisos antes de cambiar estado"""
        if self._puede_ejecutar("ofertas.editar"):
            self._toggle_estado(oferta)
        else:
            self._mostrar_advertencia("No tienes permisos para modificar ofertas")
    
    def _intentar_eliminar(self, oferta):
        """Wrapper que verifica permisos antes de eliminar"""
        if self._puede_ejecutar("ofertas.eliminar"):
            self._confirmar_eliminar(oferta)
        else:
            self._mostrar_advertencia("No tienes permisos para eliminar ofertas")
    
    
    def _mostrar_detalle(self, oferta):
        """Muestra detalles completos"""
        tipo_info = next((t for t in TIPOS_OFERTA if t[0] == oferta.TIPO), TIPOS_OFERTA[0])
        precio_original = oferta.PRODUCTO.PRECIO / 100
        precio_final = precio_original * (1 - oferta.DESCUENTO_PORCENTAJE / 100)
        
        detalles = ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Text(tipo_info[1], size=32),
                    ft.Column([
                        ft.Text(oferta.NOMBRE, size=18, weight=ft.FontWeight.BOLD),
                        ft.Text(tipo_info[2], size=12, color=ft.Colors.GREY_600, italic=True)
                    ], expand=True)
                ]),
                padding=15,
                bgcolor=ft.Colors.BLUE_50,
                border_radius=10
            ),
            ft.Divider(),
            ft.Text("📦 Producto", weight=ft.FontWeight.BOLD),
            ft.Text(oferta.PRODUCTO.NOMBRE, size=16),
            ft.Divider(),
            ft.Text("💰 Precios", weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Column([
                    ft.Text("Original", size=12, color=ft.Colors.GREY_600),
                    ft.Text(f"${precio_original:.2f}", size=16, color=ft.Colors.GREY_600)
                ]),
                ft.Icon(ft.icons.Icons.ARROW_FORWARD, color=ft.Colors.ORANGE_700),
                ft.Column([
                    ft.Text("Con descuento", size=12, color=ft.Colors.GREY_600),
                    ft.Text(f"${precio_final:.2f}", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700)
                ])
            ], spacing=15),
            ft.Text(f"Descuento: {oferta.DESCUENTO_PORCENTAJE}%", size=14, color=ft.Colors.GREEN_700),
            ft.Divider(),
            ft.Text("🏪 Sucursales", weight=ft.FontWeight.BOLD),
            ft.Text(
                "Aplica en TODAS las sucursales" if oferta.APLICAR_TODAS_SUCURSALES
                else f"{len(oferta.SUCURSALES)} sucursales específicas"
            ),
            ft.Divider(),
            ft.Text("📅 Fechas", weight=ft.FontWeight.BOLD),
            ft.Text(f"Inicio: {oferta.FECHA_INICIO.strftime('%d/%m/%Y %H:%M')}"),
            ft.Text(f"Fin: {oferta.FECHA_FIN.strftime('%d/%m/%Y %H:%M') if oferta.FECHA_FIN else 'Sin límite'}"),
        ], spacing=10, scroll=ft.ScrollMode.AUTO)
        
        overlay = ft.AlertDialog(
            title=ft.Text("Detalles de la Oferta"),
            content=ft.Container(content=detalles, width=450, height=500),
            actions=[ft.TextButton("Cerrar", on_click=lambda e: self._cerrar_overlays())]
        )
        
        self._pagina.overlay.append(overlay)
        overlay.open = True
        self._pagina.update()
    
    def _mostrar_crear(self):
        """Muestra el diálogo de creación completo - PASO 1: Información básica"""
        # Resetear datos temporales
        self._temp_oferta_data = {}
        self._temp_sucursales_seleccionadas = []
        
        # Dropdown de productos
        dropdown_producto = ft.Dropdown(
            label="Producto",
            hint_text="Selecciona un producto",
            options=[
                ft.dropdown.Option(key=str(p.ID), text=p.NOMBRE)
                for p in self._productos_cache
            ],
            width=400
        )
        
        # Dropdown de tipo
        dropdown_tipo = ft.Dropdown(
            label="Tipo de Oferta",
            hint_text="Selecciona el tipo",
            options=[
                ft.dropdown.Option(key=t[0], text=t[1])
                for t in TIPOS_OFERTA
            ],
            width=400
        )
        
        # Campo nombre
        campo_nombre = ft.TextField(
            label="Nombre de la oferta",
            hint_text="Ej: Super descuento fin de semana",
            width=400
        )
        
        # Campo descuento
        campo_descuento = ft.Slider(
            min=5,
            max=90,
            divisions=17,
            label="{value}%",
            value=10,
            width=400
        )
        
        texto_descuento = ft.Text("Descuento: 10%", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700)
        
        def on_descuento_change(e):
            texto_descuento.value = f"Descuento: {int(e.control.value)}%"
            self._pagina.update()
        
        campo_descuento.on_change = on_descuento_change
        
        def siguiente():
            if not dropdown_producto.value:
                self._mostrar_error("Selecciona un producto")
                return
            if not dropdown_tipo.value:
                self._mostrar_error("Selecciona un tipo de oferta")
                return
            if not campo_nombre.value:
                self._mostrar_error("Ingresa un nombre para la oferta")
                return
            
            # Guardar datos
            self._temp_oferta_data = {
                "producto_id": int(dropdown_producto.value),
                "tipo": dropdown_tipo.value,
                "nombre": campo_nombre.value,
                "descuento": int(campo_descuento.value)
            }
            
            self._cerrar_overlays()
            self._mostrar_crear_paso2()
        
        contenido = ft.Column([
            ft.Text("📝 Nueva Oferta - Paso 1/3", size=20, weight=ft.FontWeight.BOLD),
            ft.Text("Información básica de la oferta", color=ft.Colors.GREY_600),
            ft.Divider(),
            dropdown_producto,
            dropdown_tipo,
            campo_nombre,
            ft.Divider(),
            texto_descuento,
            campo_descuento,
        ], spacing=15, width=450, scroll=ft.ScrollMode.AUTO)
        
        self._overlay_crear = ft.AlertDialog(
            title=ft.Text("Nueva Oferta"),
            content=contenido,
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self._cerrar_overlays()),
                ft.ElevatedButton("Siguiente →", on_click=lambda e: siguiente(), bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE)
            ]
        )
        
        self._pagina.overlay.append(self._overlay_crear)
        self._overlay_crear.open = True
        self._pagina.update()
    
    def _mostrar_crear_paso2(self):
        """PASO 2: Selección de sucursales"""
        checkbox_todas = ft.Checkbox(label="Aplicar en TODAS las sucursales", value=True)
        
        checkboxes_sucursales = []
        for sucursal in self._sucursales_cache:
            cb = ft.Checkbox(label=sucursal.NOMBRE, value=False, data=sucursal.ID)
            checkboxes_sucursales.append(cb)
        
        container_sucursales = ft.Column(checkboxes_sucursales, spacing=10, visible=False)
        
        def on_todas_change(e):
            container_sucursales.visible = not checkbox_todas.value
            for cb in checkboxes_sucursales:
                cb.value = False
            container_sucursales.update()
        
        checkbox_todas.on_change = on_todas_change
        
        def siguiente():
            self._temp_oferta_data["aplicar_todas"] = checkbox_todas.value
            
            if not checkbox_todas.value:
                seleccionadas = [cb.data for cb in checkboxes_sucursales if cb.value]
                if not seleccionadas:
                    self._mostrar_error("Selecciona al menos una sucursal")
                    return
                self._temp_sucursales_seleccionadas = seleccionadas
            else:
                self._temp_sucursales_seleccionadas = []
            
            self._cerrar_overlays()
            self._mostrar_crear_paso3()
        
        contenido = ft.Column([
            ft.Text("🏪 Nueva Oferta - Paso 2/3", size=20, weight=ft.FontWeight.BOLD),
            ft.Text("Selección de sucursales", color=ft.Colors.GREY_600),
            ft.Divider(),
            checkbox_todas,
            ft.Divider(),
            ft.Text("O selecciona sucursales específicas:", weight=ft.FontWeight.BOLD, visible=not checkbox_todas.value),
            container_sucursales
        ], spacing=15, width=450, height=400, scroll=ft.ScrollMode.AUTO)
        
        self._overlay_crear = ft.AlertDialog(
            title=ft.Text("Configurar Sucursales"),
            content=contenido,
            actions=[
                ft.TextButton("← Atrás", on_click=lambda e: (self._cerrar_overlays(), self._mostrar_crear())),
                ft.ElevatedButton("Siguiente →", on_click=lambda e: siguiente(), bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE)
            ]
        )
        
        self._pagina.overlay.append(self._overlay_crear)
        self._overlay_crear.open = True
        self._pagina.update()
    
    def _mostrar_crear_paso3(self):
        """PASO 3: Fechas y confirmación con DatePickers"""
        # Valores de fecha
        fecha_inicio_val = datetime.now()
        fecha_fin_val = datetime.now() + timedelta(days=7)
        
        # Textos para mostrar fechas seleccionadas
        texto_fecha_inicio = ft.Text(
            f"📅 Inicio: {fecha_inicio_val.strftime('%d/%m/%Y %H:%M')}",
            size=14,
            weight=ft.FontWeight.W_500
        )
        
        texto_fecha_fin = ft.Text(
            f"📅 Fin: {fecha_fin_val.strftime('%d/%m/%Y %H:%M')}",
            size=14,
            weight=ft.FontWeight.W_500
        )
        
        # Checkbox para fecha fin
        checkbox_sin_limite = ft.Checkbox(label="Sin fecha de expiración", value=False)
        
        # Contenedor para fecha fin
        container_fecha_fin = ft.Column([
            texto_fecha_fin,
            ft.ElevatedButton(
                "Cambiar fecha fin",
                icon=ft.icons.Icons.CALENDAR_MONTH,
                on_click=lambda e: abrir_datepicker_fin(e),
                bgcolor=ft.Colors.RED_100,
                color=ft.Colors.RED_900
            )
        ], spacing=5)
        
        def on_sin_limite_change(e):
            nonlocal fecha_fin_val
            container_fecha_fin.visible = not checkbox_sin_limite.value
            if checkbox_sin_limite.value:
                fecha_fin_val = None
                texto_fecha_fin.value = "📅 Fin: Sin límite"
            self._pagina.update()
        
        checkbox_sin_limite.on_change = on_sin_limite_change
        
        # Funciones para DatePickers
        def on_fecha_inicio_change(e):
            nonlocal fecha_inicio_val
            if e.control.value:
                fecha_inicio_val = datetime.combine(e.control.value, datetime.min.time().replace(hour=0, minute=0))
                texto_fecha_inicio.value = f"📅 Inicio: {fecha_inicio_val.strftime('%d/%m/%Y %H:%M')}"
                self._pagina.update()
        
        def on_fecha_fin_change(e):
            nonlocal fecha_fin_val
            if e.control.value:
                fecha_fin_val = datetime.combine(e.control.value, datetime.min.time().replace(hour=23, minute=59))
                texto_fecha_fin.value = f"📅 Fin: {fecha_fin_val.strftime('%d/%m/%Y %H:%M')}"
                self._pagina.update()
        
        def abrir_datepicker_inicio(e):
            dp = ft.DatePicker(
                value=fecha_inicio_val,
                first_date=datetime(2020, 1, 1),
                last_date=datetime(2030, 12, 31),
                on_change=on_fecha_inicio_change
            )
            self._pagina.overlay.append(dp)
            dp.open = True
            self._pagina.update()
        
        def abrir_datepicker_fin(e):
            dp = ft.DatePicker(
                value=fecha_fin_val if fecha_fin_val else datetime.now() + timedelta(days=7),
                first_date=fecha_inicio_val,
                last_date=datetime(2030, 12, 31),
                on_change=on_fecha_fin_change
            )
            self._pagina.overlay.append(dp)
            dp.open = True
            self._pagina.update()
        
        # Botones rápidos para duración
        def set_duracion(dias):
            nonlocal fecha_fin_val
            fecha_fin_val = datetime.now() + timedelta(days=dias)
            fecha_fin_val = fecha_fin_val.replace(hour=23, minute=59)
            texto_fecha_fin.value = f"📅 Fin: {fecha_fin_val.strftime('%d/%m/%Y %H:%M')}"
            self._pagina.update()
        
        btns_rapidos = ft.Row([
            ft.ElevatedButton("1 día", on_click=lambda e: set_duracion(1), bgcolor=ft.Colors.BLUE_50),
            ft.ElevatedButton("3 días", on_click=lambda e: set_duracion(3), bgcolor=ft.Colors.BLUE_100),
            ft.ElevatedButton("7 días", on_click=lambda e: set_duracion(7), bgcolor=ft.Colors.BLUE_200),
            ft.ElevatedButton("30 días", on_click=lambda e: set_duracion(30), bgcolor=ft.Colors.BLUE_300),
        ], spacing=8, wrap=True)
        
        def crear_oferta():
            try:
                # Validar
                fin = None if checkbox_sin_limite.value else fecha_fin_val
                if fin and fin <= fecha_inicio_val:
                    self._mostrar_error("La fecha de fin debe ser posterior al inicio")
                    return
                
                # Crear en BD
                with OBTENER_SESION() as sesion:
                    nueva_oferta = MODELO_OFERTA(
                        PRODUCTO_ID=self._temp_oferta_data["producto_id"],
                        NOMBRE=self._temp_oferta_data["nombre"],
                        TIPO=self._temp_oferta_data["tipo"],
                        DESCUENTO_PORCENTAJE=self._temp_oferta_data["descuento"],
                        FECHA_INICIO=fecha_inicio_val,
                        FECHA_FIN=fin,
                        ACTIVA=True,
                        APLICAR_TODAS_SUCURSALES=self._temp_oferta_data["aplicar_todas"]
                    )
                    
                    sesion.add(nueva_oferta)
                    sesion.flush()
                    
                    # Si son sucursales específicas, crear registros
                    if not self._temp_oferta_data["aplicar_todas"]:
                        for sucursal_id in self._temp_sucursales_seleccionadas:
                            rel = MODELO_OFERTA_SUCURSAL(
                                OFERTA_ID=nueva_oferta.ID,
                                SUCURSAL_ID=sucursal_id,
                                FECHA_FIN_ESPECIFICA=fin,
                                ACTIVA=True
                            )
                            sesion.add(rel)
                    
                    sesion.commit()
                    
                    notify({
                        "tipo": "oferta_actualizada",
                        "oferta_id": nueva_oferta.ID
                    })
                
                self._cerrar_overlays()
                self._cargar_ofertas()
                self._mostrar_exito(f"✅ Oferta '{self._temp_oferta_data['nombre']}' creada exitosamente")
                
            except Exception as e:
                self._mostrar_error(f"Error al crear oferta: {str(e)}")
        
        contenido = ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.icons.Icons.CALENDAR_MONTH, size=28, color=ft.Colors.GREEN_700),
                    ft.Text("Paso 3/3 - Fechas", size=20, weight=ft.FontWeight.BOLD)
                ], spacing=10),
                padding=10,
                bgcolor=ft.Colors.GREEN_50,
                border_radius=10
            ),
            ft.Divider(),
            ft.Text("📆 Fecha de inicio", weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Column([
                    texto_fecha_inicio,
                    ft.ElevatedButton(
                        "Seleccionar fecha inicio",
                        icon=ft.icons.Icons.CALENDAR_MONTH,
                        on_click=abrir_datepicker_inicio,
                        bgcolor=ft.Colors.BLUE_100,
                        color=ft.Colors.BLUE_900
                    )
                ], spacing=5),
                padding=10,
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=8
            ),
            ft.Divider(),
            checkbox_sin_limite,
            ft.Container(
                content=container_fecha_fin,
                padding=10,
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=8
            ),
            ft.Text("⚡ Atajos de duración:", size=12, color=ft.Colors.GREY_600),
            btns_rapidos,
        ], spacing=12, width=450, scroll=ft.ScrollMode.AUTO)
        
        self._overlay_crear = ft.AlertDialog(
            title=ft.Text("Finalizar Oferta"),
            content=contenido,
            actions=[
                ft.TextButton("← Atrás", on_click=lambda e: (self._cerrar_overlays(), self._mostrar_crear_paso2())),
                ft.ElevatedButton("✅ Crear Oferta", on_click=lambda e: crear_oferta(), bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE)
            ]
        )
        
        self._pagina.overlay.append(self._overlay_crear)
        self._overlay_crear.open = True
        self._pagina.update()
    
    def _mostrar_editar(self, oferta):
        """Muestra diálogo para editar una oferta con DatePickers"""
        self._temp_oferta_editando = oferta.ID
        
        # Valores de fecha actuales
        fecha_inicio_val = oferta.FECHA_INICIO
        fecha_fin_val = oferta.FECHA_FIN
        
        # Dropdown de productos
        dropdown_producto = ft.Dropdown(
            label="Producto",
            value=str(oferta.PRODUCTO_ID),
            options=[
                ft.dropdown.Option(key=str(p.ID), text=p.NOMBRE)
                for p in self._productos_cache
            ],
            width=400
        )
        
        # Dropdown de tipo
        dropdown_tipo = ft.Dropdown(
            label="Tipo de Oferta",
            value=oferta.TIPO,
            options=[
                ft.dropdown.Option(key=t[0], text=t[1])
                for t in TIPOS_OFERTA
            ],
            width=400
        )
        
        # Campo nombre
        campo_nombre = ft.TextField(
            label="Nombre de la oferta",
            value=oferta.NOMBRE,
            prefix_icon=ft.icons.Icons.EDIT,
            width=400
        )
        
        # Campo descuento
        campo_descuento = ft.Slider(
            min=5,
            max=90,
            divisions=17,
            label="{value}%",
            value=float(oferta.DESCUENTO_PORCENTAJE),
            width=400
        )
        
        texto_descuento = ft.Text(f"Descuento: {oferta.DESCUENTO_PORCENTAJE}%", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700)
        
        def on_descuento_change(e):
            texto_descuento.value = f"Descuento: {int(e.control.value)}%"
            self._pagina.update()
        
        campo_descuento.on_change = on_descuento_change
        
        # Textos para mostrar fechas seleccionadas
        texto_fecha_inicio = ft.Text(
            f"📅 Inicio: {fecha_inicio_val.strftime('%d/%m/%Y %H:%M')}",
            size=14,
            weight=ft.FontWeight.W_500
        )
        
        texto_fecha_fin = ft.Text(
            f"📅 Fin: {fecha_fin_val.strftime('%d/%m/%Y %H:%M') if fecha_fin_val else 'Sin límite'}",
            size=14,
            weight=ft.FontWeight.W_500
        )
        
        checkbox_sin_limite = ft.Checkbox(
            label="Sin fecha de expiración",
            value=(fecha_fin_val is None)
        )
        
        # Contenedor para fecha fin (visible/invisible según checkbox)
        container_fecha_fin = ft.Column([
            texto_fecha_fin,
            ft.ElevatedButton(
                "Cambiar fecha fin",
                icon=ft.icons.Icons.CALENDAR_MONTH,
                on_click=lambda e: abrir_datepicker_fin(e),
                bgcolor=ft.Colors.ORANGE_100,
                color=ft.Colors.ORANGE_900
            )
        ], visible=(fecha_fin_val is not None), spacing=5)
        
        def on_sin_limite_change(e):
            nonlocal fecha_fin_val
            container_fecha_fin.visible = not checkbox_sin_limite.value
            if checkbox_sin_limite.value:
                fecha_fin_val = None
                texto_fecha_fin.value = "📅 Fin: Sin límite"
            self._pagina.update()
        
        checkbox_sin_limite.on_change = on_sin_limite_change
        
        # Funciones para DatePickers
        def on_fecha_inicio_change(e):
            nonlocal fecha_inicio_val
            if e.control.value:
                # Mantener la hora actual
                hora_actual = fecha_inicio_val.hour if fecha_inicio_val else 0
                minuto_actual = fecha_inicio_val.minute if fecha_inicio_val else 0
                fecha_inicio_val = datetime.combine(e.control.value, datetime.min.time().replace(hour=hora_actual, minute=minuto_actual))
                texto_fecha_inicio.value = f"📅 Inicio: {fecha_inicio_val.strftime('%d/%m/%Y %H:%M')}"
                self._pagina.update()
        
        def on_fecha_fin_change(e):
            nonlocal fecha_fin_val
            if e.control.value:
                hora_actual = fecha_fin_val.hour if fecha_fin_val else 23
                minuto_actual = fecha_fin_val.minute if fecha_fin_val else 59
                fecha_fin_val = datetime.combine(e.control.value, datetime.min.time().replace(hour=hora_actual, minute=minuto_actual))
                texto_fecha_fin.value = f"📅 Fin: {fecha_fin_val.strftime('%d/%m/%Y %H:%M')}"
                self._pagina.update()
        
        def abrir_datepicker_inicio(e):
            dp = ft.DatePicker(
                value=fecha_inicio_val,
                first_date=datetime(2020, 1, 1),
                last_date=datetime(2030, 12, 31),
                on_change=on_fecha_inicio_change
            )
            self._pagina.overlay.append(dp)
            dp.open = True
            self._pagina.update()
        
        def abrir_datepicker_fin(e):
            dp = ft.DatePicker(
                value=fecha_fin_val if fecha_fin_val else datetime.now(),
                first_date=fecha_inicio_val if fecha_inicio_val else datetime.now(),
                last_date=datetime(2030, 12, 31),
                on_change=on_fecha_fin_change
            )
            self._pagina.overlay.append(dp)
            dp.open = True
            self._pagina.update()
        
        def guardar_cambios():
            if not campo_nombre.value:
                self._mostrar_error("El nombre es obligatorio")
                return
            
            try:
                if not checkbox_sin_limite.value and fecha_fin_val and fecha_fin_val <= fecha_inicio_val:
                    self._mostrar_error("La fecha de fin debe ser posterior al inicio")
                    return
                
                with OBTENER_SESION() as sesion:
                    oferta_db = sesion.query(MODELO_OFERTA).filter_by(ID=oferta.ID).first()
                    if oferta_db:
                        oferta_db.PRODUCTO_ID = int(dropdown_producto.value)
                        oferta_db.TIPO = dropdown_tipo.value
                        oferta_db.NOMBRE = campo_nombre.value
                        oferta_db.DESCUENTO_PORCENTAJE = int(campo_descuento.value)
                        oferta_db.FECHA_INICIO = fecha_inicio_val
                        oferta_db.FECHA_FIN = None if checkbox_sin_limite.value else fecha_fin_val
                        
                        sesion.commit()
                        
                        notify({
                            "tipo": "oferta_actualizada",
                            "oferta_id": oferta_db.ID
                        })
                
                self._cerrar_overlays()
                self._cargar_ofertas()
                self._mostrar_exito(f"✅ Oferta '{campo_nombre.value}' actualizada exitosamente")
                
            except Exception as e:
                self._mostrar_error(f"Error al actualizar oferta: {str(e)}")
        
        contenido = ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.icons.Icons.EDIT, size=32, color=ft.Colors.ORANGE_700),
                    ft.Text("Editar Oferta", size=22, weight=ft.FontWeight.BOLD)
                ], spacing=12),
                padding=15,
                bgcolor=ft.Colors.ORANGE_50,
                border_radius=10,
            ),
            dropdown_producto,
            dropdown_tipo,
            campo_nombre,
            ft.Divider(),
            texto_descuento,
            campo_descuento,
            ft.Divider(),
            ft.Text("📆 Fechas de la oferta", weight=ft.FontWeight.BOLD, size=16),
            ft.Container(
                content=ft.Column([
                    texto_fecha_inicio,
                    ft.ElevatedButton(
                        "Cambiar fecha inicio",
                        icon=ft.icons.Icons.CALENDAR_MONTH,
                        on_click=abrir_datepicker_inicio,
                        bgcolor=ft.Colors.BLUE_100,
                        color=ft.Colors.BLUE_900
                    )
                ], spacing=5),
                padding=10,
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=8
            ),
            checkbox_sin_limite,
            ft.Container(
                content=container_fecha_fin,
                padding=10,
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=8,
                visible=(fecha_fin_val is not None)
            ),
        ], spacing=12, width=450, height=580, scroll=ft.ScrollMode.AUTO)
        
        self._overlay_editar = ft.AlertDialog(
            title=ft.Text("Editar Oferta"),
            content=contenido,
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self._cerrar_overlays()),
                ft.ElevatedButton(
                    "💾 Guardar Cambios",
                    on_click=lambda e: guardar_cambios(),
                    bgcolor=ft.Colors.ORANGE_700,
                    color=ft.Colors.WHITE
                )
            ]
        )
        
        self._pagina.overlay.append(self._overlay_editar)
        self._overlay_editar.open = True
        self._pagina.update()
    
    def _confirmar_eliminar(self, oferta):
        """Confirma eliminación lógica de oferta (soft delete)"""
        def eliminar():
            try:
                with OBTENER_SESION() as sesion:
                    oferta_db = sesion.query(MODELO_OFERTA).filter_by(ID=oferta.ID).first()
                    if oferta_db:
                        # Soft delete - solo marcar como eliminado
                        oferta_db.ELIMINADO = True
                        oferta_db.ACTIVA = False  # También desactivar
                        sesion.commit()
                        
                        notify({
                            "tipo": "oferta_actualizada",
                            "oferta_id": oferta.ID
                        })
                
                self._cerrar_overlays()
                self._cargar_ofertas()
                self._mostrar_exito(f"🗑️ Oferta '{oferta.NOMBRE}' eliminada exitosamente")
            except Exception as e:
                self._mostrar_error(f"Error al eliminar: {str(e)}")
        
        contenido = ft.Container(
            content=ft.Column([
                ft.Icon(ft.icons.Icons.DELETE_FOREVER, size=80, color=ft.Colors.RED_700),
                ft.Text(
                    f"¿Eliminar la oferta?",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Text(
                    oferta.NOMBRE,
                    size=16,
                    color=ft.Colors.GREY_700,
                    text_align=ft.TextAlign.CENTER,
                    italic=True
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.icons.Icons.INFO_OUTLINE, size=18, color=ft.Colors.BLUE_700),
                            ft.Text(
                                "Esta oferta será marcada como eliminada",
                                size=13,
                                color=ft.Colors.GREY_600
                            )
                        ], spacing=8),
                        ft.Text(
                            "No aparecerá en el sistema pero se mantendrá en el historial",
                            size=12,
                            color=ft.Colors.GREY_500
                        )
                    ], spacing=5),
                    padding=ft.Padding(15, 10, 15, 10),
                    bgcolor=ft.Colors.BLUE_50,
                    border_radius=8,
                    margin=ft.Margin(0, 10, 0, 0)
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
            padding=ft.Padding(20, 20, 20, 20)
        )
        
        overlay = ft.AlertDialog(
            content=contenido,
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e: self._cerrar_overlays()
                ),
                ft.ElevatedButton(
                    "🗑️ Sí, Eliminar",
                    on_click=lambda e: eliminar(),
                    bgcolor=ft.Colors.RED_700,
                    color=ft.Colors.WHITE
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        self._pagina.overlay.append(overlay)
        overlay.open = True
        self._pagina.update()
    
    def _toggle_estado(self, oferta):
        """Activa/desactiva oferta"""
        with OBTENER_SESION() as sesion:
            oferta_db = sesion.query(MODELO_OFERTA).filter_by(ID=oferta.ID).first()
            if oferta_db:
                oferta_db.ACTIVA = not oferta_db.ACTIVA
                sesion.commit()
                
                notify({
                    "tipo": "oferta_actualizada",
                    "oferta_id": oferta_db.ID
                })
        
        self._cargar_ofertas()
        self._mostrar_exito(f"✅ Oferta {'activada' if not oferta.ACTIVA else 'desactivada'}")
    
    def _iniciar_timer_expiracion(self):
        """Inicia timer de verificación"""
        def check_expiracion():
            self._timer_running = True
            while self._timer_running:
                try:
                    ahora = datetime.now()
                    with OBTENER_SESION() as sesion:
                        ofertas_expiradas = sesion.query(MODELO_OFERTA).filter(
                            MODELO_OFERTA.ACTIVA == True,
                            MODELO_OFERTA.FECHA_FIN != None,
                            MODELO_OFERTA.FECHA_FIN <= ahora
                        ).all()
                        
                        for oferta in ofertas_expiradas:
                            oferta.ACTIVA = False
                            sesion.commit()
                            
                            notify({
                                "tipo": "oferta_expirada",
                                "oferta_id": oferta.ID,
                                "nombre": oferta.NOMBRE,
                                "mensaje": f"⏰ La oferta '{oferta.NOMBRE}' ha expirado"
                            })
                    
                    time.sleep(30)
                except Exception as e:
                    print(f"Error en timer: {e}")
                    time.sleep(30)
        
        self._timer_thread = threading.Thread(target=check_expiracion, daemon=True)
        self._timer_thread.start()
    
    def _on_oferta_expirada(self, payload: dict):
        """Handler para oferta expirada"""
        self._cargar_ofertas()
        mensaje = payload.get("mensaje", "Una oferta ha expirado")
        self._pagina.snack_bar = ft.SnackBar(
            content=ft.Row([
                ft.Icon(ft.icons.Icons.WARNING, color=ft.Colors.WHITE),
                ft.Text(mensaje, color=ft.Colors.WHITE)
            ]),
            bgcolor=ft.Colors.ORANGE_700
        )
        self._pagina.snack_bar.open = True
        self._pagina.update()
    
    def _on_oferta_actualizada(self, payload: dict):
        """Handler para oferta actualizada"""
        self._cargar_ofertas()
    
    def _cerrar_overlays(self):
        """Cierra todos los overlays/dialogs"""
        # Cerrar overlays estableciendo open=False
        if self._overlay_crear:
            self._overlay_crear.open = False
        if self._overlay_editar:
            self._overlay_editar.open = False
        if self._overlay_configurar_sucursales:
            self._overlay_configurar_sucursales.open = False
        # Cerrar todos los dialogs en overlay
        for overlay in self._pagina.overlay:
            if hasattr(overlay, 'open'):
                overlay.open = False
        self._pagina.update()
    
    def _mostrar_exito(self, mensaje: str):
        """Mensaje de éxito"""
        self._pagina.snack_bar = ft.SnackBar(
            content=ft.Text(mensaje, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.GREEN_700
        )
        self._pagina.snack_bar.open = True
        self._pagina.update()
    
    def _mostrar_error(self, mensaje: str):
        """Mensaje de error"""
        self._pagina.snack_bar = ft.SnackBar(
            content=ft.Text(mensaje, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.RED_700
        )
        self._pagina.snack_bar.open = True
        self._pagina.update()
    
    def _mostrar_advertencia(self, mensaje: str):
        """Mensaje de advertencia"""
        self._pagina.snack_bar = ft.SnackBar(
            content=ft.Text(mensaje, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.ORANGE_700
        )
        self._pagina.snack_bar.open = True
        self._pagina.update()
    
    def _volver_dashboard(self):
        """Vuelve al dashboard"""
        self._timer_running = False
        dispatcher.unregister("oferta_expirada", self._on_oferta_expirada)
        dispatcher.unregister("oferta_actualizada", self._on_oferta_actualizada)
        
        from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
        self._pagina.controls.clear()
        self._pagina.add(PaginaAdmin(self._pagina, self._usuario))
        self._pagina.update()
    
    def _cerrar_sesion(self):
        """Cierra la sesión"""
        self._timer_running = False
        dispatcher.unregister("oferta_expirada", self._on_oferta_expirada)
        dispatcher.unregister("oferta_actualizada", self._on_oferta_actualizada)
        
        from features.autenticacion.presentation.pages.PaginaLogin import PaginaLogin
        self._pagina.controls.clear()
        self._pagina.add(PaginaLogin(self._pagina))
        self._pagina.update()
