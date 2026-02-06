# 🎯 GUÍA VISUAL - INSUMOS DESDE CERO

## 🌟 CASO REAL: NEGOCIO DE COMIDAS RÁPIDAS

Tu negocio produce:
- 🍗 PopiPapa (pollo + palomita)
- 🍗 Pollo Frito Completo
- 🧀 Quesadilla
- 🍟 Papas Fritas

---

## 📊 PASO 1: CONOCER TUS INSUMOS

### Pregunta: ¿QUÉ COMPRAS?

```
INSUMO 1: Pollo Fresco
├─ Dónde compras: Granja XYZ
├─ Cada cuánto: Cada 2 días
├─ En qué medida: Kilos
├─ Precio: $12.50 por kilo
├─ Cantidad mínima para operar: 50 kilos
└─ Hoy tienes: 100 kilos

INSUMO 2: Palomita Armada (PPA)
├─ Dónde compras: Distribuidor Central
├─ En qué medida: Arrobas (25 kilos)
├─ Precio: $50 por arroba
├─ Cantidad mínima: 30 arrobas
└─ Hoy tienes: 80 arrobas

INSUMO 3: Queso Fresco
├─ Dónde compras: Lechería Local
├─ En qué medida: Kilos
├─ Precio: $20 por kilo
├─ Cantidad mínima: 20 kilos
└─ Hoy tienes: 45 kilos
```

---

## 🖥️ PASO 2: CREAR INSUMOS EN SISTEMA

### Acción: Click ➕ NUEVO INSUMO

**Insumo 1 - Pollo Fresco:**
```
┌─────────────────────────────┐
│ ➕ Crear Nuevo Insumo       │
├─────────────────────────────┤
│ Nombre: Pollo Fresco        │
│ Descripción: Pechuga y muslo│
│ Unidad: kg                  │
│ Precio Unitario: $12.50     │
│ Stock Mínimo: 50            │
│ Proveedor: Granja XYZ       │
│                             │
│ [Cancelar] [Guardar]        │
└─────────────────────────────┘

✅ RESULTADO: Insumo creado
```

**Insumo 2 - Palomita Armada:**
```
Nombre: Palomita Armada
Unidad: arroba
Precio: $50
Stock Mínimo: 30
Proveedor: Distribuidor Central
✅ RESULTADO: Insumo creado
```

**Insumo 3 - Queso Fresco:**
```
Nombre: Queso Fresco
Unidad: kg
Precio: $20
Stock Mínimo: 20
Proveedor: Lechería Local
✅ RESULTADO: Insumo creado
```

**ESTADO FINAL - Tabla de Insumos:**
```
┌─────────────────┬──────┬───────┬──────┬─────────┐
│ Insumo          │ Unid │ Stock │ Mín  │ Precio  │
├─────────────────┼──────┼───────┼──────┼─────────┤
│ Pollo Fresco    │ kg   │ 100   │ 50   │ $12.50  │
│ Palomita Armada │ arr  │ 80    │ 30   │ $50.00  │
│ Queso Fresco    │ kg   │ 45    │ 20   │ $20.00  │
└─────────────────┴──────┴───────┴──────┴─────────┘

✅ TODO LISTO: Insumos configurados
```

---

## 🍽️ PASO 3: CREAR FÓRMULAS (RECETAS)

### Pregunta: ¿QUÉ LLEVA CADA PRODUCTO?

**PopiPapa Lleva:**
- 2 kilos de Pollo Fresco
- 1 arroba de Palomita Armada

**Pollo Frito Completo Lleva:**
- 1.5 kilos de Pollo Fresco

**Quesadilla Lleva:**
- 0.5 kilos de Queso Fresco

---

### Acción: Click 📋 NUEVA FÓRMULA

**Fórmula 1 - PopiPapa con Pollo:**
```
┌──────────────────────────────┐
│ 📋 Nueva Fórmula             │
├──────────────────────────────┤
│ Producto: PopiPapa           │
│ Insumo: Pollo Fresco         │
│ Cantidad: 2 kg               │
│ Notas: Pechuga fresca        │
│                              │
│ [Cancelar] [Guardar]         │
└──────────────────────────────┘

✅ CREADA: PopiPapa usa 2kg Pollo
```

**Fórmula 2 - PopiPapa con PPA:**
```
Producto: PopiPapa
Insumo: Palomita Armada
Cantidad: 1 arroba
Notas: PPA acompañamiento

✅ CREADA: PopiPapa usa 1 arroba PPA
```

**Fórmula 3 - Pollo Frito:**
```
Producto: Pollo Frito Completo
Insumo: Pollo Fresco
Cantidad: 1.5 kg
Notas: Completo pechuga-muslo

✅ CREADA: Pollo Frito usa 1.5kg Pollo
```

**Fórmula 4 - Quesadilla:**
```
Producto: Quesadilla
Insumo: Queso Fresco
Cantidad: 0.5 kg
Notas: Queso deshilado

✅ CREADA: Quesadilla usa 0.5kg Queso
```

**ESTADO FINAL - Tabla de Fórmulas:**
```
┌─────────────────┬──────────────────┬──────────┐
│ Producto        │ Insumo           │ Cantidad │
├─────────────────┼──────────────────┼──────────┤
│ PopiPapa        │ Pollo Fresco     │ 2 kg     │
│ PopiPapa        │ Palomita Armada  │ 1 arr    │
│ Pollo Frito     │ Pollo Fresco     │ 1.5 kg   │
│ Quesadilla      │ Queso Fresco     │ 0.5 kg   │
└─────────────────┴──────────────────┴──────────┘

✅ TODO LISTO: Recetas configuradas
```

---

## 💰 PASO 4: REGISTRAR COMPRAS (ENTRADA)

### Mañana: Compra semanal

**Compra 1:**
```
Hoy compramos 120 kg de Pollo
┌─────────────────────────────┐
│ 📊 Registrar Movimiento     │
├─────────────────────────────┤
│ Insumo: Pollo Fresco        │
│ Tipo: ENTRADA               │
│ Cantidad: 120 kg            │
│ Observación: Compra semanal │
│                             │
│ [Cancelar] [Registrar]      │
└─────────────────────────────┘

📊 RESULTADO:
├─ Stock anterior: 100 kg
├─ Se agregó: +120 kg
└─ Stock nuevo: 220 kg ✅
```

**Compra 2:**
```
Tipo: ENTRADA
Insumo: Palomita Armada
Cantidad: 50 arrobas
Observación: Compra bisemanal

📊 RESULTADO:
├─ Stock anterior: 80 arrobas
├─ Se agregó: +50 arrobas
└─ Stock nuevo: 130 arrobas ✅
```

**Compra 3:**
```
Tipo: ENTRADA
Insumo: Queso Fresco
Cantidad: 30 kg
Observación: Fresco del día

📊 RESULTADO:
├─ Stock anterior: 45 kg
├─ Se agregó: +30 kg
└─ Stock nuevo: 75 kg ✅
```

---

## 🏭 PASO 5: REGISTRAR PRODUCCIÓN (SALIDA)

### Durante el día: Vendemos comidas

**A las 10am:**
```
Hicimos 50 PopiPappas

Eso implica:
- Pollo: 50 × 2kg = 100 kg
- PPA: 50 × 1 arroba = 50 arrobas

Registramos cada uno:
```

**Movimiento 1 - Pollo para PopiPappas:**
```
┌─────────────────────────────┐
│ 📊 Registrar Movimiento     │
├─────────────────────────────┤
│ Insumo: Pollo Fresco        │
│ Tipo: PRODUCCION            │
│ Cantidad: 100 kg            │
│ Observación: 50 PopiPappas  │
│                             │
│ [Cancelar] [Registrar]      │
└─────────────────────────────┘

📊 RESULTADO:
├─ Stock anterior: 220 kg
├─ Se utilizó: -100 kg
└─ Stock nuevo: 120 kg ✅
```

**Movimiento 2 - PPA para PopiPappas:**
```
Tipo: PRODUCCION
Insumo: Palomita Armada
Cantidad: 50 arrobas
Observación: 50 PopiPappas

📊 RESULTADO:
├─ Stock anterior: 130 arrobas
├─ Se utilizó: -50 arrobas
└─ Stock nuevo: 80 arrobas ✅
```

**A las 2pm: Vendemos Pollos Fritos:**
```
Tipo: PRODUCCION
Insumo: Pollo Fresco
Cantidad: 30 kg (20 pollos × 1.5kg)
Observación: 20 Pollos Fritos

📊 RESULTADO:
├─ Stock anterior: 120 kg
├─ Se utilizó: -30 kg
└─ Stock nuevo: 90 kg ✅
```

---

## 📈 PASO 6: VER REPORTE DEL DÍA

### Al finalizar el día

**Endpoint: GET /api/reporte/diario**

**Respuesta:**
```json
{
  "exito": true,
  "fecha": "2024-02-02",
  "data": {
    "ENTRADA": [
      {"INSUMO": "Pollo Fresco", "CANTIDAD": 120, "OBS": "Compra semanal"},
      {"INSUMO": "Palomita Armada", "CANTIDAD": 50, "OBS": "Compra bisemanal"},
      {"INSUMO": "Queso Fresco", "CANTIDAD": 30, "OBS": "Fresco del día"}
    ],
    "PRODUCCION": [
      {"INSUMO": "Pollo Fresco", "CANTIDAD": -100, "OBS": "50 PopiPappas"},
      {"INSUMO": "Palomita Armada", "CANTIDAD": -50, "OBS": "50 PopiPappas"},
      {"INSUMO": "Pollo Fresco", "CANTIDAD": -30, "OBS": "20 Pollos Fritos"}
    ],
    "SALIDA": []
  },
  "total_movimientos": 6
}
```

**Interpretación del Reporte:**
```
RESUMEN DEL DÍA:

📥 ENTRADAS (Compras):
├─ Pollo: +120 kg
├─ PPA: +50 arrobas
└─ Queso: +30 kg

🏭 PRODUCCIÓN (Uso):
├─ Pollo: -100 kg (50 PopiPappas + 20 Pollos Fritos)
├─ PPA: -50 arrobas (50 PopiPappas)
└─ Queso: 0 (ninguna quesadilla se hizo)

📊 STOCK FINAL:
├─ Pollo: 220 - 130 = 90 kg ✅
├─ PPA: 130 - 50 = 80 arrobas ✅
└─ Queso: 75 - 0 = 75 kg ✅

💰 INSIGHT:
├─ Vendimos muchas PopiPappas (50 unidades)
├─ También Pollos Fritos (20 unidades)
├─ No hicimos quesadillas hoy
└─ Stock está bien, sin alertas
```

---

## 🎓 RESUMEN VISUAL

```
DÍA 1: SETUP
├─ ➕ Crear 3 Insumos (Pollo, PPA, Queso)
├─ 📋 Crear 4 Fórmulas (PopiPapa×2, Pollo, Quesadilla)
└─ ✅ Sistema listo

DÍA 2: OPERACIÓN
├─ 📊 Registrar ENTRADA: Compramos insumos
├─ 🏭 Registrar PRODUCCION: Vendemos productos
└─ 📈 Ver reporte: Consumo y stock del día

DÍA 3+: RUTINA
├─ Cada mañana: 📊 ENTRADA (compras)
├─ Durante el día: 📊 PRODUCCION (ventas)
├─ Si hay problema: 📊 AJUSTE (reconteo)
└─ Al fin de semana: 📈 Análisis de reportes
```

---

## ✅ CHECKLIST

- [ ] Identifiqué todos mis insumos (qué compro)
- [ ] Sé el precio de cada uno
- [ ] Definí stock mínimo para alertas
- [ ] Creé todas las fórmulas (recetas)
- [ ] Registré entrada de hoy
- [ ] Registré producción durante el día
- [ ] Consulté reporte diario
- [ ] Entiendo cuánto insumo sobró

---

**¡Ya controlas todo tu inventario! 🎉**
