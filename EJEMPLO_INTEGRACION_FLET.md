# 📌 EJEMPLO DE INTEGRACIÓN EN PaginaAdmin.py

## Paso 1: Importar la página de alertas

```python
# Al inicio de PaginaAdmin.py, agregar:
from features.admin.presentation.pages.vistas.AlertasInsumosPage import AlertasInsumosPage
```

## Paso 2: Agregar método para abrir alertas

```python
class PaginaAdmin(LayoutBase):
    # ... código existente ...
    
    def _VER_ALERTAS_INSUMOS(self, e):
        """Abre la página de alertas de insumos"""
        from features.admin.presentation.pages.vistas.AlertasInsumosPage import AlertasInsumosPage
        
        self._pagina.controls.clear()
        self._pagina.controls.append(AlertasInsumosPage(self._pagina, self._usuario))
        safe_update(self._pagina)
```

## Paso 3: Agregar botón en el dashboard

```python
def _construir_botones_principales(self):
    """Construye los botones del dashboard"""
    return ft.Column([
        # ... botones existentes ...
        
        # Nuevo botón para alertas
        ft.ElevatedButton(
            "⚠️ Alertas de Insumos",
            on_click=self._VER_ALERTAS_INSUMOS,
            bgcolor=ft.Colors.RED_600,
            color=ft.Colors.WHITE,
            icon=ft.icons.WARNING_ROUNDED,
            width=200,
            height=50,
        ),
    ], spacing=8)
```

## Paso 4: Integrar deducción de insumos en ventas

```python
# Cuando se procesa una venta (en PedidosPage o donde corresponda):

from features.insumos.consumo_automatico import DEDUCIR_INSUMOS_POR_VENTA

def procesar_venta_completa(pedido):
    \"\"\"Procesa una venta y deduce automáticamente insumos\"\"\"
    
    # ... lógica de venta existente ...
    
    # AL FINAL, deducir insumos automáticamente:
    for item in pedido.items:
        resultado = DEDUCIR_INSUMOS_POR_VENTA(
            producto_id=item.producto_id,
            cantidad_productos=item.cantidad
        )
        
        if resultado['exito']:
            print(f"✅ Insumos deducidos para {item.cantidad}x {item.producto.nombre}")
            
            # Si se generaron alertas, mostrar notificación
            if resultado['alertas_generadas']:
                self._pagina.snack_bar = ft.SnackBar(
                    ft.Text(
                        f"⚠️ {len(resultado['alertas_generadas'])} alerta(s) de stock bajo",
                        color=ft.Colors.WHITE
                    ),
                    bgcolor=ft.Colors.ORANGE_600,
                    duration=3000,
                )
                self._pagina.snack_bar.open = True
        else:
            print(f"❌ Error deduciendo insumos: {resultado.get('error')}")
            # Mostrar error al usuario
            self._pagina.snack_bar = ft.SnackBar(
                ft.Text(f"❌ Error: {resultado.get('error')}", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED_600,
            )
            self._pagina.snack_bar.open = True
```

## Paso 5: Mostrar contador de alertas en NavBar

```python
# En NavbarGlobal.py o donde esté el navbar:

def _actualizar_contador_alertas(self):
    \"\"\"Actualiza el contador de alertas pendientes\"\"\"
    from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_ALERTA_INSUMO
    
    try:
        with OBTENER_SESION() as session:
            pendientes = session.query(MODELO_ALERTA_INSUMO).filter(
                MODELO_ALERTA_INSUMO.RESUELTA == False,
                MODELO_ALERTA_INSUMO.LEIDA == False
            ).count()
            
            return pendientes  # Mostrar en badge del botón
    except:
        return 0
```

---

# 🔗 INTEGRACIÓN COMPLETA

## Estructura de carpetas requerida:

```
✅ Archivos implementados:
  core/utilidades/ConversionesUnidades.py
  features/insumos/consumo_automatico.py
  features/admin/presentation/pages/vistas/AlertasInsumosPage.py
  core/base_datos/ConfiguracionBD.py (MODIFICADO - new fields + modelo)
```

## Importar donde sea necesario:

```python
# Para conversiones:
from core.utilidades.ConversionesUnidades import convertir, normalizar_unidad

# Para deducir insumos:
from features.insumos.consumo_automatico import DEDUCIR_INSUMOS_POR_VENTA

# Para ver alertas:
from features.admin.presentation.pages.vistas.AlertasInsumosPage import AlertasInsumosPage

# Para acceso a BD:
from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION,
    MODELO_ALERTA_INSUMO,
    MODELO_INSUMO,
)
```

---

# 📊 FLUJO VISUAL

```
Usuario abre PaginaAdmin
        ↓
Ve botón "⚠️ Alertas de Insumos"
        ↓
Hace clic → Se abre AlertasInsumosPage
        ↓
AlertasInsumosPage carga alertas de BD
        ↓
Muestra DataTable con:
  - Nombre del insumo
  - Tipo de alerta
  - Fecha de creación
  - Botones (Marcar leída / Resolver)
        ↓
Admin puede:
  ✓ Ver qué insumos tienen stock bajo
  ✓ Marcar alertas como leídas
  ✓ Resolver cuando compra
  ✓ Ver estadísticas
```

---

# ✅ VERIFICACIÓN

Todo está lista para integrar:
- ✅ ConversionesUnidades.py (244 líneas, funcional)
- ✅ consumo_automatico.py (285 líneas, funcional)
- ✅ AlertasInsumosPage.py (200+ líneas, interfaz Flet)
- ✅ Base de datos (tabla ALERTAS_INSUMO + campos en INSUMOS)

**Solo falta agregar los botones y métodos en PaginaAdmin.py** 🚀
