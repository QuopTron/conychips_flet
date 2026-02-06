# 👥 Gestión Moderna de Usuarios con Logs de Auditoría

## 📋 Resumen

Se ha implementado una nueva página de gestión de usuarios con diseño moderno, similar a la de sucursales, que incluye:
- ✅ Vista de usuarios en tarjetas (cards) con diseño intuitivo
- ✅ Filtros avanzados por rol y estado
- ✅ Tabla de detalles en overlay
- ✅ **Logs de auditoría** visibles para ADMIN y SUPERADMIN
- ✅ Diseño responsivo y moderno

---

## 🎨 Características del Diseño

### 1. **Vista Principal con Cards**

Cada usuario se muestra en una tarjeta moderna con:
- 👤 Avatar con emoji según el rol
- 📧 Nombre de usuario y email
- 🎭 Badge de rol con colores distintivos
- ✅/❌ Estado activo/inactivo
- 📅 Fecha de creación y última conexión
- ⚙️ Menú de acciones (editar, cambiar rol, resetear contraseña, etc.)

### 2. **Filtros Intuitivos**

**Filtros por Rol:**
- 📊 Todos
- 👑 SuperAdmin (morado)
- 🔧 Admin (azul)
- 👨‍💼 Empleado (naranja)
- 🎯 Atención (verde)
- 👨‍🍳 Cocinero (rojo)

**Filtros por Estado:**
- 📋 Todos
- ✅ Activos (verde)
- ❌ Inactivos (rojo)

### 3. **Tabla de Detalles en Overlay**

Al hacer clic en "Ver detalles", se muestra una tabla con:
```
╔═══════════════════╦══════════════════════╗
║ Campo             ║ Valor                ║
╠═══════════════════╬══════════════════════╣
║ ID                ║ 1                    ║
║ Usuario           ║ admin                ║
║ Email             ║ admin@cony.com       ║
║ Roles             ║ SUPERADMIN, ADMIN    ║
║ Estado            ║ ✅ Activo            ║
║ Verificado        ║ Sí                   ║
║ Fecha Creación    ║ 01/02/2026 10:30     ║
║ Última Conexión   ║ 02/02/2026 15:45     ║
╚═══════════════════╩══════════════════════╝
```

---

## 📊 Sistema de Logs de Auditoría

### Acceso a Logs

**Botón "Ver Logs"** visible solo para:
- ✅ ADMIN
- ✅ SUPERADMIN

### Información Registrada

Cada acción sobre usuarios se registra en la tabla `AUDITORIA`:

| Acción | Descripción | Color |
|--------|-------------|-------|
| `USUARIO_CREADO` | Nuevo usuario creado | 🟢 Verde |
| `USUARIO_ACTUALIZADO` | Datos modificados | 🟠 Naranja |
| `USUARIO_CAMBIO_ESTADO` | Activado/desactivado | 🟠 Naranja |
| `USUARIO_CAMBIO_ROL` | Rol modificado | 🟠 Naranja |
| `USUARIO_ELIMINADO` | Marcado como inactivo | 🔴 Rojo |
| `USUARIO_CONTRASENA_RESET` | Contraseña reseteada | 🔵 Azul |

### Vista de Logs

Tabla moderna en overlay con:
- 📅 Fecha y hora exacta
- 🏷️ Tipo de acción (con badge de color)
- 👤 Usuario que realizó la acción
- 📝 Detalles completos

**Ejemplo visual:**
```
╔══════════════╦═══════════════╦═══════════╦════════════════════════════╗
║ Fecha/Hora   ║ Acción        ║ Usuario   ║ Detalles                   ║
╠══════════════╬═══════════════╬═══════════╬════════════════════════════╣
║ 02/02/2026   ║ [CAMBIO       ║ admin     ║ Usuario 'jperez' activado  ║
║ 15:30:25     ║  ESTADO]      ║           ║                            ║
║              ║  🟠           ║           ║                            ║
╠══════════════╬═══════════════╬═══════════╬════════════════════════════╣
║ 02/02/2026   ║ [CREADO]      ║ admin     ║ Usuario 'mcordova' creado  ║
║ 10:15:00     ║  🟢           ║           ║ con rol 'ATENCION'         ║
╚══════════════╩═══════════════╩═══════════╩════════════════════════════╝
```

Muestra los últimos **50 registros** relacionados con usuarios.

---

## 🎯 Funcionalidades Implementadas

### ✅ Ver Detalles de Usuario
- Clic en "Ver detalles" del menú
- Overlay con tabla completa de información
- Todos los campos del usuario

### ✅ Cambiar Estado (Activo/Inactivo)
- Clic en "Activar" o "Desactivar"
- Confirmación inmediata
- **Registra en auditoría** quién y cuándo
- Actualización automática de la vista

### 🔄 Funciones Pendientes de Implementar

Las siguientes funciones están preparadas pero requieren completar el formulario:

- ➕ **Crear usuario**: Formulario completo de creación
- ✏️ **Editar usuario**: Formulario de edición con datos pre-llenados
- 🔄 **Cambiar rol**: Selector de nuevo rol
- 🔒 **Resetear contraseña**: Generación de nueva contraseña

---

## 🔐 Sistema de Roles por Color

### Paleta de Colores

```python
ROLES_CONFIG = {
    "SUPERADMIN": {
        "color": ft.Colors.PURPLE_700,    # Morado oscuro
        "bg": ft.Colors.PURPLE_50,        # Morado claro
        "emoji": "👑",
        "desc": "Administrador Total"
    },
    "ADMIN": {
        "color": ft.Colors.BLUE_700,      # Azul oscuro
        "bg": ft.Colors.BLUE_50,          # Azul claro
        "emoji": "🔧",
        "desc": "Administrador"
    },
    "EMPLEADO": {
        "color": ft.Colors.ORANGE_700,    # Naranja oscuro
        "bg": ft.Colors.ORANGE_50,        # Naranja claro
        "emoji": "👨‍💼",
        "desc": "Empleado General"
    },
    "ATENCION": {
        "color": ft.Colors.GREEN_700,     # Verde oscuro
        "bg": ft.Colors.GREEN_50,         # Verde claro
        "emoji": "🎯",
        "desc": "Atención al Cliente"
    },
    "COCINERO": {
        "color": ft.Colors.RED_700,       # Rojo oscuro
        "bg": ft.Colors.RED_50,           # Rojo claro
        "emoji": "👨‍🍳",
        "desc": "Chef / Cocinero"
    },
    "MOTORIZADO": {
        "color": ft.Colors.CYAN_700,      # Cyan oscuro
        "bg": ft.Colors.CYAN_50,          # Cyan claro
        "emoji": "🏍️",
        "desc": "Motorizado"
    }
}
```

---

## 📁 Estructura de Archivos

### Nuevo Archivo

```
features/admin/presentation/pages/vistas/
└── UsuariosPageModerna.py  ← NUEVO (1050+ líneas)
```

### Archivos Modificados

```
features/admin/presentation/pages/
└── PaginaAdmin.py  ← Actualizado (método _VER_USUARIOS)
```

---

## 🔄 Flujo de Navegación

```
Dashboard Admin
     ↓ (clic en "Usuarios")
UsuariosPageModerna
     ├── Ver todos los usuarios
     ├── Filtrar por rol/estado
     ├── Ver detalles (overlay con tabla)
     ├── Cambiar estado (con auditoría)
     └── Ver Logs (overlay con tabla de auditoría) ← Solo ADMIN
```

---

## 💾 Registro en Base de Datos

### Tabla AUDITORIA

```sql
CREATE TABLE AUDITORIA (
    ID SERIAL PRIMARY KEY,
    USUARIO_ID INTEGER REFERENCES USUARIOS(ID),  -- Quién hizo la acción
    ACCION VARCHAR(120),                          -- Tipo de acción
    ENTIDAD VARCHAR(80),                          -- 'USUARIO'
    ENTIDAD_ID INTEGER,                           -- ID del usuario afectado
    DETALLE VARCHAR(300),                         -- Descripción completa
    FECHA TIMESTAMP DEFAULT NOW()                 -- Cuándo ocurrió
);
```

### Ejemplo de Registro

```sql
INSERT INTO AUDITORIA (
    USUARIO_ID,
    ACCION,
    ENTIDAD,
    ENTIDAD_ID,
    DETALLE,
    FECHA
) VALUES (
    1,                                    -- Admin que hizo la acción
    'USUARIO_CAMBIO_ESTADO',              -- Qué hizo
    'USUARIO',                            -- Sobre qué entidad
    5,                                    -- ID del usuario modificado
    'Usuario ''jperez'' activado',       -- Detalles
    '2026-02-02 15:30:25'                -- Cuándo
);
```

---

## 🎨 Componentes UI Destacados

### 1. **Card de Usuario**
```python
ft.Container(
    content=ft.Column([
        # Header: Avatar + Nombre + Badge
        ft.Row([avatar, info, badges, menu]),
        ft.Divider(),
        # Footer: Fechas y estadísticas
        ft.Column([fecha_creacion, ultima_conexion])
    ]),
    padding=20,
    border_radius=16,
    bgcolor=ft.Colors.WHITE,
    shadow=BoxShadow(...)
)
```

### 2. **Tabla de Detalles**
```python
ft.DataTable(
    columns=[
        ft.DataColumn(ft.Text("Campo")),
        ft.DataColumn(ft.Text("Valor"))
    ],
    rows=[...],
    border=ft.border.all(1, ft.Colors.GREY_300),
    heading_row_color=ft.Colors.BLUE_50
)
```

### 3. **Tabla de Logs**
```python
ft.DataTable(
    columns=[
        "Fecha/Hora", "Acción", "Usuario", "Detalles"
    ],
    rows=[
        # Cada fila con badge de color según acción
        ft.DataRow([fecha, badge_accion, usuario, detalle])
    ],
    heading_row_color=ft.Colors.ORANGE_50,
    horizontal_lines=BorderSide(...)
)
```

---

## 📊 Comparación con Sistema Anterior

| Aspecto | Anterior | Nuevo |
|---------|----------|-------|
| Vista | Tabla plana | Cards modernos |
| Filtros | 2 básicos | 6 por rol + 3 por estado |
| Detalles | En línea | Overlay con tabla |
| Logs | ❌ No disponible | ✅ Tabla completa |
| Diseño | Básico | Moderno con colores |
| Auditoría | Parcial | Completa |

---

## 🚀 Uso del Sistema

### Para ADMIN

1. **Acceder**: Dashboard → Botón "Usuarios"
2. **Filtrar**: Seleccionar rol y/o estado deseado
3. **Ver detalles**: Menú de usuario → "Ver detalles"
4. **Gestionar estado**: Menú → "Activar" o "Desactivar"
5. **Ver logs**: Botón "Ver Logs" (arriba derecha)

### Logs de Auditoría

```
1. Clic en "Ver Logs" (🔍 botón naranja)
2. Se abre overlay con tabla de logs
3. Muestra últimos 50 registros de acciones sobre usuarios
4. Incluye:
   - Fecha y hora exacta
   - Tipo de acción (con color)
   - Quién la realizó
   - Detalles completos
```

---

## 🔍 Consultas SQL Útiles

### Ver todos los logs de usuarios

```sql
SELECT 
    A.FECHA,
    A.ACCION,
    U.NOMBRE_USUARIO as QUIEN,
    A.DETALLE
FROM AUDITORIA A
JOIN USUARIOS U ON A.USUARIO_ID = U.ID
WHERE A.ACCION LIKE '%USUARIO%'
ORDER BY A.FECHA DESC
LIMIT 50;
```

### Ver cambios de estado de hoy

```sql
SELECT 
    U.NOMBRE_USUARIO as QUIEN_MODIFICO,
    A.DETALLE,
    A.FECHA
FROM AUDITORIA A
JOIN USUARIOS U ON A.USUARIO_ID = U.ID
WHERE A.ACCION = 'USUARIO_CAMBIO_ESTADO'
  AND DATE(A.FECHA) = CURRENT_DATE
ORDER BY A.FECHA DESC;
```

### Ver quién creó más usuarios

```sql
SELECT 
    U.NOMBRE_USUARIO,
    COUNT(*) as TOTAL_CREADOS
FROM AUDITORIA A
JOIN USUARIOS U ON A.USUARIO_ID = U.ID
WHERE A.ACCION = 'USUARIO_CREADO'
GROUP BY U.NOMBRE_USUARIO
ORDER BY TOTAL_CREADOS DESC;
```

---

## 📝 Próximos Pasos

### Implementaciones Pendientes

1. ✏️ **Formulario de Creación**
   - Campos: usuario, email, contraseña, rol, sucursal
   - Validaciones en tiempo real
   - Registro en auditoría

2. ✏️ **Formulario de Edición**
   - Pre-llenar con datos actuales
   - Permitir cambio de email, rol, estado
   - Tracking de cambios

3. 🔄 **Cambio de Rol**
   - Selector de rol con preview de permisos
   - Confirmación de cambio
   - Notificación al usuario afectado

4. 🔒 **Reset de Contraseña**
   - Generación automática segura
   - Envío por email (opcional)
   - Log de reset

### Mejoras Futuras

- 📊 Dashboard de estadísticas de logs
- 📧 Notificaciones por email de cambios
- 🔍 Búsqueda avanzada en logs
- 📥 Exportar logs a CSV/Excel
- 📱 Notificaciones push a usuarios afectados

---

## 📚 Documentación Relacionada

- [FLUJO_SUCURSALES_Y_ROLES.md](FLUJO_SUCURSALES_Y_ROLES.md) - Sistema de roles y permisos
- [IMPLEMENTACION_ELIMINACION_LOGICA.md](IMPLEMENTACION_ELIMINACION_LOGICA.md) - Eliminación lógica
- [UsuariosPageModerna.py](../features/admin/presentation/pages/vistas/UsuariosPageModerna.py) - Código fuente

---

**Fecha de Implementación**: 2 de Febrero, 2026  
**Versión**: 1.0.0  
**Estado**: ✅ Funcional con logs de auditoría  
**Autor**: GitHub Copilot
