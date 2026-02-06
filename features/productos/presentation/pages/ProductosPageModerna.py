"""
Página moderna para gestión de productos con CRUD completo
Similar a UsuariosPageModerna pero adaptado para productos
"""
import flet as ft
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import joinedload
from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION,
    MODELO_PRODUCTO,
    MODELO_SUCURSAL,
    MODELO_EXTRA,
    MODELO_AUDITORIA,
)
from features.admin.presentation.widgets.LayoutBase import LayoutBase


class ProductosPageModerna(LayoutBase):
    """
    Página moderna para gestión de productos con CRUD completo.
    
    Características:
    - Filtros por disponibilidad
    - Búsqueda por nombre/descripción
    - CRUD completo: crear, editar, eliminar (lógico), activar/desactivar
    - Gestión de sucursales asignadas
    - Gestión de extras asociados
    - Vista de detalles en overlay
    - Logs de auditoría
    - Diseño moderno con cards
    """

    def __init__(self, PAGINA: ft.Page, USUARIO):
        self._FILTRO_DISPONIBILIDAD = "TODOS"  # TODOS, DISPONIBLES, NO_DISPONIBLES
        self._TEXTO_BUSQUEDA = ""
        self._productos_cache = []
        
        # Inicializar LayoutBase con callbacks
        super().__init__(
            pagina=PAGINA,
            usuario=USUARIO,
            titulo_vista="🍕 Gestión de Productos",
            mostrar_boton_volver=True,
            index_navegacion=2,
            on_volver_dashboard=self._ir_dashboard,
            on_cerrar_sesion=self._cerrar_sesion
        )
        
        # Construir interfaz y cargar datos
        contenido = self._construir_interfaz()
        
        # Llamar a construir() del LayoutBase con el contenido
        self.construir(contenido)
        
        # Cargar productos
        self._cargar_productos()
    
    def _ir_dashboard(self):
        """Navega de vuelta al dashboard"""
        from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
        self._pagina.controls.clear()
        self._pagina.add(PaginaAdmin(self._pagina, self._usuario))
        self._pagina.update()
    
    def _cerrar_sesion(self):
        """Cierra la sesión del usuario"""
        from features.autenticacion.presentation.pages.login_page import LoginPage
        self._pagina.controls.clear()
        self._pagina.add(LoginPage(self._pagina))
        self._pagina.update()

    def _construir_interfaz(self):
        """Construye la interfaz moderna con filtros, búsqueda y tabla de productos"""
        
        # === SECCIÓN DE FILTROS ===
        self._contenedor_filtros = ft.Row(
            controls=[
                ft.Text("Disponibilidad:", size=14, weight=ft.FontWeight.W_500),
            ],
            spacing=8,
            wrap=True,
        )
        self._actualizar_chips_filtro()

        # === BARRA DE BÚSQUEDA Y ACCIONES ===
        self._campo_busqueda = ft.TextField(
            label="Buscar productos...",
            hint_text="Nombre, descripción...",
            prefix_icon=ft.icons.Icons.SEARCH,
            width=400,
            on_change=self._on_buscar,
            border_color=ft.Colors.BLUE_200,
        )

        boton_crear = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.icons.Icons.ADD, size=20),
                ft.Text("Crear Producto", size=14),
            ], spacing=8, tight=True),
            on_click=self._mostrar_overlay_crear,
            bgcolor=ft.Colors.GREEN_700,
            color=ft.Colors.WHITE,
        )

        boton_refrescar = ft.IconButton(
            icon=ft.icons.Icons.REFRESH,
            tooltip="Refrescar lista",
            on_click=lambda _: self._cargar_productos(),
            icon_color=ft.Colors.BLUE_700,
        )

        barra_acciones = ft.Row(
            controls=[
                self._campo_busqueda,
                ft.Container(expand=True),
                boton_crear,
                boton_refrescar,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # === TABLA DE PRODUCTOS ===
        self._tabla_productos = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD, size=13)),
                ft.DataColumn(ft.Text("Nombre", weight=ft.FontWeight.BOLD, size=13)),
                ft.DataColumn(ft.Text("Descripción", weight=ft.FontWeight.BOLD, size=13)),
                ft.DataColumn(ft.Text("Precio", weight=ft.FontWeight.BOLD, size=13)),
                ft.DataColumn(ft.Text("Disponible", weight=ft.FontWeight.BOLD, size=13)),
                ft.DataColumn(ft.Text("Sucursales", weight=ft.FontWeight.BOLD, size=13)),
                ft.DataColumn(ft.Text("Extras", weight=ft.FontWeight.BOLD, size=13)),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD, size=13)),
            ],
            rows=[],
            border=ft.Border.all(1, ft.Colors.GREY_300),
            border_radius=8,
            horizontal_lines=ft.BorderSide(1, ft.Colors.GREY_200),
            vertical_lines=ft.BorderSide(1, ft.Colors.GREY_200),
            heading_row_color=ft.Colors.GREY_100,
            heading_row_height=56,
            data_row_min_height=70,
            data_row_max_height=100,
            column_spacing=20,
        )

        contenedor_tabla = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[self._tabla_productos],
                        scroll=ft.ScrollMode.ALWAYS,
                    )
                ],
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            border=ft.Border.all(1, ft.Colors.GREY_300),
            border_radius=8,
            padding=10,
            expand=True,
        )

        # === ESTRUCTURA FINAL ===
        return ft.Container(
            content=ft.Column([
                # Header con icono
                ft.Row([
                    ft.Icon(ft.icons.Icons.INVENTORY_2, size=32, color=ft.Colors.ORANGE_700),
                    ft.Text("Gestión de Productos", size=28, weight=ft.FontWeight.BOLD),
                ], spacing=12),
                ft.Divider(height=20, color=ft.Colors.GREY_300),
                
                # Filtros
                ft.Container(
                    content=self._contenedor_filtros,
                    padding=ft.Padding.only(bottom=10),
                ),
                
                # Barra de búsqueda y acciones
                barra_acciones,
                
                ft.Divider(height=10, color=ft.Colors.GREY_200),
                
                # Tabla de productos
                contenedor_tabla,
            ], spacing=10),
            padding=20,
            expand=True,
        )

    def _actualizar_chips_filtro(self):
        """Actualiza los chips de filtro según el estado actual"""
        # Limpiar chips existentes (mantener solo el texto)
        self._contenedor_filtros.controls = [
            ft.Text("Disponibilidad:", size=14, weight=ft.FontWeight.W_500),
            self._crear_chip_filtro("TODOS", "Todos", ft.icons.Icons.SELECT_ALL, ft.Colors.BLUE),
            self._crear_chip_filtro("DISPONIBLES", "Disponibles", ft.icons.Icons.CHECK_CIRCLE, ft.Colors.GREEN),
            self._crear_chip_filtro("NO_DISPONIBLES", "No disponibles", ft.icons.Icons.CANCEL, ft.Colors.RED),
        ]

    def _crear_chip_filtro(self, valor: str, texto: str, icono, color) -> ft.Container:
        """Crea un chip de filtro clicable"""
        es_activo = self._FILTRO_DISPONIBILIDAD == valor
        
        return ft.Container(
            content=ft.Row([
                ft.Icon(icono, size=18, color=ft.Colors.WHITE if es_activo else color),
                ft.Text(texto, size=13, color=ft.Colors.WHITE if es_activo else color),
            ], spacing=6, tight=True),
            bgcolor=color if es_activo else ft.Colors.TRANSPARENT,
            border=ft.Border.all(2, color),
            border_radius=16,
            padding=ft.Padding(left=12, right=12, top=6, bottom=6),
            on_click=lambda _, v=valor: self._cambiar_filtro_disponibilidad(v),
            ink=True,
        )

    def _cambiar_filtro_disponibilidad(self, nuevo_filtro: str):
        """Cambia el filtro de disponibilidad y aplica filtros"""
        self._FILTRO_DISPONIBILIDAD = nuevo_filtro
        self._actualizar_chips_filtro()
        self._aplicar_filtros()

    def _on_buscar(self, e):
        """Maneja el cambio en el campo de búsqueda"""
        self._TEXTO_BUSQUEDA = e.control.value.lower()
        self._aplicar_filtros()

    def _cargar_productos(self):
        """Carga los productos desde la base de datos con eager loading"""
        try:
            with OBTENER_SESION() as sesion:
                # Eager loading para evitar DetachedInstanceError
                query = sesion.query(MODELO_PRODUCTO).options(
                    joinedload(MODELO_PRODUCTO.SUCURSALES),
                    joinedload(MODELO_PRODUCTO.EXTRAS)
                )
                
                productos = query.all()
                
                # Extraer datos mientras estamos en la sesión
                self._productos_cache = []
                for prod in productos:
                    self._productos_cache.append({
                        "ID": prod.ID,
                        "NOMBRE": prod.NOMBRE,
                        "DESCRIPCION": prod.DESCRIPCION or "",
                        "PRECIO": prod.PRECIO,
                        "IMAGEN": prod.IMAGEN or "",
                        "DISPONIBLE": prod.DISPONIBLE,
                        "FECHA_CREACION": prod.FECHA_CREACION,
                        "SUCURSALES": [{"ID": s.ID, "NOMBRE": s.NOMBRE} for s in prod.SUCURSALES],
                        "EXTRAS": [{"ID": e.ID, "NOMBRE": e.NOMBRE, "PRECIO": e.PRECIO_ADICIONAL} for e in prod.EXTRAS],
                    })
            
            self._aplicar_filtros()
            
        except Exception as ex:
            self._mostrar_snackbar(f"❌ Error al cargar productos: {str(ex)}", ft.Colors.RED)

    def _aplicar_filtros(self):
        """Aplica los filtros seleccionados y actualiza la tabla"""
        productos_filtrados = self._productos_cache.copy()
        
        # Filtro por disponibilidad
        if self._FILTRO_DISPONIBILIDAD == "DISPONIBLES":
            productos_filtrados = [p for p in productos_filtrados if p["DISPONIBLE"]]
        elif self._FILTRO_DISPONIBILIDAD == "NO_DISPONIBLES":
            productos_filtrados = [p for p in productos_filtrados if not p["DISPONIBLE"]]
        
        # Filtro por búsqueda de texto
        if self._TEXTO_BUSQUEDA:
            productos_filtrados = [
                p for p in productos_filtrados
                if self._TEXTO_BUSQUEDA in p["NOMBRE"].lower() or
                   self._TEXTO_BUSQUEDA in p["DESCRIPCION"].lower()
            ]
        
        self._actualizar_tabla(productos_filtrados)

    def _actualizar_tabla(self, productos: List[dict]):
        """Actualiza las filas de la tabla con los productos filtrados"""
        self._tabla_productos.rows.clear()
        
        for prod in productos:
            # Estado disponibilidad
            icono_estado = ft.Icon(
                ft.icons.Icons.CHECK_CIRCLE if prod["DISPONIBLE"] else ft.icons.Icons.CANCEL,
                color=ft.Colors.GREEN if prod["DISPONIBLE"] else ft.Colors.RED,
                size=20,
            )
            
            # Contador de sucursales
            num_sucursales = len(prod["SUCURSALES"])
            texto_sucursales = ft.Text(
                f"{num_sucursales} sucursales",
                size=12,
                color=ft.Colors.BLUE_700 if num_sucursales > 0 else ft.Colors.GREY,
            )
            
            # Contador de extras
            num_extras = len(prod["EXTRAS"])
            texto_extras = ft.Text(
                f"{num_extras} extras",
                size=12,
                color=ft.Colors.PURPLE_700 if num_extras > 0 else ft.Colors.GREY,
            )
            
            # Botones de acción
            acciones = ft.Row([
                ft.IconButton(
                    icon=ft.icons.Icons.VISIBILITY,
                    tooltip="Ver detalles",
                    icon_color=ft.Colors.BLUE,
                    on_click=lambda _, p=prod: self._mostrar_overlay_detalle(p),
                ),
                ft.IconButton(
                    icon=ft.icons.Icons.EDIT,
                    tooltip="Editar",
                    icon_color=ft.Colors.ORANGE,
                    on_click=lambda _, p=prod: self._mostrar_overlay_editar(p),
                ),
                ft.IconButton(
                    icon=ft.icons.Icons.LOCAL_OFFER,
                    tooltip="Crear oferta",
                    icon_color=ft.Colors.GREEN_700,
                    on_click=lambda _, p=prod: self._crear_oferta_producto(p),
                ),
                ft.IconButton(
                    icon=ft.icons.Icons.STORE if prod["DISPONIBLE"] else ft.icons.Icons.STORE_MALL_DIRECTORY,
                    tooltip="Gestionar sucursales",
                    icon_color=ft.Colors.BLUE_700,
                    on_click=lambda _, p=prod: self._gestionar_sucursales(p),
                ),
                ft.IconButton(
                    icon=ft.icons.Icons.ADD_CIRCLE_OUTLINE,
                    tooltip="Gestionar extras",
                    icon_color=ft.Colors.PURPLE_700,
                    on_click=lambda _, p=prod: self._gestionar_extras(p),
                ),
                ft.IconButton(
                    icon=ft.icons.Icons.TOGGLE_ON if prod["DISPONIBLE"] else ft.icons.Icons.TOGGLE_OFF,
                    tooltip="Cambiar disponibilidad",
                    icon_color=ft.Colors.GREEN if prod["DISPONIBLE"] else ft.Colors.GREY,
                    on_click=lambda _, p=prod: self._cambiar_disponibilidad(p),
                ),
                ft.IconButton(
                    icon=ft.icons.Icons.HISTORY,
                    tooltip="Ver logs",
                    icon_color=ft.Colors.INDIGO,
                    on_click=lambda _, p=prod: self._mostrar_logs_auditoria(p),
                ),
            ], spacing=0, tight=True)
            
            self._tabla_productos.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(prod["ID"]), size=12)),
                    ft.DataCell(ft.Text(prod["NOMBRE"], size=13, weight=ft.FontWeight.W_500)),
                    ft.DataCell(ft.Container(
                        content=ft.Text(
                            prod["DESCRIPCION"][:50] + "..." if len(prod["DESCRIPCION"]) > 50 else prod["DESCRIPCION"],
                            size=12,
                            color=ft.Colors.GREY_700,
                        ),
                        width=200,
                    )),
                    ft.DataCell(ft.Text(f"${prod['PRECIO']:,}", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700)),
                    ft.DataCell(icono_estado),
                    ft.DataCell(texto_sucursales),
                    ft.DataCell(texto_extras),
                    ft.DataCell(acciones),
                ])
            )
        
        self._pagina.update()

    # ========== OVERLAYS DE CRUD ==========

    def _mostrar_overlay_crear(self, e):
        """Muestra overlay para crear un nuevo producto"""
        
        # Campos del formulario
        campo_nombre = ft.TextField(
            label="Nombre del producto *",
            hint_text="Ej: Pizza Margarita",
            prefix_icon=ft.icons.Icons.INVENTORY_2,
            autofocus=True,
        )
        
        campo_descripcion = ft.TextField(
            label="Descripción",
            hint_text="Descripción breve del producto",
            prefix_icon=ft.icons.Icons.DESCRIPTION,
            multiline=True,
            min_lines=2,
            max_lines=4,
        )
        
        campo_precio = ft.TextField(
            label="Precio *",
            hint_text="0",
            prefix_icon=ft.icons.Icons.ATTACH_MONEY,
            keyboard_type=ft.KeyboardType.NUMBER,
            value="0",
        )
        
        campo_imagen = ft.TextField(
            label="URL de imagen",
            hint_text="https://ejemplo.com/imagen.jpg",
            prefix_icon=ft.icons.Icons.IMAGE,
        )
        
        switch_disponible = ft.Switch(
            label="Disponible para venta",
            value=True,
        )
        
        def guardar_producto(e):
            """Guarda el nuevo producto en la BD"""
            nombre = campo_nombre.value.strip()
            descripcion = campo_descripcion.value.strip()
            precio_str = campo_precio.value.strip()
            imagen = campo_imagen.value.strip()
            disponible = switch_disponible.value
            
            # Validaciones
            if not nombre:
                self._mostrar_snackbar("❌ El nombre es obligatorio", ft.Colors.RED)
                return
            
            try:
                precio = int(precio_str)
                if precio < 0:
                    raise ValueError("Precio negativo")
            except:
                self._mostrar_snackbar("❌ El precio debe ser un número válido", ft.Colors.RED)
                return
            
            try:
                with OBTENER_SESION() as sesion:
                    # Verificar si ya existe
                    existe = sesion.query(MODELO_PRODUCTO).filter_by(NOMBRE=nombre).first()
                    if existe:
                        self._mostrar_snackbar(f"❌ Ya existe un producto con el nombre '{nombre}'", ft.Colors.RED)
                        return
                    
                    # Crear producto
                    nuevo_producto = MODELO_PRODUCTO(
                        NOMBRE=nombre,
                        DESCRIPCION=descripcion if descripcion else None,
                        PRECIO=precio,
                        IMAGEN=imagen if imagen else None,
                        DISPONIBLE=disponible,
                    )
                    
                    sesion.add(nuevo_producto)
                    sesion.flush()
                    
                    # Registrar auditoría
                    auditoria = MODELO_AUDITORIA(
                        USUARIO_ID=self._usuario.ID,
                        ACCION=f"PRODUCTO_CREADO: {nombre}",
                        ENTIDAD="PRODUCTO",
                        ENTIDAD_ID=nuevo_producto.ID,
                        DETALLE=f"Precio: ${precio:,}, Disponible: {'Sí' if disponible else 'No'}",
                    )
                    sesion.add(auditoria)
                    sesion.commit()
                    
                    overlay.open = False
                    self._pagina.update()
                    self._cargar_productos()
                    
                    self._mostrar_snackbar(f"✅ Producto '{nombre}' creado exitosamente", ft.Colors.GREEN)
                    
            except Exception as ex:
                self._mostrar_snackbar(f"❌ Error al crear producto: {str(ex)}", ft.Colors.RED)
        
        # Crear overlay con patrón correcto
        overlay = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.icons.Icons.ADD_CIRCLE, color=ft.Colors.GREEN_700, size=28),
                ft.Text("Crear Nuevo Producto", size=20, weight=ft.FontWeight.BOLD)
            ], spacing=12),
            content=ft.Container(
                content=ft.Column([
                    campo_nombre,
                    campo_descripcion,
                    campo_precio,
                    campo_imagen,
                    switch_disponible,
                ], tight=True, spacing=16, scroll=ft.ScrollMode.ADAPTIVE),
                width=500,
                height=400
            ),
            actions=[
                ft.TextButton(
                    content=ft.Row([
                        ft.Icon(ft.icons.Icons.CLOSE, size=18),
                        ft.Text("Cancelar")
                    ], spacing=6),
                    on_click=lambda e: setattr(overlay, 'open', False) or self._pagina.update()
                ),
                ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.icons.Icons.SAVE, size=18),
                        ft.Text("Crear Producto", weight=ft.FontWeight.W_600)
                    ], spacing=6),
                    on_click=guardar_producto,
                    bgcolor=ft.Colors.GREEN_700,
                    color=ft.Colors.WHITE,
                ),
            ]
        )
        
        self._pagina.overlay.append(overlay)
        overlay.open = True
        self._pagina.update()

    def _mostrar_overlay_editar(self, producto: dict):
        """Muestra overlay para editar un producto existente"""
        
        # Campos prellenados
        campo_nombre = ft.TextField(
            label="Nombre del producto *",
            prefix_icon=ft.icons.Icons.INVENTORY_2,
            value=producto["NOMBRE"],
            autofocus=True,
        )
        
        campo_descripcion = ft.TextField(
            label="Descripción",
            prefix_icon=ft.icons.Icons.DESCRIPTION,
            value=producto["DESCRIPCION"],
            multiline=True,
            min_lines=2,
            max_lines=4,
        )
        
        campo_precio = ft.TextField(
            label="Precio *",
            prefix_icon=ft.icons.Icons.ATTACH_MONEY,
            keyboard_type=ft.KeyboardType.NUMBER,
            value=str(producto["PRECIO"]),
        )
        
        campo_imagen = ft.TextField(
            label="URL de imagen",
            prefix_icon=ft.icons.Icons.IMAGE,
            value=producto["IMAGEN"],
        )
        
        switch_disponible = ft.Switch(
            label="Disponible para venta",
            value=producto["DISPONIBLE"],
        )
        
        def guardar_cambios(e):
            """Actualiza el producto en la BD"""
            nombre = campo_nombre.value.strip()
            descripcion = campo_descripcion.value.strip()
            precio_str = campo_precio.value.strip()
            imagen = campo_imagen.value.strip()
            disponible = switch_disponible.value
            
            if not nombre:
                self._mostrar_snackbar("❌ El nombre es obligatorio", ft.Colors.RED)
                return
            
            try:
                precio = int(precio_str)
                if precio < 0:
                    raise ValueError("Precio negativo")
            except:
                self._mostrar_snackbar("❌ El precio debe ser un número válido", ft.Colors.RED)
                return
            
            try:
                with OBTENER_SESION() as sesion:
                    prod_db = sesion.query(MODELO_PRODUCTO).filter_by(ID=producto["ID"]).first()
                    if not prod_db:
                        self._mostrar_snackbar("❌ Producto no encontrado", ft.Colors.RED)
                        return
                    
                    # Verificar nombre único (si cambió)
                    if nombre != producto["NOMBRE"]:
                        existe = sesion.query(MODELO_PRODUCTO).filter_by(NOMBRE=nombre).first()
                        if existe:
                            self._mostrar_snackbar(f"❌ Ya existe un producto con el nombre '{nombre}'", ft.Colors.RED)
                            return
                    
                    # Actualizar campos
                    prod_db.NOMBRE = nombre
                    prod_db.DESCRIPCION = descripcion if descripcion else None
                    prod_db.PRECIO = precio
                    prod_db.IMAGEN = imagen if imagen else None
                    prod_db.DISPONIBLE = disponible
                    
                    # Auditoría
                    auditoria = MODELO_AUDITORIA(
                        USUARIO_ID=self._usuario.ID,
                        ACCION=f"PRODUCTO_EDITADO: {nombre}",
                        ENTIDAD="PRODUCTO",
                        ENTIDAD_ID=producto["ID"],
                        DETALLE=f"Precio: ${precio:,}, Disponible: {'Sí' if disponible else 'No'}",
                    )
                    sesion.add(auditoria)
                    sesion.commit()
                    
                    overlay.open = False
                    self._pagina.update()
                    self._cargar_productos()
                    
                    self._mostrar_snackbar(f"✅ Producto '{nombre}' actualizado", ft.Colors.GREEN)
                    
            except Exception as ex:
                self._mostrar_snackbar(f"❌ Error al actualizar: {str(ex)}", ft.Colors.RED)
        
        overlay = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.icons.Icons.EDIT, color=ft.Colors.ORANGE_700, size=28),
                ft.Text(f"Editar: {producto['NOMBRE']}", size=20, weight=ft.FontWeight.BOLD)
            ], spacing=12),
            content=ft.Container(
                content=ft.Column([
                    campo_nombre,
                    campo_descripcion,
                    campo_precio,
                    campo_imagen,
                    switch_disponible,
                ], tight=True, spacing=16, scroll=ft.ScrollMode.ADAPTIVE),
                width=500,
                height=400
            ),
            actions=[
                ft.TextButton(
                    content=ft.Row([
                        ft.Icon(ft.icons.Icons.CLOSE, size=18),
                        ft.Text("Cancelar")
                    ], spacing=6),
                    on_click=lambda e: setattr(overlay, 'open', False) or self._pagina.update()
                ),
                ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.icons.Icons.SAVE, size=18),
                        ft.Text("Guardar Cambios", weight=ft.FontWeight.W_600)
                    ], spacing=6),
                    on_click=guardar_cambios,
                    bgcolor=ft.Colors.ORANGE_700,
                    color=ft.Colors.WHITE,
                ),
            ]
        )
        
        self._pagina.overlay.append(overlay)
        overlay.open = True
        self._pagina.update()

    def _mostrar_overlay_detalle(self, producto: dict):
        """Muestra overlay con todos los detalles del producto"""
        
        # Tabla de detalles
        detalles = [
            ("ID", str(producto["ID"])),
            ("Nombre", producto["NOMBRE"]),
            ("Descripción", producto["DESCRIPCION"] or "Sin descripción"),
            ("Precio", f"${producto['PRECIO']:,}"),
            ("Disponible", "✅ Sí" if producto["DISPONIBLE"] else "❌ No"),
            ("Imagen URL", producto["IMAGEN"] or "Sin imagen"),
            ("Fecha Creación", producto["FECHA_CREACION"].strftime("%d/%m/%Y %H:%M")),
            ("Sucursales", ", ".join([s["NOMBRE"] for s in producto["SUCURSALES"]]) if producto["SUCURSALES"] else "Ninguna"),
            ("Extras", ", ".join([f"{e['NOMBRE']} (+${e['PRECIO']:,})" for e in producto["EXTRAS"]]) if producto["EXTRAS"] else "Ninguno"),
        ]
        
        tabla_detalles = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Campo", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Valor", weight=ft.FontWeight.BOLD)),
            ],
            rows=[
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(campo, size=13, weight=ft.FontWeight.W_500)),
                    ft.DataCell(ft.Text(valor, size=13)),
                ])
                for campo, valor in detalles
            ],
            border=ft.Border.all(1, ft.Colors.GREY_300),
            border_radius=8,
            horizontal_lines=ft.BorderSide(1, ft.Colors.GREY_200),
        )
        
        overlay = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.icons.Icons.INFO, color=ft.Colors.BLUE_700, size=28),
                ft.Text(f"Detalles: {producto['NOMBRE']}", size=20, weight=ft.FontWeight.BOLD)
            ], spacing=12),
            content=ft.Container(
                content=tabla_detalles,
                width=600,
                height=400
            ),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda e: setattr(overlay, 'open', False) or self._pagina.update())
            ]
        )
        
        self._pagina.overlay.append(overlay)
        overlay.open = True
        self._pagina.update()

    def _gestionar_sucursales(self, producto: dict):
        """Overlay para asignar/desasignar sucursales al producto"""
        
        # Cargar todas las sucursales
        try:
            with OBTENER_SESION() as sesion:
                todas_sucursales = sesion.query(MODELO_SUCURSAL).filter_by(ELIMINADA=False).all()
                sucursales_data = [
                    {"ID": s.ID, "NOMBRE": s.NOMBRE, "ACTIVA": s.ACTIVA}
                    for s in todas_sucursales
                ]
        except Exception as ex:
            self._mostrar_snackbar(f"❌ Error al cargar sucursales: {str(ex)}", ft.Colors.RED)
            return
        
        # IDs de sucursales ya asignadas
        ids_asignadas = {s["ID"] for s in producto["SUCURSALES"]}
        
        # Checkboxes para cada sucursal
        checkboxes = {}
        controles_sucursales = []
        
        for suc in sucursales_data:
            checkbox = ft.Checkbox(
                label=f"{suc['NOMBRE']}" + (" (Inactiva)" if not suc["ACTIVA"] else ""),
                value=suc["ID"] in ids_asignadas,
            )
            checkboxes[suc["ID"]] = checkbox
            controles_sucursales.append(checkbox)
        
        def guardar_sucursales(e):
            """Actualiza las sucursales asignadas al producto"""
            try:
                with OBTENER_SESION() as sesion:
                    prod_db = sesion.query(MODELO_PRODUCTO).filter_by(ID=producto["ID"]).first()
                    if not prod_db:
                        self._mostrar_snackbar("❌ Producto no encontrado", ft.Colors.RED)
                        return
                    
                    # Limpiar sucursales actuales
                    prod_db.SUCURSALES.clear()
                    
                    # Asignar nuevas sucursales seleccionadas
                    sucursales_seleccionadas = []
                    for suc_id, checkbox in checkboxes.items():
                        if checkbox.value:
                            sucursal = sesion.query(MODELO_SUCURSAL).filter_by(ID=suc_id).first()
                            if sucursal:
                                prod_db.SUCURSALES.append(sucursal)
                                sucursales_seleccionadas.append(sucursal.NOMBRE)
                    
                    # Auditoría
                    auditoria = MODELO_AUDITORIA(
                        USUARIO_ID=self._usuario.ID,
                        ACCION=f"PRODUCTO_SUCURSALES_ACTUALIZADO: {producto['NOMBRE']}",
                        ENTIDAD="PRODUCTO",
                        ENTIDAD_ID=producto["ID"],
                        DETALLE=f"Sucursales: {', '.join(sucursales_seleccionadas) if sucursales_seleccionadas else 'Ninguna'}",
                    )
                    sesion.add(auditoria)
                    sesion.commit()
                    
                    overlay.open = False
                    self._pagina.update()
                    self._cargar_productos()
                    
                    self._mostrar_snackbar(f"✅ Sucursales actualizadas para '{producto['NOMBRE']}'", ft.Colors.GREEN)
                    
            except Exception as ex:
                self._mostrar_snackbar(f"❌ Error al actualizar sucursales: {str(ex)}", ft.Colors.RED)
        
        overlay = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.icons.Icons.STORE, color=ft.Colors.BLUE_700, size=28),
                ft.Text(f"Gestionar Sucursales: {producto['NOMBRE']}", size=20, weight=ft.FontWeight.BOLD)
            ], spacing=12),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Selecciona las sucursales donde estará disponible el producto:", size=13),
                    ft.Container(
                        content=ft.Column(controles_sucursales, spacing=8, scroll=ft.ScrollMode.AUTO),
                        border=ft.Border.all(1, ft.Colors.GREY_300),
                        border_radius=8,
                        padding=15,
                        height=280,
                    ),
                ], tight=True, spacing=12, scroll=ft.ScrollMode.ADAPTIVE),
                width=500,
                height=400
            ),
            actions=[
                ft.TextButton(
                    content=ft.Row([
                        ft.Icon(ft.icons.Icons.CLOSE, size=18),
                        ft.Text("Cancelar")
                    ], spacing=6),
                    on_click=lambda e: setattr(overlay, 'open', False) or self._pagina.update()
                ),
                ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.icons.Icons.SAVE, size=18),
                        ft.Text("Guardar", weight=ft.FontWeight.W_600)
                    ], spacing=6),
                    on_click=guardar_sucursales,
                    bgcolor=ft.Colors.BLUE_700,
                    color=ft.Colors.WHITE,
                ),
            ]
        )
        
        self._pagina.overlay.append(overlay)
        overlay.open = True
        self._pagina.update()

    def _gestionar_extras(self, producto: dict):
        """Overlay para asignar/desasignar extras al producto"""
        
        # Cargar todos los extras
        try:
            with OBTENER_SESION() as sesion:
                todos_extras = sesion.query(MODELO_EXTRA).filter_by(ACTIVO=True).all()
                extras_data = [
                    {"ID": e.ID, "NOMBRE": e.NOMBRE, "PRECIO": e.PRECIO_ADICIONAL}
                    for e in todos_extras
                ]
        except Exception as ex:
            self._mostrar_snackbar(f"❌ Error al cargar extras: {str(ex)}", ft.Colors.RED)
            return
        
        # IDs de extras ya asignados
        ids_asignados = {e["ID"] for e in producto["EXTRAS"]}
        
        # Checkboxes para cada extra
        checkboxes = {}
        controles_extras = []
        
        for extra in extras_data:
            checkbox = ft.Checkbox(
                label=f"{extra['NOMBRE']} (+${extra['PRECIO']:,})",
                value=extra["ID"] in ids_asignados,
            )
            checkboxes[extra["ID"]] = checkbox
            controles_extras.append(checkbox)
        
        def guardar_extras(e):
            """Actualiza los extras asignados al producto"""
            try:
                with OBTENER_SESION() as sesion:
                    prod_db = sesion.query(MODELO_PRODUCTO).filter_by(ID=producto["ID"]).first()
                    if not prod_db:
                        self._mostrar_snackbar("❌ Producto no encontrado", ft.Colors.RED)
                        return
                    
                    # Limpiar extras actuales
                    prod_db.EXTRAS.clear()
                    
                    # Asignar nuevos extras seleccionados
                    extras_seleccionados = []
                    for extra_id, checkbox in checkboxes.items():
                        if checkbox.value:
                            extra = sesion.query(MODELO_EXTRA).filter_by(ID=extra_id).first()
                            if extra:
                                prod_db.EXTRAS.append(extra)
                                extras_seleccionados.append(extra.NOMBRE)
                    
                    # Auditoría
                    auditoria = MODELO_AUDITORIA(
                        USUARIO_ID=self._usuario.ID,
                        ACCION=f"PRODUCTO_EXTRAS_ACTUALIZADO: {producto['NOMBRE']}",
                        ENTIDAD="PRODUCTO",
                        ENTIDAD_ID=producto["ID"],
                        DETALLE=f"Extras: {', '.join(extras_seleccionados) if extras_seleccionados else 'Ninguno'}",
                    )
                    sesion.add(auditoria)
                    sesion.commit()
                    
                    overlay.open = False
                    self._pagina.update()
                    self._cargar_productos()
                    
                    self._mostrar_snackbar(f"✅ Extras actualizados para '{producto['NOMBRE']}'", ft.Colors.GREEN)
                    
            except Exception as ex:
                self._mostrar_snackbar(f"❌ Error al actualizar extras: {str(ex)}", ft.Colors.RED)
        
        overlay = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.icons.Icons.ADD_CIRCLE_OUTLINE, color=ft.Colors.PURPLE_700, size=28),
                ft.Text(f"Gestionar Extras: {producto['NOMBRE']}", size=20, weight=ft.FontWeight.BOLD)
            ], spacing=12),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Selecciona los extras disponibles para este producto:", size=13),
                    ft.Container(
                        content=ft.Column(controles_extras, spacing=8, scroll=ft.ScrollMode.AUTO) if controles_extras else ft.Text("No hay extras disponibles", size=14, color=ft.Colors.GREY),
                        border=ft.Border.all(1, ft.Colors.GREY_300),
                        border_radius=8,
                        padding=15,
                        height=280,
                    ),
                ], tight=True, spacing=12, scroll=ft.ScrollMode.ADAPTIVE),
                width=500,
                height=400
            ),
            actions=[
                ft.TextButton(
                    content=ft.Row([
                        ft.Icon(ft.icons.Icons.CLOSE, size=18),
                        ft.Text("Cancelar")
                    ], spacing=6),
                    on_click=lambda e: setattr(overlay, 'open', False) or self._pagina.update()
                ),
                ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.icons.Icons.SAVE, size=18),
                        ft.Text("Guardar", weight=ft.FontWeight.W_600)
                    ], spacing=6),
                    on_click=guardar_extras,
                    bgcolor=ft.Colors.PURPLE_700,
                    color=ft.Colors.WHITE,
                ),
            ]
        )
        
        self._pagina.overlay.append(overlay)
        overlay.open = True
        self._pagina.update()

    def _cambiar_disponibilidad(self, producto: dict):
        """Cambia el estado de disponibilidad del producto"""
        nueva_disponibilidad = not producto["DISPONIBLE"]
        
        try:
            with OBTENER_SESION() as sesion:
                prod_db = sesion.query(MODELO_PRODUCTO).filter_by(ID=producto["ID"]).first()
                if not prod_db:
                    self._mostrar_snackbar("❌ Producto no encontrado", ft.Colors.RED)
                    return
                
                prod_db.DISPONIBLE = nueva_disponibilidad
                
                # Auditoría
                auditoria = MODELO_AUDITORIA(
                    USUARIO_ID=self._usuario.ID,
                    ACCION=f"PRODUCTO_{'ACTIVADO' if nueva_disponibilidad else 'DESACTIVADO'}: {producto['NOMBRE']}",
                    ENTIDAD="PRODUCTO",
                    ENTIDAD_ID=producto["ID"],
                    DETALLE=f"Disponibilidad cambiada a: {'Disponible' if nueva_disponibilidad else 'No disponible'}",
                )
                sesion.add(auditoria)
                sesion.commit()
                
                self._mostrar_snackbar(
                    f"✅ Producto '{producto['NOMBRE']}' {'activado' if nueva_disponibilidad else 'desactivado'}",
                    ft.Colors.GREEN if nueva_disponibilidad else ft.Colors.ORANGE
                )
                self._cargar_productos()
                
        except Exception as ex:
            self._mostrar_snackbar(f"❌ Error al cambiar disponibilidad: {str(ex)}", ft.Colors.RED)

    def _mostrar_logs_auditoria(self, producto: dict):
        """Muestra los últimos 50 logs de auditoría del producto"""
        try:
            with OBTENER_SESION() as sesion:
                logs = sesion.query(MODELO_AUDITORIA).filter_by(
                    ENTIDAD="PRODUCTO",
                    ENTIDAD_ID=producto["ID"]
                ).order_by(MODELO_AUDITORIA.FECHA.desc()).limit(50).all()
                
                # Extraer datos dentro de la sesión
                logs_data = []
                for log in logs:
                    logs_data.append({
                        "FECHA": log.FECHA.strftime("%d/%m/%Y %H:%M:%S"),
                        "ACCION": log.ACCION,
                        "DETALLE": log.DETALLE or "",
                    })
        except Exception as ex:
            self._mostrar_snackbar(f"❌ Error al cargar logs: {str(ex)}", ft.Colors.RED)
            return
        
        if not logs_data:
            self._mostrar_snackbar("ℹ️ No hay registros de auditoría para este producto", ft.Colors.BLUE)
            return
        
        # Tabla de logs con colores según acción
        filas_logs = []
        for log in logs_data:
            color_fondo = ft.Colors.TRANSPARENT
            if "CREADO" in log["ACCION"]:
                color_fondo = ft.Colors.GREEN_50
            elif "EDITADO" in log["ACCION"] or "ACTUALIZADO" in log["ACCION"]:
                color_fondo = ft.Colors.ORANGE_50
            elif "DESACTIVADO" in log["ACCION"]:
                color_fondo = ft.Colors.RED_50
            elif "ACTIVADO" in log["ACCION"]:
                color_fondo = ft.Colors.BLUE_50
            
            filas_logs.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(log["FECHA"], size=12)),
                        ft.DataCell(ft.Text(log["ACCION"], size=12, weight=ft.FontWeight.W_500)),
                        ft.DataCell(ft.Text(log["DETALLE"], size=12)),
                    ],
                    color=color_fondo,
                )
            )
        
        tabla_logs = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Fecha", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acción", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Detalle", weight=ft.FontWeight.BOLD)),
            ],
            rows=filas_logs,
            border=ft.Border.all(1, ft.Colors.GREY_300),
            border_radius=8,
            horizontal_lines=ft.BorderSide(1, ft.Colors.GREY_200),
        )
        
        overlay = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.icons.Icons.HISTORY, color=ft.Colors.INDIGO_700, size=28),
                ft.Text(f"Logs de Auditoría: {producto['NOMBRE']}", size=20, weight=ft.FontWeight.BOLD)
            ], spacing=12),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(f"Mostrando últimos {len(logs_data)} registros:", size=13, color=ft.Colors.GREY_700),
                    ft.Container(
                        content=ft.Column([tabla_logs], scroll=ft.ScrollMode.AUTO),
                        border=ft.Border.all(1, ft.Colors.GREY_300),
                        border_radius=8,
                        padding=10,
                        height=400,
                    ),
                ], tight=True, spacing=12),
                width=800,
                height=500
            ),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda e: setattr(overlay, 'open', False) or self._pagina.update())
            ]
        )
        
        self._pagina.overlay.append(overlay)
        overlay.open = True
        self._pagina.update()
    
    def _crear_oferta_producto(self, producto: dict):
        """Muestra diálogo para crear una oferta para este producto"""
        from datetime import datetime, timedelta
        from core.base_datos.ConfiguracionBD import MODELO_OFERTA
        from core.realtime.broker_notify import notify
        
        # Verificar si ya tiene una oferta activa
        with OBTENER_SESION() as sesion:
            oferta_existente = sesion.query(MODELO_OFERTA).filter_by(
                PRODUCTO_ID=producto["ID"],
                ACTIVA=True
            ).first()
            
            if oferta_existente:
                self._mostrar_snackbar(
                    f"⚠️ {producto['NOMBRE']} ya tiene una oferta activa del {oferta_existente.DESCUENTO_PORCENTAJE}%",
                    ft.Colors.ORANGE_700
                )
                return
        
        # Campo de descuento
        campo_descuento = ft.TextField(
            label="Descuento (%)",
            hint_text="0-100",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=200,
            autofocus=True
        )
        
        # Fecha de fin
        campo_fecha_fin = ft.TextField(
            label="Fecha fin",
            hint_text="YYYY-MM-DD HH:MM",
            width=250
        )
        
        # Botones rápidos de duración
        def aplicar_duracion(horas: int):
            fecha_fin = datetime.now() + timedelta(hours=horas)
            campo_fecha_fin.value = fecha_fin.strftime("%Y-%m-%d %H:%M")
            self._pagina.update()
        
        botones_rapidos = ft.Column([
            ft.Text("Duración rápida:", weight=ft.FontWeight.BOLD, size=13),
            ft.Row([
                ft.ElevatedButton(
                    "1 hora",
                    on_click=lambda e: aplicar_duracion(1),
                    bgcolor=ft.Colors.BLUE_700,
                    color=ft.Colors.WHITE,
                    height=35
                ),
                ft.ElevatedButton(
                    "6 horas",
                    on_click=lambda e: aplicar_duracion(6),
                    bgcolor=ft.Colors.BLUE_700,
                    color=ft.Colors.WHITE,
                    height=35
                ),
                ft.ElevatedButton(
                    "24 horas",
                    on_click=lambda e: aplicar_duracion(24),
                    bgcolor=ft.Colors.BLUE_700,
                    color=ft.Colors.WHITE,
                    height=35
                )
            ], wrap=True, spacing=8),
            ft.Row([
                ft.ElevatedButton(
                    "3 días",
                    on_click=lambda e: aplicar_duracion(24*3),
                    bgcolor=ft.Colors.BLUE_700,
                    color=ft.Colors.WHITE,
                    height=35
                ),
                ft.ElevatedButton(
                    "7 días",
                    on_click=lambda e: aplicar_duracion(24*7),
                    bgcolor=ft.Colors.BLUE_700,
                    color=ft.Colors.WHITE,
                    height=35
                ),
                ft.ElevatedButton(
                    "30 días",
                    on_click=lambda e: aplicar_duracion(24*30),
                    bgcolor=ft.Colors.BLUE_700,
                    color=ft.Colors.WHITE,
                    height=35
                )
            ], wrap=True, spacing=8)
        ], spacing=10)
        
        # Preview del precio
        precio_original = producto["PRECIO"] / 100
        texto_preview = ft.Text("", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700)
        
        def actualizar_preview(e):
            try:
                descuento = float(campo_descuento.value or 0)
                if 0 <= descuento <= 100:
                    precio_final = precio_original * (1 - descuento / 100)
                    texto_preview.value = f"💰 Precio original: ${precio_original:.2f} → Precio con descuento: ${precio_final:.2f}"
                    campo_descuento.error_text = None
                else:
                    texto_preview.value = ""
                    campo_descuento.error_text = "Debe estar entre 0 y 100"
            except:
                texto_preview.value = ""
            self._pagina.update()
        
        campo_descuento.on_change = actualizar_preview
        
        def guardar_oferta(e):
            # Validaciones
            if not campo_descuento.value:
                campo_descuento.error_text = "Ingresa el descuento"
                self._pagina.update()
                return
            
            try:
                descuento = float(campo_descuento.value)
                if descuento < 0 or descuento > 100:
                    campo_descuento.error_text = "Debe estar entre 0 y 100"
                    self._pagina.update()
                    return
            except ValueError:
                campo_descuento.error_text = "Valor inválido"
                self._pagina.update()
                return
            
            # Validar fecha
            fecha_fin = None
            if campo_fecha_fin.value:
                try:
                    fecha_fin = datetime.strptime(campo_fecha_fin.value, "%Y-%m-%d %H:%M")
                    if fecha_fin <= datetime.now():
                        campo_fecha_fin.error_text = "Debe ser futura"
                        self._pagina.update()
                        return
                except ValueError:
                    campo_fecha_fin.error_text = "Formato inválido (YYYY-MM-DD HH:MM)"
                    self._pagina.update()
                    return
            else:
                campo_fecha_fin.error_text = "La fecha de fin es obligatoria"
                self._pagina.update()
                return
            
            # Crear oferta
            with OBTENER_SESION() as sesion:
                nueva_oferta = MODELO_OFERTA(
                    PRODUCTO_ID=producto["ID"],
                    DESCUENTO_PORCENTAJE=int(descuento),
                    FECHA_INICIO=datetime.now(),
                    FECHA_FIN=fecha_fin,
                    ACTIVA=True
                )
                sesion.add(nueva_oferta)
                sesion.commit()
                
                # Notificar por websocket
                notify({
                    "tipo": "oferta_creada",
                    "oferta_id": nueva_oferta.ID,
                    "producto": producto["NOMBRE"],
                    "descuento": nueva_oferta.DESCUENTO_PORCENTAJE,
                    "mensaje": f"¡Nueva oferta! {descuento}% de descuento en {producto['NOMBRE']}"
                })
            
            overlay.open = False
            self._pagina.update()
            self._mostrar_snackbar(
                f"✅ Oferta creada: {descuento}% de descuento en {producto['NOMBRE']}",
                ft.Colors.GREEN_700
            )
        
        overlay = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.icons.Icons.LOCAL_OFFER, color=ft.Colors.GREEN_700),
                ft.Text(f"Crear Oferta - {producto['NOMBRE']}")
            ]),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        f"Producto: {producto['NOMBRE']}",
                        size=15,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Text(
                        f"Precio actual: ${precio_original:.2f}",
                        size=13,
                        color=ft.Colors.GREY_700
                    ),
                    ft.Divider(height=20),
                    campo_descuento,
                    texto_preview,
                    ft.Divider(height=20),
                    botones_rapidos,
                    ft.Divider(height=20),
                    campo_fecha_fin,
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.icons.Icons.INFO_OUTLINE, size=16, color=ft.Colors.BLUE_700),
                            ft.Text(
                                "La oferta se desactivará automáticamente al expirar",
                                size=11,
                                color=ft.Colors.BLUE_700,
                                italic=True
                            )
                        ]),
                        padding=10,
                        bgcolor=ft.Colors.BLUE_50,
                        border_radius=5
                    )
                ], spacing=12, scroll=ft.ScrollMode.AUTO),
                width=450,
                height=550
            ),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e: setattr(overlay, 'open', False) or self._pagina.update()
                ),
                ft.ElevatedButton(
                    "Crear Oferta",
                    on_click=guardar_oferta,
                    bgcolor=ft.Colors.GREEN_700,
                    color=ft.Colors.WHITE
                )
            ]
        )
        
        self._pagina.overlay.append(overlay)
        overlay.open = True
        self._pagina.update()

    # ========== UTILIDADES ==========

    def _mostrar_snackbar(self, mensaje: str, color):
        """Muestra un mensaje temporal en la parte inferior"""
        snackbar = ft.SnackBar(
            content=ft.Text(mensaje, color=ft.Colors.WHITE),
            bgcolor=color,
            duration=3000,
        )
        self._pagina.overlay.append(snackbar)
        snackbar.open = True
        self._pagina.update()
