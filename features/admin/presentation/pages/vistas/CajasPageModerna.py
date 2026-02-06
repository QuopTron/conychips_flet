"""
💰 CajasPageModerna - Gestión de Cajas y Movimientos
Sistema mejorado para gestionar cajas, movimientos y análisis de flujo de efectivo
"""

import flet as ft
from typing import Optional, List, Dict
from datetime import datetime, timedelta

from core.base_datos.ConfiguracionBD import (
    MODELO_CAJA, MODELO_CAJA_MOVIMIENTO, MODELO_SUCURSAL, OBTENER_SESION
)
from features.admin.presentation.widgets.LayoutBase import LayoutBase
from core.Constantes import ROLES
from core.decoradores.DecoradorVistas import REQUIERE_ROL


@REQUIERE_ROL(ROLES.ADMIN)
class CajasPageModerna(LayoutBase):
    """Gestión de Cajas con análisis de movimientos y flujo de efectivo"""

    def __init__(self, pagina: ft.Page, usuario):
        super().__init__(
            pagina=pagina,
            usuario=usuario,
            titulo_vista="💰 Gestión de Cajas",
            mostrar_boton_volver=True,
            on_volver_dashboard=self._ir_dashboard,
            on_cerrar_sesion=self._cerrar_sesion
        )

        self.usuario = usuario
        self._pagina = pagina

        # Cache de datos
        self._cajas: List[Dict] = []
        self._movimientos: List[Dict] = []
        self._sucursales: List[Dict] = []
        self._caja_actual_id: Optional[int] = None
        self._filtro_tipo: str = "todos"  # todos, ingreso, egreso
        
        # Referencias UI
        self._tabla_cajas = None
        self._tabla_movimientos = None
        self._stat_saldo_total = None
        self._stat_ingresos = None
        self._stat_egresos = None
        self._stat_ganancias = None

        # Cargar datos PRIMERO
        self._cargar_datos()

        # Construir UI DESPUÉS
        contenido = self._construir_interfaz()
        self.construir(contenido)

    def _cargar_datos(self):
        """Carga cajas, movimientos y sucursales"""
        try:
            with OBTENER_SESION() as sesion:
                # Cargar sucursales
                sucursales = sesion.query(MODELO_SUCURSAL).filter_by(ACTIVA=True).all()
                self._sucursales = [
                    {"ID": s.ID, "NOMBRE": s.NOMBRE}
                    for s in sucursales
                ]

                # Cargar cajas activas
                cajas = sesion.query(MODELO_CAJA).filter_by(ACTIVA=True).all()
                self._cajas = [
                    {
                        "ID": c.ID,
                        "SUCURSAL_ID": c.SUCURSAL_ID,
                        "SUCURSAL": c.SUCURSAL.NOMBRE if c.SUCURSAL else "N/A",
                        "USUARIO": c.USUARIO.NOMBRE if c.USUARIO else "N/A",
                        "FECHA_APERTURA": c.FECHA_APERTURA.strftime("%d/%m/%Y %H:%M") if c.FECHA_APERTURA else "N/A",
                        "MONTO_INICIAL": c.MONTO_INICIAL,
                        "MONTO_FINAL": c.MONTO_FINAL or 0,
                        "GANANCIAS": c.GANANCIAS or 0,
                    }
                    for c in cajas
                ]

                # Cargar movimientos de los últimos 30 días
                fecha_limite = datetime.utcnow() - timedelta(days=30)
                movimientos = sesion.query(MODELO_CAJA_MOVIMIENTO).filter(
                    MODELO_CAJA_MOVIMIENTO.FECHA >= fecha_limite
                ).order_by(MODELO_CAJA_MOVIMIENTO.FECHA.desc()).all()

                self._movimientos = [
                    {
                        "ID": m.ID,
                        "TIPO": m.TIPO,
                        "CATEGORIA": m.CATEGORIA or "Sin categoría",
                        "MONTO": m.MONTO,
                        "DESCRIPCION": m.DESCRIPCION or "N/A",
                        "FECHA": m.FECHA.strftime("%d/%m/%Y %H:%M") if m.FECHA else "N/A",
                        "USUARIO": m.USUARIO.NOMBRE if m.USUARIO else "N/A",
                        "SUCURSAL": m.SUCURSAL.NOMBRE if m.SUCURSAL else "N/A",
                    }
                    for m in movimientos
                ]

        except Exception as e:
            self._mostrar_error(f"Error cargando datos: {str(e)}")

    def _construir_panel_stats(self) -> ft.Container:
        """Construye panel de estadísticas de cajas"""
        
        # Calcular totales
        saldo_total = sum(c["MONTO_FINAL"] for c in self._cajas)
        total_ingresos = sum(m["MONTO"] for m in self._movimientos if m["TIPO"] == "ingreso")
        total_egresos = sum(m["MONTO"] for m in self._movimientos if m["TIPO"] == "egreso")
        ganancias_total = sum(c["GANANCIAS"] for c in self._cajas)

        def crear_stat_card(titulo: str, valor: str, icono: str, color: str) -> ft.Container:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(icono, size=32, color=color),
                    ft.Text(titulo, size=12, color=ft.Colors.GREY_700, weight=ft.FontWeight.W_500),
                    ft.Text(valor, size=18, weight=ft.FontWeight.BOLD, color=color),
                ], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=ft.Colors.WHITE,
                border=ft.Border.all(1, ft.Colors.GREY_300),
                border_radius=8,
                padding=16,
                expand=True,
            )

        self._stat_saldo_total = crear_stat_card(
            "Saldo Total",
            f"S/. {saldo_total:,.2f}",
            ft.Icons.ACCOUNT_BALANCE_WALLET,
            ft.Colors.BLUE_700
        )

        self._stat_ingresos = crear_stat_card(
            "Ingresos (30 días)",
            f"S/. {total_ingresos:,.2f}",
            ft.Icons.TRENDING_UP,
            ft.Colors.GREEN_700
        )

        self._stat_egresos = crear_stat_card(
            "Egresos (30 días)",
            f"S/. {total_egresos:,.2f}",
            ft.Icons.TRENDING_DOWN,
            ft.Colors.RED_700
        )

        self._stat_ganancias = crear_stat_card(
            "Ganancias",
            f"S/. {ganancias_total:,.2f}",
            ft.Icons.SHOW_CHART,
            ft.Colors.AMBER_700
        )

        return ft.Container(
            content=ft.Row([
                self._stat_saldo_total,
                self._stat_ingresos,
                self._stat_egresos,
                self._stat_ganancias,
            ], spacing=16),
            padding=0,
        )

    def _generar_filas_cajas(self) -> List[ft.DataRow]:
        """Genera filas para tabla de cajas"""
        filas = []

        for c in self._cajas:
            saldo_final = c["MONTO_FINAL"]
            estado_color = ft.Colors.GREEN_100 if saldo_final > 0 else ft.Colors.RED_100
            
            filas.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(c["SUCURSAL"], size=10, weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text(c["USUARIO"], size=10)),
                        ft.DataCell(ft.Text(c["FECHA_APERTURA"], size=10)),
                        ft.DataCell(ft.Text(f"S/. {c['MONTO_INICIAL']:,.2f}", size=10)),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(f"S/. {saldo_final:,.2f}", size=10, weight=ft.FontWeight.BOLD),
                                bgcolor=estado_color,
                                padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                                border_radius=4,
                            )
                        ),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(f"S/. {c['GANANCIAS']:,.2f}", size=10, weight=ft.FontWeight.BOLD),
                                bgcolor=ft.Colors.AMBER_100,
                                padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                                border_radius=4,
                            )
                        ),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    ft.Icons.EDIT,
                                    icon_size=18,
                                    on_click=lambda e, caja_id=c["ID"]: self._overlay_editar_caja(caja_id),
                                    tooltip="Editar",
                                ),
                                ft.IconButton(
                                    ft.Icons.DELETE,
                                    icon_size=18,
                                    on_click=lambda e, caja_id=c["ID"]: self._eliminar_caja(caja_id),
                                    tooltip="Cerrar caja",
                                ),
                            ], spacing=0)
                        ),
                    ],
                    color=ft.Colors.GREY_50,
                )
            )

        return filas

    def _generar_filas_movimientos(self) -> List[ft.DataRow]:
        """Genera filas para tabla de movimientos"""
        filas = []

        # Filtrar por tipo si no está en "todos"
        movimientos_filtrados = self._movimientos
        if self._filtro_tipo != "todos":
            movimientos_filtrados = [m for m in self._movimientos if m["TIPO"] == self._filtro_tipo]

        for m in movimientos_filtrados:
            color_fondo = ft.Colors.GREEN_100 if m["TIPO"] == "ingreso" else ft.Colors.RED_100
            icono = ft.Icons.ARROW_UPWARD if m["TIPO"] == "ingreso" else ft.Icons.ARROW_DOWNWARD
            color_icono = ft.Colors.GREEN_700 if m["TIPO"] == "ingreso" else ft.Colors.RED_700
            
            filas.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Row([
                                ft.Icon(icono, size=16, color=color_icono),
                                ft.Text(m["TIPO"].upper(), size=10, weight=ft.FontWeight.BOLD),
                            ], spacing=4)
                        ),
                        ft.DataCell(ft.Text(m["CATEGORIA"], size=10)),
                        ft.DataCell(ft.Text(m["DESCRIPCION"], size=9, overflow=ft.TextOverflow.ELLIPSIS)),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(f"S/. {m['MONTO']:,.2f}", size=10, weight=ft.FontWeight.BOLD),
                                bgcolor=color_fondo,
                                padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                                border_radius=4,
                            )
                        ),
                        ft.DataCell(ft.Text(m["FECHA"], size=9)),
                        ft.DataCell(ft.Text(m["USUARIO"], size=9)),
                        ft.DataCell(ft.Text(m["SUCURSAL"], size=9)),
                        ft.DataCell(
                            ft.IconButton(
                                ft.Icons.DELETE,
                                icon_size=16,
                                on_click=lambda e, mov_id=m["ID"]: self._eliminar_movimiento(mov_id),
                                tooltip="Eliminar",
                            )
                        ),
                    ],
                    color=ft.Colors.WHITE,
                )
            )

        return filas

    def _construir_interfaz(self) -> ft.Container:
        """Construye la interfaz principal"""
        
        # Panel de estadísticas
        panel_stats = self._construir_panel_stats()

        # Tabla de cajas
        self._tabla_cajas = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Sucursal", weight=ft.FontWeight.BOLD, size=11)),
                ft.DataColumn(ft.Text("Usuario", weight=ft.FontWeight.BOLD, size=11)),
                ft.DataColumn(ft.Text("Apertura", weight=ft.FontWeight.BOLD, size=11)),
                ft.DataColumn(ft.Text("Monto Inicial", weight=ft.FontWeight.BOLD, size=11)),
                ft.DataColumn(ft.Text("Saldo Final", weight=ft.FontWeight.BOLD, size=11)),
                ft.DataColumn(ft.Text("Ganancias", weight=ft.FontWeight.BOLD, size=11)),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD, size=11)),
            ],
            rows=self._generar_filas_cajas(),
            vertical_lines=ft.BorderSide(1, ft.Colors.GREY_300),
            horizontal_lines=ft.BorderSide(1, ft.Colors.GREY_300),
            heading_row_height=40,
            data_row_max_height=50,
        )

        # Botones de cajas
        btn_nueva_caja = ft.ElevatedButton(
            "➕ Nueva Caja",
            icon=ft.Icons.ADD,
            on_click=lambda e: self._overlay_crear_caja(),
            bgcolor=ft.Colors.BLUE_600,
            color=ft.Colors.WHITE,
        )

        btn_nuevo_movimiento = ft.ElevatedButton(
            "💸 Registrar Movimiento",
            icon=ft.Icons.ADD,
            on_click=lambda e: self._overlay_crear_movimiento(),
            bgcolor=ft.Colors.GREEN_600,
            color=ft.Colors.WHITE,
        )

        # Filtro de movimientos
        def cambiar_filtro(e):
            self._filtro_tipo = e.control.value
            self._tabla_movimientos.rows = self._generar_filas_movimientos()
            self._pagina.update()

        filtro_movimientos = ft.Dropdown(
            label="Filtrar por tipo",
            value="todos",
            options=[
                ft.dropdown.Option("todos", "Todos"),
                ft.dropdown.Option("ingreso", "Ingresos"),
                ft.dropdown.Option("egreso", "Egresos"),
            ],
            on_select=cambiar_filtro,
            width=200,
        )

        # Tabla de movimientos
        self._tabla_movimientos = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Tipo", weight=ft.FontWeight.BOLD, size=10)),
                ft.DataColumn(ft.Text("Categoría", weight=ft.FontWeight.BOLD, size=10)),
                ft.DataColumn(ft.Text("Descripción", weight=ft.FontWeight.BOLD, size=10)),
                ft.DataColumn(ft.Text("Monto", weight=ft.FontWeight.BOLD, size=10)),
                ft.DataColumn(ft.Text("Fecha", weight=ft.FontWeight.BOLD, size=10)),
                ft.DataColumn(ft.Text("Usuario", weight=ft.FontWeight.BOLD, size=10)),
                ft.DataColumn(ft.Text("Sucursal", weight=ft.FontWeight.BOLD, size=10)),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD, size=10)),
            ],
            rows=self._generar_filas_movimientos(),
            vertical_lines=ft.BorderSide(1, ft.Colors.GREY_300),
            horizontal_lines=ft.BorderSide(1, ft.Colors.GREY_300),
            heading_row_height=40,
            data_row_max_height=45,
        )

        return ft.Container(
            content=ft.Column([
                # Estadísticas
                panel_stats,
                ft.Divider(height=20),

                # Sección de cajas
                ft.Row([
                    ft.Text(f"🏪 Cajas Activas: {len(self._cajas)}", size=14, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    btn_nuevo_movimiento,
                    btn_nueva_caja,
                ], spacing=12, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                ft.Container(
                    content=self._tabla_cajas,
                    border=ft.Border.all(1, ft.Colors.GREY_300),
                    border_radius=8,
                    padding=12,
                    expand=True,
                ),

                ft.Divider(height=20),

                # Sección de movimientos
                ft.Row([
                    ft.Text(f"📊 Movimientos Últimos 30 días: {len(self._movimientos)}", size=14, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    filtro_movimientos,
                ], spacing=12, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                ft.Container(
                    content=self._tabla_movimientos,
                    border=ft.Border.all(1, ft.Colors.GREY_300),
                    border_radius=8,
                    padding=12,
                    expand=True,
                ),
            ], spacing=16, expand=True),
            padding=16,
            expand=True,
        )

    # ==================== OVERLAYS CRUD ====================

    def _overlay_crear_caja(self):
        """Overlay para crear nueva caja"""
        
        # Dropdown de sucursales
        dd_sucursal = ft.Dropdown(
            label="Sucursal",
            options=[ft.dropdown.Option(str(s["ID"]), s["NOMBRE"]) for s in self._sucursales],
            width=300,
        )

        tf_monto_inicial = ft.TextField(
            label="Monto Inicial (S/.)",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=300,
        )

        def guardar(ev):
            if not dd_sucursal.value:
                self._mostrar_error("Selecciona una sucursal")
                return
            
            if not tf_monto_inicial.value.strip():
                self._mostrar_error("El monto inicial es obligatorio")
                return

            try:
                monto = float(tf_monto_inicial.value)
                
                with OBTENER_SESION() as sesion:
                    nueva_caja = MODELO_CAJA(
                        USUARIO_ID=self.usuario.ID,
                        SUCURSAL_ID=int(dd_sucursal.value),
                        FECHA_APERTURA=datetime.utcnow(),
                        MONTO_INICIAL=int(monto * 100),  # Convertir a centavos
                        MONTO_FINAL=int(monto * 100),
                        ACTIVA=True,
                    )
                    sesion.add(nueva_caja)
                    sesion.commit()

                overlay.open = False
                self._pagina.update()
                self._mostrar_exito("✅ Caja creada exitosamente")
                self._cargar_datos()
                self._tabla_cajas.rows = self._generar_filas_cajas()
                self._pagina.update()

            except ValueError:
                self._mostrar_error("El monto debe ser un número válido")
            except Exception as ex:
                self._mostrar_error(f"Error: {str(ex)}")

        overlay = ft.AlertDialog(
            modal=True,
            title=ft.Text("➕ Nueva Caja", size=16, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    dd_sucursal,
                    tf_monto_inicial,
                ], spacing=12),
                width=350,
                padding=16,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: setattr(overlay, 'open', False) or self._pagina.update()),
                ft.ElevatedButton("Crear", on_click=guardar, bgcolor=ft.Colors.BLUE_600),
            ],
        )

        self._pagina.overlay.append(overlay)
        overlay.open = True
        self._pagina.update()

    def _overlay_editar_caja(self, caja_id: int):
        """Overlay para editar caja"""
        
        caja = next((c for c in self._cajas if c["ID"] == caja_id), None)
        if not caja:
            self._mostrar_error("Caja no encontrada")
            return

        tf_monto_final = ft.TextField(
            label="Monto Final (S/.)",
            value=f"{caja['MONTO_FINAL'] / 100:.2f}",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=300,
        )

        tf_ganancias = ft.TextField(
            label="Ganancias (S/.)",
            value=f"{caja['GANANCIAS'] / 100:.2f}",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=300,
        )

        def guardar(ev):
            try:
                monto_final = float(tf_monto_final.value)
                ganancias = float(tf_ganancias.value)

                with OBTENER_SESION() as sesion:
                    c = sesion.query(MODELO_CAJA).filter_by(ID=caja_id).first()
                    if c:
                        c.MONTO_FINAL = int(monto_final * 100)
                        c.GANANCIAS = int(ganancias * 100)
                        sesion.commit()

                overlay.open = False
                self._pagina.update()
                self._mostrar_exito("✅ Caja actualizada")
                self._cargar_datos()
                self._tabla_cajas.rows = self._generar_filas_cajas()
                self._pagina.update()

            except ValueError:
                self._mostrar_error("Los montos deben ser números válidos")
            except Exception as ex:
                self._mostrar_error(f"Error: {str(ex)}")

        overlay = ft.AlertDialog(
            modal=True,
            title=ft.Text("✏️ Editar Caja", size=16, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(f"Sucursal: {caja['SUCURSAL']}", weight=ft.FontWeight.BOLD),
                    ft.Text(f"Monto Inicial: S/. {caja['MONTO_INICIAL'] / 100:.2f}"),
                    tf_monto_final,
                    tf_ganancias,
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

    def _overlay_crear_movimiento(self):
        """Overlay para registrar nuevo movimiento"""
        
        # Dropdown de tipo
        dd_tipo = ft.Dropdown(
            label="Tipo",
            options=[
                ft.dropdown.Option("ingreso", "Ingreso"),
                ft.dropdown.Option("egreso", "Egreso"),
            ],
            width=300,
        )

        dd_categoria = ft.Dropdown(
            label="Categoría",
            options=[
                ft.dropdown.Option("venta", "Venta"),
                ft.dropdown.Option("compra", "Compra"),
                ft.dropdown.Option("deposito", "Depósito"),
                ft.dropdown.Option("retiro", "Retiro"),
                ft.dropdown.Option("otro", "Otro"),
            ],
            width=300,
        )

        tf_monto = ft.TextField(
            label="Monto (S/.)",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=300,
        )

        tf_descripcion = ft.TextField(
            label="Descripción",
            multiline=True,
            width=300,
        )

        dd_sucursal = ft.Dropdown(
            label="Sucursal",
            options=[ft.dropdown.Option(str(s["ID"]), s["NOMBRE"]) for s in self._sucursales],
            width=300,
        )

        def guardar(ev):
            if not dd_tipo.value or not dd_categoria.value or not tf_monto.value or not dd_sucursal.value:
                self._mostrar_error("Completa todos los campos obligatorios")
                return

            try:
                monto = float(tf_monto.value)

                with OBTENER_SESION() as sesion:
                    nuevo_mov = MODELO_CAJA_MOVIMIENTO(
                        USUARIO_ID=self.usuario.ID,
                        SUCURSAL_ID=int(dd_sucursal.value),
                        TIPO=dd_tipo.value,
                        CATEGORIA=dd_categoria.value,
                        MONTO=int(monto * 100),  # Convertir a centavos
                        DESCRIPCION=tf_descripcion.value.strip() or None,
                        FECHA=datetime.utcnow(),
                    )
                    sesion.add(nuevo_mov)
                    sesion.commit()

                overlay.open = False
                self._pagina.update()
                self._mostrar_exito("✅ Movimiento registrado")
                self._cargar_datos()
                self._tabla_movimientos.rows = self._generar_filas_movimientos()
                self._pagina.update()

            except ValueError:
                self._mostrar_error("El monto debe ser un número válido")
            except Exception as ex:
                self._mostrar_error(f"Error: {str(ex)}")

        overlay = ft.AlertDialog(
            modal=True,
            title=ft.Text("💸 Registrar Movimiento", size=16, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    dd_tipo,
                    dd_categoria,
                    tf_monto,
                    tf_descripcion,
                    dd_sucursal,
                ], spacing=12, scroll=ft.ScrollMode.AUTO),
                width=350,
                padding=16,
                height=400,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: setattr(overlay, 'open', False) or self._pagina.update()),
                ft.ElevatedButton("Registrar", on_click=guardar, bgcolor=ft.Colors.GREEN_600),
            ],
        )

        self._pagina.overlay.append(overlay)
        overlay.open = True
        self._pagina.update()

    # ==================== UTILIDADES ====================

    def _eliminar_caja(self, caja_id: int):
        """Cierra una caja (soft delete)"""
        
        try:
            with OBTENER_SESION() as sesion:
                c = sesion.query(MODELO_CAJA).filter_by(ID=caja_id).first()
                if c:
                    c.ACTIVA = False
                    c.FECHA_CIERRE = datetime.utcnow()
                    sesion.commit()

            self._mostrar_exito("✅ Caja cerrada")
            self._cargar_datos()
            self._tabla_cajas.rows = self._generar_filas_cajas()
            self._pagina.update()

        except Exception as ex:
            self._mostrar_error(f"Error: {str(ex)}")

    def _eliminar_movimiento(self, mov_id: int):
        """Elimina un movimiento de caja"""
        
        try:
            with OBTENER_SESION() as sesion:
                m = sesion.query(MODELO_CAJA_MOVIMIENTO).filter_by(ID=mov_id).first()
                if m:
                    sesion.delete(m)
                    sesion.commit()

            self._mostrar_exito("✅ Movimiento eliminado")
            self._cargar_datos()
            self._tabla_movimientos.rows = self._generar_filas_movimientos()
            self._pagina.update()

        except Exception as ex:
            self._mostrar_error(f"Error: {str(ex)}")

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

    def _cerrar_overlay(self):
        """Cierra el overlay"""
        if self._pagina.overlay:
            self._pagina.overlay[-1].open = False
        self._pagina.update()

    def _ir_dashboard(self):
        """Volver al dashboard"""
        self.will_unmount()
        from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
        self._pagina.controls.clear()
        self._pagina.add(PaginaAdmin(self._pagina, self._usuario))
        from core.ui.safe_actions import safe_update
        safe_update(self._pagina)

    def _cerrar_sesion(self, e=None):
        """Cerrar sesión"""
        self.will_unmount()
        from features.autenticacion.presentation.pages.PaginaLogin import PaginaLogin
        self._pagina.controls.clear()
        self._pagina.add(PaginaLogin(self._pagina))
        from core.ui.safe_actions import safe_update
        safe_update(self._pagina)
