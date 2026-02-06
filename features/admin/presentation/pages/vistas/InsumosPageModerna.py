"""
📦 InsumosPageModerna - Gestión de Insumos e Inventario
Sistema para controlar ingredientes comprados y su relación con productos

CONCEPTOS:
- INSUMO: Ingrediente que se compra (pollo, arroba PPA, etc)
- FÓRMULA: Receta que asigna insumos a productos (ej: PopiPapa = 2kg pollo + 1 arroba PPA)
- MOVIMIENTO: Registro de entrada/salida de insumos (para reportes)
"""

import flet as ft
from typing import Optional, List, Dict
from datetime import datetime
import json

from core.base_datos.ConfiguracionBD import (
    MODELO_INSUMO, MODELO_PRODUCTO, MODELO_FORMULA, MODELO_MOVIMIENTO_INSUMO,
    OBTENER_SESION
)
from features.admin.presentation.widgets.LayoutBase import LayoutBase
from core.Constantes import ROLES
from core.decoradores.DecoradorVistas import REQUIERE_ROL

# Constantes
TIPOS_MOVIMIENTO = [
    ("ENTRADA", "📥 Entrada", "🟢", ft.Colors.GREEN_600),
    ("SALIDA", "📤 Salida", "🔴", ft.Colors.RED_600),
    ("AJUSTE", "⚙️ Ajuste", "🔵", ft.Colors.BLUE_600),
    ("PRODUCCION", "🏭 Producción", "🟠", ft.Colors.ORANGE_600),
]

UNIDADES_COMUNES = [
    "kg",
    "litro",
    "arroba",
    "unidad",
    "metro",
    "cm",
    "paquete",
]


@REQUIERE_ROL(ROLES.ADMIN)
class InsumosPageModerna(LayoutBase):
    """Gestión de Insumos - VERSIÓN SIMPLIFICADA"""

    def __init__(self, pagina: ft.Page, usuario):
        super().__init__(
            pagina=pagina,
            usuario=usuario,
            titulo_vista="📦 Gestión de Insumos",
            mostrar_boton_volver=True,
            on_volver_dashboard=self._volver_dashboard,
            on_cerrar_sesion=self._cerrar_sesion
        )

        self.usuario = usuario
        self._pagina = pagina

        # Caches
        self._insumos: List[Dict] = []
        self._productos: List[Dict] = []
        self._formulas: List[Dict] = []
        
        # Tablas (referencias para actualizar)
        self._tabla_insumos = None
        self._tabla_formulas = None

        # Cargar datos PRIMERO
        self._cargar_datos()

        # Construir UI DESPUÉS
        contenido = self._construir_interfaz()
        self.construir(contenido)

    def _cargar_datos(self):
        """Carga insumos, productos y fórmulas"""
        try:
            with OBTENER_SESION() as sesion:
                # Cargar insumos activos
                insumos = sesion.query(MODELO_INSUMO).filter_by(ACTIVO=True).all()
                self._insumos = [
                    {
                        "ID": i.ID,
                        "NOMBRE": i.NOMBRE,
                        "UNIDAD": i.UNIDAD,
                        "PRECIO_UNITARIO": i.PRECIO_UNITARIO,
                        "STOCK_ACTUAL": i.STOCK_ACTUAL,
                        "STOCK_MINIMO": i.STOCK_MINIMO,
                        "PROVEEDOR": i.PROVEEDOR,
                    }
                    for i in insumos
                ]

                # Cargar productos activos
                productos = sesion.query(MODELO_PRODUCTO).filter_by(DISPONIBLE=True).all()
                self._productos = [
                    {"ID": p.ID, "NOMBRE": p.NOMBRE}
                    for p in productos
                ]

                # Cargar fórmulas
                formulas = sesion.query(MODELO_FORMULA).filter_by(ACTIVA=True).all()
                self._formulas = [
                    {
                        "ID": f.ID,
                        "PRODUCTO_ID": f.PRODUCTO_ID,
                        "INSUMO_ID": f.INSUMO_ID,
                        "CANTIDAD": f.CANTIDAD,
                        "UNIDAD": f.UNIDAD,
                        "TIEMPO_PREP": f.TIEMPO_PREP or 0,
                        "NOTAS": f.NOTAS or "",
                        "PRODUCTO_NOMBRE": next(
                            (p["NOMBRE"] for p in self._productos if p["ID"] == f.PRODUCTO_ID),
                            "?"
                        ),
                        "INSUMO_NOMBRE": next(
                            (i["NOMBRE"] for i in self._insumos if i["ID"] == f.INSUMO_ID),
                            "?"
                        ),
                    }
                    for f in formulas
                ]

        except Exception as e:
            self._mostrar_error(f"Error cargando datos: {str(e)}")
        
        # Actualizar tablas si ya existen
        if self._tabla_insumos or self._tabla_formulas:
            self._actualizar_tablas()

    def _actualizar_tablas(self):
        """Actualiza las tablas de insumos y fórmulas con los datos cargados"""
        if self._tabla_insumos:
            self._tabla_insumos.rows = self._generar_filas_insumos()
        if self._tabla_formulas:
            self._tabla_formulas.rows = self._generar_filas_formulas()
        self._pagina.update()

    def _construir_interfaz(self) -> ft.Container:
        """Construye la interfaz principal con 3 secciones"""

        # ===== HEADER =====
        header = ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.INVENTORY_2, size=32, color=ft.Colors.BLUE_700),
                    ft.Column([
                        ft.Text("📦 Gestión de Insumos", size=22, weight=ft.FontWeight.BOLD),
                        ft.Text("Controla ingredientes, recetas y stock", size=11, color=ft.Colors.GREY_600),
                    ], spacing=2),
                ], spacing=12),
                ft.Row([
                    ft.ElevatedButton(
                        "➕ Nuevo Insumo",
                        on_click=self._overlay_crear_insumo,
                        bgcolor=ft.Colors.BLUE_600,
                        color=ft.Colors.WHITE,
                    ),
                    ft.ElevatedButton(
                        "📋 Nueva Fórmula",
                        on_click=self._overlay_crear_formula,
                        bgcolor=ft.Colors.AMBER_600,
                        color=ft.Colors.WHITE,
                    ),
                    ft.ElevatedButton(
                        "📊 Registrar Movimiento",
                        on_click=self._overlay_registrar_movimiento,
                        bgcolor=ft.Colors.TEAL_600,
                        color=ft.Colors.WHITE,
                    ),
                ], spacing=8),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=16,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
        )

        # ===== TABLA DE INSUMOS =====
        self._tabla_insumos = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Insumo", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Unidad", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Stock Actual", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Mínimo", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Precio Unit", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Proveedor", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
            ],
            rows=self._generar_filas_insumos(),
            border_radius=8,
        )

        # ===== TABLA DE FÓRMULAS =====
        self._tabla_formulas = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Producto", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Insumo", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Cantidad", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
            ],
            rows=self._generar_filas_formulas(),
            border_radius=8,
        )

        # ===== CONTENIDO PRINCIPAL =====
        contenido = ft.Column([
            header,
            ft.Text("📦 Insumos Disponibles", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800),
            ft.Container(content=self._tabla_insumos, border=ft.border.all(1, ft.Colors.GREY_300), border_radius=8, padding=12),
            
            ft.Text("📋 Fórmulas (Recetas)", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800),
            ft.Container(content=self._tabla_formulas, border=ft.border.all(1, ft.Colors.GREY_300), border_radius=8, padding=12),
        ], spacing=16, expand=True)

        return ft.Container(content=contenido, padding=20, expand=True)

    def _generar_filas_insumos(self) -> List[ft.DataRow]:
        """Genera filas para tabla de insumos"""
        filas = []

        for i in self._insumos:
            # Color según stock
            color_stock = ft.Colors.RED_600 if i["STOCK_ACTUAL"] <= i["STOCK_MINIMO"] else ft.Colors.GREEN_600
            
            filas.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(i["NOMBRE"], size=10)),
                        ft.DataCell(ft.Text(i["UNIDAD"], size=10)),
                        ft.DataCell(ft.Text(str(i["STOCK_ACTUAL"]), size=10, color=color_stock, weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text(str(i["STOCK_MINIMO"]), size=10)),
                        ft.DataCell(ft.Text(f"${i['PRECIO_UNITARIO']/100:.2f}", size=10)),
                        ft.DataCell(ft.Text(i["PROVEEDOR"] or "-", size=10)),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    ft.Icons.EDIT,
                                    icon_size=16,
                                    tooltip="Editar",
                                    on_click=lambda e, iid=i["ID"]: self._overlay_editar_insumo(iid),
                                ),
                                ft.IconButton(
                                    ft.Icons.DELETE,
                                    icon_size=16,
                                    tooltip="Eliminar",
                                    on_click=lambda e, iid=i["ID"]: self._eliminar_insumo(iid),
                                ),
                            ], spacing=4)
                        ),
                    ]
                )
            )

        return filas

    def _generar_filas_formulas(self) -> List[ft.DataRow]:
        """Genera filas para tabla de fórmulas"""
        filas = []

        for f in self._formulas:
            filas.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(f["PRODUCTO_NOMBRE"], size=10)),
                        ft.DataCell(ft.Text(f["INSUMO_NOMBRE"], size=10)),
                        ft.DataCell(ft.Text(f"{f['CANTIDAD']} {f['UNIDAD']}", size=10)),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    ft.Icons.EDIT,
                                    icon_size=16,
                                    tooltip="Editar",
                                    on_click=lambda e, fid=f["ID"]: self._overlay_editar_formula(fid),
                                ),
                                ft.IconButton(
                                    ft.Icons.DELETE,
                                    icon_size=16,
                                    tooltip="Eliminar",
                                    on_click=lambda e, fid=f["ID"]: self._eliminar_formula(fid),
                                ),
                            ], spacing=4)
                        ),
                    ]
                )
            )

        return filas

    # ==================== OVERLAYS ====================

    def _overlay_crear_insumo(self, e):
        """Overlay para crear nuevo insumo"""
        tf_nombre = ft.TextField(label="Nombre *", width=300)
        tf_descripcion = ft.TextField(label="Descripción", width=300)
        dd_unidad = ft.Dropdown(
            label="Unidad *",
            options=[ft.dropdown.Option(text=u) for u in UNIDADES_COMUNES],
            width=140,
        )
        tf_precio = ft.TextField(label="Precio Unitario ($) *", width=140, keyboard_type=ft.KeyboardType.NUMBER)
        tf_stock_minimo = ft.TextField(label="Stock Mínimo", value="0", width=140, keyboard_type=ft.KeyboardType.NUMBER)
        tf_proveedor = ft.TextField(label="Proveedor", width=300)

        def guardar(ev):
            if not tf_nombre.value or not dd_unidad.value or not tf_precio.value:
                self._mostrar_error("Nombre, Unidad y Precio son obligatorios")
                return

            try:
                with OBTENER_SESION() as sesion:
                    nuevo = MODELO_INSUMO(
                        NOMBRE=tf_nombre.value.strip(),
                        DESCRIPCION=tf_descripcion.value.strip() or None,
                        UNIDAD=dd_unidad.value,
                        PRECIO_UNITARIO=int(float(tf_precio.value) * 100),  # en centavos
                        STOCK_ACTUAL=0,
                        STOCK_MINIMO=int(tf_stock_minimo.value or 0),
                        PROVEEDOR=tf_proveedor.value.strip() or None,
                        ACTIVO=True,
                    )
                    sesion.add(nuevo)
                    sesion.commit()
                    sesion.flush()

                overlay.open = False
                self._pagina.update()
                self._mostrar_exito("Insumo creado exitosamente")
                self._cargar_datos()

            except Exception as ex:
                self._mostrar_error(f"Error: {str(ex)}")

        overlay = ft.AlertDialog(
            modal=True,
            title=ft.Text("➕ Crear Nuevo Insumo", size=16, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    tf_nombre,
                    tf_descripcion,
                    ft.Row([dd_unidad, tf_precio], spacing=8),
                    ft.Row([tf_stock_minimo], spacing=8),
                    tf_proveedor,
                ], spacing=12),
                width=350,
                padding=16,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: setattr(overlay, 'open', False) or self._pagina.update()),
                ft.ElevatedButton("Guardar", on_click=guardar, bgcolor=ft.Colors.BLUE_600),
            ],
        )

        self._pagina.overlay.append(overlay)
        overlay.open = True
        self._pagina.update()

    def _overlay_crear_formula(self, e):
        """Overlay para crear nueva fórmula"""
        dd_producto = ft.Dropdown(
            label="Selecciona Producto *",
            options=[
                ft.dropdown.Option(key=str(p["ID"]), text=p["NOMBRE"])
                for p in self._productos
            ],
            width=300,
        )

        dd_insumo = ft.Dropdown(
            label="Selecciona Insumo *",
            options=[
                ft.dropdown.Option(key=str(i["ID"]), text=i["NOMBRE"])
                for i in self._insumos
            ],
            width=300,
        )

        tf_cantidad = ft.TextField(label="Cantidad *", width=140, keyboard_type=ft.KeyboardType.NUMBER)
        tf_notas = ft.TextField(label="Notas", width=300, multiline=True)

        def guardar(ev):
            if not dd_producto.value or not dd_insumo.value or not tf_cantidad.value:
                self._mostrar_error("Producto, Insumo y Cantidad son obligatorios")
                return

            try:
                insumo = next(i for i in self._insumos if str(i["ID"]) == dd_insumo.value)
                cantidad = int(tf_cantidad.value) if tf_cantidad.value.isdigit() else int(float(tf_cantidad.value))
                
                with OBTENER_SESION() as sesion:
                    nueva = MODELO_FORMULA(
                        PRODUCTO_ID=int(dd_producto.value),
                        INSUMO_ID=int(dd_insumo.value),
                        CANTIDAD=cantidad,
                        UNIDAD=insumo["UNIDAD"],
                        NOTAS=tf_notas.value.strip() or None,
                        ACTIVA=True,
                    )
                    sesion.add(nueva)
                    sesion.commit()
                    sesion.flush()

                overlay.open = False
                self._pagina.update()
                self._mostrar_exito("Fórmula creada exitosamente")
                self._cargar_datos()

            except Exception as ex:
                self._mostrar_error(f"Error: {str(ex)}")

        overlay = ft.AlertDialog(
            modal=True,
            title=ft.Text("📋 Crear Nueva Fórmula", size=16, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    dd_producto,
                    dd_insumo,
                    tf_cantidad,
                    tf_notas,
                ], spacing=12),
                width=350,
                padding=16,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: setattr(overlay, 'open', False) or self._pagina.update()),
                ft.ElevatedButton("Guardar", on_click=guardar, bgcolor=ft.Colors.AMBER_600),
            ],
        )

        self._pagina.overlay.append(overlay)
        overlay.open = True
        self._pagina.update()

    def _overlay_registrar_movimiento(self, e):
        """Overlay para registrar movimiento de insumo"""
        dd_insumo = ft.Dropdown(
            label="Selecciona Insumo *",
            options=[
                ft.dropdown.Option(key=str(i["ID"]), text=i["NOMBRE"])
                for i in self._insumos
            ],
            width=300,
        )

        dd_tipo = ft.Dropdown(
            label="Tipo de Movimiento *",
            options=[
                ft.dropdown.Option(key=t[0], text=f"{t[1]}")
                for t in TIPOS_MOVIMIENTO
            ],
            width=300,
        )

        tf_cantidad = ft.TextField(label="Cantidad *", width=140, keyboard_type=ft.KeyboardType.NUMBER)
        tf_observacion = ft.TextField(label="Observación", width=300, multiline=True)

        def guardar(ev):
            if not dd_insumo.value or not dd_tipo.value or not tf_cantidad.value:
                self._mostrar_error("Insumo, Tipo y Cantidad son obligatorios")
                return

            try:
                insumo_id = int(dd_insumo.value)
                cantidad = int(tf_cantidad.value)
                tipo = dd_tipo.value

                # Calcular signo según tipo
                if tipo == "ENTRADA":
                    cantidad_efectiva = cantidad
                elif tipo in ["SALIDA", "PRODUCCION"]:
                    cantidad_efectiva = -cantidad
                else:  # AJUSTE
                    cantidad_efectiva = cantidad

                with OBTENER_SESION() as sesion:
                    insumo = sesion.query(MODELO_INSUMO).filter_by(ID=insumo_id).first()
                    if not insumo:
                        self._mostrar_error("Insumo no encontrado")
                        return

                    stock_anterior = insumo.STOCK_ACTUAL
                    stock_nuevo = stock_anterior + cantidad_efectiva

                    # Crear movimiento
                    movimiento = MODELO_MOVIMIENTO_INSUMO(
                        INSUMO_ID=insumo_id,
                        TIPO=tipo,
                        CANTIDAD=cantidad_efectiva,
                        STOCK_ANTERIOR=stock_anterior,
                        STOCK_NUEVO=stock_nuevo,
                        OBSERVACION=tf_observacion.value or None,
                        USUARIO_ID=self.usuario.ID,
                    )
                    
                    # Actualizar stock
                    insumo.STOCK_ACTUAL = stock_nuevo
                    
                    sesion.add(movimiento)
                    sesion.commit()
                    sesion.flush()

                overlay.open = False
                self._pagina.update()
                self._mostrar_exito(f"Movimiento registrado ({tipo})")
                self._cargar_datos()

            except Exception as ex:
                self._mostrar_error(f"Error: {str(ex)}")

        overlay = ft.AlertDialog(
            modal=True,
            title=ft.Text("📊 Registrar Movimiento", size=16, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    dd_insumo,
                    dd_tipo,
                    tf_cantidad,
                    tf_observacion,
                ], spacing=12),
                width=350,
                padding=16,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: setattr(overlay, 'open', False) or self._pagina.update()),
                ft.ElevatedButton("Registrar", on_click=guardar, bgcolor=ft.Colors.TEAL_600),
            ],
        )

        self._pagina.overlay.append(overlay)
        overlay.open = True
        self._pagina.update()

    def _overlay_editar_insumo(self, insumo_id: int):
        """Overlay para editar insumo"""
        insumo = next((i for i in self._insumos if i["ID"] == insumo_id), None)
        if not insumo:
            return

        tf_nombre = ft.TextField(label="Nombre", value=insumo["NOMBRE"], width=300)
        tf_precio = ft.TextField(label="Precio Unitario", value=str(insumo["PRECIO_UNITARIO"]/100), width=140)
        tf_stock_minimo = ft.TextField(label="Stock Mínimo", value=str(insumo["STOCK_MINIMO"]), width=140)

        def guardar(ev):
            try:
                with OBTENER_SESION() as sesion:
                    i = sesion.query(MODELO_INSUMO).filter_by(ID=insumo_id).first()
                    if i:
                        i.NOMBRE = tf_nombre.value.strip()
                        i.PRECIO_UNITARIO = int(float(tf_precio.value) * 100)
                        i.STOCK_MINIMO = int(tf_stock_minimo.value)
                        i.FECHA_MODIFICACION = datetime.utcnow()
                        sesion.commit()
                        sesion.flush()

                overlay.open = False
                self._pagina.update()
                self._mostrar_exito("Insumo actualizado")
                self._cargar_datos()

            except Exception as ex:
                self._mostrar_error(f"Error: {str(ex)}")

        overlay = ft.AlertDialog(
            modal=True,
            title=ft.Text("✏️ Editar Insumo", size=16, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    tf_nombre,
                    ft.Row([tf_precio, tf_stock_minimo], spacing=8),
                ], spacing=12),
                width=320,
                padding=16,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: setattr(overlay, 'open', False) or self._pagina.update()),
                ft.ElevatedButton("Guardar", on_click=guardar, bgcolor=ft.Colors.BLUE_600),
            ],
        )

        self._pagina.overlay.append(overlay)
        overlay.open = True
        self._pagina.update()

    def _overlay_editar_formula(self, formula_id: int):
        """Overlay para editar fórmula"""
        formula = next((f for f in self._formulas if f["ID"] == formula_id), None)
        if not formula:
            return

        tf_cantidad = ft.TextField(label="Cantidad", value=str(formula["CANTIDAD"]), width=140)

        def guardar(ev):
            try:
                cantidad = int(tf_cantidad.value) if tf_cantidad.value.isdigit() else int(float(tf_cantidad.value))
                with OBTENER_SESION() as sesion:
                    f = sesion.query(MODELO_FORMULA).filter_by(ID=formula_id).first()
                    if f:
                        f.CANTIDAD = cantidad
                        sesion.commit()
                        sesion.flush()

                overlay.open = False
                self._pagina.update()
                self._mostrar_exito("Fórmula actualizada")
                self._cargar_datos()

            except Exception as ex:
                self._mostrar_error(f"Error: {str(ex)}")

        overlay = ft.AlertDialog(
            modal=True,
            title=ft.Text("✏️ Editar Fórmula", size=16, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(f"{formula['PRODUCTO_NOMBRE']} + {formula['INSUMO_NOMBRE']}", weight=ft.FontWeight.BOLD),
                    tf_cantidad,
                ], spacing=12),
                width=320,
                padding=16,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: setattr(overlay, 'open', False) or self._pagina.update()),
                ft.ElevatedButton("Guardar", on_click=guardar, bgcolor=ft.Colors.AMBER_600),
            ],
        )

        self._pagina.overlay.append(overlay)
        overlay.open = True
        self._pagina.update()

    # ==================== UTILIDADES ====================

    def _eliminar_insumo(self, insumo_id: int):
        """Elimina un insumo (marca como inactivo)"""
        try:
            with OBTENER_SESION() as sesion:
                i = sesion.query(MODELO_INSUMO).filter_by(ID=insumo_id).first()
                if i:
                    i.ACTIVO = False
                    i.FECHA_MODIFICACION = datetime.utcnow()
                    sesion.commit()
                    sesion.flush()
                else:
                    self._mostrar_error("Insumo no encontrado")
                    return

            self._mostrar_exito("Insumo eliminado")
            self._cargar_datos()

        except Exception as e:
            self._mostrar_error(f"Error al eliminar: {str(e)}")

    def _eliminar_formula(self, formula_id: int):
        """Elimina una fórmula (marca como inactiva)"""
        try:
            with OBTENER_SESION() as sesion:
                f = sesion.query(MODELO_FORMULA).filter_by(ID=formula_id).first()
                if f:
                    f.ACTIVA = False
                    sesion.commit()
                    sesion.flush()
                else:
                    self._mostrar_error("Fórmula no encontrada")
                    return

            self._mostrar_exito("Fórmula eliminada")
            self._cargar_datos()

        except Exception as e:
            self._mostrar_error(f"Error al eliminar: {str(e)}")

    def _mostrar_exito(self, mensaje: str):
        """Muestra notificación de éxito"""
        snack = ft.SnackBar(
            content=ft.Text(f"✅ {mensaje}", color=ft.Colors.WHITE),
            bgcolor=ft.Colors.GREEN_600,
            duration=2000,
        )
        self._pagina.overlay.append(snack)
        snack.open = True
        self._pagina.update()

    def _mostrar_error(self, mensaje: str):
        """Muestra notificación de error"""
        snack = ft.SnackBar(
            content=ft.Text(f"❌ {mensaje}", color=ft.Colors.WHITE),
            bgcolor=ft.Colors.RED_600,
            duration=2000,
        )
        self._pagina.overlay.append(snack)
        snack.open = True
        self._pagina.update()

    # ==================== NAVEGACIÓN ====================

    def _volver_dashboard(self, e=None):
        """Vuelve al dashboard"""
        pass

    def _cerrar_sesion(self, e=None):
        """Cierra sesión"""
        pass
