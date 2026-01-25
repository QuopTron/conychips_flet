import flet as ft
from datetime import datetime, timedelta
from sqlalchemy import func

from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION,
    MODELO_CAJA_MOVIMIENTO,
    MODELO_CAJA,
    MODELO_PEDIDO,
    MODELO_REFILL_SOLICITUD,
)
from core.constantes import COLORES, TAMANOS, ICONOS
from core.decoradores.DecoradorVistas import REQUIERE_ROL


@REQUIERE_ROL("ADMIN", "SUPERADMIN")
class PaginaFinanzas:
    
    def __init__(self, PAGINA: ft.Page, USUARIO):
        self.PAGINA = PAGINA
        self.USUARIO = USUARIO
        self.USUARIO_ID = USUARIO.ID
        
        self.INGRESOS_TOTALES = ft.Text("S/ 0.00", size=24, weight=ft.FontWeight.BOLD, color=COLORES.EXITO)
        self.EGRESOS_TOTALES = ft.Text("S/ 0.00", size=24, weight=ft.FontWeight.BOLD, color=COLORES.ERROR)
        self.BALANCE = ft.Text("S/ 0.00", size=24, weight=ft.FontWeight.BOLD, color=COLORES.PRIMARIO)
        
        self.GRAFICO_MOVIMIENTOS = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
        self.MOVIMIENTOS_RECIENTES = ft.ListView(spacing=10, expand=True)
        self.SOLICITUDES_REFILL = ft.ListView(spacing=10, expand=True)
        
        self._CARGAR_DATOS()
    
    
    def _CARGAR_DATOS(self):
        self._CARGAR_ESTADISTICAS()
        self._CARGAR_GRAFICO()
        self._CARGAR_MOVIMIENTOS_RECIENTES()
        self._CARGAR_SOLICITUDES_REFILL()
    
    
    def _CARGAR_ESTADISTICAS(self):
        sesion = OBTENER_SESION()
        
        INGRESOS = (
            sesion.query(func.sum(MODELO_CAJA_MOVIMIENTO.MONTO))
            .filter_by(TIPO="ingreso")
            .scalar() or 0
        )
        
        EGRESOS = (
            sesion.query(func.sum(MODELO_CAJA_MOVIMIENTO.MONTO))
            .filter_by(TIPO="egreso")
            .scalar() or 0
        )
        
        sesion.close()
        
        self.INGRESOS_TOTALES.value = f"S/ {INGRESOS:.2f}"
        self.EGRESOS_TOTALES.value = f"S/ {EGRESOS:.2f}"
        
        BALANCE = INGRESOS - EGRESOS
        self.BALANCE.value = f"S/ {BALANCE:.2f}"
        self.BALANCE.color = COLORES.EXITO if BALANCE >= 0 else COLORES.ERROR
        
        if self.PAGINA:
            self.PAGINA.update()
    
    
    def _CARGAR_GRAFICO(self):
        sesion = OBTENER_SESION()
        
        FECHA_INICIO = datetime.utcnow() - timedelta(days=7)
        
        INGRESOS_DIA = {}
        EGRESOS_DIA = {}
        
        for i in range(7):
            fecha = (FECHA_INICIO + timedelta(days=i)).date()
            INGRESOS_DIA[fecha] = 0
            EGRESOS_DIA[fecha] = 0
        
        movimientos = (
            sesion.query(MODELO_CAJA_MOVIMIENTO)
            .filter(MODELO_CAJA_MOVIMIENTO.FECHA >= FECHA_INICIO)
            .all()
        )
        
        for mov in movimientos:
            fecha = mov.FECHA.date()
            if fecha in INGRESOS_DIA:
                if mov.TIPO == "ingreso":
                    INGRESOS_DIA[fecha] += mov.MONTO
                else:
                    EGRESOS_DIA[fecha] += mov.MONTO
        
        sesion.close()
        
        self.GRAFICO_MOVIMIENTOS.controls.clear()
        
        MAXIMO = max(
            max(INGRESOS_DIA.values() or [1]),
            max(EGRESOS_DIA.values() or [1])
        )
        
        for fecha in sorted(INGRESOS_DIA.keys()):
            INGRESO = INGRESOS_DIA[fecha]
            EGRESO = EGRESOS_DIA[fecha]
            
            ANCHO_INGRESO = (INGRESO / MAXIMO * 300) if MAXIMO > 0 else 0
            ANCHO_EGRESO = (EGRESO / MAXIMO * 300) if MAXIMO > 0 else 0
            
            self.GRAFICO_MOVIMIENTOS.controls.append(
                ft.Column([
                    ft.Text(
                        fecha.strftime("%d/%m"),
                        size=12,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Row([
                        ft.Container(
                            width=ANCHO_INGRESO,
                            height=20,
                            bgcolor=COLORES.EXITO,
                            border_radius=TAMANOS.RADIO_BORDE,
                        ),
                        ft.Text(f"S/ {INGRESO:.2f}", size=12),
                    ]),
                    ft.Row([
                        ft.Container(
                            width=ANCHO_EGRESO,
                            height=20,
                            bgcolor=COLORES.ERROR,
                            border_radius=TAMANOS.RADIO_BORDE,
                        ),
                        ft.Text(f"S/ {EGRESO:.2f}", size=12),
                    ]),
                ], spacing=5)
            )
        
        if self.PAGINA:
            self.PAGINA.update()
    
    
    def _CARGAR_MOVIMIENTOS_RECIENTES(self):
        sesion = OBTENER_SESION()
        
        movimientos = (
            sesion.query(MODELO_CAJA_MOVIMIENTO)
            .order_by(MODELO_CAJA_MOVIMIENTO.FECHA.desc())
            .limit(20)
            .all()
        )
        
        self.MOVIMIENTOS_RECIENTES.controls.clear()
        
        if not movimientos:
            self.MOVIMIENTOS_RECIENTES.controls.append(
                ft.Text("No hay movimientos registrados", color=COLORES.TEXTO_SECUNDARIO)
            )
        else:
            for mov in movimientos:
                self.MOVIMIENTOS_RECIENTES.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(
                                ICONOS.INGRESO if mov.TIPO == "ingreso" else ICONOS.EGRESO,
                                color=COLORES.EXITO if mov.TIPO == "ingreso" else COLORES.ERROR
                            ),
                            ft.Column([
                                ft.Text(mov.CONCEPTO, weight=ft.FontWeight.BOLD),
                                ft.Text(
                                    mov.FECHA.strftime("%d/%m/%Y %H:%M"),
                                    color=COLORES.TEXTO_SECUNDARIO,
                                    size=12
                                ),
                            ], expand=True),
                            ft.Text(
                                f"S/ {mov.MONTO:.2f}",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=COLORES.EXITO if mov.TIPO == "ingreso" else COLORES.ERROR
                            ),
                        ]),
                        padding=10,
                        border=ft.border.all(1, COLORES.BORDE),
                        border_radius=TAMANOS.RADIO_BORDE,
                    )
                )
        
        sesion.close()
        
        if self.PAGINA:
            self.PAGINA.update()
    
    
    def _CARGAR_SOLICITUDES_REFILL(self):
        sesion = OBTENER_SESION()
        
        solicitudes = (
            sesion.query(MODELO_REFILL_SOLICITUD)
            .filter_by(ESTADO="pendiente")
            .order_by(MODELO_REFILL_SOLICITUD.FECHA_SOLICITUD.desc())
            .all()
        )
        
        self.SOLICITUDES_REFILL.controls.clear()
        
        if not solicitudes:
            self.SOLICITUDES_REFILL.controls.append(
                ft.Text("No hay solicitudes pendientes", color=COLORES.TEXTO_SECUNDARIO)
            )
        else:
            for solicitud in solicitudes:
                from core.base_datos.ConfiguracionBD import MODELO_INSUMO, MODELO_USUARIO
                
                insumo = sesion.query(MODELO_INSUMO).filter_by(ID=solicitud.INSUMO_ID).first()
                usuario = sesion.query(MODELO_USUARIO).filter_by(ID=solicitud.USUARIO_SOLICITA).first()
                
                self.SOLICITUDES_REFILL.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ICONOS.ALERTA, color=COLORES.ADVERTENCIA),
                                ft.Text(
                                    insumo.NOMBRE if insumo else "Insumo",
                                    weight=ft.FontWeight.BOLD
                                ),
                            ]),
                            ft.Text(f"Cantidad: {solicitud.CANTIDAD_SOLICITADA}"),
                            ft.Text(
                                f"Solicitado por: {usuario.NOMBRE if usuario else 'Desconocido'}",
                                color=COLORES.TEXTO_SECUNDARIO,
                                size=12
                            ),
                            ft.Text(
                                solicitud.FECHA_SOLICITUD.strftime("%d/%m/%Y %H:%M"),
                                color=COLORES.TEXTO_SECUNDARIO,
                                size=12
                            ),
                            ft.Row([
                                ft.ElevatedButton(
                                    "Aprobar",
                                    icon=ICONOS.CONFIRMAR,
                                    bgcolor=COLORES.EXITO,
                                    on_click=lambda e, s=solicitud: self._APROBAR_REFILL(s)
                                ),
                                ft.ElevatedButton(
                                    "Rechazar",
                                    icon=ICONOS.CANCELAR,
                                    bgcolor=COLORES.ERROR,
                                    on_click=lambda e, s=solicitud: self._RECHAZAR_REFILL(s)
                                ),
                            ], spacing=10),
                        ], spacing=10),
                        padding=15,
                        border=ft.border.all(1, COLORES.ADVERTENCIA),
                        border_radius=TAMANOS.RADIO_BORDE,
                        bgcolor=COLORES.FONDO_TARJETA,
                    )
                )
        
        sesion.close()
        
        if self.PAGINA:
            self.PAGINA.update()
    
    
    def _APROBAR_REFILL(self, SOLICITUD):
        sesion = OBTENER_SESION()
        
        solicitud = sesion.query(MODELO_REFILL_SOLICITUD).filter_by(ID=SOLICITUD.ID).first()
        if solicitud:
            solicitud.ESTADO = "aprobado"
            solicitud.APROBADO_POR = self.USUARIO_ID
            solicitud.FECHA_APROBACION = datetime.utcnow()
            sesion.commit()
            
            from core.base_datos.ConfiguracionBD import MODELO_INSUMO
            insumo = sesion.query(MODELO_INSUMO).filter_by(ID=solicitud.INSUMO_ID).first()
            if insumo:
                insumo.CANTIDAD_ACTUAL += solicitud.CANTIDAD_SOLICITADA
                sesion.commit()
        
        sesion.close()
        
        self._CARGAR_SOLICITUDES_REFILL()
        
        self.PAGINA.snack_bar = ft.SnackBar(
            content=ft.Text("Solicitud aprobada y stock actualizado"),
            bgcolor=COLORES.EXITO
        )
        self.PAGINA.snack_bar.open = True
        self.PAGINA.update()
    
    
    def _RECHAZAR_REFILL(self, SOLICITUD):
        sesion = OBTENER_SESION()
        
        solicitud = sesion.query(MODELO_REFILL_SOLICITUD).filter_by(ID=SOLICITUD.ID).first()
        if solicitud:
            solicitud.ESTADO = "rechazado"
            solicitud.APROBADO_POR = self.USUARIO_ID
            solicitud.FECHA_APROBACION = datetime.utcnow()
            sesion.commit()
        
        sesion.close()
        
        self._CARGAR_SOLICITUDES_REFILL()
        
        self.PAGINA.snack_bar = ft.SnackBar(
            content=ft.Text("Solicitud rechazada"),
            bgcolor=COLORES.ADVERTENCIA
        )
        self.PAGINA.snack_bar.open = True
        self.PAGINA.update()
    
    
    def CONSTRUIR(self) -> ft.Control:
        return ft.Column([
            ft.Row([
                ft.Text("Finanzas y Control", size=TAMANOS.TITULO, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.ElevatedButton("Menú", icon=ICONOS.DASHBOARD, on_click=self._IR_MENU),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Text("INGRESOS", size=14, color=COLORES.TEXTO_SECUNDARIO),
                        self.INGRESOS_TOTALES,
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=20,
                    border=ft.border.all(2, COLORES.EXITO),
                    border_radius=TAMANOS.RADIO_BORDE,
                    expand=True,
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("EGRESOS", size=14, color=COLORES.TEXTO_SECUNDARIO),
                        self.EGRESOS_TOTALES,
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=20,
                    border=ft.border.all(2, COLORES.ERROR),
                    border_radius=TAMANOS.RADIO_BORDE,
                    expand=True,
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("BALANCE", size=14, color=COLORES.TEXTO_SECUNDARIO),
                        self.BALANCE,
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=20,
                    border=ft.border.all(2, COLORES.PRIMARIO),
                    border_radius=TAMANOS.RADIO_BORDE,
                    expand=True,
                ),
            ], spacing=10),
            
            ft.Divider(),
            
            ft.Tabs(
                selected_index=0,
                tabs=[
                    ft.Tab(
                        text="Gráfico Semanal",
                        icon=ICONOS.ESTADISTICAS,
                        content=ft.Container(
                            content=self.GRAFICO_MOVIMIENTOS,
                            padding=10,
                        )
                    ),
                    ft.Tab(
                        text="Movimientos",
                        icon=ICONOS.HISTORIAL,
                        content=ft.Container(
                            content=self.MOVIMIENTOS_RECIENTES,
                            padding=10,
                        )
                    ),
                    ft.Tab(
                        text="Solicitudes Refill",
                        icon=ICONOS.ALERTA,
                        content=ft.Container(
                            content=self.SOLICITUDES_REFILL,
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
