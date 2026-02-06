import flet as ft
from features.admin.presentation.widgets.VistaBase import VistaBase
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_MOVIMIENTO_CAJA, MODELO_USUARIO
from core.Constantes import COLORES, TAMANOS
from datetime import datetime

class VistaCaja(VistaBase):
    
    def __init__(self, pagina: ft.Page, usuario, on_volver_inicio):
        super().__init__(pagina=pagina, usuario=usuario, titulo="Gestión de Caja", on_volver_inicio=on_volver_inicio, mostrar_boton_volver=True)
        self._tabla = None
        self._cargar_vista()
    
    def _cargar_vista(self):
        boton_nuevo = ft.Button("➕ Nuevo Movimiento", icon=ft.icons.Icons.Icons.ACCOUNT_BALANCE_WALLET, on_click=self._abrir_popup_crear, bgcolor=COLORES.PRIMARIO, color=COLORES.TEXTO_BLANCO)
        
        self._tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Tipo", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Monto", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Descripción", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Usuario", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Fecha", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.Border.all(1, COLORES.BORDE),
            border_radius=TAMANOS.RADIO_MD,
            vertical_lines=ft.BorderSide(1, COLORES.BORDE),
            heading_row_color=COLORES.PRIMARIO_CLARO,
        )
        
        self.establecer_contenido([ft.Row([boton_nuevo]), ft.Container(content=ft.Column([self._tabla], scroll=ft.ScrollMode.AUTO), bgcolor=COLORES.FONDO_BLANCO, border_radius=TAMANOS.RADIO_MD, padding=TAMANOS.PADDING_MD)])
        self._cargar_datos()
    
    def _cargar_datos(self):
        sesion = OBTENER_SESION()
        items = sesion.query(MODELO_MOVIMIENTO_CAJA).order_by(MODELO_MOVIMIENTO_CAJA.FECHA.desc()).all()
        self._tabla.rows.clear()
        
        total = 0
        for item in items:
            usuario_nombre = item.USUARIO.NOMBRE_USUARIO if item.USUARIO else "Sistema"
            color_monto = COLORES.EXITO if item.TIPO == "INGRESO" else COLORES.PELIGRO
            monto_valor = item.MONTO / 100
            
            if item.TIPO == "INGRESO":
                total += monto_valor
            else:
                total -= monto_valor
            
            self._tabla.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(item.ID))),
                    ft.DataCell(ft.Text(item.TIPO, color=color_monto, weight=ft.FontWeight.BOLD)),
                    ft.DataCell(ft.Text(f"${monto_valor:.2f}", color=color_monto)),
                    ft.DataCell(ft.Text(item.DESCRIPCION or "-")),
                    ft.DataCell(ft.Text(usuario_nombre)),
                    ft.DataCell(ft.Text(item.FECHA.strftime("%d/%m/%Y %H:%M") if item.FECHA else "-")),
                    ft.DataCell(ft.Row([
                        ft.IconButton(icon=ft.icons.Icons.Icons.EDIT, tooltip="Editar", icon_color=COLORES.INFO, on_click=lambda e, i=item: self._abrir_popup_editar(i)),
                        ft.IconButton(icon=ft.icons.Icons.Icons.DELETE, tooltip="Eliminar", icon_color=COLORES.PELIGRO, on_click=lambda e, i=item: self._confirmar_eliminar(i)),
                    ])),
                ])
            )
        sesion.close()
        self.actualizar_ui()
    
    def _abrir_popup_crear(self, e):
        campo_tipo = ft.Dropdown(label="Tipo de Movimiento", options=[ft.dropdown.Option("INGRESO"), ft.dropdown.Option("EGRESO")])
        campo_monto = ft.TextField(label="Monto (centavos)", prefix_icon=ft.icons.Icons.Icons.ATTACH_MONEY, keyboard_type=ft.KeyboardType.NUMBER, hint_text="10000 = $100.00")
        campo_descripcion = ft.TextField(label="Descripción", multiline=True, max_lines=3)
        
        def guardar(e):
            if not campo_tipo.value or not campo_monto.value:
                self.mostrar_snackbar("Tipo y monto son obligatorios", es_error=True)
                return
            try:
                sesion = OBTENER_SESION()
                nuevo = MODELO_MOVIMIENTO_CAJA(
                    TIPO=campo_tipo.value,
                    MONTO=int(campo_monto.value),
                    DESCRIPCION=campo_descripcion.value,
                    USUARIO_ID=self._usuario.ID,
                    FECHA=datetime.now()
                )
                sesion.add(nuevo)
                sesion.commit()
                sesion.close()
                self.cerrar_dialogo()
                self.mostrar_snackbar("Movimiento registrado exitosamente")
                self._cargar_datos()
            except Exception as ex:
                self.mostrar_snackbar(f"Error: {str(ex)}", es_error=True)
        
        dialogo = ft.AlertDialog(
            title=ft.Text("➕ Nuevo Movimiento de Caja", color=COLORES.TEXTO),
            content=ft.Container(content=ft.Column([campo_tipo, campo_monto, campo_descripcion], tight=True, spacing=TAMANOS.ESPACIADO_MD), width=400),
            actions=[ft.TextButton("Cancelar", on_click=lambda e: self.cerrar_dialogo()), ft.Button("Guardar", icon=ft.icons.Icons.Icons.SAVE, on_click=guardar, bgcolor=COLORES.PRIMARIO, color=COLORES.TEXTO_BLANCO)]
        )
        self.mostrar_dialogo(dialogo)
    
    def _abrir_popup_editar(self, item):
        campo_tipo = ft.Dropdown(label="Tipo de Movimiento", value=item.TIPO, options=[ft.dropdown.Option("INGRESO"), ft.dropdown.Option("EGRESO")])
        campo_monto = ft.TextField(label="Monto (centavos)", value=str(item.MONTO), keyboard_type=ft.KeyboardType.NUMBER)
        campo_descripcion = ft.TextField(label="Descripción", value=item.DESCRIPCION or "", multiline=True)
        
        def guardar(e):
            try:
                sesion = OBTENER_SESION()
                item_bd = sesion.query(MODELO_MOVIMIENTO_CAJA).filter_by(ID=item.ID).first()
                if item_bd:
                    item_bd.TIPO = campo_tipo.value
                    item_bd.MONTO = int(campo_monto.value)
                    item_bd.DESCRIPCION = campo_descripcion.value
                    sesion.commit()
                sesion.close()
                self.cerrar_dialogo()
                self.mostrar_snackbar("Movimiento actualizado exitosamente")
                self._cargar_datos()
            except Exception as ex:
                self.mostrar_snackbar(f"Error: {str(ex)}", es_error=True)
        
        dialogo = ft.AlertDialog(
            title=ft.Text(f"✏️ Editar Movimiento #{item.ID}", color=COLORES.TEXTO),
            content=ft.Container(content=ft.Column([campo_tipo, campo_monto, campo_descripcion], tight=True, spacing=TAMANOS.ESPACIADO_MD), width=400),
            actions=[ft.TextButton("Cancelar", on_click=lambda e: self.cerrar_dialogo()), ft.Button("Actualizar", icon=ft.icons.Icons.Icons.SAVE, on_click=guardar, bgcolor=COLORES.INFO, color=COLORES.TEXTO_BLANCO)]
        )
        self.mostrar_dialogo(dialogo)
    
    def _confirmar_eliminar(self, item):
        def eliminar(e):
            try:
                sesion = OBTENER_SESION()
                item_bd = sesion.query(MODELO_MOVIMIENTO_CAJA).filter_by(ID=item.ID).first()
                if item_bd:
                    sesion.delete(item_bd)
                    sesion.commit()
                sesion.close()
                self.cerrar_dialogo()
                self.mostrar_snackbar("Movimiento eliminado exitosamente")
                self._cargar_datos()
            except Exception as ex:
                self.mostrar_snackbar(f"Error: {str(ex)}", es_error=True)
        
        dialogo = ft.AlertDialog(
            title=ft.Text("⚠️ Confirmar Eliminación", color=COLORES.PELIGRO),
            content=ft.Text(f"¿Eliminar movimiento #{item.ID} ({item.TIPO})?\n\nEsta acción no se puede deshacer."),
            actions=[ft.TextButton("Cancelar", on_click=lambda e: self.cerrar_dialogo()), ft.Button("Eliminar", icon=ft.icons.Icons.Icons.DELETE_FOREVER, on_click=eliminar, bgcolor=COLORES.PELIGRO, color=COLORES.TEXTO_BLANCO)]
        )
        self.mostrar_dialogo(dialogo)
