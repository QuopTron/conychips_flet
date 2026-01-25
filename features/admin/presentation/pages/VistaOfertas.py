"""
Vista de gestión de ofertas con CRUD completo en popups
"""
import flet as ft
from features.admin.presentation.widgets.VistaBase import VistaBase
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_OFERTA, MODELO_PRODUCTO
from core.Constantes import COLORES, TAMANOS
from datetime import datetime


class VistaOfertas(VistaBase):
    
    def __init__(self, pagina: ft.Page, usuario, on_volver_inicio):
        super().__init__(pagina=pagina, usuario=usuario, titulo="Gestión de Ofertas", on_volver_inicio=on_volver_inicio, mostrar_boton_volver=True)
        self._tabla = None
        self._cargar_vista()
    
    def _cargar_vista(self):
        boton_nuevo = ft.ElevatedButton("➕ Nueva Oferta", icon=ft.Icons.LOCAL_OFFER, on_click=self._abrir_popup_crear, bgcolor=COLORES.PRIMARIO, color=COLORES.TEXTO_BLANCO)
        
        self._tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Producto", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Descuento %", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Inicio", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Fin", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Activa", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, COLORES.BORDE),
            border_radius=TAMANOS.RADIO_MD,
            vertical_lines=ft.BorderSide(1, COLORES.BORDE),
            heading_row_color=COLORES.PRIMARIO_CLARO,
        )
        
        self.establecer_contenido([ft.Row([boton_nuevo]), ft.Container(content=ft.Column([self._tabla], scroll=ft.ScrollMode.AUTO), bgcolor=COLORES.FONDO_BLANCO, border_radius=TAMANOS.RADIO_MD, padding=TAMANOS.PADDING_MD)])
        self._cargar_datos()
    
    def _cargar_datos(self):
        sesion = OBTENER_SESION()
        items = sesion.query(MODELO_OFERTA).all()
        self._tabla.rows.clear()
        for item in items:
            producto_nombre = item.PRODUCTO.NOMBRE if item.PRODUCTO else "Sin producto"
            activa = "✓ Sí" if item.ACTIVA else "✗ No"
            
            self._tabla.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(item.ID))),
                    ft.DataCell(ft.Text(producto_nombre)),
                    ft.DataCell(ft.Text(f"{item.PORCENTAJE_DESCUENTO}%")),
                    ft.DataCell(ft.Text(item.FECHA_INICIO.strftime("%d/%m/%Y") if item.FECHA_INICIO else "-")),
                    ft.DataCell(ft.Text(item.FECHA_FIN.strftime("%d/%m/%Y") if item.FECHA_FIN else "-")),
                    ft.DataCell(ft.Text(activa, color=COLORES.EXITO if item.ACTIVA else COLORES.PELIGRO)),
                    ft.DataCell(ft.Row([
                        ft.IconButton(icon=ft.Icons.EDIT, tooltip="Editar", icon_color=COLORES.INFO, on_click=lambda e, i=item: self._abrir_popup_editar(i)),
                        ft.IconButton(icon=ft.Icons.DELETE, tooltip="Eliminar", icon_color=COLORES.PELIGRO, on_click=lambda e, i=item: self._confirmar_eliminar(i)),
                    ])),
                ])
            )
        sesion.close()
        self.actualizar_ui()
    
    def _abrir_popup_crear(self, e):
        sesion = OBTENER_SESION()
        productos = sesion.query(MODELO_PRODUCTO).all()
        sesion.close()
        
        campo_producto = ft.Dropdown(label="Producto", options=[ft.dropdown.Option(str(p.ID), p.NOMBRE) for p in productos])
        campo_descuento = ft.TextField(label="Descuento %", prefix_icon=ft.Icons.PERCENT, keyboard_type=ft.KeyboardType.NUMBER)
        campo_inicio = ft.TextField(label="Fecha Inicio (YYYY-MM-DD)", prefix_icon=ft.Icons.CALENDAR_TODAY, hint_text="2026-01-25")
        campo_fin = ft.TextField(label="Fecha Fin (YYYY-MM-DD)", prefix_icon=ft.Icons.CALENDAR_TODAY, hint_text="2026-02-25")
        switch_activa = ft.Switch(label="Oferta Activa", value=True)
        
        def guardar(e):
            if not campo_producto.value or not campo_descuento.value:
                self.mostrar_snackbar("Producto y descuento son obligatorios", es_error=True)
                return
            try:
                sesion = OBTENER_SESION()
                nuevo = MODELO_OFERTA(
                    PRODUCTO_ID=int(campo_producto.value),
                    PORCENTAJE_DESCUENTO=int(campo_descuento.value),
                    FECHA_INICIO=datetime.strptime(campo_inicio.value, "%Y-%m-%d") if campo_inicio.value else None,
                    FECHA_FIN=datetime.strptime(campo_fin.value, "%Y-%m-%d") if campo_fin.value else None,
                    ACTIVA=switch_activa.value
                )
                sesion.add(nuevo)
                sesion.commit()
                sesion.close()
                self.cerrar_dialogo()
                self.mostrar_snackbar("Oferta creada exitosamente")
                self._cargar_datos()
            except Exception as ex:
                self.mostrar_snackbar(f"Error: {str(ex)}", es_error=True)
        
        dialogo = ft.AlertDialog(
            title=ft.Text("➕ Nueva Oferta", color=COLORES.TEXTO),
            content=ft.Container(content=ft.Column([campo_producto, campo_descuento, campo_inicio, campo_fin, switch_activa], tight=True, spacing=TAMANOS.ESPACIADO_MD), width=400),
            actions=[ft.TextButton("Cancelar", on_click=lambda e: self.cerrar_dialogo()), ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE, on_click=guardar, bgcolor=COLORES.PRIMARIO, color=COLORES.TEXTO_BLANCO)]
        )
        self.mostrar_dialogo(dialogo)
    
    def _abrir_popup_editar(self, item):
        sesion = OBTENER_SESION()
        productos = sesion.query(MODELO_PRODUCTO).all()
        sesion.close()
        
        campo_producto = ft.Dropdown(label="Producto", value=str(item.PRODUCTO_ID) if item.PRODUCTO_ID else None, options=[ft.dropdown.Option(str(p.ID), p.NOMBRE) for p in productos])
        campo_descuento = ft.TextField(label="Descuento %", value=str(item.PORCENTAJE_DESCUENTO), keyboard_type=ft.KeyboardType.NUMBER)
        campo_inicio = ft.TextField(label="Fecha Inicio (YYYY-MM-DD)", value=item.FECHA_INICIO.strftime("%Y-%m-%d") if item.FECHA_INICIO else "")
        campo_fin = ft.TextField(label="Fecha Fin (YYYY-MM-DD)", value=item.FECHA_FIN.strftime("%Y-%m-%d") if item.FECHA_FIN else "")
        switch_activa = ft.Switch(label="Oferta Activa", value=item.ACTIVA)
        
        def guardar(e):
            try:
                sesion = OBTENER_SESION()
                item_bd = sesion.query(MODELO_OFERTA).filter_by(ID=item.ID).first()
                if item_bd:
                    item_bd.PRODUCTO_ID = int(campo_producto.value) if campo_producto.value else None
                    item_bd.PORCENTAJE_DESCUENTO = int(campo_descuento.value)
                    item_bd.FECHA_INICIO = datetime.strptime(campo_inicio.value, "%Y-%m-%d") if campo_inicio.value else None
                    item_bd.FECHA_FIN = datetime.strptime(campo_fin.value, "%Y-%m-%d") if campo_fin.value else None
                    item_bd.ACTIVA = switch_activa.value
                    sesion.commit()
                sesion.close()
                self.cerrar_dialogo()
                self.mostrar_snackbar("Oferta actualizada exitosamente")
                self._cargar_datos()
            except Exception as ex:
                self.mostrar_snackbar(f"Error: {str(ex)}", es_error=True)
        
        dialogo = ft.AlertDialog(
            title=ft.Text(f"✏️ Editar Oferta #{item.ID}", color=COLORES.TEXTO),
            content=ft.Container(content=ft.Column([campo_producto, campo_descuento, campo_inicio, campo_fin, switch_activa], tight=True, spacing=TAMANOS.ESPACIADO_MD), width=400),
            actions=[ft.TextButton("Cancelar", on_click=lambda e: self.cerrar_dialogo()), ft.ElevatedButton("Actualizar", icon=ft.Icons.SAVE, on_click=guardar, bgcolor=COLORES.INFO, color=COLORES.TEXTO_BLANCO)]
        )
        self.mostrar_dialogo(dialogo)
    
    def _confirmar_eliminar(self, item):
        def eliminar(e):
            try:
                sesion = OBTENER_SESION()
                item_bd = sesion.query(MODELO_OFERTA).filter_by(ID=item.ID).first()
                if item_bd:
                    sesion.delete(item_bd)
                    sesion.commit()
                sesion.close()
                self.cerrar_dialogo()
                self.mostrar_snackbar("Oferta eliminada exitosamente")
                self._cargar_datos()
            except Exception as ex:
                self.mostrar_snackbar(f"Error: {str(ex)}", es_error=True)
        
        dialogo = ft.AlertDialog(
            title=ft.Text("⚠️ Confirmar Eliminación", color=COLORES.PELIGRO),
            content=ft.Text(f"¿Eliminar oferta #{item.ID}?\n\nEsta acción no se puede deshacer."),
            actions=[ft.TextButton("Cancelar", on_click=lambda e: self.cerrar_dialogo()), ft.ElevatedButton("Eliminar", icon=ft.Icons.DELETE_FOREVER, on_click=eliminar, bgcolor=COLORES.PELIGRO, color=COLORES.TEXTO_BLANCO)]
        )
        self.mostrar_dialogo(dialogo)
