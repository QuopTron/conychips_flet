"""
🏭 ProveedoresPageModerna - Gestión de Proveedores
Sistema para gestionar proveedores de insumos y comparar precios
"""

import flet as ft
from typing import Optional, List, Dict
from datetime import datetime

from core.base_datos.ConfiguracionBD import (
    MODELO_PROVEEDOR, MODELO_INSUMO, OBTENER_SESION, TABLA_INSUMO_PROVEEDOR
)
from features.admin.presentation.widgets.LayoutBase import LayoutBase
from core.Constantes import ROLES
from core.decoradores.DecoradorVistas import REQUIERE_ROL


@REQUIERE_ROL(ROLES.ADMIN)
class ProveedoresPageModerna(LayoutBase):
    """Gestión de Proveedores con análisis de precios"""

    def __init__(self, pagina: ft.Page, usuario):
        super().__init__(
            pagina=pagina,
            usuario=usuario,
            titulo_vista="🏭 Gestión de Proveedores",
            mostrar_boton_volver=True,
            on_volver_dashboard=self._ir_dashboard,
            on_cerrar_sesion=self._cerrar_sesion
        )

        self.usuario = usuario
        self._pagina = pagina

        # Cache de proveedores
        self._proveedores: List[Dict] = []
        self._insumos: List[Dict] = []
        self._insumos_multiples: Dict[str, List[Dict]] = {}  # Insumos con múltiples proveedores
        
        # Tabla (referencia para actualizar)
        self._tabla_proveedores = None
        self._tab_analisis = None

        # Cargar datos PRIMERO
        self._cargar_datos()

        # Construir UI DESPUÉS
        contenido = self._construir_interfaz()
        self.construir(contenido)

    def _cargar_datos(self):
        """Carga proveedores, insumos y análiza relaciones"""
        try:
            with OBTENER_SESION() as sesion:
                # Cargar proveedores activos
                proveedores = sesion.query(MODELO_PROVEEDOR).filter_by(ACTIVO=True).all()
                self._proveedores = [
                    {
                        "ID": p.ID,
                        "NOMBRE": p.NOMBRE,
                        "TELEFONO": p.TELEFONO or "N/A",
                        "EMAIL": p.EMAIL or "N/A",
                        "DIRECCION": p.DIRECCION or "N/A",
                        "UBICACION": p.UBICACION or "N/A",
                        "FECHA_CREACION": p.FECHA_CREACION.strftime("%d/%m/%Y") if p.FECHA_CREACION else "N/A",
                        "INSUMOS": [i.NOMBRE for i in p.INSUMOS] if p.INSUMOS else [],
                    }
                    for p in proveedores
                ]

                # Cargar insumos activos con sus proveedores
                insumos = sesion.query(MODELO_INSUMO).filter_by(ACTIVO=True).all()
                self._insumos = [
                    {
                        "ID": i.ID,
                        "NOMBRE": i.NOMBRE,
                        "UNIDAD": i.UNIDAD,
                        "PRECIO_UNITARIO": i.PRECIO_UNITARIO,
                        "STOCK_ACTUAL": i.STOCK_ACTUAL,
                        "PROVEEDORES": [p.NOMBRE for p in i.PROVEEDORES],
                    }
                    for i in insumos
                ]
                
                # Agrupar insumos con múltiples proveedores
                self._insumos_multiples = {}
                for insumo in self._insumos:
                    if len(insumo["PROVEEDORES"]) > 1:
                        self._insumos_multiples[insumo["NOMBRE"]] = insumo

        except Exception as e:
            self._mostrar_error(f"Error cargando datos: {str(e)}")

    def _construir_panel_analisis(self) -> ft.Container:
        """Construye panel de análisis de precios comparativos"""
        
        filas = []
        
        if not self._insumos_multiples:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.INFO, size=48, color=ft.Colors.GREY_400),
                    ft.Text("No hay insumos con múltiples proveedores", size=14, color=ft.Colors.GREY_700),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                height=300,
            )
        
        # Encabezado
        filas.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text("Insumo", weight=ft.FontWeight.BOLD, size=11)),
                    ft.DataCell(ft.Text("Unidad", weight=ft.FontWeight.BOLD, size=11)),
                    ft.DataCell(ft.Text("Proveedor", weight=ft.FontWeight.BOLD, size=11)),
                    ft.DataCell(ft.Text("Precio Unit.", weight=ft.FontWeight.BOLD, size=11)),
                    ft.DataCell(ft.Text("Stock", weight=ft.FontWeight.BOLD, size=11)),
                ],
                selected=False,
                color=ft.Colors.GREY_100,
            )
        )
        
        # Datos por insumo
        for insumo_nombre, insumo_data in self._insumos_multiples.items():
            proveedores = insumo_data["PROVEEDORES"]
            
            for i, proveedor in enumerate(proveedores):
                color_fondo = ft.Colors.LIGHT_GREEN_100 if i == 0 else ft.Colors.LIGHT_BLUE_100 if i == 1 else ft.Colors.WHITE
                
                filas.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(
                                ft.Text(
                                    insumo_nombre if i == 0 else "",
                                    size=10,
                                    weight=ft.FontWeight.BOLD if i == 0 else ft.FontWeight.NORMAL
                                )
                            ),
                            ft.DataCell(ft.Text(insumo_data["UNIDAD"], size=10)),
                            ft.DataCell(
                                ft.Container(
                                    content=ft.Text(proveedor, size=10, weight=ft.FontWeight.BOLD),
                                    bgcolor=ft.Colors.BLUE_100,
                                    padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                                    border_radius=4,
                                )
                            ),
                            ft.DataCell(
                                ft.Container(
                                    content=ft.Text(f"${insumo_data['PRECIO_UNITARIO']}", size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                    bgcolor=ft.Colors.GREEN_600 if i == 0 else ft.Colors.ORANGE_600,
                                    padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                                    border_radius=4,
                                )
                            ),
                            ft.DataCell(ft.Text(f"{insumo_data['STOCK_ACTUAL']} {insumo_data['UNIDAD']}", size=10)),
                        ],
                        color=color_fondo,
                    )
                )
        
        tabla_analisis = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Insumo", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Unidad", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Proveedor", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Precio Unitario", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Stock Disponible", weight=ft.FontWeight.BOLD)),
            ],
            rows=filas,
            vertical_lines=ft.BorderSide(1, ft.Colors.GREY_300),
            horizontal_lines=ft.BorderSide(1, ft.Colors.GREY_300),
            heading_row_height=40,
            data_row_max_height=45,
        )
        
        info = ft.Column([
            ft.Text(f"🎯 {len(self._insumos_multiples)} insumos con múltiples proveedores", size=12, weight=ft.FontWeight.BOLD),
            ft.Text("🟢 Verde = Mejor precio | 🟠 Naranja = Alternativa", size=10, color=ft.Colors.GREY_700),
        ], spacing=8)
        
        return ft.Container(
            content=ft.Column([
                info,
                ft.Container(
                    content=tabla_analisis,
                    border=ft.Border.all(1, ft.Colors.GREY_300),
                    border_radius=8,
                    padding=12,
                    expand=True,
                ),
            ], spacing=16),
            padding=16,
            expand=True,
        )

    def _actualizar_tabla(self):
        """Actualiza la tabla de proveedores"""
        if self._tabla_proveedores:
            self._tabla_proveedores.rows = self._generar_filas_proveedores()
            self._pagina.update()

    def _construir_interfaz(self) -> ft.Container:
        """Construye la interfaz principal sin tabs - solo lista de proveedores"""
        
        # Tabla de proveedores
        self._tabla_proveedores = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre", weight=ft.FontWeight.BOLD, size=11)),
                ft.DataColumn(ft.Text("Teléfono", weight=ft.FontWeight.BOLD, size=11)),
                ft.DataColumn(ft.Text("Email", weight=ft.FontWeight.BOLD, size=11)),
                ft.DataColumn(ft.Text("Insumos", weight=ft.FontWeight.BOLD, size=11)),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD, size=11)),
            ],
            rows=self._generar_filas_proveedores(),
            vertical_lines=ft.BorderSide(1, ft.Colors.GREY_300),
            horizontal_lines=ft.BorderSide(1, ft.Colors.GREY_300),
            border=ft.Border.all(1, ft.Colors.GREY_300),
            heading_row_height=40,
            data_row_max_height=50,
        )

        # Botones de acción
        btn_nuevo_proveedor = ft.ElevatedButton(
            "➕ Nuevo Proveedor",
            icon=ft.Icons.ADD,
            on_click=lambda e: self._overlay_crear_proveedor(),
            bgcolor=ft.Colors.BLUE_600,
            color=ft.Colors.WHITE,
        )

        btn_nuevo_insumo = ft.ElevatedButton(
            "📦 Nuevo Insumo",
            icon=ft.Icons.ADD,
            on_click=lambda e: self._overlay_crear_insumo(),
            bgcolor=ft.Colors.GREEN_600,
            color=ft.Colors.WHITE,
        )

        # Panel de análisis de precios
        panel_analisis = self._construir_panel_analisis()

        # Sección de análisis
        seccion_analisis = ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Text("💰 Análisis de Precios - Comparativa de Proveedores", weight=ft.FontWeight.BOLD, size=12),
                    ft.Text(f"({len(self._insumos_multiples)} insumos)", size=10, color=ft.Colors.GREY_700),
                ], spacing=12, wrap=False),
                padding=12,
                bgcolor=ft.Colors.BLUE_50,
                border_radius=8,
            ),
            panel_analisis,
        ], spacing=8)

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(f"📦 Proveedores Activos: {len(self._proveedores)}", size=14, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    btn_nuevo_insumo,
                    btn_nuevo_proveedor,
                ], spacing=12, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Container(
                    content=self._tabla_proveedores,
                    border=ft.Border.all(1, ft.Colors.GREY_300),
                    border_radius=8,
                    padding=12,
                    expand=True,
                ),
                
                ft.Divider(height=20),
                
                seccion_analisis,
            ], spacing=16, expand=True),
            padding=16,
            expand=True,
        )

    def _generar_filas_proveedores(self) -> List[ft.DataRow]:
        """Genera filas para tabla de proveedores"""
        filas = []

        for p in self._proveedores:
            insumos_texto = ", ".join(p["INSUMOS"]) if p["INSUMOS"] else "Sin insumos"
            
            filas.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(p["NOMBRE"], size=10, weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text(p["TELEFONO"], size=10)),
                        ft.DataCell(ft.Text(p["EMAIL"], size=10, overflow=ft.TextOverflow.ELLIPSIS)),
                        ft.DataCell(ft.Text(insumos_texto, size=9, overflow=ft.TextOverflow.ELLIPSIS)),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    ft.Icons.EDIT,
                                    icon_size=16,
                                    tooltip="Editar",
                                    on_click=lambda e, pid=p["ID"]: self._overlay_editar_proveedor(pid),
                                ),
                                ft.IconButton(
                                    ft.Icons.DELETE,
                                    icon_size=16,
                                    tooltip="Eliminar",
                                    on_click=lambda e, pid=p["ID"]: self._eliminar_proveedor(pid),
                                ),
                            ], spacing=4)
                        ),
                    ]
                )
            )

        return filas

    # ==================== OVERLAYS ====================

    def _overlay_crear_proveedor(self):
        """Overlay para crear nuevo proveedor"""
        tf_nombre = ft.TextField(label="Nombre *", width=300)
        tf_telefono = ft.TextField(label="Teléfono", width=300)
        tf_email = ft.TextField(label="Email", width=300)
        tf_direccion = ft.TextField(label="Dirección", width=300, multiline=True)
        tf_ubicacion = ft.TextField(label="Ubicación", width=300, multiline=True)

        def guardar(ev):
            if not tf_nombre.value.strip():
                self._mostrar_error("El nombre es obligatorio")
                return

            try:
                with OBTENER_SESION() as sesion:
                    # Verificar si existe
                    existe = sesion.query(MODELO_PROVEEDOR).filter_by(
                        NOMBRE=tf_nombre.value.strip()
                    ).first()
                    
                    if existe:
                        self._mostrar_error("El proveedor ya existe")
                        return

                    nuevo = MODELO_PROVEEDOR(
                        NOMBRE=tf_nombre.value.strip(),
                        TELEFONO=tf_telefono.value.strip() or None,
                        EMAIL=tf_email.value.strip() or None,
                        DIRECCION=tf_direccion.value.strip() or None,
                        UBICACION=tf_ubicacion.value.strip() or None,
                        ACTIVO=True,
                    )
                    sesion.add(nuevo)
                    sesion.commit()
                    sesion.flush()

                overlay.open = False
                self._pagina.update()
                self._mostrar_exito("Proveedor creado exitosamente")
                self._cargar_datos()
                self._actualizar_tabla()

            except Exception as ex:
                self._mostrar_error(f"Error: {str(ex)}")

        overlay = ft.AlertDialog(
            modal=True,
            title=ft.Text("➕ Nuevo Proveedor", size=16, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    tf_nombre,
                    tf_telefono,
                    tf_email,
                    tf_direccion,
                    tf_ubicacion,
                ], spacing=12, scroll=ft.ScrollMode.AUTO),
                width=350,
                padding=16,
                height=400,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: setattr(overlay, 'open', False) or self._pagina.update()),
                ft.ElevatedButton("Guardar", on_click=guardar, bgcolor=ft.Colors.GREEN_600),
            ],
        )

        self._pagina.overlay.append(overlay)
        overlay.open = True
        self._pagina.update()

    def _overlay_editar_proveedor(self, proveedor_id: int):
        """Overlay para editar proveedor y asociar insumos"""
        proveedor = next((p for p in self._proveedores if p["ID"] == proveedor_id), None)
        if not proveedor:
            return

        tf_nombre = ft.TextField(label="Nombre *", value=proveedor["NOMBRE"], width=300)
        tf_telefono = ft.TextField(label="Teléfono", value=proveedor["TELEFONO"], width=300)
        tf_email = ft.TextField(label="Email", value=proveedor["EMAIL"], width=300)
        tf_direccion = ft.TextField(label="Dirección", value=proveedor["DIRECCION"], width=300, multiline=True)
        tf_ubicacion = ft.TextField(label="Ubicación", value=proveedor["UBICACION"], width=300, multiline=True)

        # Checkboxes para insumos
        checkboxes_insumos = []
        insumos_seleccionados = proveedor["INSUMOS"]
        
        for insumo in self._insumos:
            cb = ft.Checkbox(
                label=f"{insumo['NOMBRE']} ({insumo['UNIDAD']})",
                value=insumo["NOMBRE"] in insumos_seleccionados,
                data=insumo["ID"],
            )
            checkboxes_insumos.append(cb)

        def guardar(ev):
            if not tf_nombre.value.strip():
                self._mostrar_error("El nombre es obligatorio")
                return

            try:
                with OBTENER_SESION() as sesion:
                    p = sesion.query(MODELO_PROVEEDOR).filter_by(ID=proveedor_id).first()
                    if p:
                        # Verificar que no exista otro con el mismo nombre
                        existe = sesion.query(MODELO_PROVEEDOR).filter(
                            MODELO_PROVEEDOR.NOMBRE == tf_nombre.value.strip(),
                            MODELO_PROVEEDOR.ID != proveedor_id
                        ).first()
                        
                        if existe:
                            self._mostrar_error("El nombre ya existe en otro proveedor")
                            return

                        p.NOMBRE = tf_nombre.value.strip()
                        p.TELEFONO = tf_telefono.value.strip() or None
                        p.EMAIL = tf_email.value.strip() or None
                        p.DIRECCION = tf_direccion.value.strip() or None
                        p.UBICACION = tf_ubicacion.value.strip() or None
                        
                        # Actualizar insumos asociados
                        insumos_marcados = [cb.data for cb in checkboxes_insumos if cb.value]
                        insumos_obj = sesion.query(MODELO_INSUMO).filter(MODELO_INSUMO.ID.in_(insumos_marcados)).all()
                        p.INSUMOS = insumos_obj
                        
                        sesion.commit()
                        sesion.flush()

                overlay.open = False
                self._pagina.update()
                self._mostrar_exito("Proveedor actualizado")
                self._cargar_datos()
                self._actualizar_tabla()

            except Exception as ex:
                self._mostrar_error(f"Error: {str(ex)}")

        overlay = ft.AlertDialog(
            modal=True,
            title=ft.Text("✏️ Editar Proveedor", size=16, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    tf_nombre,
                    tf_telefono,
                    tf_email,
                    tf_direccion,
                    tf_ubicacion,
                    ft.Divider(),
                    ft.Text("Insumos que proporciona:", weight=ft.FontWeight.BOLD, size=12),
                    ft.Column(checkboxes_insumos, scroll=ft.ScrollMode.AUTO, height=150),
                ], spacing=12, scroll=ft.ScrollMode.AUTO),
                width=350,
                padding=16,
                height=500,
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

    def _mostrar_error(self, mensaje: str):
        """Muestra mensaje de error"""
        snack = ft.SnackBar(ft.Text(mensaje, color=ft.Colors.WHITE))
        snack.bgcolor = ft.Colors.RED
        self._pagina.snack_bar = snack
        snack.open = True
        self._pagina.update()

    def _mostrar_exito(self, mensaje: str):
        """Muestra mensaje de éxito"""
        snack = ft.SnackBar(ft.Text(mensaje, color=ft.Colors.WHITE))
        snack.bgcolor = ft.Colors.GREEN
        self._pagina.snack_bar = snack
        snack.open = True
        self._pagina.update()

    def _eliminar_proveedor(self, proveedor_id: int):
        """Elimina un proveedor (marca como inactivo)"""
        try:
            with OBTENER_SESION() as sesion:
                p = sesion.query(MODELO_PROVEEDOR).filter_by(ID=proveedor_id).first()
                if p:
                    p.ACTIVO = False
                    sesion.commit()
                    sesion.flush()
                    
                    self._mostrar_exito("Proveedor eliminado")
                    self._cargar_datos()
                    self._actualizar_tabla()
                else:
                    self._mostrar_error("Proveedor no encontrado")

        except Exception as ex:
            self._mostrar_error(f"Error al eliminar: {str(ex)}")

    def _overlay_crear_insumo(self):
        """Overlay para crear nuevo insumo con proveedores y precios específicos"""
        tf_nombre = ft.TextField(label="Nombre del Insumo", width=400)
        tf_unidad = ft.TextField(label="Unidad (kg, L, unidad, etc)", width=400)
        tf_precio_base = ft.TextField(label="Precio Unitario Base", keyboard_type=ft.KeyboardType.NUMBER, width=400)
        tf_stock = ft.TextField(label="Stock Inicial", value="0", keyboard_type=ft.KeyboardType.NUMBER, width=400)
        tf_tiempo_prep = ft.TextField(label="Tiempo Preparación (minutos)", value="0", keyboard_type=ft.KeyboardType.NUMBER, width=400)
        tf_notas = ft.TextField(label="Notas", multiline=True, min_lines=3, width=400)

        # Filas de proveedores con checkbox y precio
        proveedores_filas = []
        proveedores_datos = {}  # {proveedor_id: (checkbox, precio_textfield)}
        
        for prov in self._proveedores:
            cb = ft.Checkbox(label=prov["NOMBRE"], value=False)
            tf_precio_prov = ft.TextField(
                label=f"Precio",
                keyboard_type=ft.KeyboardType.NUMBER,
                width=120,
                visible=False,  # Se hace visible cuando se marca
                on_focus=lambda e, cbox=cb: None
            )
            
            # Función para mostrar/ocultar campo de precio
            def toggle_precio(e, checkbox=cb, price_field=tf_precio_prov):
                price_field.visible = checkbox.value
                e.control.page.update()
            
            cb.on_change = toggle_precio
            
            fila = ft.Row([
                cb,
                tf_precio_prov,
            ], spacing=12, alignment=ft.MainAxisAlignment.START)
            
            proveedores_filas.append(fila)
            proveedores_datos[prov["ID"]] = (cb, tf_precio_prov)

        # Container scrollable para proveedores
        proveedores_scroll = ft.Column(
            proveedores_filas,
            spacing=8,
            height=200,
            scroll=ft.ScrollMode.AUTO
        )

        def guardar_insumo(e):
            nombre = tf_nombre.value.strip()
            unidad = tf_unidad.value.strip()
            precio_base_str = tf_precio_base.value.strip()
            stock_str = tf_stock.value.strip()
            tiempo_prep_str = tf_tiempo_prep.value.strip()
            notas = tf_notas.value.strip()

            # Validaciones
            if not nombre:
                self._mostrar_error("El nombre del insumo es obligatorio")
                return
            if not unidad:
                self._mostrar_error("La unidad es obligatoria")
                return
            if not precio_base_str:
                self._mostrar_error("El precio es obligatorio")
                return

            try:
                precio_base = float(precio_base_str)
                stock = int(stock_str) if stock_str else 0
                tiempo_prep = int(tiempo_prep_str) if tiempo_prep_str else 0

                with OBTENER_SESION() as sesion:
                    # Verificar si ya existe
                    existe = sesion.query(MODELO_INSUMO).filter_by(NOMBRE=nombre).first()
                    if existe:
                        self._mostrar_error(f"El insumo '{nombre}' ya existe")
                        return

                    # Crear nuevo insumo
                    nuevo_insumo = MODELO_INSUMO(
                        NOMBRE=nombre,
                        UNIDAD=unidad,
                        PRECIO_UNITARIO=int(precio_base * 100),  # Guardar en centavos
                        STOCK_ACTUAL=stock,
                        TIEMPO_PREP=tiempo_prep,
                        NOTAS=notas,
                        ACTIVO=True
                    )
                    sesion.add(nuevo_insumo)
                    sesion.commit()
                    sesion.flush()

                    # Asociar proveedores seleccionados con sus precios
                    proveedores_asociados = 0
                    for proveedor_id, (checkbox, precio_field) in proveedores_datos.items():
                        if checkbox.value:
                            proveedor = sesion.query(MODELO_PROVEEDOR).filter_by(ID=proveedor_id).first()
                            if proveedor:
                                precio_prov_str = precio_field.value.strip()
                                try:
                                    precio_prov = float(precio_prov_str) if precio_prov_str else precio_base
                                    # Actualizar la relación con el precio específico del proveedor
                                    nuevo_insumo.PROVEEDORES.append(proveedor)
                                    sesion.flush()
                                    
                                    # Actualizar precio en la relación
                                    from sqlalchemy import update
                                    stmt = update(TABLA_INSUMO_PROVEEDOR).where(
                                        TABLA_INSUMO_PROVEEDOR.c.INSUMO_ID == nuevo_insumo.ID,
                                        TABLA_INSUMO_PROVEEDOR.c.PROVEEDOR_ID == proveedor_id
                                    ).values(PRECIO_PROVEEDOR=int(precio_prov * 100))  # Centavos
                                    sesion.execute(stmt)
                                    proveedores_asociados += 1
                                except ValueError:
                                    pass
                    
                    sesion.commit()
                    sesion.flush()

                    msg = f"✅ Insumo '{nombre}' creado"
                    if proveedores_asociados > 0:
                        msg += f" y asociado a {proveedores_asociados} proveedor(es)"
                    self._mostrar_exito(msg)
                    self._cargar_datos()
                    self._actualizar_tabla()
                    
                    # Cerrar overlay
                    if self._pagina.overlay:
                        self._pagina.overlay.pop()
                    self._pagina.update()

            except ValueError:
                self._mostrar_error("El precio y stock deben ser números válidos")
            except Exception as ex:
                self._mostrar_error(f"Error al crear insumo: {str(ex)}")

        # Overlay
        overlay = ft.AlertDialog(
            title=ft.Text("📦 Nuevo Insumo", size=16, weight=ft.FontWeight.BOLD),
            content=ft.Column([
                tf_nombre,
                tf_unidad,
                tf_precio_base,
                tf_stock,
                tf_tiempo_prep,
                tf_notas,
                ft.Divider(),
                ft.Text("👥 Asociar Proveedores (con precios específicos):", weight=ft.FontWeight.BOLD, size=12),
                proveedores_scroll,
            ], spacing=12, width=500, height=600, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self._cerrar_overlay()),
                ft.ElevatedButton(
                    "💾 Guardar",
                    bgcolor=ft.Colors.GREEN_600,
                    color=ft.Colors.WHITE,
                    on_click=guardar_insumo
                ),
            ],
        )
        self._pagina.overlay.append(overlay)
        overlay.open = True
        self._pagina.update()

    def _cerrar_overlay(self):
        """Cierra el último overlay"""
        if self._pagina.overlay:
            self._pagina.overlay.pop()
            self._pagina.update()
