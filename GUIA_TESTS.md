# 🧪 Suite de Pruebas - Cony Chips

## Estructura de Tests

Los tests están organizados en dos categorías siguiendo las metodologías de testing estándar:

### 📦 Caja Negra (Black Box Testing)
**Ubicación:** `tests/caja_negra/`

Pruebas de **integración** que validan el comportamiento desde la perspectiva del usuario final:

- `test_flujo_navegacion.py` - Verifica el flujo completo de navegación entre todas las vistas
- `test_dropdown_interaccion.py` - Valida la interacción con el selector de sucursales

**Características:**
- No requieren conocimiento de la implementación interna
- Prueban casos de uso reales
- Verifican flujos end-to-end

### 🔬 Caja Blanca (White Box Testing)
**Ubicación:** `tests/caja_blanca/`

Pruebas **unitarias** que validan la estructura y lógica interna del código:

- `test_layout_estructura.py` - Verifica la estructura interna de LayoutBase
- `test_navbar_logica.py` - Valida la lógica interna del NavbarGlobal

**Características:**
- Requieren conocimiento de la implementación
- Prueban métodos y atributos privados
- Verifican estados internos

## 🚀 Ejecución de Tests

### Ejecutar TODOS los tests

```bash
python tests/ejecutar_todos_tests.py
```

Este script ejecuta automáticamente ambas categorías y muestra un resumen completo.

## 📊 Cobertura de Tests

### Vistas Probadas
- ✅ Dashboard Administrativo
- ✅ Vouchers
- ✅ Finanzas y Reportes
- ✅ Gestión de Usuarios
- ✅ Auditoría del Sistema

### Componentes Probados
- ✅ LayoutBase (estructura y construcción)
- ✅ NavbarGlobal (lógica y estado)
- ✅ BottomNavigation (navegación)
- ✅ Dropdown de sucursales (interacción)
