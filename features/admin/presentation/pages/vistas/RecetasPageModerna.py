"""
📖 RecetasPageModerna - Gestión de Recetas de Productos
Crea recetas vinculando insumos a productos con cantidades y unidades convertibles
"""

import flet as ft
from typing import List, Dict, Optional
from datetime import datetime
from core.base_datos.ConfiguracionBD import (
    MODELO_FORMULA, MODELO_INSUMO, MODELO_PRODUCTO, OBTENER_SESION, CERRAR_SESION
)
from core.utilidades.ConversionesUnidades import (
    obtener_unidades_por_categoria, es_unidad_peso, es_unidad_volumen, es_unidad_longitud
)
from features.admin.presentation.widgets.LayoutBase import LayoutBase
from core.Constantes import ROLES
from core.decoradores.DecoradorVistas import REQUIERE_ROL
import logging

logger = logging.getLogger(__name__)


@REQUIERE_ROL(ROLES.ADMIN)
class RecetasPageModerna(LayoutBase):
    """Página para gestionar recetas (fórmulas) de productos"""

    def __init__(self, pagina: ft.Page, usuario):
        super().__init__(
            pagina=pagina,
            usuario=usuario,
            titulo_vista="📖 Gestión de Recetas",
            mostrar_boton_volver=True,
            on_volver_dashboard=self._volver_dashboard,
            on_cerrar_sesion=self._cerrar_sesion
        )

        self.usuario = usuario
        self._pagina = pagina

        # Datos
        self._recetas: List[Dict] = []
        self._productos: List[Dict] = []
        self._insumos: List[Dict] = []
        self._tabla_recetas = None

        # Cargar datos
        self._cargar_datos()

        # Construir UI
        contenido = self._construir_interfaz()
        self.construir(contenido)

    def _cargar_datos(self):
        """Carga productos, insumos y recetas"""
        try:
            with OBTENER_SESION() as session:
                # Productos
                productos = session.query(MODELO_PRODUCTO).filter_by(ACTIVO=True).all()
                self._productos = [
                    {"ID": p.ID, "NOMBRE": p.NOMBRE} for p in productos
                ]

                # Insumos
                insumos = session.query(MODELO_INSUMO).filter_by(ACTIVO=True).all()
                self._insumos = [
                    {
                        "ID": i.ID,
                        "NOMBRE": i.NOMBRE,
                        "UNIDAD": i.UNIDAD,
                        "STOCK_ACTUAL": i.STOCK_ACTUAL,
                    }
                    for i in insumos
                ]

                # Recetas
                recetas = session.query(MODELO_FORMULA).all()
                self._recetas = []
                for r in recetas:
                    producto = r.PRODUCTO
                    insumo = r.INSUMO
                    self._recetas.append({
                        "ID": r.ID,
                        "PRODUCTO_ID": r.PRODUCTO_ID,
                        "PRODUCTO_NOMBRE": producto.NOMBRE if producto else "N/A",
                        "INSUMO_ID": r.INSUMO_ID,
                        "INSUMO_NOMBRE": insumo.NOMBRE if insumo else "N/A",
                        "CANTIDAD": r.CANTIDAD,
                        "UNIDAD": r.UNIDAD,
                        "TIEMPO_PREP": getattr(r, "TIEMPO_PREP", 0),
                        "ACTIVA": r.ACTIVA,
                        "objeto": r
                    })

                logger.info(f"Cargadas {len(self._recetas)} recetas")
        except Exception as e:
            logger.error(f"Error al cargar datos: {e}")
        finally:
            CERRAR_SESION()

    def _construir_interfaz(self) -> ft.Container:
        """Construye la interfaz principal"""

        # Header
        header = ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Icon(ft.icons.RECEIPT_LONG, size=32, color=ft.Colors.AMBER_700),
                    ft.Column([
                        ft.Text("📖 Gestión de Recetas", size=22, weight=ft.FontWeight.BOLD),
                        ft.Text("Define qué insumos lleva cada producto", size=11, color=ft.Colors.GREY_600),
                    ], spacing=2),
                ], spacing=12),
                ft.ElevatedButton(
                    "➕ Nueva Receta",
                    on_click=self._overlay_crear_receta,
                    bgcolor=ft.Colors.AMBER_600,
                    color=ft.Colors.WHITE,
                    icon=ft.icons.ADD,
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=16,
            bgcolor=ft.Colors.AMBER_50,
            border_radius=10,
        )

        # Tabla de recetas
        self._tabla_recetas = self._crear_tabla_recetas()

        # Contenedor principal
        return ft.Container(
            content=ft.Column([
                header,
                ft.Divider(height=1),
                ft.Text(f"Total: {len(self._recetas)} recetas", size=12, color=ft.Colors.GREY_600),
                self._tabla_recetas,
            ], spacing=12, expand=True),
            padding=16,
        )

    def _crear_tabla_recetas(self) -> ft.Column:
        """Crea tabla de recetas"""
        filas = []

        for receta in self._recetas:
            filas.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(receta["PRODUCTO_NOMBRE"], weight=ft.FontWeight.W_500)),
                        ft.DataCell(ft.Text(receta["INSUMO_NOMBRE"])),
                        ft.DataCell(ft.Text(f"{receta['CANTIDAD']} {receta['UNIDAD']}", size=11)),
                        ft.DataCell(ft.Text(f"{receta['TIEMPO_PREP']} min", size=11, color=ft.Colors.GREY_600)),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    ft.icons.EDIT,
                                    tooltip="Editar",
                                    on_click=lambda e, rid=receta["ID"]: self._overlay_editar_receta(rid),
                                    icon_color=ft.Colors.BLUE_600,
                                ),
                                ft.IconButton(
                                    ft.icons.DELETE,
                                    tooltip="Eliminar",
                                    on_click=lambda e, rid=receta["ID"]: self._eliminar_receta(rid),
                                    icon_color=ft.Colors.RED_600,
                                ),
                            ], spacing=0),
                        ),
                    ]
                )
            )

        tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Producto", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Insumo", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Cantidad", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Tiempo Prep", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
            ],
            rows=filas if filas else [
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("✨ Sin recetas. ¡Crea una!", size=14, color=ft.Colors.AMBER_600)),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                ])
            ],
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=8,
            heading_row_color=ft.Colors.AMBER_100,
            heading_row_height=50,
            data_row_max_height=60,
        )

        return ft.Column([tabla], expand=True, scroll=ft.ScrollMode.ADAPTIVE)

    def _overlay_crear_receta(self, e):
        """Overlay para crear receta"""
        
        # Dropdowns
        select_producto = ft.Dropdown(
            label="Producto",
            options=[ft.dropdown.Option(f"{p['NOMBRE']}", p['ID']) for p in self._productos],
            width=200,
        )

        select_insumo = ft.Dropdown(
            label="Insumo",
            options=[ft.dropdown.Option(f"{i['NOMBRE']} ({i['UNIDAD']})", i['ID']) for i in self._insumos],
            width=200,
        )

        # Categoría y unidad
        select_categoria = ft.Dropdown(
            label="Categoría de Medida",
            options=[
                ft.dropdown.Option("📦 PESO", "PESO"),
                ft.dropdown.Option("💧 VOLUMEN", "VOLUMEN"),
                ft.dropdown.Option("📏 LONGITUD", "LONGITUD"),
            ],
            on_change=lambda e: self._actualizar_unidades(e, select_unidad),
            width=150,
        )

        select_unidad = ft.Dropdown(
            label="Unidad",
            width=150,
        )

        # Cantidad
        input_cantidad = ft.TextField(
            label="Cantidad",
            input_filter="0123456789.",
            width=100,
        )

        # Tiempo de preparación
        input_tiempo = ft.TextField(
            label="Tiempo (minutos)",
            input_filter="0123456789",
            value="0",
            width=120,
        )

        def guardar(e):
            try:
                if not select_producto.value or not select_insumo.value or not input_cantidad.value or not select_unidad.value:
                    self._mostrar_error("⚠️ Completa todos los campos")
                    return

                with OBTENER_SESION() as session:
                    receta = MODELO_FORMULA(
                        PRODUCTO_ID=int(select_producto.value),
                        INSUMO_ID=int(select_insumo.value),
                        CANTIDAD=float(input_cantidad.value),
                        UNIDAD=select_unidad.value,
                        TIEMPO_PREP=int(input_tiempo.value),
                        ACTIVA=True,
                    )
                    session.add(receta)
                    session.commit()

                logger.info("Receta creada")
                self._mostrar_exito("✅ Receta creada")
                dlg.open = False
                self._cargar_datos()
                self._tabla_recetas.content[0] = self._crear_tabla_recetas().content[0]
                self._pagina.update()

            except Exception as ex:
                logger.error(f"Error: {ex}")
                self._mostrar_error(f"❌ {ex}")
            finally:
                CERRAR_SESION()

        def cerrar_dialogo(e):
            dlg.open = False
            self._pagina.update()

        dlg = ft.AlertDialog(
            title=ft.Text("📖 Nueva Receta", weight=ft.FontWeight.BOLD),
            content=ft.Column([
                select_producto,
                select_insumo,
                ft.Row([select_categoria, select_unidad], spacing=10),
                ft.Row([input_cantidad, input_tiempo], spacing=10),
            ], spacing=15, width=400),
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar_dialogo),
                ft.ElevatedButton("Crear", on_click=guardar, bgcolor=ft.Colors.AMBER_600),
            ],
        )

        self._pagina.dialog = dlg
        dlg.open = True
        self._pagina.update()

    def _actualizar_unidades(self, e, select_unidad):
        """Actualiza opciones de unidad según categoría"""
        categoria = e.control.value
        if categoria == "PESO":
            unidades = ["g", "kg", "lb", "oz", "arroba"]
        elif categoria == "VOLUMEN":
            unidades = ["ml", "litro", "gallon", "taza", "onza_fl"]
        else:  # LONGITUD
            unidades = ["cm", "m", "km", "in", "ft"]

        select_unidad.options = [ft.dropdown.Option(u, u) for u in unidades]
        select_unidad.value = unidades[0] if unidades else None
        self._pagina.update()

    def _overlay_editar_receta(self, receta_id: int):
        """Overlay para editar receta"""
        receta = next((r for r in self._recetas if r["ID"] == receta_id), None)
        if not receta:
            return

        select_cantidad = ft.TextField(
            label="Cantidad",
            value=str(receta["CANTIDAD"]),
            input_filter="0123456789.",
            width=100,
        )

        select_unidad = ft.Dropdown(
            label="Unidad",
            value=receta["UNIDAD"],
            options=[ft.dropdown.Option(u, u) for u in ["g", "kg", "ml", "litro", "cm", "m"]],
            width=100,
        )

        input_tiempo = ft.TextField(
            label="Tiempo (minutos)",
            value=str(receta["TIEMPO_PREP"]),
            input_filter="0123456789",
            width=120,
        )

        def guardar(e):
            try:
                with OBTENER_SESION() as session:
                    receta_obj = session.query(MODELO_FORMULA).filter_by(ID=receta_id).first()
                    if receta_obj:
                        receta_obj.CANTIDAD = float(select_cantidad.value)
                        receta_obj.UNIDAD = select_unidad.value
                        receta_obj.TIEMPO_PREP = int(input_tiempo.value)
                        session.commit()

                logger.info("Receta actualizada")
                self._mostrar_exito("✅ Receta actualizada")
                dlg.open = False
                self._cargar_datos()
                self._tabla_recetas.content[0] = self._crear_tabla_recetas().content[0]
                self._pagina.update()

            except Exception as ex:
                logger.error(f"Error: {ex}")
                self._mostrar_error(f"❌ {ex}")
            finally:
                CERRAR_SESION()

        def cerrar_dialogo(e):
            dlg.open = False
            self._pagina.update()

        dlg = ft.AlertDialog(
            title=ft.Text(f"✏️ Editar: {receta['PRODUCTO_NOMBRE']}", weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Text(f"Insumo: {receta['INSUMO_NOMBRE']}", size=12, color=ft.Colors.GREY_700),
                ft.Row([select_cantidad, select_unidad, input_tiempo], spacing=10),
            ], spacing=15, width=400),
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar_dialogo),
                ft.ElevatedButton("Guardar", on_click=guardar, bgcolor=ft.Colors.BLUE_600),
            ],
        )

        self._pagina.dialog = dlg
        dlg.open = True
        self._pagina.update()

    def _eliminar_receta(self, receta_id: int):
        """Elimina una receta"""
        try:
            with OBTENER_SESION() as session:
                receta = session.query(MODELO_FORMULA).filter_by(ID=receta_id).first()
                if receta:
                    session.delete(receta)
                    session.commit()

            logger.info("Receta eliminada")
            self._mostrar_exito("✅ Receta eliminada")
            self._cargar_datos()
            self._tabla_recetas.content[0] = self._crear_tabla_recetas().content[0]
            self._pagina.update()

        except Exception as e:
            logger.error(f"Error: {e}")
            self._mostrar_error(f"❌ {e}")
        finally:
            CERRAR_SESION()

    def _mostrar_exito(self, mensaje: str):
        """Muestra mensaje de éxito"""
        self._pagina.snack_bar = ft.SnackBar(
            ft.Text(mensaje, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.GREEN_600,
        )
        self._pagina.snack_bar.open = True
        self._pagina.update()

    def _mostrar_error(self, mensaje: str):
        """Muestra mensaje de error"""
        self._pagina.snack_bar = ft.SnackBar(
            ft.Text(mensaje, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.RED_600,
        )
        self._pagina.snack_bar.open = True
        self._pagina.update()

    def _volver_dashboard(self, e=None):
        """Vuelve al dashboard"""
        from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
        self._pagina.controls.clear()
        self._pagina.controls.append(PaginaAdmin(self._pagina, self.usuario))
        self._pagina.update()

    def _cerrar_sesion(self, e=None):
        """Cierra sesión"""
        pass
