# 🔄 FLUJO COMPLETO DEL SISTEMA - CONYCHIPS

## 📊 Datos Agregados al Sistema

### Resumen Actual:
- ✅ **30 Reseñas** (calificaciones 1-5 estrellas)
- ✅ **24 Productos** (hamburguesas, bebidas, combos)
- ✅ **5 Proveedores** (carnes, verduras, panadería, lácteos, bebidas)
- ✅ **68 Pedidos/Ventas** (últimos 7 días)
- ✅ **8 Usuarios** (diferentes roles)
- ✅ **5 Sucursales**

---

## 🔄 FLUJO PRINCIPAL DEL SISTEMA

### 1. **CLIENTE** (Usuario Final)

#### A. Hacer un Pedido
```
1. Login como CLIENTE
   └─> Dashboard Cliente
       
2. Tab "Hacer Pedido"
   └─> Ver productos disponibles (24 productos)
       └─> Click en "+" para agregar al carrito
           └─> Ver carrito
               └─> Confirmar pedido
                   ├─> Seleccionar tipo: Delivery/Tienda/Recoger
                   ├─> Confirmar dirección
                   └─> Crear pedido (ESTADO: pendiente)
```

#### B. Subir Voucher de Pago
```
1. Tab "Pedidos Activos"
   └─> Ver pedido con ESTADO = "pendiente"
       └─> Click "Subir Voucher"
           └─> Seleccionar imagen del voucher
               └─> Enviar
                   └─> ESTADO cambia a "pendiente_validacion"
```

#### C. Chat con Atención
```
1. Click en botón flotante 💬 (esquina inferior derecha)
   └─> Ver lista de pedidos con chat
       └─> Click en pedido
           └─> Abrir chat
               ├─> Escribir mensaje
               ├─> Ver estado: ⏳ enviando → ✓ enviado → ✓✓ entregado → leído
               └─> Ver "escribiendo..." cuando admin responde
```

#### D. Dar Reseña
```
1. Pedido ESTADO = "entregado"
   └─> Click "Calificar"
       ├─> Calificación comida: 1-5 ⭐
       ├─> Calificación servicio: 1-5 ⭐
       ├─> Calificación entrega: 1-5 ⭐
       └─> Comentario opcional
           └─> Guardar → Reseña registrada
```

---

### 2. **ATENCIÓN** (Personal de Servicio)

#### A. Validar Vouchers
```
1. Login como ATENCION
   └─> Dashboard Atención
       
2. Bottom Nav → "Vouchers"
   └─> Ver pedidos con vouchers pendientes
       └─> Click en pedido
           ├─> Ver imagen del voucher
           ├─> Verificar monto
           └─> Acciones:
               ├─> ✅ Aprobar → ESTADO = "confirmado"
               └─> ❌ Rechazar → ESTADO = "pendiente" (notificar cliente)
```

#### B. Gestionar Pedidos en Tienda
```
1. Click "Registrar Pedido en Tienda"
   └─> Formulario rápido:
       ├─> Seleccionar productos
       ├─> Cantidad
       ├─> Cliente (opcional)
       └─> Confirmar
           └─> Pedido creado → Enviar a cocina
               └─> ESTADO = "en_preparacion"
```

#### C. Responder Chat
```
1. Click botón flotante 💬
   └─> Ver conversaciones con badge 🔴 (no leídos)
       └─> Click en conversación
           └─> Leer mensajes del cliente
               └─> Responder
                   └─> Cliente recibe notificación
```

#### D. Manejar Caja
```
1. Tab "Caja"
   ├─> Ver saldo actual
   ├─> Abrir Caja (inicio de turno)
   │   └─> Registrar monto inicial
   ├─> Registrar movimientos:
   │   ├─> Ingreso (ventas)
   │   └─> Egreso (gastos)
   └─> Cerrar Caja (fin de turno)
       └─> Arqueo de caja
           └─> Comparar físico vs. sistema
```

---

### 3. **COCINA** (Preparación)

```
1. Login como COCINA
   └─> Dashboard Cocina
       
2. Ver pedidos ESTADO = "en_preparacion"
   └─> Lista ordenada por antigüedad
       └─> Click en pedido
           ├─> Ver detalle de productos
           ├─> Ver observaciones del cliente
           └─> Marcar como "listo"
               └─> ESTADO = "listo"
                   └─> Notificación a ATENCION
```

---

### 4. **MOTORIZADO** (Delivery)

```
1. Login como MOTORIZADO
   └─> Dashboard Motorizado
       
2. Ver pedidos asignados ESTADO = "listo" (tipo: delivery)
   └─> Click "Tomar pedido"
       └─> ESTADO = "en_camino"
           ├─> Ver dirección del cliente
           ├─> Chat con cliente
           └─> Al entregar:
               └─> Click "Marcar como entregado"
                   └─> ESTADO = "entregado"
                       └─> Cliente puede calificar
```

---

### 5. **ADMIN** (Gestión Operativa)

#### A. Dashboard Principal
```
1. Login como ADMIN
   └─> Dashboard Admin
       ├─> Cards de estadísticas:
       │   ├─> Total usuarios
       │   ├─> Pedidos hoy
       │   ├─> Ganancias hoy
       │   └─> Productos disponibles
       ├─> Gráficos:
       │   ├─> Usuarios por rol
       │   ├─> Pedidos por sucursal
       │   ├─> Ventas última semana
       │   └─> Estado del inventario
       └─> Botones de gestión (14 módulos)
```

#### B. Gestión de Productos
```
Bottom Nav → Productos
├─> Ver lista de productos (24 productos)
├─> Agregar nuevo producto:
│   ├─> Nombre
│   ├─> Descripción
│   ├─> Precio
│   ├─> Categoría
│   └─> Disponibilidad
├─> Editar producto existente
└─> Desactivar/Activar producto
```

#### C. Ver Reseñas
```
Bottom Nav → Más → Reseñas
├─> Ver 30 reseñas
├─> Filtrar por calificación:
│   ├─> Todas
│   ├─> ⭐⭐⭐⭐⭐ (9 reseñas)
│   ├─> ⭐⭐⭐⭐ (11 reseñas)
│   ├─> ⭐⭐⭐ (4 reseñas)
│   ├─> ⭐⭐ (5 reseñas)
│   └─> ⭐ (1 reseña)
└─> Ver:
    ├─> Usuario que calificó
    ├─> Fecha
    ├─> Estrellas
    └─> Comentario
```

#### D. Gestión de Proveedores
```
Módulo Proveedores
├─> Ver proveedores (5):
│   ├─> Distribuidora San José (Carnes)
│   ├─> Verduras Frescas del Valle
│   ├─> Panadería El Trigal
│   ├─> Lácteos Premium
│   └─> Bebidas y Refrescos SAC
├─> Agregar proveedor:
│   ├─> Nombre
│   ├─> Contacto
│   ├─> Teléfono
│   ├─> Email
│   └─> Dirección
└─> Editar/Desactivar proveedor
```

#### E. Finanzas y Reportes
```
Bottom Nav → Finanzas
├─> Resumen financiero:
│   ├─> Ventas del día
│   ├─> Ventas del mes
│   └─> Proyección
├─> Gráficos de ventas:
│   ├─> Por día
│   ├─> Por semana
│   └─> Por mes
├─> Reporte de pedidos (68 pedidos):
│   ├─> Estados:
│   │   ├─> Pendiente: 19
│   │   ├─> Confirmado: 7
│   │   ├─> En preparación: 9
│   │   ├─> Listo: 3
│   │   ├─> En camino: 6
│   │   └─> Entregado: 4
│   └─> Filtros:
│       ├─> Por fecha
│       ├─> Por estado
│       └─> Por sucursal
└─> Exportar reportes (PDF/Excel)
```

#### F. Chat Flotante (Todas las páginas)
```
Click botón 💬 (esquina inferior derecha)
└─> Panel de conversaciones
    ├─> Ver todos los pedidos con mensajes
    ├─> Badge 🔴 con mensajes no leídos
    └─> Click en conversación
        └─> Chat completo con cliente
            ├─> Historial de mensajes
            ├─> Indicador "escribiendo..."
            └─> Estados de mensaje
```

---

### 6. **SUPERADMIN** (Administración Total)

```
Login como SUPERADMIN
└─> Todo lo de ADMIN +
    ├─> Gestionar Roles
    │   ├─> Crear nuevos roles
    │   ├─> Asignar permisos
    │   └─> Editar roles existentes
    ├─> Gestionar Sucursales (5 sucursales)
    │   ├─> Crear sucursal
    │   ├─> Configurar horarios
    │   ├─> Asignar personal
    │   └─> Ver estadísticas por sucursal
    └─> Auditoría
        ├─> Ver logs del sistema
        ├─> Acciones de usuarios
        ├─> Cambios en datos
        └─> Exportar auditoría
```

---

## 🔔 NOTIFICACIONES Y EVENTOS EN TIEMPO REAL

### WebSocket Broadcast
```
Evento                    → Notifica a
─────────────────────────────────────────
Nuevo pedido              → Admin, Atención
Voucher subido            → Admin, Atención
Voucher aprobado          → Cliente
Pedido en preparación     → Cliente, Cocina
Pedido listo              → Cliente, Motorizado, Atención
Pedido en camino          → Cliente
Pedido entregado          → Cliente, Admin
Nuevo mensaje chat        → Cliente ↔ Admin/Atención
Usuario escribiendo       → Participantes del chat
```

### Sonidos de Notificación
```
GestorSonidos
├─> Nuevo pedido          → 🔔 beep.mp3
├─> Mensaje nuevo chat    → 🔔 notification.mp3
├─> Pedido listo          → 🔔 success.mp3
└─> Error/Rechazo         → 🔔 error.mp3
```

---

## 📍 NAVEGACIÓN DEL SISTEMA

### BottomNavigation (Admin/SuperAdmin)
```
┌──────────────────────────────────┐
│ [🏠] Dashboard                   │
│ [👥] Usuarios                    │
│ [📦] Productos                   │
│ [💰] Finanzas                    │
│ [⚙️] Más                         │
│     ├─> Vouchers                 │
│     ├─> Proveedores              │
│     ├─> Reseñas                  │
│     ├─> Insumos                  │
│     ├─> Horarios                 │
│     └─> Configuración            │
└──────────────────────────────────┘
```

### NavbarGlobal (Superior)
```
┌──────────────────────────────────┐
│ [≡] Título Vista    [🏪↓] [@]   │
│     Filtro Sucursal   Usuario    │
└──────────────────────────────────┘
```

### Chat Flotante (Siempre visible)
```
                            ╔═══╗
                            ║💬 ║ ← Click aquí
                            ║[3]║    Badge con
                            ╚═══╝    no leídos
```

---

## 🔒 PERMISOS POR ROL

```
Función                CLIENTE  ATENCION  COCINA  MOTORIZADO  ADMIN  SUPERADMIN
──────────────────────────────────────────────────────────────────────────────
Hacer pedido             ✅       ✅       ❌        ❌        ✅       ✅
Subir voucher            ✅       ❌       ❌        ❌        ❌       ❌
Validar voucher          ❌       ✅       ❌        ❌        ✅       ✅
Ver pedidos propios      ✅       ❌       ❌        ❌        ❌       ❌
Ver todos pedidos        ❌       ✅       ✅        ✅        ✅       ✅
Chat con admin           ✅       ✅       ❌        ❌        ✅       ✅
Gestionar productos      ❌       ❌       ❌        ❌        ✅       ✅
Ver reseñas              ❌       ❌       ❌        ❌        ✅       ✅
Gestionar proveedores    ❌       ❌       ❌        ❌        ✅       ✅
Ver finanzas             ❌       ✅       ❌        ❌        ✅       ✅
Gestionar roles          ❌       ❌       ❌        ❌        ❌       ✅
Gestionar sucursales     ❌       ❌       ❌        ❌        ❌       ✅
Ver auditoría            ❌       ❌       ❌        ❌        ❌       ✅
```

---

## 🎯 FLUJO TÍPICO COMPLETO

### Ejemplo: Pedido de Hamburguesa con Delivery

```
1. CLIENTE hace pedido
   └─> 2 Hamburguesas BBQ + 1 Papas + 1 Gaseosa
       └─> Total: S/ 55.00
           └─> Tipo: Delivery
               └─> ESTADO: "pendiente"

2. CLIENTE sube voucher
   └─> Foto del pago
       └─> ESTADO: "pendiente_validacion"
           └─> 🔔 Notificación a ATENCIÓN

3. ATENCIÓN valida voucher
   └─> Verifica monto
       └─> Aprueba ✅
           └─> ESTADO: "confirmado"
               └─> 🔔 Notificación a COCINA
               └─> 🔔 Notificación a CLIENTE

4. COCINA prepara pedido
   └─> Ve productos en pantalla
       └─> Prepara hamburguesas
           └─> Marca como "listo"
               └─> ESTADO: "listo"
                   └─> 🔔 Notificación a MOTORIZADO
                   └─> 🔔 Notificación a CLIENTE

5. MOTORIZADO toma pedido
   └─> Ve dirección
       └─> Marca "en camino"
           └─> ESTADO: "en_camino"
               └─> 🔔 Notificación a CLIENTE
               └─> Chat activo con cliente

6. MOTORIZADO entrega
   └─> Llega a domicilio
       └─> Marca "entregado"
           └─> ESTADO: "entregado"
               └─> 🔔 Notificación a CLIENTE

7. CLIENTE califica
   └─> Comida: ⭐⭐⭐⭐⭐
   └─> Servicio: ⭐⭐⭐⭐⭐
   └─> Entrega: ⭐⭐⭐⭐
   └─> Comentario: "Excelente, muy rápido"
       └─> Reseña guardada
           └─> Visible en módulo de reseñas para ADMIN
```

---

## 📈 REPORTES Y ANALÍTICAS

### Dashboard Admin
- Total usuarios registrados
- Pedidos del día en tiempo real
- Ganancias del día
- Productos más vendidos
- Calificación promedio (de reseñas)
- Pedidos por estado (gráfico de torta)
- Ventas última semana (gráfico de líneas)
- Inventario bajo stock (alertas)

### Módulo Finanzas
- Reporte diario/semanal/mensual
- Comparativa por sucursal
- Productos más rentables
- Análisis de costos vs ventas
- Proyecciones

---

**Sistema completamente funcional con:**
- ✅ 30 Reseñas de clientes
- ✅ 24 Productos variados
- ✅ 5 Proveedores activos
- ✅ 68 Pedidos/Ventas de ejemplo
- ✅ Chat en tiempo real con WebSockets
- ✅ Notificaciones sonoras
- ✅ Estados de mensaje (enviando/enviado/leído)
- ✅ Permisos por rol
- ✅ Navegación intuitiva
- ✅ Reportes y gráficos

🚀 **Sistema listo para producción!**
