# CajasPageModerna - Documentación

## 📋 Descripción General

**CajasPageModerna** es una versión mejorada del módulo de gestión de cajas siguiendo los patrones establecidos en `ProveedoresPageModerna` y otros módulos modernizados.

## 🎯 Características Principales

### 1. **Panel de Estadísticas**
- **Saldo Total**: Suma del saldo final de todas las cajas activas
- **Ingresos (30 días)**: Total de movimientos de ingreso
- **Egresos (30 días)**: Total de movimientos de egreso
- **Ganancias**: Total de ganancias registradas

### 2. **Gestión de Cajas**
- Visualización de todas las cajas activas por sucursal
- Información: Usuario responsable, fecha de apertura, montos iniciales/finales, ganancias
- Estado visual con colores: Verde para saldo positivo, Rojo para negativo
- Operaciones CRUD completas:
  - **Crear**: Nueva caja con sucursal y monto inicial
  - **Editar**: Actualizar monto final y ganancias
  - **Cerrar**: Soft-delete (desactivar caja)

### 3. **Registro de Movimientos**
- Registro de ingresos y egresos
- Categorización: Venta, Compra, Depósito, Retiro, Otro
- Filtros por tipo: Todos, Ingresos, Egresos
- Información de movimiento: Monto, Descripción, Fecha, Usuario, Sucursal
- Eliminación de movimientos con soft-delete

### 4. **Integración con LayoutBase**
- Hereda toda la funcionalidad de navegación global
- Navbar con filtro de sucursales
- BottomNavigation integrado
- Diseño responsive y consistente

## 🗄️ Modelos de Datos

### MODELO_CAJA
```python
ID                  # ID único
USUARIO_ID          # Usuario que abre la caja
SUCURSAL_ID         # Sucursal asociada
FECHA_APERTURA      # Fecha/hora de apertura
FECHA_CIERRE        # Fecha/hora de cierre
MONTO_INICIAL       # Dinero inicial en centavos
MONTO_FINAL         # Dinero final en centavos
GANANCIAS           # Ganancias del período
ACTIVA              # Boolean (soft delete)
```

### MODELO_CAJA_MOVIMIENTO
```python
ID                  # ID único
USUARIO_ID          # Usuario que registra el movimiento
SUCURSAL_ID         # Sucursal asociada
TIPO                # 'ingreso' o 'egreso'
CATEGORIA           # 'venta', 'compra', 'deposito', 'retiro', 'otro'
MONTO               # Monto en centavos
DESCRIPCION         # Descripción del movimiento
FECHA               # Fecha/hora del movimiento
```

## 🎨 Estructura de Componentes

```
CajasPageModerna
├── Panel de Estadísticas (4 cards)
│   ├── Saldo Total
│   ├── Ingresos
│   ├── Egresos
│   └── Ganancias
├── Sección de Cajas
│   ├── Botones de acción
│   │   ├── Nueva Caja
│   │   └── Registrar Movimiento
│   └── DataTable de Cajas
├── Divisor
└── Sección de Movimientos
    ├── Filtro por tipo
    └── DataTable de Movimientos
```

## 💾 Métodos Principales

### Carga de Datos
- `_cargar_datos()`: Carga cajas, movimientos y sucursales desde BD
- `_construir_datos()`: Prepara datos para visualización

### UI
- `_construir_interfaz()`: Construye la interfaz completa
- `_construir_panel_stats()`: Panel de estadísticas
- `_generar_filas_cajas()`: Genera filas de tabla de cajas
- `_generar_filas_movimientos()`: Genera filas de tabla de movimientos

### CRUD
- `_overlay_crear_caja()`: Dialog para crear nueva caja
- `_overlay_editar_caja(caja_id)`: Dialog para editar caja
- `_overlay_crear_movimiento()`: Dialog para registrar movimiento
- `_eliminar_caja(caja_id)`: Cierra una caja (soft-delete)
- `_eliminar_movimiento(mov_id)`: Elimina un movimiento

### Utilidades
- `_mostrar_error(mensaje)`: Muestra SnackBar rojo
- `_mostrar_exito(mensaje)`: Muestra SnackBar verde
- `_ir_dashboard()`: Vuelve al dashboard
- `_cerrar_sesion()`: Cierra la sesión de usuario

## 🔄 Flujo de Datos

```
1. __init__
   ├─ Cargar datos (_cargar_datos)
   ├─ Construir interfaz (_construir_interfaz)
   └─ Actualizar UI

2. Usuario abre una caja
   ├─ Clic en "Nueva Caja"
   ├─ _overlay_crear_caja()
   ├─ Guardar en BD
   ├─ _cargar_datos() para refrescar
   └─ Actualizar tabla

3. Usuario registra movimiento
   ├─ Clic en "Registrar Movimiento"
   ├─ _overlay_crear_movimiento()
   ├─ Insertar en MODELO_CAJA_MOVIMIENTO
   ├─ Refrescar datos
   └─ Mostrar SnackBar de éxito
```

## 🔌 Integración en Admin

### En `LayoutBase._mostrar_menu_mas()`
```python
("Caja", ft.icons.Icons.POINT_OF_SALE)
```

### En `LayoutBase._navegar_a()`
```python
elif route == "caja":
    self._ir_a_caja()
```

### En `LayoutBase._ir_a_caja()`
```python
def _ir_a_caja(self):
    from features.admin.presentation.pages.vistas.CajasPageModerna import CajasPageModerna
    self._pagina.controls.clear()
    self._pagina.add(CajasPageModerna(self._pagina, self._usuario))
```

## 🎓 Acceso a la Página

1. Login con usuario Admin/SuperAdmin
2. Dashboard → Click en "Más"
3. Seleccionar "Caja"
4. CajasPageModerna se cargará

## 🔍 Validaciones

### Crear Caja
- ✅ Sucursal requerida
- ✅ Monto inicial requerido
- ✅ Monto debe ser número válido

### Crear Movimiento
- ✅ Tipo requerido (ingreso/egreso)
- ✅ Categoría requerida
- ✅ Monto requerido y válido
- ✅ Sucursal requerida

### Editar Caja
- ✅ Montos deben ser números válidos

## 📊 Cálculos

### Saldo Total
```python
sum(c["MONTO_FINAL"] for c in self._cajas)
```

### Ingresos/Egresos
```python
sum(m["MONTO"] for m in movimientos if m["TIPO"] == "ingreso/egreso")
```

### Período de Movimientos
- Últimos 30 días desde hoy
- `fecha_limite = datetime.utcnow() - timedelta(days=30)`

## 🎨 Colores y Estilos

- **Saldo positivo**: Verde claro (#C8E6C9)
- **Saldo negativo**: Rojo claro (#FFCDD2)
- **Ingreso**: Verde oscuro (#4CAF50)
- **Egreso**: Rojo oscuro (#F44336)
- **Ganancias**: Ámbar (#FFC107)
- **Fondo**: Blanco (#FFFFFF)
- **Bordes**: Gris claro (#E0E0E0)

## 🚀 Mejoras Implementadas respecto a FinanzasPage

| Aspecto | FinanzasPage | CajasPageModerna |
|---------|--------------|------------------|
| Estructura | BLoC complejo | Carga directa de BD |
| CRUD | Limitado | Completo (C+R+U+D) |
| UI | Widgets refactorizados | DataTable + Overlays |
| Validaciones | Básicas | Completas |
| Estadísticas | Limitadas | 4 cards con cálculos |
| Filtros | Estado/Código | Tipo de movimiento |
| Soft-delete | No | Sí |
| Código | 185 líneas | 655 líneas (más funcional) |

## ⚡ Performance

- Carga de datos: O(n) - una sola query por tabla
- Renderizado: O(n) en tabla - crecimiento lineal
- Filtros: O(n) - filtrado en memoria
- Actualización: Completa (recarga datos)

## 📝 Notas

1. **Montos en Centavos**: Todos los montos se guardan en centavos (Int) para evitar errores de precisión con decimales
2. **Soft-delete**: Se utiliza flag ACTIVA=False en lugar de eliminar registros
3. **30 días**: Los movimientos muestran datos de últimos 30 días para mejor legibilidad
4. **Sucursales**: Hereda del navbar global, permite filtrar por sucursal(es) seleccionadas
5. **Threading**: Operaciones de BD se hacen en thread principal (sin async para mantener compatibilidad con Flet 0.80.3)

---

**Fecha de Creación**: 03/02/2026  
**Versión**: 1.0 Moderna  
**Estado**: ✅ Producción
