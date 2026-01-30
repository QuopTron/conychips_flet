"""
BLoC principal de Finanzas
Gestiona estados y eventos del módulo financiero
"""
from typing import Callable, Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy import func, or_, String
from sqlalchemy.orm import joinedload
from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION, MODELO_PEDIDO, MODELO_VOUCHER,
    MODELO_DETALLE_PEDIDO, MODELO_PRODUCTO, MODELO_OFERTA,
    MODELO_CAJA_MOVIMIENTO, MODELO_USUARIO
)
from core.cache.GestorRedis import REDIS_GLOBAL
from .finanzas_estados import *
from .finanzas_eventos import *


class FinanzasBloc:
    """BLoC para gestión de finanzas"""
    
    CACHE_KEY_RESUMEN = "finanzas:resumen"
    CACHE_TTL = 300  # 5 minutos
    
    def __init__(self, sucursales_ids: Optional[List[int]] = None):
        self.estado_actual: EstadoFinanzas = EstadoFinanzasInicial()
        self._subscriptores: list[Callable[[EstadoFinanzas], None]] = []
        self._sucursales_ids: Optional[List[int]] = sucursales_ids  # Filtro de sucursales activo
    
    def cambiar_sucursales(self, sucursales_ids: Optional[List[int]]):
        """Cambia el filtro de sucursales y recarga datos"""
        self._sucursales_ids = sucursales_ids
        self.invalidar_cache()
        self._manejar_cargar_resumen()
    
    @staticmethod
    def invalidar_cache():
        """Invalidar cache de finanzas (llamar después de modificar datos)"""
        REDIS_GLOBAL.INVALIDAR_CACHE(FinanzasBloc.CACHE_KEY_RESUMEN)
        
    def subscribirse(self, callback: Callable[[EstadoFinanzas], None]):
        """Suscribir un callback a cambios de estado"""
        if callback not in self._subscriptores:
            self._subscriptores.append(callback)
    
    def desuscribirse(self, callback: Callable[[EstadoFinanzas], None]):
        """Desuscribir un callback"""
        if callback in self._subscriptores:
            self._subscriptores.remove(callback)
    
    def _emitir_estado(self, nuevo_estado: EstadoFinanzas):
        """Emitir nuevo estado a todos los subscriptores"""
        self.estado_actual = nuevo_estado
        for callback in self._subscriptores:
            try:
                callback(nuevo_estado)
            except Exception as e:
                print(f"❌ Error en callback de estado: {e}")
    
    def agregar_evento(self, evento: EventoFinanzas):
        """Agregar evento al BLoC"""
        if isinstance(evento, CargarResumenFinanciero):
            self._manejar_cargar_resumen()
        elif isinstance(evento, FiltrarPorEstado):
            self._manejar_filtrar_estado(evento)
        elif isinstance(evento, FiltrarPorFecha):
            self._manejar_filtrar_fecha(evento)
        elif isinstance(evento, BuscarPorCodigo):
            self._manejar_buscar_codigo(evento)
        elif isinstance(evento, VerDetallePedido):
            self._manejar_ver_detalle(evento)
        elif isinstance(evento, FiltrarConOfertas):
            self._manejar_filtrar_ofertas(evento)
        elif isinstance(evento, FiltrarVoucherEstado):
            self._manejar_filtrar_voucher(evento)
    
    def _manejar_cargar_resumen(self):
        """Cargar resumen financiero completo con cache"""
        try:
            self._emitir_estado(EstadoFinanzasCargando("Cargando datos financieros..."))
            
            # Intentar obtener del cache (TTL: 5 minutos)
            cached_data = REDIS_GLOBAL.OBTENER_CACHE(self.CACHE_KEY_RESUMEN)
            
            if cached_data:
                # OBTENER_CACHE ya deserializa JSON automáticamente
                resumen = ResumenFinanciero(**cached_data['resumen'])
                pedidos = [
                    PedidoResumen(
                        **{**p, 'fecha': datetime.fromisoformat(p['fecha'])}
                    ) for p in cached_data['pedidos']
                ]
                
                self._emitir_estado(EstadoFinanzasCargado(
                    resumen=resumen,
                    pedidos=pedidos
                ))
                return
            
            sesion = OBTENER_SESION()
            
            # Calcular resumen
            resumen = self._calcular_resumen(sesion)
            pedidos = self._obtener_pedidos_optimizado(sesion)
            
            sesion.close()
            
            # Guardar en cache (5 minutos)
            cache_data = {
                'resumen': {
                    'total_ingresos': resumen.total_ingresos,
                    'total_egresos': resumen.total_egresos,
                    'utilidad_neta': resumen.utilidad_neta,
                    'total_pedidos': resumen.total_pedidos,
                    'pedidos_completados': resumen.pedidos_completados,
                    'pedidos_cancelados': resumen.pedidos_cancelados,
                    'pedidos_pendientes': resumen.pedidos_pendientes,
                    'vouchers_aprobados': resumen.vouchers_aprobados,
                    'vouchers_rechazados': resumen.vouchers_rechazados,
                    'vouchers_pendientes': resumen.vouchers_pendientes
                },
                'pedidos': [{
                    'id': p.id,
                    'codigo': p.codigo,
                    'cliente': p.cliente,
                    'fecha': p.fecha.isoformat(),
                    'estado': p.estado,
                    'monto_total': p.monto_total,
                    'tiene_voucher': p.tiene_voucher,
                    'voucher_estado': p.voucher_estado,
                    'tiene_oferta': p.tiene_oferta
                } for p in pedidos]
            }
            REDIS_GLOBAL.GUARDAR_CACHE(
                self.CACHE_KEY_RESUMEN, 
                cache_data, 
                TTL_SECONDS=self.CACHE_TTL
            )
            
            self._emitir_estado(EstadoFinanzasCargado(
                resumen=resumen,
                pedidos=pedidos
            ))
            
        except Exception as e:
            self._emitir_estado(EstadoFinanzasError(
                mensaje=f"Error al cargar finanzas: {str(e)}",
                error=e
            ))
    
    def _calcular_resumen(self, sesion) -> ResumenFinanciero:
        """Calcular resumen financiero con filtro de sucursales"""
        # Base de queries
        query_base = sesion.query(MODELO_PEDIDO)
        if self._sucursales_ids:
            query_base = query_base.filter(MODELO_PEDIDO.SUCURSAL_ID.in_(self._sucursales_ids))
        
        # Contar pedidos por estado
        total_pedidos = query_base.count()
        pedidos_completados = query_base.filter_by(ESTADO="COMPLETADO").count()
        pedidos_cancelados = query_base.filter_by(ESTADO="CANCELADO").count()
        pedidos_pendientes = query_base.filter_by(ESTADO="PENDIENTE").count()
        
        # Calcular ingresos (pedidos completados) con filtro sucursales
        query_ingresos = sesion.query(MODELO_PEDIDO).filter_by(ESTADO="COMPLETADO")
        if self._sucursales_ids:
            query_ingresos = query_ingresos.filter(MODELO_PEDIDO.SUCURSAL_ID.in_(self._sucursales_ids))
        pedidos_comp = query_ingresos.all()
        total_ingresos = sum([p.MONTO_TOTAL for p in pedidos_comp if p.MONTO_TOTAL])
        
        # Calcular egresos (movimientos de caja) con filtro sucursales
        query_egresos = sesion.query(MODELO_CAJA_MOVIMIENTO).filter_by(TIPO="egreso")
        if self._sucursales_ids:
            query_egresos = query_egresos.filter(MODELO_CAJA_MOVIMIENTO.SUCURSAL_ID.in_(self._sucursales_ids))
        egresos = query_egresos.all()
        total_egresos = sum([e.MONTO for e in egresos])
        
        # Contar vouchers por estado
        vouchers_aprobados = sesion.query(MODELO_VOUCHER).filter_by(VALIDADO=True).count()
        vouchers_rechazados = sesion.query(MODELO_VOUCHER).filter_by(RECHAZADO=True).count()
        vouchers_pendientes = sesion.query(MODELO_VOUCHER).filter(
            MODELO_VOUCHER.VALIDADO == False,
            MODELO_VOUCHER.RECHAZADO == False
        ).count()
        
        return ResumenFinanciero(
            total_ingresos=total_ingresos,
            total_egresos=total_egresos,
            utilidad_neta=total_ingresos - total_egresos,
            total_pedidos=total_pedidos,
            pedidos_completados=pedidos_completados,
            pedidos_cancelados=pedidos_cancelados,
            pedidos_pendientes=pedidos_pendientes,
            vouchers_aprobados=vouchers_aprobados,
            vouchers_rechazados=vouchers_rechazados,
            vouchers_pendientes=vouchers_pendientes
        )
    
    def _obtener_pedidos_optimizado(self, sesion) -> List[PedidoResumen]:
        """Obtener pedidos con JOINS optimizados (reduce N+1 queries) y filtro de sucursales"""
        from sqlalchemy.orm import joinedload
        
        # Query con eager loading de relaciones y filtro de sucursales
        query = sesion.query(MODELO_PEDIDO)
        if self._sucursales_ids:
            query = query.filter(MODELO_PEDIDO.SUCURSAL_ID.in_(self._sucursales_ids))
        
        pedidos_db = query.order_by(MODELO_PEDIDO.FECHA_CREACION.desc()).limit(100).all()
        
        # Obtener todos los IDs de pedidos
        pedido_ids = [p.ID for p in pedidos_db]
        
        # Cargar todos los vouchers en una sola query
        vouchers_dict = {}
        if pedido_ids:
            vouchers = sesion.query(MODELO_VOUCHER).filter(
                MODELO_VOUCHER.PEDIDO_ID.in_(pedido_ids)
            ).all()
            vouchers_dict = {v.PEDIDO_ID: v for v in vouchers}
        
        # Cargar todos los clientes en una sola query
        cliente_ids = list(set([p.CLIENTE_ID for p in pedidos_db if p.CLIENTE_ID]))
        clientes_dict = {}
        if cliente_ids:
            clientes = sesion.query(MODELO_USUARIO).filter(
                MODELO_USUARIO.ID.in_(cliente_ids)
            ).all()
            clientes_dict = {c.ID: c for c in clientes}
        
        # Verificar ofertas en batch
        ofertas_dict = self._verificar_ofertas_batch(sesion, pedido_ids)
        
        # Construir resumen
        pedidos_resumen = []
        for pedido in pedidos_db:
            voucher = vouchers_dict.get(pedido.ID)
            cliente = clientes_dict.get(pedido.CLIENTE_ID)
            nombre_cliente = cliente.NOMBRE_USUARIO if cliente else "Cliente desconocido"
            
            # Determinar estado del voucher
            voucher_estado = None
            if voucher:
                if voucher.VALIDADO:
                    voucher_estado = "APROBADO"
                elif voucher.RECHAZADO:
                    voucher_estado = "RECHAZADO"
                else:
                    voucher_estado = "PENDIENTE"
            
            pedidos_resumen.append(PedidoResumen(
                id=pedido.ID,
                codigo=f"#{pedido.ID:05d}",
                cliente=nombre_cliente,
                fecha=pedido.FECHA_CREACION,
                estado=pedido.ESTADO,
                monto_total=pedido.MONTO_TOTAL,
                tiene_voucher=voucher is not None,
                voucher_estado=voucher_estado,
                tiene_oferta=ofertas_dict.get(pedido.ID, False)
            ))
        
        return pedidos_resumen
    
    def _verificar_ofertas_batch(self, sesion, pedido_ids: list) -> dict:
        """Verificar ofertas para múltiples pedidos en batch"""
        if not pedido_ids:
            return {}
        
        # Obtener todos los detalles de pedidos
        detalles = sesion.query(MODELO_DETALLE_PEDIDO).filter(
            MODELO_DETALLE_PEDIDO.PEDIDO_ID.in_(pedido_ids)
        ).all()
        
        # Agrupar por pedido
        detalles_por_pedido = {}
        for detalle in detalles:
            if detalle.PEDIDO_ID not in detalles_por_pedido:
                detalles_por_pedido[detalle.PEDIDO_ID] = []
            detalles_por_pedido[detalle.PEDIDO_ID].append(detalle.PRODUCTO_ID)
        
        # Obtener todos los productos con ofertas activas
        productos_con_oferta = set()
        if detalles:
            ofertas = sesion.query(MODELO_OFERTA).filter(
                MODELO_OFERTA.ACTIVA == True
            ).all()
            productos_con_oferta = {o.PRODUCTO_ID for o in ofertas}
        
        # Verificar qué pedidos tienen ofertas
        resultado = {}
        for pedido_id, producto_ids in detalles_por_pedido.items():
            resultado[pedido_id] = any(pid in productos_con_oferta for pid in producto_ids)
        
        return resultado
    
    def _obtener_pedidos(
        self, 
        sesion,
        filtro_estado: Optional[str] = None,
        filtro_fecha_inicio: Optional[datetime] = None,
        filtro_fecha_fin: Optional[datetime] = None,
        busqueda_codigo: Optional[str] = None
    ) -> List[PedidoResumen]:
        """Obtener lista de pedidos con filtros"""
        query = sesion.query(MODELO_PEDIDO)
        
        # Aplicar filtros
        if filtro_estado:
            query = query.filter(MODELO_PEDIDO.ESTADO == filtro_estado)
        
        if filtro_fecha_inicio and filtro_fecha_fin:
            query = query.filter(
                MODELO_PEDIDO.FECHA_CREACION >= filtro_fecha_inicio,
                MODELO_PEDIDO.FECHA_CREACION <= filtro_fecha_fin
            )
        
        if busqueda_codigo:
            query = query.filter(
                or_(
                    func.cast(MODELO_PEDIDO.ID, String).ilike(f"%{busqueda_codigo}%"),
                    MODELO_PEDIDO.NOTAS.ilike(f"%{busqueda_codigo}%")
                )
            )
        
        # Ordenar por fecha descendente
        query = query.order_by(MODELO_PEDIDO.FECHA_CREACION.desc())
        
        pedidos_db = query.limit(100).all()  # Limitar a 100 para rendimiento
        
        # Convertir a PedidoResumen
        pedidos_resumen = []
        for pedido in pedidos_db:
            # Obtener voucher asociado
            voucher = sesion.query(MODELO_VOUCHER).filter_by(PEDIDO_ID=pedido.ID).first()
            
            # Verificar si tiene ofertas
            tiene_oferta = self._pedido_tiene_oferta(sesion, pedido.ID)
            
            # Obtener nombre del cliente
            cliente = sesion.query(MODELO_USUARIO).filter_by(ID=pedido.CLIENTE_ID).first()
            nombre_cliente = cliente.NOMBRE_USUARIO if cliente else "Cliente desconocido"
            
            # Determinar estado del voucher
            voucher_estado = None
            if voucher:
                if voucher.VALIDADO:
                    voucher_estado = "APROBADO"
                elif voucher.RECHAZADO:
                    voucher_estado = "RECHAZADO"
                else:
                    voucher_estado = "PENDIENTE"
            
            pedidos_resumen.append(PedidoResumen(
                id=pedido.ID,
                codigo=f"#{pedido.ID:05d}",
                cliente=nombre_cliente,
                fecha=pedido.FECHA_CREACION,
                estado=pedido.ESTADO,
                monto_total=pedido.MONTO_TOTAL,
                tiene_voucher=voucher is not None,
                voucher_estado=voucher_estado,
                tiene_oferta=tiene_oferta
            ))
        
        return pedidos_resumen
    
    def _pedido_tiene_oferta(self, sesion, pedido_id: int) -> bool:
        """Verificar si un pedido tiene ofertas aplicadas"""
        detalles = sesion.query(MODELO_DETALLE_PEDIDO).filter_by(PEDIDO_ID=pedido_id).all()
        
        for detalle in detalles:
            oferta = sesion.query(MODELO_OFERTA).filter_by(
                PRODUCTO_ID=detalle.PRODUCTO_ID,
                ACTIVA=True
            ).first()
            if oferta:
                return True
        
        return False
    
    def _manejar_filtrar_estado(self, evento: FiltrarPorEstado):
        """Filtrar pedidos por estado"""
        if not isinstance(self.estado_actual, EstadoFinanzasCargado):
            return
        
        try:
            sesion = OBTENER_SESION()
            pedidos = self._obtener_pedidos(
                sesion,
                filtro_estado=evento.estado,
                filtro_fecha_inicio=self.estado_actual.filtro_fecha_inicio,
                filtro_fecha_fin=self.estado_actual.filtro_fecha_fin,
                busqueda_codigo=self.estado_actual.busqueda_codigo
            )
            sesion.close()
            
            self._emitir_estado(EstadoFinanzasCargado(
                resumen=self.estado_actual.resumen,
                pedidos=pedidos,
                filtro_estado=evento.estado,
                filtro_fecha_inicio=self.estado_actual.filtro_fecha_inicio,
                filtro_fecha_fin=self.estado_actual.filtro_fecha_fin,
                busqueda_codigo=self.estado_actual.busqueda_codigo
            ))
        except Exception as e:
            self._emitir_estado(EstadoFinanzasError(
                mensaje=f"Error al filtrar: {str(e)}",
                error=e
            ))
    
    def _manejar_filtrar_fecha(self, evento: FiltrarPorFecha):
        """Filtrar por rango de fechas"""
        if not isinstance(self.estado_actual, EstadoFinanzasCargado):
            return
        
        try:
            sesion = OBTENER_SESION()
            pedidos = self._obtener_pedidos(
                sesion,
                filtro_estado=self.estado_actual.filtro_estado,
                filtro_fecha_inicio=evento.fecha_inicio,
                filtro_fecha_fin=evento.fecha_fin,
                busqueda_codigo=self.estado_actual.busqueda_codigo
            )
            sesion.close()
            
            self._emitir_estado(EstadoFinanzasCargado(
                resumen=self.estado_actual.resumen,
                pedidos=pedidos,
                filtro_estado=self.estado_actual.filtro_estado,
                filtro_fecha_inicio=evento.fecha_inicio,
                filtro_fecha_fin=evento.fecha_fin,
                busqueda_codigo=self.estado_actual.busqueda_codigo
            ))
        except Exception as e:
            self._emitir_estado(EstadoFinanzasError(
                mensaje=f"Error al filtrar por fecha: {str(e)}",
                error=e
            ))
    
    def _manejar_buscar_codigo(self, evento: BuscarPorCodigo):
        """Buscar por código de pedido"""
        if not isinstance(self.estado_actual, EstadoFinanzasCargado):
            return
        
        try:
            sesion = OBTENER_SESION()
            pedidos = self._obtener_pedidos(
                sesion,
                filtro_estado=self.estado_actual.filtro_estado,
                filtro_fecha_inicio=self.estado_actual.filtro_fecha_inicio,
                filtro_fecha_fin=self.estado_actual.filtro_fecha_fin,
                busqueda_codigo=evento.codigo
            )
            sesion.close()
            
            self._emitir_estado(EstadoFinanzasCargado(
                resumen=self.estado_actual.resumen,
                pedidos=pedidos,
                filtro_estado=self.estado_actual.filtro_estado,
                filtro_fecha_inicio=self.estado_actual.filtro_fecha_inicio,
                filtro_fecha_fin=self.estado_actual.filtro_fecha_fin,
                busqueda_codigo=evento.codigo
            ))
        except Exception as e:
            self._emitir_estado(EstadoFinanzasError(
                mensaje=f"Error al buscar: {str(e)}",
                error=e
            ))
    
    def _manejar_ver_detalle(self, evento: VerDetallePedido):
        """Seleccionar un pedido para ver su detalle"""
        if not isinstance(self.estado_actual, EstadoFinanzasCargado):
            return
        
        pedido = next((p for p in self.estado_actual.pedidos if p.id == evento.pedido_id), None)
        if pedido:
            self._emitir_estado(EstadoFinanzasCargado(
                resumen=self.estado_actual.resumen,
                pedidos=self.estado_actual.pedidos,
                filtro_estado=self.estado_actual.filtro_estado,
                filtro_fecha_inicio=self.estado_actual.filtro_fecha_inicio,
                filtro_fecha_fin=self.estado_actual.filtro_fecha_fin,
                busqueda_codigo=self.estado_actual.busqueda_codigo,
                pedido_seleccionado=pedido
            ))
    
    def _manejar_filtrar_ofertas(self, evento: FiltrarConOfertas):
        """Filtrar pedidos con ofertas"""
        # TODO: Implementar filtro de ofertas
        pass
    
    def _manejar_filtrar_voucher(self, evento: FiltrarVoucherEstado):
        """Filtrar por estado de voucher"""
        if not isinstance(self.estado_actual, EstadoFinanzasCargado):
            return
        
        try:
            sesion = OBTENER_SESION()
            
            # Obtener pedidos base
            query = sesion.query(MODELO_PEDIDO)
            
            # Aplicar filtros existentes
            if self.estado_actual.filtro_estado:
                query = query.filter(MODELO_PEDIDO.ESTADO == self.estado_actual.filtro_estado)
            
            if self.estado_actual.filtro_fecha_inicio and self.estado_actual.filtro_fecha_fin:
                query = query.filter(
                    MODELO_PEDIDO.FECHA_CREACION >= self.estado_actual.filtro_fecha_inicio,
                    MODELO_PEDIDO.FECHA_CREACION <= self.estado_actual.filtro_fecha_fin
                )
            
            if self.estado_actual.busqueda_codigo:
                query = query.filter(
                    or_(
                        func.cast(MODELO_PEDIDO.ID, String).ilike(f"%{self.estado_actual.busqueda_codigo}%"),
                        MODELO_PEDIDO.NOTAS.ilike(f"%{self.estado_actual.busqueda_codigo}%")
                    )
                )
            
            # Obtener todos los pedidos
            pedidos_db = query.order_by(MODELO_PEDIDO.FECHA_CREACION.desc()).all()
            
            # Filtrar por estado de voucher
            pedidos_filtrados = []
            for pedido in pedidos_db:
                voucher = sesion.query(MODELO_VOUCHER).filter_by(PEDIDO_ID=pedido.ID).first()
                
                # Si no se especifica filtro, incluir todos
                if not evento.voucher_estado:
                    incluir = True
                # Si el pedido no tiene voucher
                elif not voucher:
                    incluir = False
                # Verificar estado del voucher
                elif evento.voucher_estado == "APROBADO":
                    incluir = voucher.VALIDADO
                elif evento.voucher_estado == "RECHAZADO":
                    incluir = voucher.RECHAZADO
                elif evento.voucher_estado == "PENDIENTE":
                    incluir = not voucher.VALIDADO and not voucher.RECHAZADO
                else:
                    incluir = True
                
                if incluir:
                    pedidos_filtrados.append(pedido)
            
            # Convertir a PedidoResumen
            pedidos_resumen = []
            for pedido in pedidos_filtrados[:100]:  # Limitar a 100
                voucher = sesion.query(MODELO_VOUCHER).filter_by(PEDIDO_ID=pedido.ID).first()
                tiene_oferta = self._pedido_tiene_oferta(sesion, pedido.ID)
                cliente = sesion.query(MODELO_USUARIO).filter_by(ID=pedido.CLIENTE_ID).first()
                nombre_cliente = cliente.NOMBRE_USUARIO if cliente else "Cliente desconocido"
                
                voucher_estado = None
                if voucher:
                    if voucher.VALIDADO:
                        voucher_estado = "APROBADO"
                    elif voucher.RECHAZADO:
                        voucher_estado = "RECHAZADO"
                    else:
                        voucher_estado = "PENDIENTE"
                
                pedidos_resumen.append(PedidoResumen(
                    id=pedido.ID,
                    codigo=f"#{pedido.ID:05d}",
                    cliente=nombre_cliente,
                    fecha=pedido.FECHA_CREACION,
                    estado=pedido.ESTADO,
                    monto_total=pedido.MONTO_TOTAL,
                    tiene_voucher=voucher is not None,
                    voucher_estado=voucher_estado,
                    tiene_oferta=tiene_oferta
                ))
            
            sesion.close()
            
            # Actualizar estado con nuevo filtro
            self._emitir_estado(EstadoFinanzasCargado(
                resumen=self.estado_actual.resumen,
                pedidos=pedidos_resumen,
                filtro_estado=self.estado_actual.filtro_estado,
                filtro_fecha_inicio=self.estado_actual.filtro_fecha_inicio,
                filtro_fecha_fin=self.estado_actual.filtro_fecha_fin,
                busqueda_codigo=self.estado_actual.busqueda_codigo
            ))
            
        except Exception as e:
            self._emitir_estado(EstadoFinanzasError(
                mensaje=f"Error al filtrar por voucher: {str(e)}",
                error=e
            ))

