"""
📅 HorariosPageModerna V2 - SIMPLIFICADA Y CLARA
Sistema de Gestión de Horarios con Plantillas Reutilizables

CONCEPTOS:
- HORARIOS: Asignaciones reales de horarios a usuarios
- PLANTILLAS: Horarios modelo reutilizables
"""

import flet as ft
from typing import Optional, List, Dict
from datetime import datetime
import json

from core.base_datos.ConfiguracionBD import (
    MODELO_HORARIO, MODELO_USUARIO, MODELO_PLANTILLA, OBTENER_SESION
)
from features.admin.presentation.widgets.LayoutBase import LayoutBase
from core.Constantes import ROLES
from core.decoradores.DecoradorVistas import REQUIERE_ROL

# Constantes
DIAS_SEMANA = [
    ("LUNES", "Lun", "🟢", ft.Colors.GREEN_600),
    ("MARTES", "Mar", "🔵", ft.Colors.BLUE_600),
    ("MIERCOLES", "Mié", "🟣", ft.Colors.PURPLE_600),
    ("JUEVES", "Jue", "🟠", ft.Colors.ORANGE_600),
    ("VIERNES", "Vie", "🔴", ft.Colors.RED_600),
    ("SABADO", "Sáb", "🟡", ft.Colors.AMBER_600),
    ("DOMINGO", "Dom", "⚪", ft.Colors.GREY_600),
]


@REQUIERE_ROL(ROLES.ADMIN)
class HorariosPageModerna(LayoutBase):
    """Gestión de Horarios - VERSIÓN SIMPLIFICADA"""

    def __init__(self, pagina: ft.Page, usuario):
        # Inicializar LayoutBase
        super().__init__(
            pagina=pagina,
            usuario=usuario,
            titulo_vista="📅 Gestión de Horarios",
            mostrar_boton_volver=True,
            on_volver_dashboard=self._volver_dashboard,
            on_cerrar_sesion=self._cerrar_sesion
        )

        self.usuario = usuario
        self._pagina = pagina

        # Caches
        self._usuarios: List[Dict] = []
        self._horarios: List[Dict] = []
        self._plantillas: List[Dict] = []

        # Construir UI
        contenido = self._construir_interfaz()
        self.construir(contenido)

        # Cargar datos
        self._cargar_datos()

    def _cargar_datos(self):
        """Carga usuarios, horarios y plantillas"""
        try:
            with OBTENER_SESION() as sesion:
                # Cargar usuarios activos
                usuarios = sesion.query(MODELO_USUARIO).filter_by(ACTIVO=True).all()
                self._usuarios = [
                    {
                        "ID": u.ID,
                        "NOMBRE_USUARIO": u.NOMBRE_USUARIO,
                        "EMAIL": u.EMAIL,
                    }
                    for u in usuarios
                ]

                # Cargar horarios
                horarios = sesion.query(MODELO_HORARIO).filter_by(ACTIVO=True).all()
                self._horarios = [
                    {
                        "ID": h.ID,
                        "USUARIO_ID": h.USUARIO_ID,
                        "DIA_SEMANA": h.DIA_SEMANA,
                        "HORA_INICIO": h.HORA_INICIO,
                        "HORA_FIN": h.HORA_FIN,
                        "USUARIO_NOMBRE": next(
                            (u["NOMBRE_USUARIO"] for u in self._usuarios if u["ID"] == h.USUARIO_ID),
                            "?"
                        ),
                    }
                    for h in horarios
                ]

                # Cargar plantillas
                plantillas = sesion.query(MODELO_PLANTILLA).filter_by(ACTIVO=True).all()
                self._plantillas = [
                    {
                        "ID": p.ID,
                        "NOMBRE": p.NOMBRE,
                        "DESCRIPCION": p.DESCRIPCION,
                        "HORA_INICIO": p.HORA_INICIO,
                        "HORA_FIN": p.HORA_FIN,
                        "DIAS": json.loads(p.DIAS) if p.DIAS else [],
                    }
                    for p in plantillas
                ]

        except Exception as e:
            self._mostrar_error(f"Error cargando datos: {str(e)}")

    def _construir_interfaz(self) -> ft.Container:
        """Construye la interfaz principal"""

        # ===== HEADER =====
        header = ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.SCHEDULE, size=32, color=ft.Colors.BLUE_700),
                    ft.Column([
                        ft.Text("📅 Gestión de Horarios", size=22, weight=ft.FontWeight.BOLD),
                        ft.Text("Crea y asigna horarios a usuarios", size=11, color=ft.Colors.GREY_600),
                    ], spacing=2),
                ], spacing=12),
                ft.Row([
                    ft.ElevatedButton(
                        "➕ Nuevo Horario",
                        on_click=self._overlay_crear_horario,
                        bgcolor=ft.Colors.BLUE_600,
                        color=ft.Colors.WHITE,
                    ),
                    ft.ElevatedButton(
                        "📦 Nueva Plantilla",
                        on_click=self._overlay_crear_plantilla,
                        bgcolor=ft.Colors.AMBER_600,
                        color=ft.Colors.WHITE,
                    ),
                    ft.ElevatedButton(
                        "🔄 Aplicar Plantilla",
                        on_click=self._overlay_aplicar_plantilla,
                        bgcolor=ft.Colors.TEAL_600,
                        color=ft.Colors.WHITE,
                    ),
                ], spacing=8),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=16,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
        )

        # ===== TABLA DE HORARIOS =====
        self._tabla_horarios = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Usuario", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Día", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Inicio", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Fin", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
            ],
            rows=self._generar_filas_horarios(),
            border_radius=8,
        )

        contenedor_tabla = ft.Container(
            content=self._tabla_horarios,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=8,
            padding=12,
        )

        # ===== CONTENIDO PRINCIPAL =====
        contenido = ft.Column([
            header,
            ft.Text("📋 Horarios Asignados", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800),
            contenedor_tabla,
        ], spacing=16, expand=True)

        return ft.Container(
            content=contenido,
            padding=20,
            expand=True,
        )

    def _generar_filas_horarios(self) -> List[ft.DataRow]:
        """Genera filas para la tabla de horarios"""
        filas = []

        for h in self._horarios:
            filas.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(h["USUARIO_NOMBRE"], size=10)),
                        ft.DataCell(ft.Text(h["DIA_SEMANA"], size=10)),
                        ft.DataCell(ft.Text(h["HORA_INICIO"], size=10)),
                        ft.DataCell(ft.Text(h["HORA_FIN"], size=10)),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    ft.Icons.EDIT,
                                    icon_size=16,
                                    tooltip="Editar",
                                    on_click=lambda e, hid=h["ID"]: self._overlay_editar_horario(hid),
                                ),
                                ft.IconButton(
                                    ft.Icons.DELETE,
                                    icon_size=16,
                                    tooltip="Eliminar",
                                    on_click=lambda e, hid=h["ID"]: self._eliminar_horario(hid),
                                ),
                            ], spacing=4)
                        ),
                    ]
                )
            )

        return filas

    # ==================== OVERLAYS ====================

    def _overlay_crear_horario(self, e):
        """Overlay para crear nuevo horario"""
        dd_usuario = ft.Dropdown(
            label="Selecciona Usuario",
            options=[
                ft.dropdown.Option(key=str(u["ID"]), text=u["NOMBRE_USUARIO"])
                for u in self._usuarios
            ],
            width=300,
        )

        dd_dia = ft.Dropdown(
            label="Selecciona Día",
            options=[
                ft.dropdown.Option(key=d[0], text=f"{d[2]} {d[0]}")
                for d in DIAS_SEMANA
            ],
            width=300,
        )

        tf_inicio = ft.TextField(label="Hora Inicio (HH:MM)", width=140)
        tf_fin = ft.TextField(label="Hora Fin (HH:MM)", width=140)

        def guardar(ev):
            if not dd_usuario.value or not dd_dia.value or not tf_inicio.value or not tf_fin.value:
                self._mostrar_error("Todos los campos son obligatorios")
                return

            try:
                with OBTENER_SESION() as sesion:
                    # Validar horario único
                    existe = sesion.query(MODELO_HORARIO).filter_by(
                        USUARIO_ID=int(dd_usuario.value),
                        DIA_SEMANA=dd_dia.value
                    ).first()

                    if existe:
                        self._mostrar_error("Este usuario ya tiene horario en ese día")
                        return

                    # Crear horario
                    nuevo = MODELO_HORARIO(
                        USUARIO_ID=int(dd_usuario.value),
                        DIA_SEMANA=dd_dia.value,
                        HORA_INICIO=tf_inicio.value,
                        HORA_FIN=tf_fin.value,
                        ACTIVO=True,
                    )
                    sesion.add(nuevo)
                    sesion.commit()

                overlay.open = False
                self._pagina.update()
                self._mostrar_exito("Horario creado exitosamente")
                self._cargar_datos()

            except Exception as ex:
                self._mostrar_error(f"Error: {str(ex)}")

        overlay = ft.AlertDialog(
            modal=True,
            title=ft.Text("➕ Crear Nuevo Horario", size=16, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    dd_usuario,
                    dd_dia,
                    ft.Row([tf_inicio, tf_fin], spacing=8),
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

    def _overlay_crear_plantilla(self, e):
        """Overlay para crear nueva plantilla"""
        tf_nombre = ft.TextField(label="Nombre *", width=300)
        tf_descripcion = ft.TextField(label="Descripción", width=300, multiline=True)
        tf_inicio = ft.TextField(label="Hora Inicio (HH:MM) *", width=140)
        tf_fin = ft.TextField(label="Hora Fin (HH:MM) *", width=140)

        checks_dias = {}
        dias_row = ft.Row(wrap=True)

        for dia, abrev, emoji, _ in DIAS_SEMANA:
            check = ft.Checkbox(label=f"{emoji} {abrev}")
            checks_dias[dia] = check
            dias_row.controls.append(check)

        def guardar(ev):
            if not tf_nombre.value or not tf_inicio.value or not tf_fin.value:
                self._mostrar_error("Nombre, Inicio y Fin son obligatorios")
                return

            dias_seleccionados = [d for d, c in checks_dias.items() if c.value]
            if not dias_seleccionados:
                self._mostrar_error("Debes seleccionar al menos un día")
                return

            try:
                with OBTENER_SESION() as sesion:
                    nueva = MODELO_PLANTILLA(
                        NOMBRE=tf_nombre.value,
                        DESCRIPCION=tf_descripcion.value or None,
                        HORA_INICIO=tf_inicio.value,
                        HORA_FIN=tf_fin.value,
                        DIAS=json.dumps(dias_seleccionados),
                        CREADO_POR=self.usuario.ID,
                        ACTIVO=True,
                    )
                    sesion.add(nueva)
                    sesion.commit()

                overlay.open = False
                self._pagina.update()
                self._mostrar_exito("Plantilla creada exitosamente")
                self._cargar_datos()

            except Exception as ex:
                self._mostrar_error(f"Error: {str(ex)}")

        overlay = ft.AlertDialog(
            modal=True,
            title=ft.Text("📦 Crear Nueva Plantilla", size=16, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    tf_nombre,
                    tf_descripcion,
                    ft.Row([tf_inicio, tf_fin], spacing=8),
                    ft.Text("Días:", size=11, weight=ft.FontWeight.BOLD),
                    dias_row,
                ], spacing=12),
                width=400,
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

    def _overlay_aplicar_plantilla(self, e):
        """Overlay para aplicar plantilla a usuario"""
        dd_usuario = ft.Dropdown(
            label="Selecciona Usuario",
            options=[
                ft.dropdown.Option(key=str(u["ID"]), text=u["NOMBRE_USUARIO"])
                for u in self._usuarios
            ],
            width=300,
        )

        dd_plantilla = ft.Dropdown(
            label="Selecciona Plantilla",
            options=[
                ft.dropdown.Option(key=str(p["ID"]), text=f"{p['NOMBRE']} ({p['HORA_INICIO']}-{p['HORA_FIN']})")
                for p in self._plantillas
            ],
            width=300,
        )

        def aplicar(ev):
            if not dd_usuario.value or not dd_plantilla.value:
                self._mostrar_error("Debes seleccionar usuario y plantilla")
                return

            try:
                plantilla = next(p for p in self._plantillas if str(p["ID"]) == dd_plantilla.value)
                usuario_id = int(dd_usuario.value)

                with OBTENER_SESION() as sesion:
                    creados = 0
                    for dia in plantilla["DIAS"]:
                        existe = sesion.query(MODELO_HORARIO).filter_by(
                            USUARIO_ID=usuario_id,
                            DIA_SEMANA=dia
                        ).first()

                        if not existe:
                            nuevo = MODELO_HORARIO(
                                USUARIO_ID=usuario_id,
                                DIA_SEMANA=dia,
                                HORA_INICIO=plantilla["HORA_INICIO"],
                                HORA_FIN=plantilla["HORA_FIN"],
                                ACTIVO=True,
                            )
                            sesion.add(nuevo)
                            creados += 1

                    sesion.commit()

                overlay.open = False
                self._pagina.update()
                self._mostrar_exito(f"Plantilla aplicada ({creados} horarios creados)")
                self._cargar_datos()

            except Exception as ex:
                self._mostrar_error(f"Error: {str(ex)}")

        overlay = ft.AlertDialog(
            modal=True,
            title=ft.Text("🔄 Aplicar Plantilla", size=16, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    dd_usuario,
                    dd_plantilla,
                ], spacing=12),
                width=350,
                padding=16,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: setattr(overlay, 'open', False) or self._pagina.update()),
                ft.ElevatedButton("Aplicar", on_click=aplicar, bgcolor=ft.Colors.TEAL_600),
            ],
        )

        self._pagina.overlay.append(overlay)
        overlay.open = True
        self._pagina.update()

    def _overlay_editar_horario(self, horario_id: int):
        """Overlay para editar horario"""
        # Buscar horario
        horario = next((h for h in self._horarios if h["ID"] == horario_id), None)
        if not horario:
            return

        tf_inicio = ft.TextField(label="Hora Inicio", value=horario["HORA_INICIO"], width=140)
        tf_fin = ft.TextField(label="Hora Fin", value=horario["HORA_FIN"], width=140)

        def guardar(ev):
            try:
                with OBTENER_SESION() as sesion:
                    h = sesion.query(MODELO_HORARIO).filter_by(ID=horario_id).first()
                    if h:
                        h.HORA_INICIO = tf_inicio.value
                        h.HORA_FIN = tf_fin.value
                        sesion.commit()

                overlay.open = False
                self._pagina.update()
                self._mostrar_exito("Horario actualizado")
                self._cargar_datos()

            except Exception as ex:
                self._mostrar_error(f"Error: {str(ex)}")

        overlay = ft.AlertDialog(
            modal=True,
            title=ft.Text("✏️ Editar Horario", size=16, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(f"{horario['USUARIO_NOMBRE']} - {horario['DIA_SEMANA']}", weight=ft.FontWeight.BOLD),
                    ft.Row([tf_inicio, tf_fin], spacing=8),
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

    # ==================== UTILIDADES ====================

    def _eliminar_horario(self, horario_id: int):
        """Elimina un horario"""
        try:
            with OBTENER_SESION() as sesion:
                h = sesion.query(MODELO_HORARIO).filter_by(ID=horario_id).first()
                if h:
                    h.ACTIVO = False
                    sesion.commit()

            self._mostrar_exito("Horario eliminado")
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
