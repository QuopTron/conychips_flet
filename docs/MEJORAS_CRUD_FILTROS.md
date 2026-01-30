# Mejoras en CRUD y Filtros por Sucursal

## Resumen de Cambios

Se implementaron mejoras significativas en los módulos de **Gestión de Usuarios**, **Finanzas** y **Vouchers** para:

1. ✅ Aplicar filtros automáticos por sucursal seleccionada
2. ✅ Mejorar diseño y UX de tablas y formularios
3. ✅ Optimizar queries con filtros prehechos
4. ✅ Sincronizar con el dropdown de sucursal en NavbarAdmin

---

## 1. Gestión de Usuarios

### Cambios Implementados

#### ✅ Filtro por Sucursal
- **PaginaGestionUsuarios.py**: Usa `SUCURSAL_SELECCIONADA` del usuario admin
- **UsuariosEvento.py**: `CargarUsuarios` acepta `sucursal_id` opcional
- **FuenteUsuariosLocal.py**: Query filtra por `SUCURSAL_ID` cuando se especifica

```python
# Ejemplo de uso
def _CARGAR_USUARIOS(self):
    sucursal_id = None
    rol_usuario = self._usuario.ROLES[0].NOMBRE if hasattr(self._usuario.ROLES[0], 'NOMBRE') else self._usuario.ROLES[0]
    
    # ADMIN solo ve su sucursal
    if rol_usuario == "ADMIN":
        sucursal_id = self._usuario.SUCURSAL_ID
    
    # SUPERADMIN puede filtrar por sucursal o ver todas
    elif rol_usuario == "SUPERADMIN":
        sucursal_id = getattr(self._usuario, 'SUCURSAL_SELECCIONADA', None)
    
    self._bloc.AGREGAR_EVENTO(CargarUsuarios(
        rol_filtro=rol_filtro,
        estado_filtro=estado_filtro,
        sucursal_id=sucursal_id
    ))
```

#### ✅ Diseño Mejorado
- **TablaUsuarios.py**: 
  - DataTable con colores por rol
  - Estados visuales (✓ Activo / ✗ Inactivo)
  - Botones contextuales según permisos
  - Badges de color para roles

- **DialogosUsuario.py**:
  - Validación completa de formularios
  - Mensajes de error claros
  - Campos optimizados con íconos

#### ✅ Permisos Jerárquicos
| Rol | Puede Editar | Notas |
|-----|--------------|-------|
| SUPERADMIN | Todos | Sin restricciones |
| ADMIN | Solo roles menores + misma sucursal | No puede editar SUPERADMIN/ADMIN |
| Otros | Ninguno | Solo lectura |

---

## 2. Finanzas

### Cambios Implementados

#### ✅ Filtro Automático por Sucursal
- **finanzas_bloc.py**:
  - Constructor acepta `sucursal_id` opcional
  - Método `cambiar_sucursal()` para actualizar filtro dinámicamente
  - Todas las queries filtran por sucursal automáticamente

```python
class FinanzasBloc:
    def __init__(self, sucursal_id: Optional[int] = None):
        self._sucursal_id = sucursal_id  # None = todas las sucursales
    
    def _calcular_resumen(self, sesion):
        query_base = sesion.query(MODELO_PEDIDO)
        
        # Aplicar filtro si está configurado
        if self._sucursal_id is not None:
            query_base = query_base.filter(
                MODELO_PEDIDO.SUCURSAL_ID == self._sucursal_id
            )
        
        # ... resto de la lógica
```

- **FinanzasPage.py**:
  - Obtiene `SUCURSAL_SELECCIONADA` del usuario al iniciar
  - Crea BLoC con ese filtro pre-aplicado

```python
def __init__(self, PAGINA: ft.Page, USUARIO):
    sucursal_seleccionada = getattr(USUARIO, 'SUCURSAL_SELECCIONADA', None)
    self.bloc = FinanzasBloc(sucursal_id=sucursal_seleccionada)
```

#### ✅ Queries Optimizadas
- **Ingresos**: Filtra `MODELO_PEDIDO` por `SUCURSAL_ID`
- **Egresos**: Filtra `MODELO_CAJA_MOVIMIENTO` por `SUCURSAL_ID`
- **Pedidos**: Lista optimizada con JOINs y filtro de sucursal
- **Vouchers**: Cuenta por estado con filtro de sucursal

#### ✅ Cache Invalidado Correctamente
```python
def cambiar_sucursal(self, sucursal_id: Optional[int]):
    """Cambia el filtro de sucursal y recarga datos"""
    self._sucursal_id = sucursal_id
    self.invalidar_cache()  # Limpia cache anterior
    self._manejar_cargar_resumen()  # Recarga con nuevo filtro
```

---

## 3. Vouchers

### Estado Actual

#### ✅ Ya Implementado (desde refactorización anterior)
- **VouchersBloc.py**: Ya usa `sucursal_id` en eventos
- **CargarVouchers**: Acepta `sucursal_id` opcional
- **FuenteVouchersLocal.py**: Query filtra por sucursal mediante JOIN con PEDIDOS

```python
def obtener_por_estado(self, estado: str, limite: int = 50, offset: int = 0, sucursal_id: int | None = None):
    # Base query por estado
    query = sesion.query(MODELO_VOUCHER).filter(...)
    
    # Filtro por sucursal via JOIN
    if sucursal_id is not None:
        query = query.join(
            MODELO_PEDIDO, 
            MODELO_PEDIDO.ID == MODELO_VOUCHER.PEDIDO_ID
        ).filter(
            MODELO_PEDIDO.SUCURSAL_ID == sucursal_id
        )
    
    return query.order_by(...).limit(limite).offset(offset).all()
```

- **VouchersPage.py**: Ya usa `SUCURSAL_SELECCIONADA` del usuario

```python
def _CARGAR_INICIAL(self):
    suc = getattr(self._USUARIO, 'SUCURSAL_SELECCIONADA', None)
    VOUCHERS_BLOC.AGREGAR_EVENTO(CargarVouchers(
        estado="PENDIENTE", 
        offset=0, 
        sucursal_id=suc
    ))
```

---

## 4. Integración con NavbarAdmin

### Cómo Funciona

1. **NavbarAdmin.py** tiene dropdown de sucursales
2. Al seleccionar una sucursal, se ejecuta `_on_sucursal_change()`
3. Se actualiza `USUARIO.SUCURSAL_SELECCIONADA`
4. Se invalida cache de Redis
5. Se registra en auditoría
6. **Las páginas deben recargar sus datos al detectar el cambio**

### Flujo de Datos

```
┌─────────────────┐
│  NavbarAdmin    │
│  Dropdown       │
└────────┬────────┘
         │ on_select
         ▼
┌─────────────────┐
│ _on_sucursal_   │
│ change()        │
└────────┬────────┘
         │
         ├─► USUARIO.SUCURSAL_SELECCIONADA = nueva_id
         ├─► INVALIDAR_CACHE_DASHBOARD()
         └─► REGISTRAR_AUDITORIA()
                 │
                 ▼
         ┌───────────────┐
         │  PÁGINAS      │
         │  (deben       │
         │  escuchar     │
         │  cambio)      │
         └───────────────┘
```

### Recomendación para Páginas

Para que las páginas reaccionen automáticamente:

```python
class PaginaEjemplo(ft.Column):
    def __init__(self, PAGINA, USUARIO):
        self._USUARIO = USUARIO
        
        # Guardar sucursal inicial
        self._sucursal_actual = getattr(USUARIO, 'SUCURSAL_SELECCIONADA', None)
        
        # Iniciar timer para verificar cambios
        self._iniciar_verificador_sucursal()
    
    def _iniciar_verificador_sucursal(self):
        """Verifica cada 2s si cambió la sucursal"""
        import threading
        
        def verificar():
            nueva_suc = getattr(self._USUARIO, 'SUCURSAL_SELECCIONADA', None)
            if nueva_suc != self._sucursal_actual:
                self._sucursal_actual = nueva_suc
                # Recargar datos con nuevo filtro
                self._bloc.cambiar_sucursal(nueva_suc)
            
            # Repetir cada 2s
            threading.Timer(2.0, verificar).start()
        
        threading.Timer(2.0, verificar).start()
```

---

## 5. Patrones Aplicados

### BLoC Pattern (sin Streams)

Todos los módulos usan el mismo patrón:

```python
class MiBloc:
    def __init__(self, sucursal_id: Optional[int] = None):
        self._sucursal_id = sucursal_id
        self._estado = EstadoInicial()
        self._listeners = []
    
    def AGREGAR_LISTENER(self, listener):
        if listener not in self._listeners:
            self._listeners.append(listener)
    
    def _CAMBIAR_ESTADO(self, nuevo_estado):
        self._estado = nuevo_estado
        for listener in self._listeners:
            try:
                listener(nuevo_estado)
            except Exception as e:
                print(f"Error: {e}")
    
    def AGREGAR_EVENTO(self, evento):
        thread = threading.Thread(
            target=self._PROCESAR_EVENTO,
            args=(evento,),
            daemon=True
        )
        thread.start()
```

### Clean Architecture

```
Presentation Layer (UI)
    ↓ eventos
BLoC (Estado + Lógica)
    ↓ llamadas
Repository (Interface)
    ↓ implementación
DataSource (PostgreSQL/Redis)
```

### Filtros Prehechos

Todas las queries aceptan filtros opcionales:

```python
def OBTENER_DATOS(
    self,
    filtro1: Optional[str] = None,
    filtro2: Optional[bool] = None,
    sucursal_id: Optional[int] = None  # ← Siempre incluir
):
    query = sesion.query(MODELO)
    
    if filtro1:
        query = query.filter(MODELO.CAMPO1 == filtro1)
    
    if filtro2 is not None:
        query = query.filter(MODELO.CAMPO2 == filtro2)
    
    if sucursal_id is not None:
        query = query.filter(MODELO.SUCURSAL_ID == sucursal_id)
    
    return query.all()
```

---

## 6. Testing

### Escenarios de Prueba

#### Como SUPERADMIN
1. Login como `superadmin@conychips.com`
2. Verificar dropdown de sucursales aparece
3. Seleccionar "Todas las Sucursales"
4. Ir a Finanzas → Ver datos de todas las sucursales
5. Ir a Vouchers → Ver vouchers de todas
6. Ir a Usuarios → Ver todos los usuarios
7. Cambiar a "Sucursal Centro"
8. Verificar que todos los módulos filtran por esa sucursal

#### Como ADMIN
1. Login como `admin@sucursalcentro.com`
2. Verificar que NO aparece dropdown (sucursal fija)
3. Ir a Finanzas → Solo ver datos de su sucursal
4. Ir a Vouchers → Solo ver vouchers de su sucursal
5. Ir a Usuarios → Solo ver usuarios de su sucursal
6. Intentar editar usuario de otra sucursal → **Debe fallar**

### Comandos de Testing

```bash
# Reiniciar app
pkill -f "python.*main.py" && sleep 1 && python main.py

# Ver logs en tiempo real
tail -f app_logs.txt

# Verificar sucursales en BD
psql -d nombre_bd -c "SELECT ID, NOMBRE FROM SUCURSALES;"

# Verificar usuarios por sucursal
psql -d nombre_bd -c "SELECT ID, NOMBRE_USUARIO, SUCURSAL_ID FROM USUARIOS ORDER BY SUCURSAL_ID;"
```

---

## 7. Archivos Modificados

### Gestión de Usuarios
- ✅ `features/gestion_usuarios/presentation/pages/PaginaGestionUsuarios.py`
- ✅ `features/gestion_usuarios/presentation/widgets/TablaUsuarios.py`
- ✅ `features/gestion_usuarios/presentation/widgets/DialogosUsuario.py`
- ✅ `features/gestion_usuarios/presentation/bloc/UsuariosEvento.py`
- ✅ `features/gestion_usuarios/presentation/bloc/UsuariosBloc.py`
- ✅ `features/gestion_usuarios/data/datasources/FuenteUsuariosLocal.py`

### Finanzas
- ✅ `features/finanzas/presentation/bloc/finanzas_bloc.py`
- ✅ `features/admin/presentation/pages/vistas/FinanzasPage.py`

### Vouchers
- ⚠️ Ya estaba implementado (no requiere cambios)

### Admin/Navbar
- ⚠️ NavbarAdmin ya funcional (cambios previos)

---

## 8. Próximos Pasos

### Recomendaciones

1. **Implementar listener de cambio de sucursal** en todas las páginas
2. **Agregar indicador visual** cuando hay filtro activo
3. **Persistir sucursal seleccionada** en sesión de usuario
4. **Agregar exportación de reportes** por sucursal
5. **Dashboard comparativo** entre sucursales (solo SUPERADMIN)

### Mejoras Futuras

- [ ] Cache por sucursal separado (evitar invalidar todo)
- [ ] WebSocket para sincronizar cambio de sucursal en tiempo real
- [ ] Estadísticas comparativas entre sucursales
- [ ] Gráficos con Chart.js/Plotly
- [ ] Exportar a Excel/PDF con filtros aplicados

---

## 9. Notas Importantes

⚠️ **Limitaciones**
- Redis cache se invalida completamente al cambiar sucursal
- Timer de verificación consume recursos (considerar WebSocket)
- Filtro de sucursal es opcional (None = todas)

✅ **Ventajas**
- Queries optimizadas con filtros en BD (no en memoria)
- Patrón consistente en todos los módulos
- Fácil agregar nuevos filtros
- Auditoría completa de cambios

---

**Fecha**: 2026-01-28  
**Autor**: GitHub Copilot  
**Versión**: 1.0
