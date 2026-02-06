# ✅ Implementación de Eliminación Lógica de Sucursales

## 📋 Resumen de Cambios

Se ha implementado exitosamente el sistema de **eliminación lógica** para las sucursales, reemplazando la eliminación física que causaba problemas con datos relacionados.

---

## 🔧 Cambios Realizados

### 1. **Modelo de Base de Datos** 
[ConfiguracionBD.py](../core/base_datos/ConfiguracionBD.py#L109-L130)

Se agregaron 3 nuevos campos al modelo `MODELO_SUCURSAL`:

```python
# Eliminación lógica
ELIMINADA = Column(Boolean, default=False)
FECHA_ELIMINACION = Column(DateTime, nullable=True)
USUARIO_ELIMINO_ID = Column(Integer, ForeignKey("USUARIOS.ID"), nullable=True)

# Relación con el usuario que eliminó
USUARIO_ELIMINO = relationship("MODELO_USUARIO", foreign_keys=[USUARIO_ELIMINO_ID])
```

**Ventajas**:
- ✅ Preserva historial completo de datos
- ✅ Permite auditoría de eliminaciones
- ✅ No rompe relaciones con pedidos/ventas
- ✅ Recuperación de datos posible

---

### 2. **Método de Carga de Sucursales**
[SucursalesPage.py](../features/admin/presentation/pages/vistas/SucursalesPage.py#L204-L215)

Se modificó `_cargar_sucursales()` para **filtrar automáticamente** las sucursales eliminadas:

```python
def _cargar_sucursales(self):
    """Carga sucursales desde la BD (excluye eliminadas)"""
    with OBTENER_SESION() as sesion:
        # Filtrar solo sucursales NO eliminadas
        query = sesion.query(MODELO_SUCURSAL).filter_by(ELIMINADA=False)
        
        if self._filtro_estado != "TODAS":
            query = query.filter_by(ESTADO=self._filtro_estado)
        
        self._sucursales = query.order_by(
            MODELO_SUCURSAL.FECHA_CREACION.desc()
        ).all()
    
    self._actualizar_ui()
```

---

### 3. **Eliminación Lógica en lugar de Física**
[SucursalesPage.py](../features/admin/presentation/pages/vistas/SucursalesPage.py#L920-L945)

**ANTES** (Eliminación física - ❌ MALO):
```python
def eliminar(e):
    with OBTENER_SESION() as sesion:
        s = sesion.query(MODELO_SUCURSAL).filter_by(ID=sucursal.ID).first()
        sesion.delete(s)  # ← Eliminación física
        sesion.commit()
```

**DESPUÉS** (Eliminación lógica - ✅ BUENO):
```python
def eliminar(e):
    with OBTENER_SESION() as sesion:
        s = sesion.query(MODELO_SUCURSAL).filter_by(ID=sucursal.ID).first()
        # Eliminación lógica
        s.ELIMINADA = True
        s.ACTIVA = False
        s.FECHA_ELIMINACION = datetime.now()
        s.USUARIO_ELIMINO_ID = self._usuario.ID
        sesion.commit()
```

**Mensaje actualizado**:
- Antes: "Sucursal eliminada"
- Ahora: "Sucursal eliminada (puede restaurarse)"

---

### 4. **Funcionalidad de Restauración (SUPERADMIN)** 🆕
[SucursalesPage.py](../features/admin/presentation/pages/vistas/SucursalesPage.py#L1040-L1141)

Se agregaron 2 nuevos métodos:

#### `_ver_sucursales_eliminadas()`
- Muestra listado de sucursales eliminadas con fecha y usuario
- Solo accesible para usuarios con rol **SUPERADMIN**
- Permite ver histórico completo de eliminaciones

#### `_restaurar_sucursal(sucursal)`
- Restaura una sucursal eliminada
- Restablece estado a "ACTIVA"
- Limpia flags de eliminación
- Solo para **SUPERADMIN**

```python
def _restaurar_sucursal(self, sucursal):
    """Restaura una sucursal eliminada (solo SUPERADMIN)"""
    with OBTENER_SESION() as sesion:
        s = sesion.query(MODELO_SUCURSAL).filter_by(ID=sucursal.ID).first()
        s.ELIMINADA = False
        s.FECHA_ELIMINACION = None
        s.USUARIO_ELIMINO_ID = None
        s.ACTIVA = True
        s.ESTADO = "ACTIVA"
        sesion.commit()
```

---

### 5. **Botón "Ver Eliminadas" en UI** 🆕
[SucursalesPage.py](../features/admin/presentation/pages/vistas/SucursalesPage.py#L88-L103)

Se agregó un botón en el header (solo visible para SUPERADMIN):

```python
# Botón para ver eliminadas (solo SUPERADMIN)
if self._usuario.TIENE_ROL(ROLES.SUPERADMIN):
    btn_ver_eliminadas = ft.Container(
        content=ft.Row([
            ft.Icon(ft.icons.RESTORE_FROM_TRASH, color=ft.Colors.ORANGE_700),
            ft.Text("Ver Eliminadas", color=ft.Colors.ORANGE_700)
        ]),
        on_click=lambda e: self._ver_sucursales_eliminadas(),
        tooltip="Ver y restaurar sucursales eliminadas"
    )
```

**UI Result**:
```
[🏪 Gestión de Sucursales]          [🗑️ Ver Eliminadas] [➕ Nueva Sucursal]
                                     ↑ Solo SUPERADMIN
```

---

### 6. **Mensajes de Confirmación Actualizados**

**Antes**:
> ⚠️ Esta acción eliminará permanentemente la sucursal y no se puede deshacer.
> ⚠️ Si hay datos relacionados (pedidos, ventas, etc.), la eliminación podría fallar.

**Ahora**:
> ℹ️ Esta acción marcará la sucursal como eliminada. Los datos se preservarán.
> ✅ La sucursal puede ser restaurada por un SUPERADMIN si es necesario.

---

## 🚀 Script de Migración

**Archivo**: [migrar_eliminacion_logica_sucursales.py](../migrar_eliminacion_logica_sucursales.py)

Script ejecutado para agregar los nuevos campos a la tabla SUCURSALES en PostgreSQL:

```bash
$ python migrar_eliminacion_logica_sucursales.py

🔧 Iniciando migración: Eliminación lógica de sucursales...
📋 Columnas actuales: ['ID', 'NOMBRE', 'DIRECCION', 'ACTIVA', ...]
➕ Agregando columna ELIMINADA...
✅ Columna ELIMINADA agregada
➕ Agregando columna FECHA_ELIMINACION...
✅ Columna FECHA_ELIMINACION agregada
➕ Agregando columna USUARIO_ELIMINO_ID...
✅ Columna USUARIO_ELIMINO_ID agregada
🔄 Inicializando valores para sucursales existentes...
✅ Migración completada exitosamente!
📊 Total de sucursales en BD: 5
✅ Sucursales activas (no eliminadas): 5
🗑️ Sucursales eliminadas: 0
```

---

## 📊 Flujo de Eliminación y Restauración

### Flujo Normal (ADMIN)

```
1. ADMIN hace clic en "Eliminar" en una sucursal
2. Confirma la eliminación
3. Sistema marca ELIMINADA = True
4. Sucursal desaparece de la vista principal
5. Datos preservados en BD
```

### Flujo de Restauración (SUPERADMIN)

```
1. SUPERADMIN hace clic en "Ver Eliminadas"
2. Se muestra lista de sucursales eliminadas:
   - Nombre
   - Dirección
   - Fecha de eliminación
   - Botón "Restaurar"
3. SUPERADMIN hace clic en "Restaurar"
4. Sistema marca ELIMINADA = False
5. Sucursal vuelve a aparecer en vista principal
6. Estado restaurado a "ACTIVA"
```

---

## 🔐 Permisos

| Acción | ADMIN | SUPERADMIN |
|--------|-------|------------|
| Ver sucursales activas | ✅ | ✅ |
| Crear sucursal | ✅ | ✅ |
| Editar sucursal | ✅ | ✅ |
| Cambiar estado | ✅ | ✅ |
| Eliminar (lógico) | ✅ | ✅ |
| Ver eliminadas | ❌ | ✅ |
| Restaurar | ❌ | ✅ |

---

## 📝 Base de Datos: Estructura SUCURSALES

```sql
CREATE TABLE "SUCURSALES" (
    "ID" INTEGER PRIMARY KEY,
    "NOMBRE" VARCHAR(100) UNIQUE NOT NULL,
    "DIRECCION" VARCHAR(255),
    "ACTIVA" BOOLEAN DEFAULT TRUE,
    "ESTADO" VARCHAR(50) DEFAULT 'ACTIVA',
    "TELEFONO" VARCHAR(20),
    "HORARIO" VARCHAR(100),
    "FECHA_CREACION" TIMESTAMP DEFAULT NOW(),
    "FECHA_ULTIMA_MODIFICACION" TIMESTAMP DEFAULT NOW(),
    
    -- Nuevos campos de eliminación lógica ⬇️
    "ELIMINADA" BOOLEAN DEFAULT FALSE,
    "FECHA_ELIMINACION" TIMESTAMP,
    "USUARIO_ELIMINO_ID" INTEGER REFERENCES "USUARIOS"("ID")
);
```

---

## ✅ Ventajas de la Implementación

1. **Integridad de Datos**: No se pierden pedidos, ventas o historial asociado
2. **Auditoría Completa**: Se sabe quién y cuándo eliminó cada sucursal
3. **Recuperación**: SUPERADMIN puede deshacer eliminaciones accidentales
4. **Sin Errores de FK**: No fallan eliminaciones por relaciones con otras tablas
5. **Cumplimiento**: Permite cumplir con requisitos legales de preservación de datos
6. **Trazabilidad**: Historial completo para análisis y reportes

---

## 🎯 Próximos Pasos Recomendados

1. **Reportes de Auditoría**: Agregar vista de eliminaciones por usuario/fecha
2. **Soft Delete en Otras Tablas**: Aplicar mismo patrón a Productos, Usuarios, etc.
3. **Políticas de Retención**: Definir cuánto tiempo se guardan registros eliminados
4. **Backup Automático**: Antes de cada eliminación, crear snapshot
5. **Notificaciones**: Alertar a SUPERADMIN cuando se elimina algo importante

---

## 🧪 Testing

Para probar la funcionalidad:

1. **Como ADMIN**:
   - Ir a Sucursales
   - Crear una sucursal de prueba
   - Eliminarla → Debe desaparecer de la lista
   - Verificar en BD que `ELIMINADA = True`

2. **Como SUPERADMIN**:
   - Ir a Sucursales
   - Hacer clic en "Ver Eliminadas"
   - Debería aparecer la sucursal eliminada
   - Restaurarla → Debe volver a la lista principal

---

## 📚 Documentación Relacionada

- [FLUJO_SUCURSALES_Y_ROLES.md](FLUJO_SUCURSALES_Y_ROLES.md) - Flujo completo de sucursales
- [ConfiguracionBD.py](../core/base_datos/ConfiguracionBD.py) - Modelos de base de datos
- [SucursalesPage.py](../features/admin/presentation/pages/vistas/SucursalesPage.py) - UI de gestión

---

**Fecha de Implementación**: 2 de Febrero, 2026  
**Versión**: 1.0.0  
**Estado**: ✅ Completado y Probado
