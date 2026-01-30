# SISTEMA COMPLETO DE GESTIÓN - CONY CHIPS

## NUEVAS FUNCIONALIDADES IMPLEMENTADAS

### 1. SISTEMA DE NOTIFICACIONES EN TIEMPO REAL

**Archivo:** `core/websocket/GestorNotificaciones.py`

**Características:**

- Singleton para gestión centralizada
- Notificaciones por usuario y por tipo
- Callbacks asíncronos
- Persistencia en base de datos
- Tipos: pedido, pago, entrega, chat, gps, refill, sistema

**Métodos principales:**

- `ENVIAR_NOTIFICACION()`: Envía notificación a usuario específico
- `ENVIAR_MENSAJE_CHAT()`: Mensajes de chat en pedidos
- `ACTUALIZAR_GPS()`: Actualiza ubicación del motorizado
- `NOTIFICAR_CAMBIO_ESTADO_PEDIDO()`: Notifica cambios de estado
- `NOTIFICAR_REFILL_SOLICITADO()`: Alerta a admins de solicitudes

---

### 2. DASHBOARD CLIENTE

**Archivo:** `features/cliente/presentation/pages/PaginaDashboardCliente.py`

**Funcionalidades:**

- Ver pedidos activos con estados
- Catálogo de productos disponibles
- Carrito de compras
- Crear pedidos
- Subir voucher de pago
- Chat con motorizado (en delivery)
- Calificar pedidos entregados (comida, servicio, entrega)
- Ver detalle de pedidos

**Decorador:** `@REQUIERE_ROL("CLIENTE", "ADMIN", "SUPERADMIN")`

---

### 3. DASHBOARD MOTORIZADO

**Archivo:** `features/motorizado/presentation/pages/PaginaDashboardMotorizado.py`

**Funcionalidades:**

- Ver pedidos asignados
- Confirmar salida (cambio a "en_camino")
- Activar/desactivar GPS
- Enviar ubicación en tiempo real
- Chat con cliente
- Confirmar entrega
- Notificaciones automáticas de estados

**Decorador:** `@REQUIERE_ROL("MOTORIZADO", "ADMIN", "SUPERADMIN")`

---

### 4. DASHBOARD COCINA

**Archivo:** `features/cocina/presentation/pages/PaginaDashboardCocina.py`

**Funcionalidades:**

- Ver pedidos pendientes y en preparación
- Iniciar preparación
- Marcar pedido como listo
- Ver inventario de insumos
- Alertas de stock bajo
- Solicitar refill de insumos
- Historial de solicitudes de refill

**Decorador:** `@REQUIERE_ROL("COCINERO", "ADMIN", "SUPERADMIN")`

---

### 5. DASHBOARD ATENCIÓN

**Archivo:** `features/atencion/presentation/pages/PaginaDashboardAtencion.py`

**Funcionalidades:**

- Abrir/cerrar caja
- Ver saldo actual
- Ver pedidos listos
- Servir pedidos (marca como entregado)
- Cobrar automáticamente (crea ingreso en caja)
- Ver movimientos de caja
- Historial de ingresos/egresos

**Decorador:** `@REQUIERE_ROL("ATENCION", "ADMIN", "SUPERADMIN")`

---

### 6. DASHBOARD LIMPIEZA

**Archivo:** `features/limpieza/presentation/pages/PaginaDashboardLimpieza.py`

**Funcionalidades:**

- Crear reportes de limpieza
- Seleccionar sucursal y área
- Agregar observaciones
- Subir múltiples fotos por reporte
- Ver historial de reportes propios
- Ver fotos de reportes anteriores

**Decorador:** `@REQUIERE_ROL("LIMPIEZA", "ADMIN", "SUPERADMIN")`

---

### 7. PANEL FINANCIERO (ADMIN)

**Archivo:** `features/admin/presentation/pages/PaginaFinanzas.py`

**Funcionalidades:**

- Dashboard con totales: ingresos, egresos, balance
- Gráfico de barras de última semana
- Movimientos recientes con filtros
- Gestión de solicitudes de refill
- Aprobar/rechazar solicitudes
- Actualización automática de inventario

**Decorador:** `@REQUIERE_ROL("ADMIN", "SUPERADMIN")`

---

### 8. VALIDACIÓN DE VOUCHERS (ADMIN)

**Archivo:** `features/admin/presentation/pages/PaginaValidarVouchers.py`

**Funcionalidades:**

- Ver vouchers pendientes
- Ver imagen del voucher
- Validar voucher (confirma pedido automáticamente)
- Rechazar voucher
- Historial de vouchers validados
- Verificación de montos

**Decorador:** `@REQUIERE_ROL("ADMIN", "SUPERADMIN")`

---

## MODELOS DE BASE DE DATOS NUEVOS

### 1. MODELO_VOUCHER

**Campos:**

- `ID`, `PEDIDO_ID`, `USUARIO_ID`
- `IMAGEN_URL`: URL de la imagen del voucher
- `MONTO`: Monto del pago
- `METODO_PAGO`: yape, plin, transferencia, efectivo
- `VALIDADO`: boolean
- `VALIDADO_POR`: ID del admin que validó
- `FECHA_SUBIDA`, `FECHA_VALIDACION`

### 2. MODELO_REPORTE_LIMPIEZA_FOTO

**Campos:**

- `ID`, `REPORTE_ID`
- `IMAGEN_URL`: URL de la foto
- `DESCRIPCION`: Descripción opcional
- `FECHA_SUBIDA`

### 3. MODELO_UBICACION_MOTORIZADO

**Campos:**

- `ID`, `USUARIO_ID`, `PEDIDO_ID`
- `LATITUD`, `LONGITUD`
- `ESTADO`: salida, en_camino, llegada
- `FECHA`

### 4. MODELO_MENSAJE_CHAT

**Campos:**

- `ID`, `PEDIDO_ID`, `USUARIO_ID`
- `MENSAJE`: Contenido del mensaje
- `TIPO`: texto, imagen, ubicacion
- `LEIDO`: boolean
- `FECHA`

### 5. MODELO_NOTIFICACION

**Campos:**

- `ID`, `USUARIO_ID`
- `TITULO`, `MENSAJE`
- `TIPO`: pedido, pago, entrega, chat, gps, refill, sistema
- `LEIDA`: boolean
- `DATOS_EXTRA`: JSON con información adicional
- `FECHA`

### 6. MODELO_CALIFICACION

**Campos:**

- `ID`, `PEDIDO_ID`, `USUARIO_ID`
- `CALIFICACION_COMIDA`: 1-5
- `CALIFICACION_SERVICIO`: 1-5
- `CALIFICACION_ENTREGA`: 1-5
- `COMENTARIO`: Opcional
- `FECHA`

### 7. MODELO_REFILL_SOLICITUD

**Campos:**

- `ID`, `INSUMO_ID`, `USUARIO_SOLICITA`
- `CANTIDAD_SOLICITADA`
- `ESTADO`: pendiente, aprobado, rechazado
- `APROBADO_POR`: ID del admin
- `FECHA_SOLICITUD`, `FECHA_APROBACION`

---

## CONSTANTES AGREGADAS

### ICONOS NUEVOS (ConstantesUI.py)

```python
VOUCHER = ft.Icons.RECEIPT
INGRESO = ft.Icons.ARROW_CIRCLE_UP
EGRESO = ft.Icons.ARROW_CIRCLE_DOWN
DINERO = ft.Icons.ATTACH_MONEY
IMAGEN = ft.Icons.IMAGE
CHAT = ft.Icons.CHAT
ENVIAR = ft.Icons.SEND
CONFIRMAR = ft.Icons.CHECK_CIRCLE
VER = ft.Icons.VISIBILITY
ALERTA = ft.Icons.NOTIFICATION_IMPORTANT
FAVORITO = ft.Icons.FAVORITE
CARRITO = ft.Icons.SHOPPING_BAG
PEDIDO = ft.Icons.RECEIPT_LONG
HISTORIAL = ft.Icons.HISTORY
ESTADISTICAS = ft.Icons.ANALYTICS
INVENTARIO = ft.Icons.WAREHOUSE
```

### PERMISOS EXPANDIDOS (ConstantesPermisos.py)

Se agregaron 40+ permisos nuevos:

- `SUBIR_VOUCHER`, `VALIDAR_VOUCHER`
- `ACTUALIZAR_GPS`, `VER_GPS`
- `ENVIAR_MENSAJE_CHAT`, `VER_CHAT`
- `CALIFICAR_PEDIDO`, `VER_CALIFICACIONES`
- `SOLICITAR_REFILL`, `APROBAR_REFILL`
- `SUBIR_FOTO_LIMPIEZA`, `VER_REPORTES_LIMPIEZA`
- Y más...

---

## FLUJOS DE TRABAJO

### FLUJO PEDIDO COMPLETO (Cliente → Cocina → Motorizado → Cliente)

1. **Cliente:** Crea pedido desde dashboard
2. **Cliente:** Sube voucher de pago
3. **Admin:** Valida voucher → Pedido pasa a "confirmado"
4. **Cocina:** Ve pedido confirmado → Inicia preparación
5. **Cocina:** Marca pedido como "listo"
6. **Atención:** Sirve pedido (local) O Motorizado recibe asignación (delivery)
7. **Motorizado:** Confirma salida → Estado "en_camino"
8. **Motorizado:** Activa GPS → Cliente ve ubicación en tiempo real
9. **Motorizado:** Confirma entrega → Estado "entregado"
10. **Cliente:** Recibe notificación → Puede calificar

### FLUJO REFILL (Cocina → Admin → Inventario)

1. **Cocina:** Ve stock bajo en insumo
2. **Cocina:** Solicita refill con cantidad
3. **Admin:** Recibe notificación de solicitud
4. **Admin:** Revisa en PaginaFinanzas → Aprueba/rechaza
5. **Sistema:** Si aprueba, actualiza inventario automáticamente
6. **Cocina:** Ve solicitud aprobada en historial

### FLUJO CAJA (Atención → Finanzas)

1. **Atención:** Abre caja con monto inicial
2. **Atención:** Sirve pedidos → Crea ingreso automático
3. **Admin:** Ve movimientos en PaginaFinanzas
4. **Admin:** Registra egresos (compras a proveedores)
5. **Atención:** Cierra caja al finalizar turno
6. **Admin:** Revisa balance diario/semanal

---

## MIGRACIÓN DE BASE DE DATOS

**Ejecutar:**

```bash
python migrar_nuevas_tablas.py
```

Este script:

- Crea todas las tablas nuevas
- Verifica la creación
- Muestra confirmación

---

## ROLES Y NAVEGACIÓN

El sistema ahora navega automáticamente al dashboard correcto según el rol:

| ROL        | DASHBOARD                                                         |
| ---------- | ----------------------------------------------------------------- |
| CLIENTE    | PaginaDashboardCliente                                            |
| MOTORIZADO | PaginaDashboardMotorizado                                         |
| COCINERO   | PaginaDashboardCocina                                             |
| ATENCION   | PaginaDashboardAtencion                                           |
| LIMPIEZA   | PaginaDashboardLimpieza                                           |
| ADMIN      | PaginaAdmin (con acceso a PaginaFinanzas y PaginaValidarVouchers) |
| SUPERADMIN | PaginaAdmin (acceso completo)                                     |

---

## PENDIENTES / MEJORAS FUTURAS

1. **Implementación real de GPS:** Actualmente usa coordenadas fijas de ejemplo
2. **WebSocket real:** Conexión con servidor WebSocket externo
3. **Subida de imágenes:** Implementar con servicio de almacenamiento (S3, Cloudinary)
4. **Notificaciones push:** Integrar con servicio de notificaciones móviles
5. **Mapa en tiempo real:** Mostrar mapa con ubicación del motorizado
6. **Recuperación de contraseña:** Implementar envío de emails
7. **Exportar reportes:** PDF/Excel de finanzas
8. **Dashboard móvil:** Optimizar para dispositivos móviles

---

## CARACTERÍSTICAS TÉCNICAS

- **Arquitectura:** Hexagonal (Clean Architecture)
- **Patrón de estado:** BLoC
- **Base de datos:** SQLAlchemy con SQLite
- **UI:** Flet 0.80.3
- **Autenticación:** JWT + bcrypt
- **Decoradores:** Control de acceso por roles y permisos
- **Constantes:** Modularizadas en 7 archivos
- **Código:** 100% español, sin comentarios, DRY

---

## TESTING

Para probar el sistema completo:

1. Ejecutar migración: `python migrar_nuevas_tablas.py`
2. Crear usuarios de prueba con diferentes roles
3. Iniciar aplicación: `python main.py`
4. Login con cada rol y probar funcionalidades

**Usuarios sugeridos:**

- cliente@test.com (CLIENTE)
- motorizado@test.com (MOTORIZADO)
- cocinero@test.com (COCINERO)
- atencion@test.com (ATENCION)
- limpieza@test.com (LIMPIEZA)
- admin@test.com (ADMIN)
- super@test.com (SUPERADMIN)

---

## SOPORTE

Para dudas o issues, revisar:

- Logs en consola
- `app_logs.txt`
- Código fuente documentado (nombres descriptivos en español)
