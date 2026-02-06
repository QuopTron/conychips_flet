# 📦 QUICK START INSUMOS (5 MINUTOS)

## ¿QUÉ ES?

Sistema para controlar:
- **INSUMOS** = Lo que compras (pollo, arroz, queso, etc)
- **FÓRMULAS** = Las recetas (PopiPapa = 2kg pollo + 1 arroba PPA)
- **MOVIMIENTOS** = El registro de compras/ventas

---

## 🎯 LOS 3 BOTONES

### ➕ NUEVO INSUMO
- **Qué:** Creas un ingrediente que compras
- **Ejemplo:** Pollo Fresco - $12.50/kg - Stock mín: 50kg
- **Cuándo:** Al principio y cuando agregues nuevo ingrediente

### 📋 NUEVA FÓRMULA
- **Qué:** Defines qué insumos lleva cada producto
- **Ejemplo:** PopiPapa = 2kg Pollo + 1 arroba PPA
- **Cuándo:** Cuando creas un nuevo producto

### 📊 REGISTRAR MOVIMIENTO
- **Qué:** Registras entrada/salida de insumos
- **Ejemplo:** ENTRADA +100kg Pollo / PRODUCCION -30kg Pollo
- **Cuándo:** Diariamente (compras y ventas)

---

## ⚡ FLUJO RÁPIDO (HOY)

### 1️⃣ Setup (10 min)
```
➕ Nuevo Insumo → Pollo (kg)
➕ Nuevo Insumo → PPA (arroba)
📋 Nueva Fórmula → PopiPapa = Pollo + PPA
```

### 2️⃣ Compra (2 min)
```
📊 ENTRADA → +100kg Pollo
📊 ENTRADA → +50 arrobas PPA
```

### 3️⃣ Producción (1 min)
```
📊 PRODUCCION → -30kg Pollo (30 PopiPappas)
📊 PRODUCCION → -30 arrobas PPA
```

### 4️⃣ Reporte (30 seg)
```
GET /api/reporte/diario
→ Muestra: Compré 100kg, Usé 30kg, Me quedan 70kg ✅
```

---

## 📊 EJEMPLO REAL

### NEGOCIO: Comidas Rápidas

**Insumos:**
- Pollo Fresco: 100kg hoy
- Palomita Armada: 80 arrobas hoy
- Queso: 45kg hoy

**Productos que venden:**
- PopiPapa = Pollo + PPA
- Pollo Frito = Solo pollo
- Quesadilla = Queso

**Hoy vendieron:**
- 50 PopiPappas → Usó 100kg Pollo + 50 arrobas PPA
- 20 Pollos Fritos → Usó 30kg Pollo
- 0 Quesadillas → Usó 0kg Queso

**Resultado del reporte:**
- Pollo: Tenía 100kg, Usé 130kg = FALTA 30kg
- PPA: Tenía 80 arrobas, Usé 50 = Quedan 30
- Queso: Tenía 45kg, Usé 0 = Quedan 45kg

---

## ✅ CHECKLIST RÁPIDO

- [ ] Creé mis insumos (pollo, PPA, queso, etc)
- [ ] Definí stock mínimo para alertas
- [ ] Creé fórmulas para cada producto
- [ ] Registré compra de hoy (ENTRADA)
- [ ] Registré ventas de hoy (PRODUCCION)
- [ ] Ví reporte diario

---

## 📁 ARCHIVOS

**Código:**
- `features/admin/presentation/pages/vistas/InsumosPageModerna.py` - UI (560 líneas)
- `features/admin/api/rutas_insumos.py` - APIs REST

**Documentación:**
- `INSUMOS_V1_SIMPLIFICADO.md` - Guía completa
- `INSUMOS_GUIA_VISUAL.md` - Ejemplo paso a paso
- `QUICK_START_INSUMOS.md` - Este archivo

**Base de datos:**
- `MODELO_INSUMO` - Tabla de insumos
- `MODELO_FORMULA` - Tabla de fórmulas
- `MODELO_MOVIMIENTO_INSUMO` - Tabla de movimientos

---

## 🚀 COMANDOS ÚTILES

```bash
# Ver si está bien
python -m py_compile features/admin/presentation/pages/vistas/InsumosPageModerna.py

# Ver insumos por API
curl http://localhost:5000/api/insumos

# Ver reporte del día
curl http://localhost:5000/api/reporte/diario
```

---

## 💡 TIPS

1. **Crea insumos primero** - Los necesitas antes de fórmulas
2. **Un producto = múltiples insumos** - PopiPapa usa pollo Y PPA
3. **Registra todos los días** - Entrada (compra) + Producción (venta)
4. **Stock mínimo es alerta** - Se pone rojo si baja
5. **Soft delete** - Nada se borra, solo se marca inactivo

---

**¡Listo! Ya sabes todo lo necesario. 🎉**

Próximo: Lee `INSUMOS_GUIA_VISUAL.md` para ver ejemplo completo
