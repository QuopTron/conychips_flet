import threading
from typing import Callable, List

from .VouchersEstado import *
from .VouchersEvento import *
from ...domain.usecases import (
    ObtenerVouchersPorEstado,
    AprobarVoucher,
    RechazarVoucher,
    ObtenerEstadisticasVouchers,
)
from ...data.RepositorioVouchersImpl import REPOSITORIO_VOUCHERS_IMPL

class VouchersBloc:
    
    def __init__(self, use_threads: bool = True):
        self._estado: VouchersEstado = VouchersInicial()
        self._listeners: List[Callable[[VouchersEstado], None]] = []
        self._disposed = False
        self._use_threads = use_threads
        
        self._estado_filtro = "PENDIENTE"
        self._offset_actual = 0
        self._limite = 20
        self._vouchers_actuales = []
        # Mantener lista por estado para evitar mezcla entre estados
        self._vouchers_por_estado = {"PENDIENTE": [], "APROBADO": [], "RECHAZADO": []}
        
        self._obtener_vouchers = ObtenerVouchersPorEstado(REPOSITORIO_VOUCHERS_IMPL)
        self._aprobar_voucher = AprobarVoucher(REPOSITORIO_VOUCHERS_IMPL)
        self._rechazar_voucher = RechazarVoucher(REPOSITORIO_VOUCHERS_IMPL)
        self._obtener_estadisticas = ObtenerEstadisticasVouchers(REPOSITORIO_VOUCHERS_IMPL)
        
        # Registrar callback para eventos realtime de vouchers
        self._registrar_realtime()
    
    def _registrar_realtime(self):
        """Registra callbacks para eventos WebSocket de nuevos vouchers"""
        try:
            from core.realtime import dispatcher
            dispatcher.register('voucher_nuevo', self._on_voucher_nuevo_realtime)
            dispatcher.register('voucher_whatsapp', self._on_voucher_nuevo_realtime)
        except Exception as e:
            pass  # Silenciar si dispatcher no disponible
    
    def _on_voucher_nuevo_realtime(self, payload: dict):
        """Callback cuando llega un nuevo voucher via WebSocket"""
        try:
            # Recargar vouchers pendientes para mostrar el nuevo
            evento = CargarVouchers(estado="PENDIENTE", offset=0, sucursal_id=payload.get('sucursal_id'))
            self.AGREGAR_EVENTO(evento)
        except Exception as e:
            pass
    
    @property
    def ESTADO(self) -> VouchersEstado:
        return self._estado
    
    def AGREGAR_LISTENER(self, listener: Callable[[VouchersEstado], None]):
        if listener not in self._listeners:
            self._listeners.append(listener)
    
    def REMOVER_LISTENER(self, listener: Callable[[VouchersEstado], None]):
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def _CAMBIAR_ESTADO(self, nuevo_estado: VouchersEstado):
        self._estado = nuevo_estado
        self._NOTIFICAR_LISTENERS()
    
    def _NOTIFICAR_LISTENERS(self):
        for listener in self._listeners:
            try:
                listener(self._estado)
            except Exception as error:
                pass
    
    def AGREGAR_EVENTO(self, evento: VouchersEvento):
        print(f"[DEBUG BLoC] BLoC recibe evento: {evento.__class__.__name__}")
        if isinstance(evento, CargarVouchers):
            self._manejar_cargar_vouchers(evento)
        elif isinstance(evento, CargarMasVouchers):
            self._manejar_cargar_mas()
        elif isinstance(evento, AprobarVoucherEvento):
            self._manejar_aprobar(evento)
        elif isinstance(evento, RechazarVoucherEvento):
            print(f"[DEBUG BLoC] Manejando RechazarVoucherEvento: voucher_id={evento.voucher_id}, motivo={evento.motivo[:20]}...")
            self._manejar_rechazar(evento)
        elif isinstance(evento, CambiarEstadoFiltro):
            self._manejar_cambiar_estado(evento)
        elif isinstance(evento, CargarEstadisticas):
            self._manejar_cargar_estadisticas()
    
    def _manejar_cargar_vouchers(self, evento: CargarVouchers):
        # Guardar valores de evento localmente para evitar condiciones de carrera
        estado_solicitado = evento.estado
        offset = evento.offset
        sucursal_id = evento.sucursal_id
        self._offset_actual = offset
        # Inicializar snapshot por estado
        self._vouchers_por_estado.setdefault(estado_solicitado, [])
        self._vouchers_por_estado[estado_solicitado] = []
        self._vouchers_actuales = []

        self._CAMBIAR_ESTADO(VouchersCargando(estado_actual=estado_solicitado))

        thread = threading.Thread(target=self._cargar_vouchers_sync, args=(estado_solicitado, offset, sucursal_id), daemon=True)
        thread.start()
    
    def _manejar_cargar_mas(self):
        # Calcular nuevo offset y capturar el estado actual y snapshot de vouchers
        nuevo_offset = self._offset_actual + self._limite
        estado_solicitado = self._estado_filtro
        snapshot_vouchers = list(self._vouchers_actuales) if self._vouchers_actuales else []
        self._offset_actual = nuevo_offset

        thread = threading.Thread(target=self._cargar_mas_sync, args=(estado_solicitado, nuevo_offset, snapshot_vouchers), daemon=True)
        thread.start()
    
    def _manejar_aprobar(self, evento: AprobarVoucherEvento):
        self._CAMBIAR_ESTADO(VoucherValidando(voucher_id=evento.voucher_id))
        
        thread = threading.Thread(
            target=self._aprobar_sync,
            args=(evento.voucher_id, evento.validador_id),
            daemon=True
        )
        thread.start()
    
    def _manejar_rechazar(self, evento: RechazarVoucherEvento):
        print(f"[DEBUG BLoC] _manejar_rechazar iniciado para voucher {evento.voucher_id}")
        self._CAMBIAR_ESTADO(VoucherValidando(voucher_id=evento.voucher_id))
        print(f"[DEBUG BLoC] Estado cambiado a VoucherValidando")
        
        thread = threading.Thread(
            target=self._rechazar_sync,
            args=(evento.voucher_id, evento.validador_id, evento.motivo),
            daemon=True
        )
        thread.start()
        print(f"[DEBUG BLoC] Thread de rechazo iniciado")
    
    def _manejar_cambiar_estado(self, evento: CambiarEstadoFiltro):
        # Cambiar filtro y recargar, pasando el nuevo estado al worker
        self._estado_filtro = evento.nuevo_estado
        self._offset_actual = 0
        self._vouchers_actuales = []

        estado_solicitado = evento.nuevo_estado
        self._CAMBIAR_ESTADO(VouchersCargando(estado_actual=estado_solicitado))

        thread = threading.Thread(target=self._cargar_vouchers_sync, args=(estado_solicitado, 0, None), daemon=True)
        thread.start()
    
    def _manejar_cargar_estadisticas(self):
        thread = threading.Thread(target=self._cargar_estadisticas_sync, daemon=True)
        thread.start()
    
    def _cargar_vouchers_sync(self, estado: str, offset: int = 0, sucursal_id: int | None = None):
        try:
            print(f"[DEBUG BLoC] _cargar_vouchers_sync iniciado - estado: {estado}, offset: {offset}, sucursal_id: {sucursal_id}")
            # Usar el estado proporcionado explícitamente para evitar race conditions
            vouchers = self._obtener_vouchers.ejecutar(
                estado,
                self._limite,
                offset
            )
            print(f"[DEBUG BLoC] Vouchers obtenidos: {len(vouchers)} items")

            # Guardar en la lista por estado y en el arreglo actual
            self._vouchers_por_estado.setdefault(estado, [])
            self._vouchers_por_estado[estado] = vouchers
            self._vouchers_actuales = vouchers

            total = REPOSITORIO_VOUCHERS_IMPL.contar_por_estado(estado)
            tiene_mas = (offset + len(vouchers)) < total
            
            print(f"[DEBUG BLoC] Emitiendo VouchersCargados - {len(vouchers)} vouchers, total: {total}, tiene_mas: {tiene_mas}")

            self._CAMBIAR_ESTADO(VouchersCargados(
                vouchers=vouchers,
                total=total,
                tiene_mas=tiene_mas,
                estado_actual=estado
            ))
            print(f"[DEBUG BLoC] Estado VouchersCargados emitido correctamente")
        except Exception as error:
            print(f"[DEBUG BLoC] Error en _cargar_vouchers_sync: {error}")
            import traceback
            traceback.print_exc()
            self._CAMBIAR_ESTADO(VouchersError(mensaje=f"Error: {str(error)}"))
    
    def _cargar_mas_sync(self, estado: str, offset: int = 0, snapshot_vouchers=None, sucursal_id: int | None = None):
        try:
            # Cargar más items usando el estado y offset proporcionados
            vouchers_nuevos = self._obtener_vouchers.ejecutar(
                estado,
                self._limite,
                offset
            )

            # Construir acumulado usando la lista por estado para evitar mezcla
            self._vouchers_por_estado.setdefault(estado, [])
            if estado == self._estado_filtro:
                acumulado = self._vouchers_por_estado[estado] + vouchers_nuevos
                # Actualizar la lista por estado y el arreglo interno
                self._vouchers_por_estado[estado] = acumulado
                self._vouchers_actuales = acumulado
            else:
                acumulado = vouchers_nuevos

            total = REPOSITORIO_VOUCHERS_IMPL.contar_por_estado(estado)
            tiene_mas = (offset + len(vouchers_nuevos)) < total

            self._CAMBIAR_ESTADO(VouchersCargados(
                vouchers=acumulado,
                total=total,
                tiene_mas=tiene_mas,
                estado_actual=estado
            ))
        except Exception as error:
            self._CAMBIAR_ESTADO(VouchersError(mensaje=f"Error: {str(error)}"))
    
    def _aprobar_sync(self, voucher_id: int, validador_id: int):
        try:
            resultado = self._aprobar_voucher.ejecutar(voucher_id, validador_id)
            
            if resultado["exito"]:
                # Recargar el estado actual (generalmente PENDIENTE)
                vouchers = self._obtener_vouchers.ejecutar(
                    self._estado_filtro,
                    self._limite,
                    0
                )

                # Actualizar lista por estado y offset
                self._vouchers_por_estado.setdefault(self._estado_filtro, [])
                self._vouchers_por_estado[self._estado_filtro] = vouchers
                self._vouchers_actuales = vouchers
                self._offset_actual = 0
                
                total = REPOSITORIO_VOUCHERS_IMPL.contar_por_estado(self._estado_filtro)
                tiene_mas = len(vouchers) < total
                
                # Emitir VoucherValidado con el estado destino = APROBADO
                self._CAMBIAR_ESTADO(VoucherValidado(
                    mensaje=resultado["mensaje"],
                    vouchers=vouchers,
                    total=total,
                    tiene_mas=tiene_mas,
                    estado_actual="APROBADO"  # Estado al que se movió el voucher
                ))
            else:
                self._CAMBIAR_ESTADO(VouchersError(mensaje=resultado["mensaje"]))
        except Exception as error:
            self._CAMBIAR_ESTADO(VouchersError(mensaje=f"Error: {str(error)}"))
    
    def _rechazar_sync(self, voucher_id: int, validador_id: int, motivo: str):
        print(f"[DEBUG BLoC] _rechazar_sync ejecutando: voucher={voucher_id}, validador={validador_id}")
        try:
            print(f"[DEBUG BLoC] Llamando use case rechazar_voucher.ejecutar()")
            resultado = self._rechazar_voucher.ejecutar(voucher_id, validador_id, motivo)
            print(f"[DEBUG BLoC] Resultado del use case: {resultado}")
            
            if resultado["exito"]:
                print(f"[DEBUG BLoC] Rechazo exitoso, recargando vouchers del estado {self._estado_filtro}")
                vouchers = self._obtener_vouchers.ejecutar(
                    self._estado_filtro,
                    self._limite,
                    0
                )
                print(f"[DEBUG BLoC] Vouchers obtenidos: {len(vouchers)} items")
                
                # Actualizar lista por estado y offset
                self._vouchers_por_estado.setdefault(self._estado_filtro, [])
                self._vouchers_por_estado[self._estado_filtro] = vouchers
                self._vouchers_actuales = vouchers
                self._offset_actual = 0
                
                total = REPOSITORIO_VOUCHERS_IMPL.contar_por_estado(self._estado_filtro)
                tiene_mas = len(vouchers) < total
                
                print(f"[DEBUG BLoC] Emitiendo VoucherValidado")
                # Emitir VoucherValidado con el estado destino = RECHAZADO
                self._CAMBIAR_ESTADO(VoucherValidado(
                    mensaje=resultado["mensaje"],
                    vouchers=vouchers,
                    total=total,
                    tiene_mas=tiene_mas,
                    estado_actual="RECHAZADO"  # Estado al que se movió el voucher
                ))
            else:
                print(f"[DEBUG BLoC] Rechazo fallido: {resultado['mensaje']}")
                self._CAMBIAR_ESTADO(VouchersError(mensaje=resultado["mensaje"]))
        except Exception as error:
            print(f"[DEBUG BLoC] EXCEPCIÓN en _rechazar_sync: {error}")
            import traceback
            traceback.print_exc()
            self._CAMBIAR_ESTADO(VouchersError(mensaje=f"Error: {str(error)}"))
    
    def _cargar_estadisticas_sync(self):
        try:
            stats = self._obtener_estadisticas.ejecutar()
            self._CAMBIAR_ESTADO(EstadisticasCargadas(estadisticas=stats))
        except Exception as error:
            self._CAMBIAR_ESTADO(VouchersError(mensaje=f"Error: {str(error)}"))
    
    def DISPOSE(self):
        self._listeners.clear()

VOUCHERS_BLOC = VouchersBloc()
