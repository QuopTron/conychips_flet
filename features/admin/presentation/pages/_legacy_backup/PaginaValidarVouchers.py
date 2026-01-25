import flet as ft
from datetime import datetime

from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION,
    MODELO_VOUCHER,
    MODELO_PEDIDO,
    MODELO_USUARIO,
)
from core.constantes import COLORES, TAMANOS, ICONOS
from core.decoradores.DecoradorVistas import REQUIERE_ROL


@REQUIERE_ROL("ADMIN", "SUPERADMIN")
class PaginaValidarVouchers:
    
    def __init__(self, PAGINA: ft.Page, USUARIO):
        self.PAGINA = PAGINA
        self.USUARIO = USUARIO
        self.USUARIO_ID = USUARIO.ID
        
        self.VOUCHERS_PENDIENTES = ft.ListView(spacing=10, expand=True)
        self.VOUCHERS_VALIDADOS = ft.ListView(spacing=10, expand=True)
        
        self._CARGAR_DATOS()
    
    
    def _CARGAR_DATOS(self):
        self._CARGAR_PENDIENTES()
        self._CARGAR_VALIDADOS()
    
    
    def _CARGAR_PENDIENTES(self):
        sesion = OBTENER_SESION()
        
        vouchers = (
            sesion.query(MODELO_VOUCHER)
            .filter_by(VALIDADO=False)
            .order_by(MODELO_VOUCHER.FECHA_SUBIDA.desc())
            .all()
        )
        
        self.VOUCHERS_PENDIENTES.controls.clear()
        
        if not vouchers:
            self.VOUCHERS_PENDIENTES.controls.append(
                ft.Text("No hay vouchers pendientes", color=COLORES.TEXTO_SECUNDARIO)
            )
        else:
            for voucher in vouchers:
                self.VOUCHERS_PENDIENTES.controls.append(
                    self._CREAR_TARJETA_VOUCHER(voucher, PENDIENTE=True)
                )
        
        sesion.close()
        
        if self.PAGINA:
            self.PAGINA.update()
    
    
    def _CARGAR_VALIDADOS(self):
        sesion = OBTENER_SESION()
        
        vouchers = (
            sesion.query(MODELO_VOUCHER)
            .filter_by(VALIDADO=True)
            .order_by(MODELO_VOUCHER.FECHA_VALIDACION.desc())
            .limit(20)
            .all()
        )
        
        self.VOUCHERS_VALIDADOS.controls.clear()
        
        if not vouchers:
            self.VOUCHERS_VALIDADOS.controls.append(
                ft.Text("No hay vouchers validados", color=COLORES.TEXTO_SECUNDARIO)
            )
        else:
            for voucher in vouchers:
                self.VOUCHERS_VALIDADOS.controls.append(
                    self._CREAR_TARJETA_VOUCHER(voucher, PENDIENTE=False)
                )
        
        sesion.close()
        
        if self.PAGINA:
            self.PAGINA.update()
    
    
    def _CREAR_TARJETA_VOUCHER(self, VOUCHER, PENDIENTE: bool):
        sesion = OBTENER_SESION()
        
        pedido = sesion.query(MODELO_PEDIDO).filter_by(ID=VOUCHER.PEDIDO_ID).first()
        usuario = sesion.query(MODELO_USUARIO).filter_by(ID=VOUCHER.USUARIO_ID).first()
        
        sesion.close()
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ICONOS.VOUCHER, color=COLORES.PRIMARIO),
                    ft.Text(f"Voucher #{VOUCHER.ID}", weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.Chip(
                        label=ft.Text(
                            "PENDIENTE" if PENDIENTE else "VALIDADO",
                            size=12
                        ),
                        bgcolor=COLORES.ADVERTENCIA if PENDIENTE else COLORES.EXITO,
                    ),
                ]),
                ft.Row([
                    ft.Column([
                        ft.Text(f"Pedido: #{VOUCHER.PEDIDO_ID}"),
                        ft.Text(
                            f"Cliente: {usuario.NOMBRE if usuario else 'Desconocido'}",
                            color=COLORES.TEXTO_SECUNDARIO,
                            size=12
                        ),
                        ft.Text(f"Método: {VOUCHER.METODO_PAGO.upper()}"),
                        ft.Text(f"Monto: S/ {VOUCHER.MONTO:.2f}", size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(
                            f"Total Pedido: S/ {pedido.TOTAL if pedido else 0:.2f}",
                            color=COLORES.TEXTO_SECUNDARIO,
                            size=12
                        ),
                    ], expand=True),
                ]),
                ft.Text(
                    f"Subido: {VOUCHER.FECHA_SUBIDA.strftime('%d/%m/%Y %H:%M')}",
                    color=COLORES.TEXTO_SECUNDARIO,
                    size=12
                ),
                ft.Row([
                    ft.TextButton(
                        "Ver Imagen",
                        icon=ICONOS.IMAGEN,
                        on_click=lambda e, v=VOUCHER: self._VER_IMAGEN(v)
                    ),
                    ft.ElevatedButton(
                        "Validar",
                        icon=ICONOS.CONFIRMAR,
                        bgcolor=COLORES.EXITO,
                        on_click=lambda e, v=VOUCHER: self._VALIDAR_VOUCHER(v),
                        visible=PENDIENTE
                    ),
                    ft.ElevatedButton(
                        "Rechazar",
                        icon=ICONOS.CANCELAR,
                        bgcolor=COLORES.ERROR,
                        on_click=lambda e, v=VOUCHER: self._RECHAZAR_VOUCHER(v),
                        visible=PENDIENTE
                    ),
                ], spacing=10),
            ], spacing=10),
            padding=15,
            border=ft.border.all(1, COLORES.BORDE),
            border_radius=TAMANOS.RADIO_BORDE,
            bgcolor=COLORES.FONDO_TARJETA,
        )
    
    
    def _VER_IMAGEN(self, VOUCHER):
        dialog = ft.AlertDialog(
            title=ft.Text(f"Voucher #{VOUCHER.ID}"),
            content=ft.Column([
                ft.Text("URL de la imagen:", weight=ft.FontWeight.BOLD),
                ft.Text(VOUCHER.IMAGEN_URL, selectable=True, size=12),
                ft.Text(
                    "Copiar la URL para ver en navegador",
                    color=COLORES.TEXTO_SECUNDARIO,
                    size=10
                ),
            ], tight=True),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda e: self._CERRAR_DIALOG()),
            ]
        )
        
        self.PAGINA.dialog = dialog
        dialog.open = True
        self.PAGINA.update()
    
    
    def _VALIDAR_VOUCHER(self, VOUCHER):
        sesion = OBTENER_SESION()
        
        voucher = sesion.query(MODELO_VOUCHER).filter_by(ID=VOUCHER.ID).first()
        if voucher:
            voucher.VALIDADO = True
            voucher.VALIDADO_POR = self.USUARIO_ID
            voucher.FECHA_VALIDACION = datetime.utcnow()
            sesion.commit()
            
            pedido = sesion.query(MODELO_PEDIDO).filter_by(ID=voucher.PEDIDO_ID).first()
            if pedido and pedido.ESTADO == "pendiente":
                pedido.ESTADO = "confirmado"
                sesion.commit()
        
        sesion.close()
        
        self._CARGAR_DATOS()
        
        self.PAGINA.snack_bar = ft.SnackBar(
            content=ft.Text("Voucher validado y pedido confirmado"),
            bgcolor=COLORES.EXITO
        )
        self.PAGINA.snack_bar.open = True
        self.PAGINA.update()
    
    
    def _RECHAZAR_VOUCHER(self, VOUCHER):
        sesion = OBTENER_SESION()
        
        voucher = sesion.query(MODELO_VOUCHER).filter_by(ID=VOUCHER.ID).first()
        if voucher:
            sesion.delete(voucher)
            sesion.commit()
        
        sesion.close()
        
        self._CARGAR_DATOS()
        
        self.PAGINA.snack_bar = ft.SnackBar(
            content=ft.Text("Voucher rechazado y eliminado"),
            bgcolor=COLORES.ADVERTENCIA
        )
        self.PAGINA.snack_bar.open = True
        self.PAGINA.update()
    
    
    def _CERRAR_DIALOG(self):
        if self.PAGINA.dialog:
            self.PAGINA.dialog.open = False
            self.PAGINA.update()
    
    
    def CONSTRUIR(self) -> ft.Control:
        return ft.Column([
            ft.Row([
                ft.Text("Validar Vouchers de Pago", size=TAMANOS.TITULO, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.ElevatedButton("Menú", icon=ICONOS.DASHBOARD, on_click=self._IR_MENU),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            ft.Tabs(
                selected_index=0,
                tabs=[
                    ft.Tab(
                        text="Pendientes",
                        icon=ICONOS.ALERTA,
                        content=ft.Container(
                            content=self.VOUCHERS_PENDIENTES,
                            padding=10,
                        )
                    ),
                    ft.Tab(
                        text="Validados",
                        icon=ICONOS.CONFIRMAR,
                        content=ft.Container(
                            content=self.VOUCHERS_VALIDADOS,
                            padding=10,
                        )
                    ),
                ],
                expand=True,
            )
        ], expand=True)


    def _IR_MENU(self, e):
        from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin

        self.PAGINA.controls.clear()
        self.PAGINA.controls.append(PaginaAdmin(self.PAGINA, self.USUARIO))
        self.PAGINA.update()
