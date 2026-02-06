"""
Vista de Monitoreo en Tiempo Real para Admin/SuperAdmin
Muestra logs de eventos WebSocket, alertas de cocina, solicitudes de refill, etc.
"""
import flet as ft
from datetime import datetime, timezone
import json

from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION,
    MODELO_EVENTO_REALTIME,
    MODELO_ALERTA_COCINA,
    MODELO_REFILL_SOLICITUD,
    MODELO_USUARIO,
    MODELO_PEDIDO,
)
from core.constantes import COLORES, TAMANOS, ICONOS
from core.decoradores.DecoradorVistas import REQUIERE_ROL
from core.Constantes import ROLES
from core.realtime import dispatcher, logs


@REQUIERE_ROL(ROLES.ADMIN, ROLES.SUPERADMIN)
class MonitorRealtimePage:
    """Panel de monitoreo de eventos en tiempo real"""
    
    def __init__(self, PAGINA: ft.Page, USUARIO):
        self._pagina = PAGINA
        self._usuario = USUARIO
        
        # Listas para mostrar datos
        self._logs_live = ft.ListView(spacing=5, expand=True, auto_scroll=True)
        self._alertas_cocina = ft.ListView(spacing=10, expand=True)
        self._solicitudes_refill = ft.ListView(spacing=10, expand=True)
        self._eventos_bd = ft.ListView(spacing=10, expand=True)
        
        # Contador de eventos
        self._contador_eventos = ft.Text("0 eventos", size=14, color=COLORES.TEXTO_SECUNDARIO)
        
        # Registrar callbacks realtime
        self._registrar_callbacks()
        
        # Cargar datos iniciales
        self._cargar_datos()
    
    def _registrar_callbacks(self):
        """Registra callbacks para todos los tipos de eventos"""
        try:
            # Catch-all para cualquier tipo de evento
            dispatcher.register('voucher_nuevo', self._on_evento_realtime)
            dispatcher.register('voucher_whatsapp', self._on_evento_realtime)
            dispatcher.register('voucher_aprobado', self._on_evento_realtime)
            dispatcher.register('voucher_rechazado', self._on_evento_realtime)
            dispatcher.register('pedido_aprobado', self._on_evento_realtime)
            dispatcher.register('alerta_cocina', self._on_evento_realtime)
            dispatcher.register('refill_solicitado', self._on_evento_realtime)
        except Exception:
            pass
    
    def _on_evento_realtime(self, payload: dict):
        """Callback para eventos en tiempo real"""
        try:
            tipo = payload.get('tipo', 'desconocido')
            fecha = payload.get('fecha', datetime.now(timezone.utc).isoformat())
            
            # Crear tarjeta visual del evento
            color_icono = COLORES.PRIMARIO
            icono = ft.icons.NOTIFICATIONS
            
            if 'voucher' in tipo:
                icono = ft.icons.RECEIPT
                color_icono = COLORES.ADVERTENCIA
            elif 'alerta' in tipo:
                icono = ft.icons.WARNING
                color_icono = COLORES.ERROR
            elif 'refill' in tipo:
                icono = ft.icons.REFRESH
                color_icono = COLORES.EXITO
            elif 'pedido' in tipo:
                icono = ft.icons.SHOPPING_BAG
                color_icono = COLORES.PRIMARIO
            
            evento_card = ft.Container(
                content=ft.Row([
                    ft.Icon(icono, color=color_icono, size=20),
                    ft.Column([
                        ft.Text(f"{tipo.upper()}", weight=ft.FontWeight.BOLD, size=12),
                        ft.Text(f"{json.dumps(payload, ensure_ascii=False)[:100]}...", size=10, color=COLORES.TEXTO_SECUNDARIO),
                        ft.Text(fecha[:19], size=9, color=COLORES.TEXTO_SECUNDARIO),
                    ], spacing=2, expand=True),
                ], spacing=10),
                padding=8,
                border=ft.Border.all(1, COLORES.BORDE),
                border_radius=5,
                bgcolor=COLORES.FONDO_TARJETA,
            )
            
            # Añadir al inicio de la lista
            self._logs_live.controls.insert(0, evento_card)
            
            # Limitar a 100 eventos
            if len(self._logs_live.controls) > 100:
                self._logs_live.controls.pop()
            
            # Actualizar contador
            self._contador_eventos.value = f"{len(logs)} eventos totales"
            
            # Recargar datos de BD si es alerta o refill
            if 'alerta' in tipo:
                self._cargar_alertas_cocina()
            elif 'refill' in tipo:
                self._cargar_solicitudes_refill()
            
            if self._pagina:
                self._pagina.update()
        except Exception as e:
            pass
    
    def _cargar_datos(self):
        """Carga datos iniciales desde BD"""
        self._cargar_logs_memoria()
        self._cargar_alertas_cocina()
        self._cargar_solicitudes_refill()
        self._cargar_eventos_bd()
    
    def _cargar_logs_memoria(self):
        """Carga logs en memoria del dispatcher"""
        try:
            self._logs_live.controls.clear()
            
            # Mostrar últimos 50 eventos en memoria
            for evento in reversed(logs[-50:]):
                tipo = evento.get('tipo', 'desconocido')
                fecha = evento.get('fecha', '')
                
                self._logs_live.controls.append(ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.CIRCLE, size=8, color=COLORES.PRIMARIO),
                        ft.Text(f"{tipo}", size=11, weight=ft.FontWeight.BOLD),
                        ft.Text(f"{str(evento)[:80]}...", size=10, color=COLORES.TEXTO_SECUNDARIO, expand=True),
                    ], spacing=5),
                    padding=5,
                ))
            
            self._contador_eventos.value = f"{len(logs)} eventos en memoria"
            
            if self._pagina:
                self._pagina.update()
        except Exception:
            pass
    
    def _cargar_alertas_cocina(self):
        """Carga alertas de cocina desde BD"""
        try:
            sesion = OBTENER_SESION()
            
            # Últimas 20 alertas
            alertas = (
                sesion.query(MODELO_ALERTA_COCINA)
                .order_by(MODELO_ALERTA_COCINA.FECHA_ENVIO.desc())
                .limit(20)
                .all()
            )
            
            self._alertas_cocina.controls.clear()
            
            for alerta in alertas:
                color_borde = COLORES.EXITO if alerta.LEIDA else COLORES.ERROR
                
                self._alertas_cocina.controls.append(ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.icons.WARNING, color=color_borde),
                            ft.Text(f"Alerta #{alerta.ID} - Pedido #{alerta.PEDIDO_ID}", weight=ft.FontWeight.BOLD),
                            ft.Container(expand=True),
                            ft.Text("✓ Leída" if alerta.LEIDA else "● Pendiente", color=color_borde),
                        ]),
                        ft.Text(alerta.MENSAJE or "Sin mensaje", size=12),
                        ft.Text(f"Prioridad: {alerta.PRIORIDAD} | {alerta.FECHA_ENVIO.strftime('%Y-%m-%d %H:%M')}", size=10, color=COLORES.TEXTO_SECUNDARIO),
                    ], spacing=5),
                    padding=10,
                    border=ft.Border.all(1, color_borde),
                    border_radius=8,
                ))
            
            sesion.close()
            
            if self._pagina:
                self._pagina.update()
        except Exception:
            pass
    
    def _cargar_solicitudes_refill(self):
        """Carga solicitudes de refill desde BD"""
        try:
            sesion = OBTENER_SESION()
            
            # Últimas 20 solicitudes
            solicitudes = (
                sesion.query(MODELO_REFILL_SOLICITUD)
                .order_by(MODELO_REFILL_SOLICITUD.FECHA_SOLICITUD.desc())
                .limit(20)
                .all()
            )
            
            self._solicitudes_refill.controls.clear()
            
            for sol in solicitudes:
                color_estado = COLORES.ADVERTENCIA if sol.ESTADO == "pendiente" else COLORES.EXITO
                
                self._solicitudes_refill.controls.append(ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.icons.REFRESH, color=color_estado),
                            ft.Text(f"Refill #{sol.ID}", weight=ft.FontWeight.BOLD),
                            ft.Container(expand=True),
                            ft.Text(sol.ESTADO.upper(), color=color_estado),
                        ]),
                        ft.Text(f"Cantidad: {sol.CANTIDAD_SOLICITADA}", size=12),
                        ft.Text(sol.FECHA_SOLICITUD.strftime('%Y-%m-%d %H:%M'), size=10, color=COLORES.TEXTO_SECUNDARIO),
                    ], spacing=5),
                    padding=10,
                    border=ft.Border.all(1, color_estado),
                    border_radius=8,
                ))
            
            sesion.close()
            
            if self._pagina:
                self._pagina.update()
        except Exception:
            pass
    
    def _cargar_eventos_bd(self):
        """Carga eventos almacenados en BD"""
        try:
            sesion = OBTENER_SESION()
            
            # Últimos 30 eventos
            eventos = (
                sesion.query(MODELO_EVENTO_REALTIME)
                .order_by(MODELO_EVENTO_REALTIME.FECHA.desc())
                .limit(30)
                .all()
            )
            
            self._eventos_bd.controls.clear()
            
            for evento in eventos:
                try:
                    payload = json.loads(evento.PAYLOAD)
                except:
                    payload = {}
                
                self._eventos_bd.controls.append(ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.icons.DATA_OBJECT, color=COLORES.PRIMARIO, size=16),
                            ft.Text(f"{evento.TIPO}", weight=ft.FontWeight.BOLD, size=12),
                            ft.Container(expand=True),
                            ft.Text(evento.FECHA.strftime('%H:%M:%S'), size=10, color=COLORES.TEXTO_SECUNDARIO),
                        ]),
                        ft.Text(f"{str(payload)[:100]}...", size=10, color=COLORES.TEXTO_SECUNDARIO),
                    ], spacing=3),
                    padding=8,
                    border=ft.Border.all(1, COLORES.BORDE),
                    border_radius=5,
                ))
            
            sesion.close()
            
            if self._pagina:
                self._pagina.update()
        except Exception:
            pass
    
    def CONSTRUIR(self):
        """Construye la vista completa"""
        return ft.Column([
            # Header
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.icons.MONITOR_HEART, color=COLORES.PRIMARIO, size=32),
                    ft.Column([
                        ft.Text("Monitor en Tiempo Real", size=24, weight=ft.FontWeight.BOLD),
                        self._contador_eventos,
                    ], spacing=0),
                    ft.Container(expand=True),
                    ft.IconButton(
                        icon=ft.icons.REFRESH,
                        on_click=lambda _: self._cargar_datos(),
                        tooltip="Recargar"
                    ),
                ]),
                padding=20,
                bgcolor=COLORES.FONDO_TARJETA,
                border_radius=TAMANOS.RADIO_BORDE,
            ),
            
            ft.Divider(height=20),
            
            # Tabs con diferentes vistas
            ft.Tabs(
                selected_index=0,
                animation_duration=300,
                tabs=[
                    ft.Tab(
                        text="Eventos Live",
                        icon=ft.icons.BOLT,
                        content=ft.Container(
                            content=self._logs_live,
                            padding=10,
                        ),
                    ),
                    ft.Tab(
                        text="Alertas Cocina",
                        icon=ft.icons.WARNING,
                        content=ft.Container(
                            content=self._alertas_cocina,
                            padding=10,
                        ),
                    ),
                    ft.Tab(
                        text="Solicitudes Refill",
                        icon=ft.icons.REFRESH,
                        content=ft.Container(
                            content=self._solicitudes_refill,
                            padding=10,
                        ),
                    ),
                    ft.Tab(
                        text="Eventos BD",
                        icon=ft.icons.DATABASE,
                        content=ft.Container(
                            content=self._eventos_bd,
                            padding=10,
                        ),
                    ),
                ],
                expand=True,
            ),
        ], expand=True, spacing=10)
