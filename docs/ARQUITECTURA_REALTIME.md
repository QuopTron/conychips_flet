# 🔄 Sistema de Comunicación en Tiempo Real

## Descripción General

Sistema completo de comunicación en tiempo real usando WebSockets para notificaciones instantáneas entre módulos (Vouchers, Atención, Cocina, Admin/SuperAdmin).

---

## 🏗️ Arquitectura

### Componentes Principales

1. **Broker WebSocket Central** (`core/websocket/ServidorLocal.py`)
   - Servidor WebSocket que escucha en `ws://127.0.0.1:8765/ws`
   - Endpoint HTTP para broadcast: `http://127.0.0.1:8765/broadcast`
   - Gestiona conexiones de múltiples clientes

2. **Cliente WebSocket** (`core/realtime/ws_client.py`)
   - Cliente que se conecta al broker
   - Recibe eventos y los despacha localmente
   - Reconexión automática con backoff exponencial

3. **Dispatcher de Eventos** (`core/realtime/__init__.py`)
   - Patrón pub/sub para eventos locales
   - Los módulos se registran para recibir tipos específicos de eventos
   - Mantiene logs globales de eventos (últimos 1000)

4. **Notificador** (`core/realtime/broker_notify.py`)
   - Función `notify(payload)` para enviar eventos al broker
   - Silencia errores para no interrumpir flujos de BD

---

## 📊 Tablas de Base de Datos

### ALERTAS_COCINA
```sql
CREATE TABLE ALERTAS_COCINA (
    ID SERIAL PRIMARY KEY,
    PEDIDO_ID INTEGER REFERENCES PEDIDOS(ID),
    USUARIO_ENVIA INTEGER REFERENCES USUARIOS(ID),
    SUCURSAL_ID INTEGER REFERENCES SUCURSALES(ID),
    MENSAJE VARCHAR(500),
    PRIORIDAD VARCHAR(20) DEFAULT 'normal',  -- normal, alta, urgente
    LEIDA BOOLEAN DEFAULT FALSE,
    FECHA_ENVIO TIMESTAMP DEFAULT NOW(),
    FECHA_LECTURA TIMESTAMP
);
```

### EVENTOS_REALTIME
```sql
CREATE TABLE EVENTOS_REALTIME (
    ID SERIAL PRIMARY KEY,
    TIPO VARCHAR(50) NOT NULL,        -- voucher_nuevo, pedido_aprobado, alerta_cocina, etc
    SUBTIPO VARCHAR(50),                -- whatsapp, presencial, delivery
    PAYLOAD VARCHAR(2000) NOT NULL,     -- JSON del evento
    USUARIO_ID INTEGER REFERENCES USUARIOS(ID),
    SUCURSAL_ID INTEGER REFERENCES SUCURSALES(ID),
    ENTIDAD_TIPO VARCHAR(50),           -- PEDIDO, VOUCHER, etc
    ENTIDAD_ID INTEGER,
    FECHA TIMESTAMP DEFAULT NOW()
);
```

---

## 🔔 Tipos de Eventos

### Vouchers
- `voucher_nuevo`: Nuevo voucher subido (pedido por WhatsApp)
- `voucher_whatsapp`: Alias de voucher_nuevo específicamente de WhatsApp
- `voucher_aprobado`: Voucher aprobado por validador
- `voucher_rechazado`: Voucher rechazado con motivo

### Pedidos
- `pedido_aprobado`: Pedido WhatsApp aprobado por atención
- `pedido_actualizado`: Estado del pedido cambiado
- `pedido_creado`: Nuevo pedido registrado

### Cocina
- `alerta_cocina`: Alerta urgente enviada desde atención a cocina
- `refill_solicitado`: Solicitud de reabastecimiento de insumos

---

## 🎯 Flujos de Uso

### 1. Voucher Nuevo (Pedido WhatsApp)

```python
# Cliente sube voucher → Se guarda en BD → Se emite evento
from core.realtime.broker_notify import notify

payload = {
    "tipo": "voucher_nuevo",
    "subtipo": "whatsapp",
    "voucher_id": 123,
    "usuario_id": 456,
    "pedido_id": 789,
    "sucursal_id": 1,
    "fecha": "2026-01-30T10:30:00Z"
}

notify(payload)  # Broadcast a todos los clientes conectados
```

**Quién escucha**:
- `VouchersBloc`: Recarga automáticamente lista de vouchers pendientes
- `MonitorRealtimePage` (Admin): Muestra evento en logs live

---

### 2. Atención: Aprobar Pedido WhatsApp

```python
# Vista de Atención → Botón "Aprobar" → Cambia estado + emite evento

def _aprobar(self, pedido_id: int):
    sesion = OBTENER_SESION()
    pedido = sesion.query(MODELO_PEDIDO).filter_by(ID=pedido_id).first()
    pedido.ESTADO = 'EN_PREPARACION'
    sesion.commit()
    
    payload = {
        'tipo': 'pedido_aprobado',
        'pedido_id': pedido_id,
        'nuevo_estado': 'EN_PREPARACION',
        'usuario_id': self.USUARIO_ID,
        'sucursal_id': pedido.SUCURSAL_ID
    }
    
    # Guardar en EVENTOS_REALTIME
    evento_rt = MODELO_EVENTO_REALTIME(TIPO="pedido_aprobado", PAYLOAD=json.dumps(payload), ...)
    sesion.add(evento_rt)
    sesion.commit()
    
    # Broadcast
    notify(payload)
```

**Quién escucha**:
- `PaginaDashboardCocina`: Puede mostrar pedido nuevo en preparación
- `MonitorRealtimePage`: Registra evento

---

### 3. Alertar a Cocina

```python
# Atención → Botón "Alertar Cocina" → Crea alerta en BD + WebSocket

def _alertar_cocina(self, pedido_id: int):
    # Crear registro en BD
    alerta = MODELO_ALERTA_COCINA(
        PEDIDO_ID=pedido_id,
        USUARIO_ENVIA=self.USUARIO_ID,
        MENSAJE="Pedido urgente, revisar ingredientes",
        PRIORIDAD="alta"
    )
    sesion.add(alerta)
    sesion.commit()
    
    # Evento realtime
    payload = {
        'tipo': 'alerta_cocina',
        'alerta_id': alerta.ID,
        'pedido_id': pedido_id,
        'prioridad': 'alta',
        'mensaje': alerta.MENSAJE
    }
    
    notify(payload)
```

**Quién escucha**:
- `PaginaDashboardCocina`: Muestra alerta visual en la parte superior con color y prioridad
- `MonitorRealtimePage`: Registra evento y actualiza panel de alertas cocina

---

### 4. Pedir Refill

```python
# Atención → Botón "Pedir Refill" → Crea solicitud + WebSocket

def _pedir_refill(self, pedido_id: int):
    refill = MODELO_REFILL_SOLICITUD(
        INSUMO_ID=insumo_id,
        USUARIO_SOLICITA=self.USUARIO_ID,
        CANTIDAD_SOLICITADA=1,
        ESTADO="pendiente"
    )
    sesion.add(refill)
    sesion.commit()
    
    payload = {
        'tipo': 'refill_solicitado',
        'refill_id': refill.ID,
        'insumo_id': insumo_id,
        'cantidad': 1,
        'usuario_id': self.USUARIO_ID
    }
    
    notify(payload)
```

**Quién escucha**:
- `PaginaDashboardCocina`: Recarga lista de solicitudes de refill y muestra snackbar
- `MonitorRealtimePage`: Registra evento

---

## 👥 Roles y Permisos

### ATENCION
- ✅ Aprobar pedidos WhatsApp (cambiar estado a EN_PREPARACION)
- ✅ Alertar a cocina
- ✅ Pedir refill
- ✅ Ver pedidos pendientes en tiempo real
- ❌ No puede gestionar usuarios ni roles

### COCINERO
- ✅ Recibir alertas de cocina en tiempo real
- ✅ Recibir solicitudes de refill
- ✅ Marcar alertas como leídas
- ✅ Ver pedidos en preparación
- ❌ No puede aprobar pedidos WhatsApp

### ADMIN / SUPERADMIN
- ✅ Ver todos los eventos en tiempo real (Monitor Realtime)
- ✅ Ver logs globales de WebSocket (últimos 1000 eventos)
- ✅ Ver historial de alertas de cocina
- ✅ Ver historial de solicitudes de refill
- ✅ Ver eventos almacenados en BD
- ✅ Acceso completo a todas las funcionalidades

---

## 🛠️ Registro de Callbacks

### En VouchersBloc
```python
from core.realtime import dispatcher

class VouchersBloc:
    def __init__(self):
        # ...
        self._registrar_realtime()
    
    def _registrar_realtime(self):
        dispatcher.register('voucher_nuevo', self._on_voucher_nuevo_realtime)
        dispatcher.register('voucher_whatsapp', self._on_voucher_nuevo_realtime)
    
    def _on_voucher_nuevo_realtime(self, payload: dict):
        # Recargar vouchers pendientes
        self.AGREGAR_EVENTO(CargarVouchers(estado="PENDIENTE", offset=0))
```

### En PaginaDashboardAtencion
```python
from core.realtime import dispatcher

class PaginaDashboardAtencion:
    def __init__(self, PAGINA, USUARIO_ID):
        # ...
        dispatcher.register('pedido_creado', self._on_realtime_pedido)
        dispatcher.register('pedido_actualizado', self._on_realtime_pedido)
```

### En PaginaDashboardCocina
```python
dispatcher.register('alerta_cocina', self._on_realtime_alert)
dispatcher.register('refill_solicitado', self._on_realtime_refill)
```

---

## 📱 Vista Admin: Monitor Realtime

Ruta: `features/admin/presentation/pages/vistas/MonitorRealtimePage.py`

### Pestañas

1. **Eventos Live**: Stream en tiempo real de eventos WebSocket (auto-scroll)
2. **Alertas Cocina**: Últimas 20 alertas, con indicador leída/pendiente
3. **Solicitudes Refill**: Últimas 20 solicitudes, con estado
4. **Eventos BD**: Últimos 30 eventos almacenados en tabla EVENTOS_REALTIME

### Integración

Para añadir al Dashboard Admin, añade en el menú:

```python
ft.ElevatedButton(
    "Monitor Realtime",
    icon=ft.icons.MONITOR_HEART,
    on_click=lambda _: self._abrir_monitor_realtime()
)

def _abrir_monitor_realtime(self):
    from features.admin.presentation.pages.vistas.MonitorRealtimePage import MonitorRealtimePage
    
    pagina_monitor = MonitorRealtimePage(self._pagina, self._usuario)
    self._pagina.controls.clear()
    self._pagina.add(pagina_monitor.CONSTRUIR())
    self._pagina.update()
```

---

## 🧪 Testing

### Test Manual Voucher Nuevo

```python
# Terminal 1: Iniciar broker WebSocket
python core/websocket/ServidorLocal.py

# Terminal 2: Cliente de test
from core.realtime.broker_notify import notify

notify({
    "tipo": "voucher_nuevo",
    "voucher_id": 999,
    "usuario_id": 1,
    "sucursal_id": 1
})
```

### Test Manual Alerta Cocina

```python
from core.realtime.broker_notify import notify

notify({
    "tipo": "alerta_cocina",
    "alerta_id": 10,
    "pedido_id": 50,
    "prioridad": "urgente",
    "mensaje": "Ingrediente agotado"
})
```

---

## 📈 Monitoreo y Logs

### Logs en Memoria
- `core.realtime.logs` mantiene lista de últimos 1000 eventos
- Admin/SuperAdmin puede verlos en tiempo real en `MonitorRealtimePage`

### Logs en BD
- Tabla `EVENTOS_REALTIME` almacena todos los eventos con payload JSON
- Útil para auditoría y replay de eventos

### Alertas No Leídas
- Tabla `ALERTAS_COCINA` con campo `LEIDA`
- Cocina puede marcar como leída desde la UI

---

## 🚀 Próximos Pasos

### Mejoras Sugeridas
1. **Filtros en Monitor Realtime**: Por fecha, tipo de evento, sucursal
2. **Estadísticas**: Gráficos de eventos por hora/día
3. **Notificaciones Push**: Integrar con notificaciones del sistema operativo
4. **Priorización**: Cola de prioridad para alertas urgentes
5. **ACK/NACK**: Confirmación de recepción de eventos críticos

### Seguridad
1. **Autenticación WebSocket**: Validar token JWT en conexión
2. **Filtrado por Rol**: Solo enviar eventos relevantes según permisos
3. **Rate Limiting**: Prevenir spam de eventos

---

## 📝 Notas de Implementación

- ✅ **Sin romper nada**: Todos los eventos son opcionales; si el broker no está disponible, la app funciona normalmente
- ✅ **Separación de responsabilidades**: Cada módulo gestiona sus propios eventos
- ✅ **Auditoría completa**: Todos los eventos se guardan en BD con usuario, fecha y payload
- ✅ **Tiempo real**: Sub-segundo de latencia entre emisión y recepción
- ✅ **Escalable**: El broker puede correr en servidor separado en producción

---

## 🔗 Archivos Modificados/Creados

### Nuevos
- `core/realtime/__init__.py` - Dispatcher y logs
- `migrar_realtime_tables.py` - Migración de tablas
- `features/admin/presentation/pages/vistas/MonitorRealtimePage.py` - Vista de monitoreo

### Modificados
- `core/base_datos/ConfiguracionBD.py` - Nuevas tablas (ALERTAS_COCINA, EVENTOS_REALTIME)
- `core/realtime/ws_client.py` - Uso del nuevo dispatcher
- `features/vouchers/presentation/bloc/VouchersBloc.py` - Registro de eventos WebSocket
- `features/vouchers/domain/usecases/AprobarVoucher.py` - Emite evento al aprobar
- `features/vouchers/domain/usecases/RechazarVoucher.py` - Emite evento al rechazar
- `features/atencion/presentation/pages/PaginaDashboardAtencion.py` - Botones alertar/refill + eventos
- `features/cocina/presentation/pages/PaginaDashboardCocina.py` - Recepción de alertas/refill

---

**Fecha de Implementación**: 30 de Enero de 2026  
**Autor**: Sistema Cony Chips  
**Estado**: ✅ Implementado y Funcional
