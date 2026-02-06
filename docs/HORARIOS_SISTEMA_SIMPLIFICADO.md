# 📅 Sistema de Horarios Simplificado

## Conceptos Claros:

### 1. **Horarios** (Lo real)
- Son los horarios reales asignados a cada usuario
- Cada usuario puede tener múltiples horarios (uno por día de la semana)
- Se crean por:
  - Creación individual
  - Aplicando una plantilla

### 2. **Plantillas** (Reutilizable)
- Son "horarios modelo" que se reutilizan
- Contienen: Nombre, Descripción, Hora inicio, Hora fin, Días
- Ejemplos: "Turno Mañana", "Turno Tarde", "Jornada Completa"
- Se pueden aplicar a varios usuarios a la vez

---

## 📋 FLUJO DE USO:

### Crear un Horario Individual:
1. Click en "➕ Nuevo Horario"
2. Seleccionar usuario
3. Elegir día y horas
4. Guardar

### Crear una Plantilla:
1. Click en "📦 Nueva Plantilla"
2. Llenar: Nombre, Descripción, Horas, Días
3. Guardar

### Aplicar Plantilla a Usuario:
1. Click en "🔄 Aplicar Plantilla"
2. Seleccionar usuario
3. Seleccionar plantilla
4. Confirmar días (si es necesario)
5. Aplicar

---

## 🎨 INTERFAZ PROPUESTA:

### Header:
```
📅 Gestión de Horarios | Usuarios: 5 | Plantillas: 4 | Horarios: 23
```

### 3 Botones Principales:
- ➕ Nuevo Horario (BLUE)
- 📦 Nueva Plantilla (AMBER) 
- 🔄 Aplicar Plantilla (TEAL)

### DataTable Principal:
Mostrar HORARIOS asignados (filtrable por usuario/día)

### Sidebar Secundario (OPCIONAL):
Mostrar plantillas disponibles

---

## 🗄️ BASE DE DATOS:

### HORARIOS (tabla)
- ID
- USUARIO_ID
- DIA_SEMANA
- HORA_INICIO
- HORA_FIN
- ACTIVO

### PLANTILLAS (tabla)
- ID
- NOMBRE
- DESCRIPCION
- HORA_INICIO
- HORA_FIN
- DIAS (JSON list)
- CREADO_POR
- FECHA_CREACION
- ACTIVO

---

## ✅ FUNCIONALIDAD ESPERADA:

- [x] Ver todos los horarios asignados
- [x] Crear horario individual
- [x] Editar horario
- [x] Eliminar horario
- [x] Crear plantilla
- [x] Aplicar plantilla a usuario
- [x] Ver detalles de plantilla
- [x] Filtros (usuario, día, estado)
- [ ] Validar cruces de horarios
- [ ] Reportes de horarios

---

## 🎯 PRIORIDADES:

1. **CRÍTICO**: Que funcione crear horario individual
2. **CRÍTICO**: Que funcione crear plantilla
3. **CRÍTICO**: Que funcione aplicar plantilla
4. **IMPORTANTE**: Validaciones de datos
5. **NICE**: Reportes y estadísticas
