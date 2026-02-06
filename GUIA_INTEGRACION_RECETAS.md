# 🔗 Guía de Integración - RecetasPageModerna + AlertasInsumosPage

## Ubicación de los componentes

- **RecetasPageModerna.py** → `features/admin/presentation/pages/vistas/RecetasPageModerna.py`
- **AlertasInsumosPage.py** → `features/admin/presentation/pages/vistas/AlertasInsumosPage.py`
- **ConversionesUnidades.py** (actualizado) → `core/utilidades/ConversionesUnidades.py`
- **consumo_automatico.py** (actualizado) → `features/insumos/consumo_automatico.py`

---

## Opción 1: Integración en PaginaAdmin.py

### Paso 1: Agregar métodos de navegación

En `features/admin/presentation/pages/PaginaAdmin.py`, agregar:

```python
def _IR_A_RECETAS(self, e=None):
    """Navega a la página de recetas"""
    from features.admin.presentation.pages.vistas.RecetasPageModerna import RecetasPageModerna
    from core.decoradores.DecoradorVistas import safe_update
    
    self._pagina.controls.clear()
    self._pagina.controls.append(RecetasPageModerna(self._pagina, self.usuario))
    safe_update(self._pagina)

def _IR_A_ALERTAS(self, e=None):
    """Navega a la página de alertas"""
    from features.admin.presentation.pages.vistas.AlertasInsumosPage import AlertasInsumosPage
    from core.decoradores.DecoradorVistas import safe_update
    
    self._pagina.controls.clear()
    self._pagina.controls.append(AlertasInsumosPage(self._pagina, self.usuario))
    safe_update(self._pagina)
```

### Paso 2: Agregar botones en el dashboard

En la construcción del contenido del dashboard:

```python
# En la sección de botones de admin
ft.Row([
    ft.ElevatedButton(
        "📖 Recetas",
        on_click=self._IR_A_RECETAS,
        bgcolor=ft.Colors.AMBER_600,
        color=ft.Colors.WHITE,
        icon=ft.icons.RECEIPT_LONG,
        expand=True,
    ),
    ft.ElevatedButton(
        "🚨 Alertas",
        on_click=self._IR_A_ALERTAS,
        bgcolor=ft.Colors.RED_600,
        color=ft.Colors.WHITE,
        icon=ft.icons.WARNING_ROUNDED,
        expand=True,
    ),
], spacing=10, expand=True)
```

---

## Opción 2: Integración en NavbarGlobal

Si prefieres agregar los botones en la barra de navegación:

```python
# En NavbarGlobal.py o LayoutBase.py

def _agregar_botones_insumos(self):
    """Agrega botones de Recetas y Alertas a la navbar"""
    
    return ft.Row([
        ft.IconButton(
            ft.icons.RECEIPT_LONG,
            tooltip="📖 Recetas",
            on_click=self._IR_A_RECETAS,
            icon_color=ft.Colors.AMBER_600,
        ),
        ft.Badge(
            content=ft.IconButton(
                ft.icons.WARNING_ROUNDED,
                tooltip="🚨 Alertas",
                on_click=self._IR_A_ALERTAS,
                icon_color=ft.Colors.RED_600,
            ),
            label=self._obtener_alertas_pendientes(),
            bgcolor=ft.Colors.RED_700,
        ),
    ], spacing=10)
```

---

## Integración de Deducción Automática en Ventas

### Integrar DEDUCIR_INSUMOS_POR_VENTA en el flujo de ventas

En el archivo donde se registran las ventas (ej: `PedidosPage.py`):

```python
from features.insumos.consumo_automatico import DEDUCIR_INSUMOS_POR_VENTA

def _registrar_venta(self, producto_id: int, cantidad: int):
    """
    Registra venta y deduce insumos automáticamente
    """
    try:
        # 1. Registrar la venta (tu lógica actual)
        # ... código de registro de venta ...
        
        # 2. Deducir insumos automáticamente
        resultado = DEDUCIR_INSUMOS_POR_VENTA(
            producto_id=producto_id,
            cantidad_productos=cantidad
        )
        
        if resultado["exito"]:
            # Mostrar confirmación
            self._mostrar_exito(f"✅ Venta registrada. Insumos deducidos.")
            
            # Si hay alertas generadas
            if resultado["alertas_generadas"]:
                alerta_msg = f"⚠️ {len(resultado['alertas_generadas'])} alertas de stock bajo generadas"
                self._mostrar_advertencia(alerta_msg)
        else:
            self._mostrar_error(f"❌ {resultado['error']}")
            
    except Exception as e:
        logger.error(f"Error en venta: {e}")
        self._mostrar_error(f"❌ Error: {e}")
```

---

## Ejemplo Completo de Flujo

```python
# PASO 1: Admin crea receta
# Entra a RecetasPageModerna
# - Producto: PopiPapa
# - Insumo: Pollo
# - Cantidad: 30
# - Unidad: gr
# - Tiempo: 5 minutos
# - Guarda

# PASO 2: Se registra venta
resultado = DEDUCIR_INSUMOS_POR_VENTA(
    producto_id=1,  # PopiPapa
    cantidad_productos=5  # Se venden 5
)

# Sistema:
# 1. Obtiene fórmula: 30gr Pollo por PopiPapa
# 2. Calcula: 30gr * 5 = 150gr
# 3. Deduce: stock_pollo = 1000 - 150 = 850gr
# 4. Crea movimiento tipo PRODUCCION
# 5. Verifica: 850 < 500 (mínimo)?
# 6. NO → Sin alertas
# 
# Si hubiera sido 25 vendidas:
# Resultado: 1000 - (30*25) = 250gr < 500 → ALERTA CREADA

# PASO 3: Admin ve alertas
# Entra a AlertasInsumosPage
# - Muestra: "Pollo - Stock bajo: 250 < 500 gr"
# - Admin compra más Pollo
# - Marca alerta como "Resuelta"
# - Sistema:✓ ALERTA.RESUELTA = True
```

---

## Funciones Disponibles para Usar

### Desde ConversionesUnidades.py

```python
from core.utilidades.ConversionesUnidades import (
    obtener_categorias,                    # → ["PESO", "VOLUMEN", "LONGITUD"]
    obtener_unidades_por_categoria,       # → ["gr", "kg", "lb", "oz", "arroba"]
    obtener_categoria_unidad,             # → "PESO" (para una unidad)
    convertir,                            # → convertir(30, "gr", "kg") → 0.03
    normalizar_unidad,                    # → "gramo" → "gr"
    obtener_unidades_compatibles          # → ["gr", "kg", "lb", ...]
)
```

### Desde consumo_automatico.py

```python
from features.insumos.consumo_automatico import (
    DEDUCIR_INSUMOS_POR_VENTA,           # Función principal
    VERIFICAR_STOCK_INSUMO,              # Ver estado actual
    OBTENER_INSUMOS_STOCK_BAJO           # Listar insumos bajos
)
```

---

## Validaciones Implementadas

✅ **RecetasPageModerna:**
- Campos requeridos: producto, insumo, cantidad, unidad
- Validación de números positivos
- Manejo de errores de BD

✅ **Deducción Automática:**
- Stock suficiente antes de deducir
- Conversión correcta de unidades
- No crear alertas duplicadas

✅ **Alertas:**
- Solo crear si no existe alerta pendiente
- Validar stock < mínimo
- Registrar fecha/hora

---

## Testing Recomendado

```python
# Test 1: Crear receta y verificar
receta_id = crear_receta(
    producto_id=1,
    insumo_id=1,
    cantidad=30,
    unidad="gr",
    tiempo_prep=5
)
assert receta_id > 0

# Test 2: Deducción sin alerta
resultado = DEDUCIR_INSUMOS_POR_VENTA(1, 1)
assert resultado["exito"] == True
assert len(resultado["alertas_generadas"]) == 0

# Test 3: Deducción con alerta
resultado = DEDUCIR_INSUMOS_POR_VENTA(1, 100)
assert resultado["exito"] == True
assert len(resultado["alertas_generadas"]) > 0

# Test 4: Conversiones
assert convertir(1, "kg", "gr") == 1000
assert convertir(1000, "ml", "litro") == 1
```

---

## Permisos Requeridos

```python
@REQUIERE_ROL(ROLES.ADMIN, ROLES.SUPERADMIN)
```

Ambas páginas (RecetasPageModerna y AlertasInsumosPage) requieren:
- Rol **ADMIN** o **SUPERADMIN**

---

## Estructura de Datos Retornados

### DEDUCIR_INSUMOS_POR_VENTA

```python
{
    "exito": True,
    "mensaje": "Insumos deducidos para 5x PopiPapa",
    "producto": {
        "id": 1,
        "nombre": "PopiPapa"
    },
    "insumos_deducidos": [
        {
            "insumo_id": 1,
            "insumo_nombre": "Pollo",
            "estado": "OK",
            "stock_anterior": 1000,
            "cantidad_deducida": 150,
            "stock_nuevo": 850,
            "unidad": "gr"
        }
    ],
    "alertas_generadas": [
        {
            "insumo_id": 2,
            "insumo_nombre": "PPA",
            "stock_actual": 40,
            "stock_minimo": 100,
            "alerta_id": 5
        }
    ]
}
```

---

## Notas Importantes

1. **Flet Framework:** Sistema usa Flet 0.80.3 (desktop)
2. **BD:** SQLAlchemy + PostgreSQL
3. **Imports:** Todas las funciones están listas para importar
4. **Conversiones:** Soporta 15 unidades en 3 categorías
5. **Alertas:** Se crean automáticamente, no manualmente

---

## Troubleshooting

### ❌ "No module named 'RecetasPageModerna'"
**Solución:** Verificar que el archivo está en `features/admin/presentation/pages/vistas/`

### ❌ "DEDUCIR_INSUMOS_POR_VENTA no encuentra fórmulas"
**Solución:** Verificar que existan recetas creadas para ese producto

### ❌ "Stock insuficiente"
**Solución:** Es un warning, no un error. La venta se rechaza si falta stock

### ❌ "AlertasInsumosPage no muestra alertas"
**Solución:** Ejecutar una deducción que genere alertas (stock < mínimo)

---

## Próximas Funcionalidades (Opcional)

- [ ] Reportes de consumo de insumos
- [ ] Histórico de cambios de recetas
- [ ] Previsión de stock basada en ventas
- [ ] Integración con compras automáticas
- [ ] Export de recetas a PDF
- [ ] Duplicar/Clonar recetas existentes

---

**Documento versión:** 1.0  
**Fecha:** 2 de Febrero, 2026  
**Estado:** ✅ LISTO PARA INTEGRACIÓN
