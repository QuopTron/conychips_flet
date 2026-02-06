# ⚡ QUICK START - SISTEMA DE INSUMOS CON ALERTAS

## 🎯 5 PASOS PARA ACTIVAR EL SISTEMA

### Paso 1: Base de Datos (YA HECHO ✅)
```bash
# La tabla ALERTAS_INSUMO ya está creada
# La tabla INSUMOS tiene 3 campos nuevos:
# - FECHA_PROXIMA_COMPRA
# - RECORDATORIO_ACTIVO  
# - FRECUENCIA_COMPRA
```

### Paso 2: Crear Primer Insumo
```python
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_INSUMO
from datetime import datetime, timedelta

with OBTENER_SESION() as session:
    insumo = MODELO_INSUMO(
        NOMBRE="Carne de Res",
        DESCRIPCION="Para hamburguesas",
        UNIDAD="gr",
        PRECIO_UNITARIO=2500,
        STOCK_ACTUAL=1000,
        STOCK_MINIMO=500,
        PROVEEDOR="Carnicería Central",
        FRECUENCIA_COMPRA="semanal",
        FECHA_PROXIMA_COMPRA=datetime.utcnow() + timedelta(days=7),
        RECORDATORIO_ACTIVO=True,
        ACTIVO=True
    )
    session.add(insumo)
    session.commit()
    print(f"✅ Insumo creado: ID={insumo.ID}")
```

### Paso 3: Crear Fórmula (Relación Producto-Insumo)
```python
from core.base_datos.ConfiguracionBD import MODELO_FORMULA

with OBTENER_SESION() as session:
    # Para hamburguesa (PRODUCTO_ID=1) usa 30gr de carne (INSUMO_ID=1)
    formula = MODELO_FORMULA(
        PRODUCTO_ID=1,
        INSUMO_ID=1,
        CANTIDAD=30,
        UNIDAD="gr",
        ACTIVA=True
    )
    session.add(formula)
    session.commit()
    print("✅ Fórmula creada: Hamburguesa = 30gr Carne")
```

### Paso 4: Procesar Una Venta (Consume Automáticamente)
```python
from features.insumos.consumo_automatico import DEDUCIR_INSUMOS_POR_VENTA

# Se venden 5 hamburguesas
resultado = DEDUCIR_INSUMOS_POR_VENTA(
    producto_id=1,
    cantidad_productos=5
)

if resultado['exito']:
    print(f"✅ Insumos deducidos:")
    for insumo in resultado['insumos_deducidos']:
        print(f"  {insumo['insumo_nombre']}: {insumo['stock_anterior']} → {insumo['stock_nuevo']}")
    
    if resultado['alertas_generadas']:
        print(f"⚠️ Alertas generadas: {len(resultado['alertas_generadas'])}")
```

### Paso 5: Ver Alertas (ADMIN/SUPERADMIN)
```python
import requests

headers = {
    'Authorization': 'Bearer <TOKEN_ADMIN>',
    'Content-Type': 'application/json'
}

# Obtener todas las alertas
response = requests.get(
    'http://localhost:5000/api/alertas/',
    headers=headers
)

alertas = response.json()['alertas']
for alerta in alertas:
    print(f"⚠️ {alerta['INSUMO_NOMBRE']}: {alerta['MENSAJE']}")
    print(f"   ID: {alerta['ID']}")

# Marcar como leída
if alertas:
    alerta_id = alertas[0]['ID']
    requests.put(
        f'http://localhost:5000/api/alertas/{alerta_id}/leer',
        headers=headers
    )
    print(f"✅ Alerta {alerta_id} marcada como leída")
    
    # Resolver cuando se compre el insumo
    requests.put(
        f'http://localhost:5000/api/alertas/{alerta_id}/resolver',
        json={'notas': 'Comprado 2kg de carne'},
        headers=headers
    )
    print(f"✅ Alerta {alerta_id} resuelta")
```

---

## 🔄 CONVERSIONES DISPONIBLES

```python
from core.utilidades.ConversionesUnidades import convertir, normalizar_unidad

# PESO
convertir(1, "kg", "gr")      # 1000
convertir(1, "lb", "gr")      # 453.592
convertir(1, "arroba", "kg")  # 11.3398

# VOLUMEN
convertir(1, "litro", "ml")   # 1000
convertir(1, "gallon", "litro") # 3.78541
convertir(1, "taza", "ml")    # 236.588

# LONGITUD
convertir(1, "m", "cm")       # 100
convertir(1, "km", "m")       # 1000
convertir(1, "ft", "cm")      # 30.48

# MANEJO DE SINÓNIMOS
normalizar_unidad("kilogramos")   # "kg"
normalizar_unidad("litros")       # "litro"
normalizar_unidad("gramos")       # "gr"
```

---

## 📊 FLUJO OPERATIVO DIARIO

```
MAÑANA (Apertura de Negocio)
├─ ADMIN revisa alertas: GET /api/alertas/
├─ Si hay insumos bajos, compra
└─ Marca alertas como resueltas: PUT /api/alertas/<id>/resolver

DÍA (Ventas)
├─ Cada venta automáticamente:
│  ├─ Deduce insumos
│  ├─ Crea movimientos de auditoría
│  └─ Genera alertas si es necesario
└─ Sistema notifica ADMIN de alertas

NOCHE (Cierre)
├─ Revisar resumen: GET /api/alertas/estadisticas
├─ Verificar stock bajo: GET /api/alertas/?filtro=stock_bajo
└─ Programar compras para próximo día
```

---

## 🔍 VERIFICAR INSUMOS CON STOCK BAJO

```python
from features.insumos.consumo_automatico import OBTENER_INSUMOS_STOCK_BAJO

criticos = OBTENER_INSUMOS_STOCK_BAJO()

print(f"Total insumos críticos: {criticos['total']}")
for insumo in criticos['insumos']:
    diferencia = insumo['diferencia']
    simbolo = "🔴" if diferencia < 0 else "🟡"
    print(f"{simbolo} {insumo['nombre']}")
    print(f"  Stock: {insumo['stock_actual']} / Mínimo: {insumo['stock_minimo']}")
    print(f"  Diferencia: {diferencia} {insumo['unidad']}")
    if insumo['tiene_alerta']:
        print(f"  ⚠️ ALERTA ABIERTA (ID: {insumo['alerta_id']})")
```

---

## 🛠️ INTEGRACIÓN CON PEDIDOS

**En el módulo donde se procesa una venta:**

```python
from features.insumos.consumo_automatico import DEDUCIR_INSUMOS_POR_VENTA

def procesar_venta_completa(pedido):
    """Procesa una venta y deduce automáticamente insumos"""
    
    # ... lógica de venta existente ...
    
    # AL FINAL, deducir insumos:
    for item in pedido.items:
        resultado = DEDUCIR_INSUMOS_POR_VENTA(
            producto_id=item.producto_id,
            cantidad_productos=item.cantidad
        )
        
        if not resultado['exito']:
            # Manejar error de stock insuficiente
            logger.error(f"Error deduciendo insumos: {resultado['error']}")
            # Posiblemente cancelar venta o alertar al usuario
        else:
            logger.info(f"Insumos deducidos para {item.cantidad}x {item.producto.nombre}")
```

---

## 🚨 CASOS DE ERROR Y SOLUCIONES

| Error | Causa | Solución |
|-------|-------|----------|
| "Stock insuficiente" | No hay suficiente insumo | Comprar más insumo antes de vender |
| "Producto sin fórmula" | No se definió receta | Crear MODELO_FORMULA con relación producto-insumo |
| "Unidad no convertible" | Intenta convertir peso a volumen | Verificar que sean unidades compatibles |
| "Insumo no encontrado" | ID inválido | Verificar que el insumo existe en BD |

---

## 📈 MÉTRICAS Y REPORTES

```python
# Estadísticas de alertas
response = requests.get(
    'http://localhost:5000/api/alertas/estadisticas',
    headers={'Authorization': 'Bearer <TOKEN>'}
)

stats = response.json()['estadisticas']
print(f"Total alertas: {stats['total']}")
print(f"Pendientes: {stats['pendientes']}")
print(f"No leídas: {stats['no_leidas']}")
print(f"Resueltas: {stats['resueltas']}")

# Insumos críticos
criticos = OBTENER_INSUMOS_STOCK_BAJO()
print(f"Insumos en riesgo: {criticos['total']}")

# Movimientos recientes
movimientos = session.query(MODELO_MOVIMIENTO_INSUMO).limit(10).all()
for mov in movimientos:
    print(f"{mov.FECHA} - {mov.TIPO}: {mov.CANTIDAD} {mov.INSUMO.UNIDAD}")
```

---

## ⏰ RECORDATORIOS PROGRAMADOS

```python
# Estructura para recordatorios (puede implementarse con APScheduler)
from datetime import datetime, timedelta

def verificar_recordatorios():
    """Verifica si hay insumos con compra próxima"""
    
    with OBTENER_SESION() as session:
        ahora = datetime.utcnow()
        proximamente = ahora + timedelta(days=1)
        
        insumos_para_comprar = session.query(MODELO_INSUMO).filter(
            MODELO_INSUMO.RECORDATORIO_ACTIVO == True,
            MODELO_INSUMO.FECHA_PROXIMA_COMPRA.between(ahora, proximamente)
        ).all()
        
        for insumo in insumos_para_comprar:
            print(f"🔔 RECORDATORIO: Comprar {insumo.NOMBRE}")
            print(f"   Programado para: {insumo.FECHA_PROXIMA_COMPRA}")
            print(f"   Frecuencia: {insumo.FRECUENCIA_COMPRA}")
            
            # Enviar notificación a ADMIN
```

---

## 🧪 TEST RÁPIDO

```bash
# Terminal 1: Iniciar la app
python main.py

# Terminal 2: Ejecutar pruebas
python << 'EOF'
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_INSUMO
from core.utilidades.ConversionesUnidades import convertir
from features.insumos.consumo_automatico import DEDUCIR_INSUMOS_POR_VENTA

# Test 1: Conversiones
assert convertir(1, "kg", "gr") == 1000
assert convertir(1000, "gr", "kg") == 1
print("✅ Conversiones OK")

# Test 2: Obtener insumo
with OBTENER_SESION() as s:
    insumo = s.query(MODELO_INSUMO).first()
    if insumo:
        print(f"✅ Insumo encontrado: {insumo.NOMBRE}")

# Test 3: Deducción (si existe producto con fórmula)
resultado = DEDUCIR_INSUMOS_POR_VENTA(1, 1)
if resultado['exito']:
    print(f"✅ Deducción OK: {resultado['mensaje']}")
else:
    print(f"⚠️ {resultado.get('error', 'Sin error')}")

print("\n🎉 SISTEMA LISTO")
EOF
```

---

## 📞 PRÓXIMOS PASOS

1. **Integrar en PedidosPage:**
   - Llamar `DEDUCIR_INSUMOS_POR_VENTA()` cuando se procesa venta

2. **Agregar UI en Dashboard:**
   - Widget de alertas pendientes
   - Indicadores de stock bajo
   - Botón para ver detalles

3. **Implementar Recordatorios:**
   - Usar APScheduler para verificar FECHA_PROXIMA_COMPRA
   - Notificaciones visuales

4. **Reportes Avanzados:**
   - Gráficas de consumo
   - Análisis de tendencias
   - Proyecciones de stock

---

**¡Sistema listo para usar! 🚀**
