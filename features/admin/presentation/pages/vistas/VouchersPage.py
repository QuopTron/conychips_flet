"""
Página de validación de vouchers de pago.
Vista de verificación y aprobación.
Arquitectura: Clean Architecture + Hexagonal
"""
import flet as ft
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_VOUCHER
from core.Constantes import COLORES, TAMANOS, ICONOS, ROLES
from core.decoradores.DecoradorVistas import REQUIERE_ROL
from features.admin.presentation.widgets.ComponentesGlobales import (
    HeaderAdmin, ContenedorPagina, Notificador, DialogoConfirmacion
)


@REQUIERE_ROL(ROLES.SUPERVISOR)
class VouchersPage(ft.Column):
    """Vista de validación de vouchers de pago."""
    
    def __init__(self, PAGINA: ft.Page, USUARIO):
        super().__init__()
        self._PAGINA = PAGINA
        self._USUARIO = USUARIO
        
        self.expand = True
        self._CONSTRUIR_UI()
        self._CARGAR_VOUCHERS()
    
    def _CONSTRUIR_UI(self):
        """Construye interfaz."""
        # Header
        header = HeaderAdmin(
            titulo="Validar Vouchers",
            icono=ICONOS.VOUCHER,
            on_menu=self._IR_MENU,
            on_salir=self._SALIR
        )
        
        # Tabs de filtrado
        tabs = ft.Tabs(
            selected_index=0,
            on_change=self._CAMBIAR_TAB,
            tabs=[
                ft.Tab(text="Pendientes", icon=ICONOS.PENDIENTE),
                ft.Tab(text="Aprobados", icon=ICONOS.VERIFICADO),
                ft.Tab(text="Rechazados", icon=ICONOS.CANCELAR),
            ]
        )
        
        # Lista de vouchers
        self._lista = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
        
        # Contenedor principal
        contenido = ContenedorPagina(
            controles=[header, tabs, self._lista]
        )
        
        self.controls = [contenido]
    
    def _CARGAR_VOUCHERS(self, estado="PENDIENTE"):
        """Carga vouchers según estado."""
        try:
            sesion = OBTENER_SESION()
            vouchers = sesion.query(MODELO_VOUCHER).filter(
                MODELO_VOUCHER.ESTADO == estado
            ).order_by(MODELO_VOUCHER.FECHA.desc()).all()
            
            self._ACTUALIZAR_LISTA(vouchers)
            
        except Exception as e:
            Notificador.ERROR(self._PAGINA, f"Error al cargar vouchers: {str(e)}")
    
    def _ACTUALIZAR_LISTA(self, vouchers):
        """Actualiza lista de vouchers."""
        self._lista.controls.clear()
        
        if not vouchers:
            self._lista.controls.append(
                ft.Text("No hay vouchers", size=16, color=COLORES.TEXTO_SECUNDARIO)
            )
        else:
            for voucher in vouchers:
                card = ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(f"Voucher #{voucher.ID}", 
                                       weight=ft.FontWeight.BOLD, size=16),
                                ft.Container(expand=True),
                                ft.Text(f"S/. {voucher.MONTO:.2f}", 
                                       size=18, color=COLORES.EXITO),
                            ]),
                            ft.Divider(),
                            ft.Row([
                                ft.Column([
                                    ft.Text("Cliente:", size=12, 
                                           color=COLORES.TEXTO_SECUNDARIO),
                                    ft.Text(voucher.CLIENTE or "N/A"),
                                ]),
                                ft.Column([
                                    ft.Text("Fecha:", size=12, 
                                           color=COLORES.TEXTO_SECUNDARIO),
                                    ft.Text(voucher.FECHA.strftime("%d/%m/%Y %H:%M")),
                                ]),
                                ft.Column([
                                    ft.Text("Método:", size=12, 
                                           color=COLORES.TEXTO_SECUNDARIO),
                                    ft.Text(voucher.METODO_PAGO or "N/A"),
                                ]),
                            ]),
                            ft.Row([
                                ft.Text("Código de Operación:", size=12, 
                                       color=COLORES.TEXTO_SECUNDARIO),
                                ft.Text(voucher.CODIGO_OPERACION or "N/A", 
                                       weight=ft.FontWeight.BOLD),
                            ]),
                            # Imagen del voucher si existe
                            ft.Image(
                                src=voucher.IMAGEN_URL if hasattr(voucher, 'IMAGEN_URL') else None,
                                width=200,
                                height=200,
                                fit=ft.ImageFit.CONTAIN,
                            ) if hasattr(voucher, 'IMAGEN_URL') and voucher.IMAGEN_URL else ft.Container(),
                            # Acciones
                            ft.Row([
                                ft.ElevatedButton(
                                    "Aprobar",
                                    icon=ICONOS.VERIFICADO,
                                    bgcolor=COLORES.EXITO,
                                    color=COLORES.TEXTO_BLANCO,
                                    on_click=lambda e, v=voucher: self._APROBAR_VOUCHER(v)
                                ),
                                ft.ElevatedButton(
                                    "Rechazar",
                                    icon=ICONOS.CANCELAR,
                                    bgcolor=COLORES.PELIGRO,
                                    color=COLORES.TEXTO_BLANCO,
                                    on_click=lambda e, v=voucher: self._RECHAZAR_VOUCHER(v)
                                ),
                            ], spacing=10) if voucher.ESTADO == "PENDIENTE" else ft.Container(),
                        ], spacing=10),
                        padding=TAMANOS.PADDING_MD,
                    )
                )
                self._lista.controls.append(card)
        
        self._PAGINA.update()
    
    def _APROBAR_VOUCHER(self, voucher):
        """Aprueba un voucher."""
        def confirmar(e):
            try:
                sesion = OBTENER_SESION()
                voucher.ESTADO = "APROBADO"
                voucher.VALIDADO_POR = self._USUARIO.USUARIO
                sesion.commit()
                Notificador.EXITO(self._PAGINA, "Voucher aprobado correctamente")
                self._CARGAR_VOUCHERS("PENDIENTE")
            except Exception as ex:
                Notificador.ERROR(self._PAGINA, f"Error: {str(ex)}")
        
        DialogoConfirmacion.MOSTRAR(
            self._PAGINA,
            f"¿Aprobar voucher #{voucher.ID}?",
            confirmar
        )
    
    def _RECHAZAR_VOUCHER(self, voucher):
        """Rechaza un voucher."""
        def confirmar(e):
            try:
                sesion = OBTENER_SESION()
                voucher.ESTADO = "RECHAZADO"
                voucher.VALIDADO_POR = self._USUARIO.USUARIO
                sesion.commit()
                Notificador.EXITO(self._PAGINA, "Voucher rechazado")
                self._CARGAR_VOUCHERS("PENDIENTE")
            except Exception as ex:
                Notificador.ERROR(self._PAGINA, f"Error: {str(ex)}")
        
        DialogoConfirmacion.MOSTRAR(
            self._PAGINA,
            f"¿Rechazar voucher #{voucher.ID}?",
            confirmar
        )
    
    def _CAMBIAR_TAB(self, e):
        """Cambia entre tabs."""
        estados = ["PENDIENTE", "APROBADO", "RECHAZADO"]
        self._CARGAR_VOUCHERS(estados[e.control.selected_index])
    
    def _IR_MENU(self, e=None):
        """Retorna al menú principal."""
        from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
        self._PAGINA.controls.clear()
        self._PAGINA.add(PaginaAdmin(self._PAGINA, self._USUARIO))
        self._PAGINA.update()
    
    def _SALIR(self, e=None):
        """Cierra sesión."""
        from features.autenticacion.presentation.pages.PaginaLogin import PaginaLogin
        self._PAGINA.controls.clear()
        self._PAGINA.add(PaginaLogin(self._PAGINA))
        self._PAGINA.update()
