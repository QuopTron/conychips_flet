# 🎯 Sistema de Filtro de Sucursales - Dashboard Admin

## ✅ Implementación Completada

### 📋 Características

1. **Filtro de Sucursales en Navbar**
   - Dropdown en el navbar del admin permite seleccionar sucursal
   - Opción "Todas" para ver datos globales
   - Filtro se mantiene al navegar entre páginas

2. **Auditoría de Cambios**
   - Cada cambio de sucursal se registra en la tabla AUDITORIA
   - Incluye usuario, fecha, sucursal anterior y nueva
   - Permite tracking de quién filtró qué y cuándo

3. **Sistema de Cache Inteligente**
   - Cache específico por sucursal
   - Invalidación automática al cambiar filtro
   - TTL de 5 minutos para estadísticas
   - Mejora rendimiento significativamente

4. **Indicador Visual**
   - Dashboard muestra sucursal activa
   - Formato: "📍 [Nombre Sucursal]"
   - Visible solo cuando hay filtro activo

## 🔧 Implementación Técnica

### Flujo de Datos

```
Usuario selecciona sucursal en Navbar
    ↓
NavbarAdmin._on_sucursal_change()
    ↓
1. Actualiza _USUARIO.SUCURSAL_SELECCIONADA
2. Registra en AUDITORIA
3. Invalida cache
    ↓
AdminBloc.CargarDashboard(sucursal_id)
    ↓
1. Verifica cache específico de sucursal
2. Si no existe, consulta BD con filtro
3. Guarda en cache
    ↓
Dashboard muestra datos filtrados
```

### Archivos Modificados

1. **NavbarAdmin.py**
   - Método `_on_sucursal_change()` - Maneja cambio y auditoría
   - Método `_registrar_cambio_sucursal()` - Registro en BD
   - Método `_invalidar_cache_dashboard()` - Limpia cache

2. **AdminBloc.py**
   - Soporte para `sucursal_id` en eventos
   - Métodos de cache específico por sucursal
   - `_obtener_dashboard_cache()` y `_guardar_dashboard_cache()`

3. **AdminEvento.py**
   - `CargarDashboard(sucursal_id: Optional[int])`
   - `RecargarDashboard(sucursal_id: Optional[int])`

4. **CargarEstadisticasDashboard.py**
   - `EJECUTAR(sucursal_id: Optional[int])`

5. **FuenteAdminLocal.py**
   - Filtros SQL por `SUCURSAL_ID`
   - Aplicado en pedidos, ganancias, estadísticas semanales

6. **PaginaAdmin.py**
   - Header muestra sucursal activa
   - Pasa `sucursal_id` al BLoC al iniciar

## 📊 Tabla de Auditoría

### Registro Ejemplo

```sql
INSERT INTO AUDITORIA (
    USUARIO_ID,
    ACCION,
    ENTIDAD,
    ENTIDAD_ID,
    DETALLE,
    FECHA
) VALUES (
    1,
    'CAMBIO_FILTRO_SUCURSAL',
    'SUCURSAL',
    5,
    'Cambió filtro de "Todas las sucursales" a "Sucursal Centro"',
    '2026-01-28 20:30:00'
);
```

### Consultas Útiles

```sql
-- Ver todos los cambios de filtro de un usuario
SELECT * FROM AUDITORIA 
WHERE USUARIO_ID = 1 
AND ACCION = 'CAMBIO_FILTRO_SUCURSAL'
ORDER BY FECHA DESC;

-- Ver actividad de filtros hoy
SELECT U.NOMBRE_USUARIO, A.DETALLE, A.FECHA
FROM AUDITORIA A
JOIN USUARIOS U ON A.USUARIO_ID = U.ID
WHERE A.ACCION = 'CAMBIO_FILTRO_SUCURSAL'
AND DATE(A.FECHA) = CURRENT_DATE
ORDER BY A.FECHA DESC;
```

## 🗄️ Cache Redis

### Keys Utilizadas

```
# Dashboard global (todas las sucursales)
dashboard:estadisticas
dashboard:graficos

# Dashboard por sucursal específica
dashboard:estadisticas:sucursal:1
dashboard:estadisticas:sucursal:2
...
```

### Comandos Redis

```bash
# Ver todas las keys de dashboard
redis-cli KEYS "dashboard:*"

# Ver cache de sucursal específica
redis-cli GET "dashboard:estadisticas:sucursal:1"

# Limpiar cache de todas las sucursales
redis-cli DEL $(redis-cli KEYS "dashboard:estadisticas:sucursal:*")

# Ver TTL de cache
redis-cli TTL "dashboard:estadisticas"
```

## 🎯 Uso

### Para Usuarios

1. Iniciar sesión como admin o superadmin
2. En el navbar, ver dropdown "Sucursal"
3. Seleccionar sucursal deseada o "Todas"
4. Dashboard se actualiza automáticamente
5. El filtro persiste al navegar por el sistema

### Para Desarrolladores

```python
# Obtener sucursal seleccionada
sucursal_id = getattr(usuario, 'SUCURSAL_SELECCIONADA', None)

# Cargar datos filtrados
if sucursal_id is None:
    # Todas las sucursales
    query = sesion.query(MODELO_PEDIDO)
else:
    # Sucursal específica
    query = sesion.query(MODELO_PEDIDO).filter_by(SUCURSAL_ID=sucursal_id)

# En BLoCs
ADMIN_BLOC.AGREGAR_EVENTO(CargarDashboard(sucursal_id=sucursal_id))

# En Vistas (Vouchers, Finanzas, Pedidos)
suc = getattr(self._USUARIO, 'SUCURSAL_SELECCIONADA', None)
VOUCHERS_BLOC.AGREGAR_EVENTO(CargarVouchers(
    estado="PENDIENTE",
    sucursal_id=suc
))
```

## ✅ Beneficios

1. **Auditoría Completa**: Trazabilidad total de filtros
2. **Performance**: Cache evita consultas repetidas
3. **UX**: Filtro persiste en navegación
4. **Seguridad**: Registro de acciones en BD
5. **Escalabilidad**: Cache por sucursal independiente

## 📝 Notas

- El atributo `SUCURSAL_SELECCIONADA` se almacena en el objeto usuario en memoria (no persiste entre sesiones)
- Al cerrar sesión, el filtro se resetea
- Compatible con páginas: Dashboard, Vouchers, Finanzas, Pedidos, y todas las CRUD
- Los gráficos del dashboard también respetan el filtro

---

**Fecha**: 28 de Enero 2026  
**Versión**: 2.0.0  
**Patrón**: Siguiendo lógica de Vouchers y Finanzas
