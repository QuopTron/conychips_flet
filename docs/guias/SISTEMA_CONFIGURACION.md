# 🔧 Sistema de Configuración Dinámica

## ✅ Funcionalidades Implementadas

### 1. **Configuraciones en Base de Datos**
- Tabla `CONFIGURACION_SISTEMA` con:
  - Clave única
  - Valor (string)
  - Tipo (int, float, bool, str)
  - Descripción
  - Categoría
  - Fecha de modificación
  - Usuario que modificó

### 2. **Log de Auditoría**
- Tabla `LOG_CONFIGURACION` que registra:
  - Valor anterior
  - Valor nuevo
  - Usuario que realizó el cambio
  - Fecha y hora exacta
  - Referencia a la configuración modificada

### 3. **Servicio de Configuración**
- `ServicioConfiguracion` con:
  - Cache en memoria para performance
  - Métodos para obtener/actualizar valores
  - Registro automático de cambios
  - Historial completo de modificaciones

### 4. **Interfaz de Usuario**

#### Overlay de Configuración (400x400)
- Popup compacto con todas las configuraciones
- Campos específicos según tipo (TextField para números, Switch para booleanos)
- Actualización en tiempo real
- Botón para ver historial

#### Overlay de Historial (700x500)
- Tabla `DataTable` con:
  - Configuración modificada
  - Valor anterior
  - Valor nuevo
  - Usuario que hizo el cambio
  - Fecha del cambio
- Scroll para ver muchos registros
- Ordenado por fecha descendente

## 📊 Configuraciones Disponibles

### Vouchers
```python
"vouchers.tiempo_bloqueo_minutos"
Valor: 5 (int)
Descripción: Tiempo en minutos antes de que un voucher se bloquee automáticamente
```

### Pedidos
```python
"pedidos.tiempo_preparacion_minutos"
Valor: 30 (int)
Descripción: Tiempo estimado de preparación de pedidos en minutos
```

### Sistema
```python
"sistema.modo_debug"
Valor: false (bool)
Descripción: Activar modo debug del sistema
```

## 🎯 Uso

### Configuración por Categoría (Cada Vista)

Cada vista/módulo tiene su propio botón de configuración que muestra solo sus configuraciones relevantes:

```python
# En VouchersPage.py
from core.ui.OverlayConfiguracion import OverlayConfiguracion

def _abrir_configuracion(self):
    overlay = OverlayConfiguracion(
        pagina=self.pagina,
        usuario_id=self.usuario.id,
        categoria="vouchers"  # Solo configs de vouchers
    )
    overlay.mostrar()

# Botón en el header
btn_config = ft.IconButton(
    icon=ft.Icons.SETTINGS_ROUNDED,
    tooltip="Configuración de Vouchers",
    on_click=lambda _: self._abrir_configuracion(),
)
```

### Abrir Configuración Global (Admin/SuperAdmin)

```python
# Desde el admin dashboard (todas las configs)
overlay = OverlayConfiguracion(pagina, usuario_id=usuario_actual.id)
overlay.mostrar()
```

### Obtener Valor en Código
```python
from core.configuracion.ServicioConfiguracion import ServicioConfiguracion

# Obtener tiempo de bloqueo
minutos = ServicioConfiguracion.obtener_valor("vouchers.tiempo_bloqueo_minutos", default=5)

# Usar en cálculos
if tiempo_transcurrido > timedelta(minutes=minutos):
    bloquear_voucher()
```

### Actualizar Valor
```python
# Con usuario (se registra en log)
ok = ServicioConfiguracion.actualizar_valor(
    "vouchers.tiempo_bloqueo_minutos", 
    10,
    usuario_id=1
)

# Sin usuario (cambio del sistema)
ok = ServicioConfiguracion.actualizar_valor(
    "sistema.modo_debug", 
    True
)
```

### Ver Historial
```python
# Historial de una configuración específica
historial = ServicioConfiguracion.obtener_historial(
    clave="vouchers.tiempo_bloqueo_minutos",
    limite=20
)

# Historial completo
historial_completo = ServicioConfiguracion.obtener_historial(limite=100)

for log in historial:
    print(f"{log['valor_anterior']} → {log['valor_nuevo']}")
    print(f"Por: {log['usuario_nombre']} el {log['fecha']}")
```

## 🔐 Permisos

Solo **admin** y **superadmin** pueden:
- Ver configuraciones
- Modificar valores
- Acceder al historial de cambios

## 🎨 Diseño de Overlays

### Overlay de Configuración por Categoría

Cada vista muestra solo sus configuraciones relevantes con **confirmación de cambios**:

```
┌─────────────────────────────────────┐
│ ⚙️  Configuración - VOUCHERS  [X]  │ ← Header con categoría
├─────────────────────────────────────┤
│                                     │
│ Tiempo Bloqueo Minutos      [5  ]  │ ← Campo editable
│ Tiempo en minutos antes de...      │
│                                     │
├─────────────────────────────────────┤
│ [Ver Historial]          [Cerrar]  │ ← Detecta cambios
└─────────────────────────────────────┘
       400px × 400px

Flujo de cambios:
1. Usuario cambia "5" a "10" pero NO presiona Enter
2. Usuario hace clic en [Cerrar]
3. Sistema detecta: valor actual (10) ≠ valor original (5)
4. Muestra diálogo de confirmación ↓

┌────────────────────────────┐
│ ⚠️ Cambios sin guardar     │
├────────────────────────────┤
│ Hay cambios sin guardar.   │
│ ¿Deseas cerrar sin guardar?│
├────────────────────────────┤
│ [Cancelar] [Cerrar sin...] │
└────────────────────────────┘

Si NO hay cambios:
- Cierra inmediatamente sin mostrar nada
```

### Overlay de Configuración Global
```
┌─────────────────────────────────────┐
│ ⚙️  Configuración            [X]    │ ← Sin categoría específica
├─────────────────────────────────────┤
│                                     │
│ Tiempo Bloqueo Minutos      [5  ]  │
│ Tiempo en minutos antes de...      │
│                                     │
│ Tiempo Preparacion          [30 ]  │
│ Tiempo estimado de...              │
│                                     │
│ Modo Debug                  [OFF]  │
│ Activar modo debug                 │
│                                     │
├─────────────────────────────────────┤
│ [Ver Historial]          [Cerrar]  │
└─────────────────────────────────────┘
       400px × 400px
```

### Overlay de Historial
```
┌──────────────────────────────────────────────────────────┐
│ 📜 Historial de Cambios                          [X]    │ ← Header (SECUNDARIO)
├──────────────────────────────────────────────────────────┤
│ Config      │ Anterior │ Nuevo  │ Usuario   │ Fecha    │
├─────────────┼──────────┼────────┼───────────┼──────────┤
│ Tiempo...   │ 5        │ 10     │ superadm  │ 27/01... │
│ Tiempo...   │ 10       │ 3      │ Sistema   │ 27/01... │
│ Tiempo...   │ 3        │ 15     │ admin     │ 27/01... │
│             │          │        │           │          │
│                     (scroll)                            │
│                                                          │
├──────────────────────────────────────────────────────────┤
│ Total: 3 cambios                          [Cerrar]     │ ← Footer
└──────────────────────────────────────────────────────────┘
              700px × 550px
```

## 🗄️ Esquema de Base de Datos

### CONFIGURACION_SISTEMA
```sql
CREATE TABLE CONFIGURACION_SISTEMA (
    ID SERIAL PRIMARY KEY,
    CLAVE VARCHAR(100) UNIQUE NOT NULL,
    VALOR VARCHAR(500) NOT NULL,
    TIPO VARCHAR(20) NOT NULL,
    DESCRIPCION VARCHAR(300),
    CATEGORIA VARCHAR(50),
    FECHA_MODIFICACION TIMESTAMP DEFAULT NOW(),
    MODIFICADO_POR INTEGER REFERENCES USUARIOS(ID)
);
```

### LOG_CONFIGURACION
```sql
CREATE TABLE LOG_CONFIGURACION (
    ID SERIAL PRIMARY KEY,
    CONFIGURACION_ID INTEGER REFERENCES CONFIGURACION_SISTEMA(ID),
    CLAVE VARCHAR(100) NOT NULL,
    VALOR_ANTERIOR VARCHAR(500),
    VALOR_NUEVO VARCHAR(500) NOT NULL,
    USUARIO_ID INTEGER REFERENCES USUARIOS(ID),
    FECHA TIMESTAMP DEFAULT NOW()
);
```

## ✅ Tests Pasados

```bash
python test_sistema_configuracion.py
```

Verifica:
- ✅ Configuraciones dinámicas en BD
- ✅ Cache en memoria
- ✅ Log de cambios (auditoría)
- ✅ Registro de usuario que modifica
- ✅ Historial completo
- ✅ Persistencia en PostgreSQL

## 📝 Próximos Pasos

1. ✅ Agregar botón "⚙️ Configuración" en vista de vouchers
2. Agregar botón de configuración en otras vistas:
   - PedidosPage → categoría="pedidos"
   - CocinaPage → categoría="cocina"
   - CajaPage → categoría="cajas"
3. Validar permisos antes de mostrar overlay
4. Agregar más configuraciones según necesidad:
   - `cajas.monto_inicial_default`
   - `pedidos.tiempo_maximo_espera`
   - `cocina.items_por_pagina`
   - `notificaciones.activar_email`

## 🎓 Ventajas del Sistema por Categoría

1. **Enfocado**: Cada vista solo muestra sus configuraciones relevantes
2. **Simplicidad**: No abrumar al usuario con configs de otros módulos
3. **Contexto**: La configuración está donde se usa
4. **Escalable**: Fácil agregar nuevas categorías y configs
5. **Flexible**: Admin puede ver todas o filtradas
6. **Auditoría**: Saber quién cambió qué en cada módulo
7. **Seguridad**: Confirmación de cambios sin guardar
   - Detecta automáticamente si hay cambios pendientes
   - Pregunta antes de cerrar si hay modificaciones
   - No molesta si no hubo cambios
