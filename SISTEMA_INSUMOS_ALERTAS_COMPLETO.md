# 🎉 SISTEMA COMPLETO DE INSUMOS CON ALERTAS - IMPLEMENTACIÓN FINAL

## 📋 RESUMEN EJECUTIVO

Se ha implementado un **sistema integral de gestión de insumos** que incluye:

✅ **Compras Programadas** - Fecha y frecuencia de compra con recordatorios
✅ **Consumo Automático** - Deducción automática cuando se vende un producto
✅ **Conversiones de Unidades** - Local (15 unidades, 26 sinónimos, sin API externa)
✅ **Alertas de Stock Bajo** - Notificaciones automáticas a ADMIN/SUPERADMIN
✅ **Control de Acceso** - Solo ADMIN y SUPERADMIN ven alertas por defecto

---

## 🏗️ ARQUITECTURA DEL SISTEMA

### 1. **BASE DE DATOS** (ConfiguracionBD.py)

#### Modelos Actualizados:

**MODELO_INSUMO** (22 columnas)
```python
ID, NOMBRE, DESCRIPCION, UNIDAD, PRECIO_UNITARIO, STOCK_ACTUAL,
STOCK_MINIMO, PROVEEDOR, FECHA_PROXIMA_COMPRA,        # ← NUEVO
RECORDATORIO_ACTIVO, FRECUENCIA_COMPRA,               # ← NUEVO
ACTIVO, FECHA_CREACION, ...
```

**MODELO_ALERTA_INSUMO** (Tabla nueva)
```python
ID, INSUMO_ID, TIPO (stock_bajo), MENSAJE, LEIDA, RESUELTA,
FECHA_CREACION, FECHA_RESOLUCION
```

**MODELO_FORMULA** (Relación producto-insumo)
```python
ID, PRODUCTO_ID, INSUMO_ID, CANTIDAD, UNIDAD, NOTAS, ACTIVA, FECHA_CREACION
```

**MODELO_MOVIMIENTO_INSUMO** (Auditoría)
```python
ID, INSUMO_ID, TIPO (ENTRADA|SALIDA|AJUSTE|PRODUCCION), CANTIDAD,
STOCK_ANTERIOR, STOCK_NUEVO, OBSERVACION, USUARIO_ID, FECHA
```

---

### 2. **CONVERSIONES DE UNIDADES** (`core/utilidades/ConversionesUnidades.py`)

**Sistema Local Completo** (244 líneas)

```python
# Categorías soportadas:
CONVERSIONES = {
    "peso": {
        "gr": 1, "kg": 1000, "lb": 453.592, "arroba": 11339.8, "oz": 28.3495
    },
    "volumen": {
        "ml": 1, "litro": 1000, "gallon": 3785.41, "taza": 236.588, "onza_fl": 29.5735
    },
    "longitud": {
        "cm": 1, "m": 100, "km": 100000, "in": 2.54, "ft": 30.48
    }
}

# Funciones disponibles:
- convertir(cantidad, de_unidad, a_unidad)      # Bidireccional automático
- normalizar_unidad(unidad)                      # Maneja sinónimos
- es_unidad_peso/volumen/longitud()             # Validación
- obtener_unidades_compatibles(unidad)          # Lista convertibles
```

**Ejemplos:**
```python
convertir(1, "kg", "gr")           # → 1000
convertir(1000, "gr", "kg")        # → 1
convertir(5, "litro", "ml")        # → 5000
normalizar_unidad("kilogramos")    # → "kg"
normalizar_unidad("litros")        # → "litro"
```

---

### 3. **CONSUMO AUTOMÁTICO** (`features/insumos/consumo_automatico.py`)

**Función Principal: `DEDUCIR_INSUMOS_POR_VENTA(producto_id, cantidad=1)`**

Proceso automatizado:
```
1. Obtiene fórmula del producto vendido
2. Para cada insumo en la fórmula:
   - Calcula: cantidad_total = cantidad_insumo × cantidad_productos_vendidos
   - Convierte unidades si es necesario
   - Deduce del STOCK_ACTUAL
   - Crea MODELO_MOVIMIENTO_INSUMO de tipo PRODUCCION
   - Genera alerta si stock < STOCK_MINIMO

Ejemplo:
- Se vende hamburguesa (cantidad=1)
- Fórmula: 30gr carne + 10gr queso
- Se deduce: 30gr de carne, 10gr de queso
- Si quedó < stock_minimo → crea alerta automáticamente
```

**Funciones Auxiliares:**
```python
VERIFICAR_STOCK_INSUMO(insumo_id)           # Estado actual del stock
OBTENER_INSUMOS_STOCK_BAJO()                # Todos los críticos
```

---

### 4. **SISTEMA DE ALERTAS** (`features/admin/api/rutas_alertas.py`)

**Tabla de Alertas: ALERTAS_INSUMO**
- Se crean automáticamente cuando stock baja del mínimo
- Solo ADMIN y SUPERADMIN las ven
- Pueden marcar como leídas/resueltas
- Histórico de 30 días mantenido

#### APIs REST Disponibles:

**GET `/api/alertas/`** - Obtener todas las alertas pendientes
```json
{
  "exito": true,
  "total": 3,
  "alertas": [
    {
      "ID": 1,
      "INSUMO_ID": 5,
      "INSUMO_NOMBRE": "Carne de Res",
      "TIPO": "stock_bajo",
      "MENSAJE": "Stock bajo: Carne de Res. Stock actual: 450, Mínimo: 500",
      "LEIDA": false,
      "FECHA_CREACION": "2024-01-15T10:30:00"
    }
  ]
}
```

**GET `/api/alertas/<id>`** - Obtener detalles de una alerta
```json
{
  "exito": true,
  "alerta": {
    "ID": 1,
    "INSUMO": {
      "ID": 5,
      "NOMBRE": "Carne de Res",
      "STOCK_ACTUAL": 450,
      "STOCK_MINIMO": 500,
      "UNIDAD": "gr"
    },
    "TIPO": "stock_bajo",
    "MENSAJE": "...",
    "LEIDA": false,
    "RESUELTA": false
  }
}
```

**PUT `/api/alertas/<id>/leer`** - Marcar como leída
**PUT `/api/alertas/<id>/resolver`** - Resolver la alerta (cuando se compre)
**GET `/api/alertas/estadisticas`** - Resumen de alertas
**DELETE `/api/alertas/limpiar-antiguas`** - Limpiar alertas de >30 días (SUPERADMIN)

---

## 🔄 FLUJO COMPLETO DE OPERACIÓN

### Escenario: Venta de Hamburguesas

```
1. DEFINIR FÓRMULA (Una sola vez)
   └─ Hamburguesa = 30gr Carne + 10gr Queso + 5gr Pan rallado

2. REGISTRAR INSUMOS
   ├─ Carne: Stock 1000gr, Mínimo 500gr
   ├─ Queso: Stock 300gr, Mínimo 200gr  
   └─ Pan: Stock 200gr, Mínimo 100gr

3. VENTA: Se venden 10 hamburguesas
   └─ Sistema automáticamente:
      ├─ Deduce: 300gr de Carne (1000-300=700)
      ├─ Deduce: 100gr de Queso (300-100=200) ← Stock crítico!
      ├─ Deduce: 50gr de Pan (200-50=150)
      ├─ Crea MOVIMIENTOS_INSUMO (3 registros)
      └─ GENERA ALERTA: "Queso stock bajo (200 < 200)"

4. ALERTA EN DASHBOARD
   ├─ ADMIN ve alerta: "Queso - Stock bajo (200/200)"
   ├─ Puede hacer clic → Ver detalles
   ├─ Marca como leída
   ├─ Compra el insumo
   └─ Marca como "Resuelta"

5. AUDITORÍA COMPLETA
   └─ Historial de movimientos registrado:
      • 10x venta de hambur guesa
      • Carne: 1000→700gr (PRODUCCION)
      • Queso: 300→200gr (PRODUCCION)
      • Pan: 200→150gr (PRODUCCION)
```

---

## 📁 ARCHIVOS CREADOS/MODIFICADOS

### Nuevos Archivos:

| Archivo | Líneas | Descripción |
|---------|--------|-------------|
| `core/utilidades/ConversionesUnidades.py` | 244 | Sistema local de conversiones |
| `features/insumos/consumo_automatico.py` | 285 | Lógica de consumo automático |
| `features/admin/api/rutas_alertas.py` | 305 | APIs REST para alertas |

### Archivos Modificados:

| Archivo | Cambios |
|---------|---------|
| `core/base_datos/ConfiguracionBD.py` | +3 campos a MODELO_INSUMO, +1 modelo MODELO_ALERTA_INSUMO |
| `features/admin/api/__init__.py` | +alertas_bp al export |

---

## 🚀 CÓMO USAR EL SISTEMA

### 1. **Configurar Insumo Nuevo**
```python
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_INSUMO
from datetime import datetime, timedelta

with OBTENER_SESION() as session:
    insumo = MODELO_INSUMO(
        NOMBRE="Carne de Res",
        DESCRIPCION="Carne fresca para hamburguesas",
        UNIDAD="gr",
        PRECIO_UNITARIO=2500,  # En centavos
        STOCK_ACTUAL=1000,
        STOCK_MINIMO=500,
        PROVEEDOR="Carnicería Central",
        FRECUENCIA_COMPRA="semanal",              # ← NUEVO
        FECHA_PROXIMA_COMPRA=datetime.utcnow() + timedelta(days=7),  # ← NUEVO
        RECORDATORIO_ACTIVO=True,                 # ← NUEVO
        ACTIVO=True
    )
    session.add(insumo)
    session.commit()
```

### 2. **Crear Fórmula de Producto**
```python
from core.base_datos.ConfiguracionBD import MODELO_FORMULA

formula = MODELO_FORMULA(
    PRODUCTO_ID=1,      # Hamburguesa
    INSUMO_ID=5,        # Carne
    CANTIDAD=30,        # 30 gramos
    UNIDAD="gr",
    ACTIVA=True
)
session.add(formula)
session.commit()
```

### 3. **Procesar Venta (Automático)**
```python
from features.insumos.consumo_automatico import DEDUCIR_INSUMOS_POR_VENTA

# Cuando se vende un producto:
resultado = DEDUCIR_INSUMOS_POR_VENTA(
    producto_id=1,      # Hamburguesa
    cantidad_productos=5 # Se venden 5
)

# Resultado:
{
    "exito": True,
    "insumos_deducidos": [
        {
            "insumo_nombre": "Carne",
            "estado": "OK",
            "stock_anterior": 1000,
            "cantidad_deducida": 150,
            "stock_nuevo": 850,
            "unidad": "gr"
        }
    ],
    "alertas_generadas": [
        {
            "insumo_nombre": "Queso",
            "stock_actual": 190,
            "stock_minimo": 200
        }
    ]
}
```

### 4. **Verificar Alertas**
```python
import requests

# ADMIN accede a alertas:
response = requests.get(
    'http://localhost:5000/api/alertas/',
    headers={'Authorization': 'Bearer <TOKEN>'}
)

# Obtener detalles:
response = requests.get(
    'http://localhost:5000/api/alertas/1',
    headers={'Authorization': 'Bearer <TOKEN>'}
)

# Marcar como leída:
response = requests.put(
    'http://localhost:5000/api/alertas/1/leer',
    headers={'Authorization': 'Bearer <TOKEN>'}
)

# Resolver (cuando se compre):
response = requests.put(
    'http://localhost:5000/api/alertas/1/resolver',
    json={'notas': 'Comprado 5kg de carne'},
    headers={'Authorization': 'Bearer <TOKEN>'}
)
```

### 5. **Conversiones de Unidades**
```python
from core.utilidades.ConversionesUnidades import convertir, normalizar_unidad

# Convertir 2.5 kg a gramos
resultado = convertir(2.5, "kg", "gr")  # → 2500

# Convertir 5 libras a kg
resultado = convertir(5, "lb", "kg")    # → 2.268

# Normalizar entrada del usuario
unidad_normalizada = normalizar_unidad("kilogramos")  # → "kg"
unidad_normalizada = normalizar_unidad("litros")      # → "litro"

# Obtener unidades compatibles
compatibles = obtener_unidades_compatibles("gr")  
# → ["gr", "kg", "lb", "arroba", "oz"]
```

---

## 📊 DIAGRAMA DE FLUJOS

```
┌─────────────────────────────────────────────────────────────┐
│                    VENTA DE PRODUCTO                        │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ DEDUCIR_INSUMOS()    │
                    └──────────────┬───────┘
                                   │
                   ┌───────────────┼───────────────┐
                   │               │               │
                   ▼               ▼               ▼
            ┌────────────┐  ┌────────────┐  ┌────────────┐
            │ Obtener    │  │ Obtener    │  │ Obtener    │
            │ Fórmula    │  │ Insumos    │  │ Stock      │
            └────────────┘  └────────────┘  └────────────┘
                   │               │               │
                   └───────────────┼───────────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │ Para cada insumo:    │
                        │ - Calcular cantidad  │
                        │ - Convertir unidades │
                        └──────────────┬───────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
            ┌─────────────┐    ┌──────────────┐   ┌──────────────┐
            │ Actualizar  │    │ Crear        │   │ Verificar    │
            │ STOCK       │    │ MOVIMIENTO   │   │ Stock bajo   │
            └─────────────┘    └──────────────┘   └──────┬───────┘
                                                          │
                                          ┌───────────────┘
                                          │
                                    ¿Stock < Mínimo?
                                          │
                            ┌─────────────┴─────────────┐
                            │                           │
                           SÍ                           NO
                            │                           │
                            ▼                           ▼
                    ┌────────────────┐         ┌──────────────┐
                    │ CREAR ALERTA   │         │ Continuar    │
                    │ STOCK_BAJO     │         └──────────────┘
                    └────────────────┘
                            │
                            ▼
                    ┌──────────────────────┐
                    │ Notificación para     │
                    │ ADMIN/SUPERADMIN      │
                    └──────────────────────┘
```

---

## 🔐 CONTROL DE ACCESO

### Permisos por Rol:

| Operación | ADMIN | SUPERADMIN | USUARIO |
|-----------|-------|-----------|---------|
| Ver alertas | ✅ | ✅ | ❌ |
| Marcar como leída | ✅ | ✅ | ❌ |
| Resolver alerta | ✅ | ✅ | ❌ |
| Ver estadísticas | ✅ | ✅ | ❌ |
| Limpiar alertas antiguas | ❌ | ✅ | ❌ |
| Ver movimientos | ✅ | ✅ | ❌ |
| Deducir insumos (automático) | ✅* | ✅* | ❌ |

*Se ejecuta automáticamente cuando un usuario vende un producto

---

## 🧪 EJEMPLO DE PRUEBA COMPLETA

```python
"""Prueba del sistema completo de insumos"""

from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION, MODELO_INSUMO, MODELO_FORMULA, MODELO_PRODUCTO
)
from features.insumos.consumo_automatico import DEDUCIR_INSUMOS_POR_VENTA
from core.utilidades.ConversionesUnidades import convertir

# 1. Crear insumo
with OBTENER_SESION() as session:
    carne = MODELO_INSUMO(
        NOMBRE="Carne de Res",
        UNIDAD="gr",
        STOCK_ACTUAL=2000,
        STOCK_MINIMO=500,
        ACTIVO=True
    )
    session.add(carne)
    session.commit()
    carne_id = carne.ID

# 2. Crear fórmula (hamburguesa = 50gr de carne)
with OBTENER_SESION() as session:
    formula = MODELO_FORMULA(
        PRODUCTO_ID=1,
        INSUMO_ID=carne_id,
        CANTIDAD=50,
        UNIDAD="gr",
        ACTIVA=True
    )
    session.add(formula)
    session.commit()

# 3. Simular venta de 30 hamburguesas
resultado = DEDUCIR_INSUMOS_POR_VENTA(1, cantidad_productos=30)

# Verificar:
# - Carne: 2000 - (50*30) = 500 ← Stock en mínimo exacto
# - Si fuera una venta más, se dispararía alerta

print(f"✅ Stock deducido: {resultado['insumos_deducidos'][0]['stock_nuevo']}gr")
print(f"✅ Alertas generadas: {len(resultado['alertas_generadas'])}")

# 4. Probar conversión de unidades
cantidad_kg = convertir(500, "gr", "kg")  # → 0.5
print(f"✅ Conversión: 500gr = {cantidad_kg}kg")
```

---

## 📈 CASOS DE USO

### Caso 1: Compra Programada con Recordatorio
```
Lunes: Se configura Carne
  - FECHA_PROXIMA_COMPRA = Miércoles
  - RECORDATORIO_ACTIVO = True
  - FRECUENCIA_COMPRA = semanal
  
Miércoles: Sistema envía recordatorio
  - "Recordatorio: Tiempo de comprar Carne"
  
Admin compra → Actualiza STOCK_ACTUAL + FECHA_PROXIMA_COMPRA
```

### Caso 2: Alerta de Stock Bajo
```
Martes 10:30: Se venden 15 hamburguesas
  - Carne baja de 1000gr a 450gr
  - STOCK_MINIMO = 500gr
  - ¡Se dispara alerta!
  
Sistema automáticamente:
  - Crea MODELO_ALERTA_INSUMO
  - Notifica a ADMIN y SUPERADMIN
  - ADMIN resuelve la alerta cuando compra más carne
```

### Caso 3: Conversión Automática
```
Usuario quiere agregar 2 libras de queso
  
Sistema:
  - Normaliza: "libras" → "lb"
  - Convierte: 2 lb → 907.2 gr
  - Agrega 907.2 gr al stock
  - Registra movimiento de tipo ENTRADA
```

---

## 📝 CHECKLIST DE IMPLEMENTACIÓN

✅ **Base de Datos:**
- [x] MODELO_INSUMO actualizado (+3 campos)
- [x] MODELO_ALERTA_INSUMO creado
- [x] Tabla ALERTAS_INSUMO creada en BD
- [x] Migraciones ejecutadas correctamente

✅ **Lógica de Negocio:**
- [x] ConversionesUnidades.py completo (15 unidades, 26 sinónimos)
- [x] DEDUCIR_INSUMOS_POR_VENTA() funcional
- [x] CREAR_ALERTA_STOCK_BAJO() integrado
- [x] Auditoría de movimientos (MODELO_MOVIMIENTO_INSUMO)

✅ **APIs REST:**
- [x] GET /api/alertas/ (obtener todas)
- [x] GET /api/alertas/<id> (detalles)
- [x] PUT /api/alertas/<id>/leer (marcar leída)
- [x] PUT /api/alertas/<id>/resolver (resolver)
- [x] GET /api/alertas/estadisticas (resumen)
- [x] DELETE /api/alertas/limpiar-antiguas (limpieza)

✅ **Control de Acceso:**
- [x] Validación de permisos en decoradores
- [x] Solo ADMIN/SUPERADMIN ven alertas
- [x] SUPERADMIN puede limpiar alertas antiguas

⚠️ **Pendiente - UI (Flet):**
- [ ] DateTime picker en InsumosPageModerna para FECHA_PROXIMA_COMPRA
- [ ] Checkbox para RECORDATORIO_ACTIVO
- [ ] Dropdown para FRECUENCIA_COMPRA
- [ ] Widget de alertas en Dashboard
- [ ] Indicador visual de stock bajo (rojo)

---

## 🔗 INTEGRACIÓN CON FLUJO EXISTENTE

### Dónde se llama DEDUCIR_INSUMOS_POR_VENTA():

**Opción 1: En la venta de productos**
```python
# En PedidosPage o donde se procesa una venta:
from features.insumos.consumo_automatico import DEDUCIR_INSUMOS_POR_VENTA

# Al procesar compra del cliente:
for item_pedido in pedido.items:
    DEDUCIR_INSUMOS_POR_VENTA(
        producto_id=item_pedido.producto_id,
        cantidad_productos=item_pedido.cantidad
    )
```

**Opción 2: En la confirmación de pago**
```python
# En módulo de Finanzas:
def confirmar_venta(venta_id):
    venta = obtener_venta(venta_id)
    
    # Deducir insumos
    for producto in venta.productos:
        DEDUCIR_INSUMOS_POR_VENTA(
            producto_id=producto.id,
            cantidad_productos=producto.cantidad
        )
    
    # Continuar con flujo de venta...
```

---

## 🛠️ MANTENIMIENTO

### Limpieza de Alertas Antiguas
```bash
# Ejecutar periodicamente (ej: cron job)
curl -X DELETE http://localhost:5000/api/alertas/limpiar-antiguas \
  -H "Authorization: Bearer <SUPERADMIN_TOKEN>"
```

### Verificar Stock Crítico
```bash
curl http://localhost:5000/api/alertas/ \
  -H "Authorization: Bearer <ADMIN_TOKEN>"
```

---

## 📞 SOPORTE Y DEBUGGING

### Logs disponibles:
```python
import logging
logger = logging.getLogger(__name__)

# Ver detalles de deducción:
logger.info(f"Deducido {cantidad}gr de {insumo.NOMBRE}")

# Ver errores de conversión:
logger.error(f"Error en conversión de unidades: {e}")

# Ver alertas generadas:
logger.info(f"Alerta creada para insumo {insumo.NOMBRE}")
```

### Verificar estado del sistema:
```python
from features.insumos.consumo_automatico import OBTENER_INSUMOS_STOCK_BAJO

# Obtener todos los insumos críticos:
criticos = OBTENER_INSUMOS_STOCK_BAJO()
for insumo in criticos['insumos']:
    print(f"{insumo['nombre']}: {insumo['stock_actual']}/{insumo['stock_minimo']}")
```

---

## 📚 REFERENCIAS Y DOCUMENTACIÓN

- [ConversionesUnidades.py](core/utilidades/ConversionesUnidades.py) - Sistema de conversiones
- [consumo_automatico.py](features/insumos/consumo_automatico.py) - Lógica de deducción
- [rutas_alertas.py](features/admin/api/rutas_alertas.py) - APIs REST
- [ConfiguracionBD.py](core/base_datos/ConfiguracionBD.py) - Modelos de datos

---

## ✨ CARACTERÍSTICAS DESTACADAS

🎯 **Sin Dependencias Externas**
- Conversiones completamente locales
- No requiere llamadas a APIs externas
- Funciona offline

🔄 **Bidireccional**
- 1 kg = 1000 gr
- 1000 gr = 1 kg
- Sistema automático de conversión

🛡️ **Auditoría Completa**
- Cada movimiento registrado
- Histórico de stock
- Trazabilidad de cambios

⚡ **Automático**
- Alertas se crean sin intervención
- Recordatorios configurables
- Deducción transparente

🔐 **Control Granular**
- Permisos por rol
- Historial de cambios
- Resolución de alertas

