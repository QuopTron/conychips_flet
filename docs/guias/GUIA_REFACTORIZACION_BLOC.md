# Guía de Refactorización: BLoC Pattern + Arquitectura Hexagonal

## ✅ Refactorización Completada: Módulo Admin

### 📁 Nueva Estructura del Módulo Admin

```
features/admin/
├── data/                                    # Capa de Datos
│   ├── datasources/
│   │   └── FuenteAdminLocal.py             # Acceso directo a BD
│   └── RepositorioAdminImpl.py             # Implementación del repositorio
│
├── domain/                                  # Capa de Dominio (Lógica de Negocio)
│   ├── entities/
│   │   ├── EstadisticasDashboard.py        # Entidades del dominio
│   │   └── __init__.py
│   ├── usecases/
│   │   ├── CargarEstadisticasDashboard.py  # Casos de uso
│   │   ├── ActualizarRolUsuario.py
│   │   ├── ObtenerRolesDisponibles.py
│   │   └── __init__.py
│   └── RepositorioAdmin.py                 # Interface (contrato)
│
└── presentation/                            # Capa de Presentación
    ├── bloc/
    │   ├── AdminBloc.py                    # Gestor de estado
    │   ├── AdminEstado.py                  # Estados posibles
    │   ├── AdminEvento.py                  # Eventos del usuario
    │   └── __init__.py
    ├── pages/
    │   └── PaginaAdmin.py                  # Vista refactorizada
    └── widgets/
        ├── CardEstadistica.py              # Widgets reutilizables
        ├── GraficoRoles.py
        ├── GraficoSucursales.py
        ├── GraficoSemanal.py
        ├── GraficoInventario.py
        └── __init__.py
```

---

## 🎯 Cambios Principales en PaginaAdmin.py

### **Antes (Código Acoplado):**

```python
# ❌ Lógica mezclada con presentación
async def _OBTENER_STATS(self):
    sesion = OBTENER_SESION()  # Acceso directo a BD
    hoy = datetime.utcnow().date()
    TOTAL_USUARIOS = sesion.query(MODELO_USUARIO).count()
    # ... más código de BD en la vista
    self._STATS_USUARIOS.content.controls[1].value = str(TOTAL_USUARIOS)
```

### **Después (Arquitectura Limpia):**

```python
# ✅ Vista solo renderiza basada en estado del BLoC
def _ON_ESTADO_CAMBIO(self, estado: AdminEstado):
    if isinstance(estado, AdminCargado):
        self._ACTUALIZAR_UI_CON_DATOS(estado.dashboard)

# El BLoC maneja la lógica
ADMIN_BLOC.AGREGAR_EVENTO(CargarDashboard())
```

---

## 🔄 Flujo de Datos (Arquitectura Hexagonal)

```
┌─────────────┐
│   Usuario   │  Interactúa con la UI
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│  PRESENTATION LAYER (UI)                    │
│  - PaginaAdmin.py (Vista reactiva)          │
│  - Widgets reutilizables                    │
└──────┬──────────────────────────────────────┘
       │
       │ Dispara Evento
       ▼
┌─────────────────────────────────────────────┐
│  PRESENTATION LOGIC (BLoC)                  │
│  - AdminBloc.py                             │
│  - AdminEstado.py (estados)                 │
│  - AdminEvento.py (eventos)                 │
└──────┬──────────────────────────────────────┘
       │
       │ Llama Casos de Uso
       ▼
┌─────────────────────────────────────────────┐
│  DOMAIN LAYER (Lógica de Negocio)          │
│  - CargarEstadisticasDashboard              │
│  - ActualizarRolUsuario                     │
│  - Entidades del dominio                    │
└──────┬──────────────────────────────────────┘
       │
       │ Usa Repositorio (Interface)
       ▼
┌─────────────────────────────────────────────┐
│  DATA LAYER (Acceso a Datos)               │
│  - RepositorioAdminImpl                     │
│  - FuenteAdminLocal (PostgreSQL)            │
└─────────────────────────────────────────────┘
```

---

## 📋 Pasos para Aplicar a Otros Módulos

### **1. Crear Entidades del Dominio**

```python
# features/[modulo]/domain/entities/[Entidad].py
from dataclasses import dataclass

@dataclass
class MiEntidad:
    id: int
    nombre: str
    # ... campos relevantes
```

### **2. Crear Interface del Repositorio**

```python
# features/[modulo]/domain/Repositorio[Modulo].py
from abc import ABC, abstractmethod

class Repositorio[Modulo](ABC):
    @abstractmethod
    def OBTENER_DATOS(self):
        pass
```

### **3. Crear Casos de Uso**

```python
# features/[modulo]/domain/usecases/[CasoDeUso].py
class [CasoDeUso]:
    def __init__(self, repositorio):
        self._repositorio = repositorio

    def EJECUTAR(self, parametros):
        # Lógica de negocio
        return self._repositorio.OBTENER_DATOS()
```

### **4. Implementar Repositorio**

```python
# features/[modulo]/data/Repositorio[Modulo]Impl.py
class Repositorio[Modulo]Impl(Repositorio[Modulo]):
    def __init__(self):
        self._fuente_local = Fuente[Modulo]Local()

    def OBTENER_DATOS(self):
        return self._fuente_local.CONSULTAR_BD()
```

### **5. Crear Fuente de Datos Local**

```python
# features/[modulo]/data/datasources/Fuente[Modulo]Local.py
class Fuente[Modulo]Local:
    def CONSULTAR_BD(self):
        sesion = OBTENER_SESION()
        try:
            return sesion.query(MODELO).all()
        finally:
            sesion.close()
```

### **6. Crear Estados del BLoC**

```python
# features/[modulo]/presentation/bloc/[Modulo]Estado.py
from dataclasses import dataclass

@dataclass
class [Modulo]Estado:
    pass

@dataclass
class [Modulo]Inicial([Modulo]Estado):
    pass

@dataclass
class [Modulo]Cargando([Modulo]Estado):
    pass

@dataclass
class [Modulo]Cargado([Modulo]Estado):
    datos: MiEntidad
```

### **7. Crear Eventos del BLoC**

```python
# features/[modulo]/presentation/bloc/[Modulo]Evento.py
from dataclasses import dataclass

@dataclass
class [Modulo]Evento:
    pass

@dataclass
class CargarDatos([Modulo]Evento):
    pass
```

### **8. Crear BLoC**

```python
# features/[modulo]/presentation/bloc/[Modulo]Bloc.py
import asyncio

class [Modulo]Bloc:
    def __init__(self):
        self._estado = [Modulo]Inicial()
        self._listeners = []
        self._caso_uso = CasoDeUso(REPOSITORIO_IMPL)

    def AGREGAR_EVENTO(self, evento):
        if isinstance(evento, CargarDatos):
            self._MANEJAR_CARGAR()

    async def _MANEJAR_CARGAR(self):
        self._CAMBIAR_ESTADO([Modulo]Cargando())
        datos = self._caso_uso.EJECUTAR()
        self._CAMBIAR_ESTADO([Modulo]Cargado(datos=datos))
```

### **9. Crear Widgets Reutilizables**

```python
# features/[modulo]/presentation/widgets/MiWidget.py
import flet as ft

class MiWidget(ft.Container):
    def __init__(self, datos):
        super().__init__()
        self.ACTUALIZAR_DATOS(datos)

    def ACTUALIZAR_DATOS(self, datos):
        # Renderizar UI
        pass
```

### **10. Refactorizar la Página**

```python
# features/[modulo]/presentation/pages/Pagina[Modulo].py
from ..bloc import BLOC, Evento, Estado

class Pagina[Modulo](ft.Column):
    def __init__(self, PAGINA, USUARIO):
        super().__init__()
        self._PAGINA = PAGINA

        # Widgets
        self._widget = MiWidget()

        # Suscribir al BLoC
        BLOC.AGREGAR_LISTENER(self._ON_ESTADO_CAMBIO)

        # Cargar datos
        BLOC.AGREGAR_EVENTO(CargarDatos())

    def _ON_ESTADO_CAMBIO(self, estado):
        if isinstance(estado, EstadoCargado):
            self._widget.ACTUALIZAR_DATOS(estado.datos)
            self.update()
```

---

## 🎨 Principios Aplicados

### **1. Separación de Responsabilidades (SRP)**

- Cada clase tiene una única responsabilidad
- Vista solo renderiza
- BLoC solo gestiona estado
- Caso de uso solo ejecuta lógica de negocio
- Repositorio solo accede a datos

### **2. Inversión de Dependencias (DIP)**

- Domain no depende de Data
- Se usan interfaces (contratos)
- Inyección de dependencias

### **3. Don't Repeat Yourself (DRY)**

- Widgets reutilizables
- Factory methods para botones
- Casos de uso compartidos

### **4. Open/Closed Principle (OCP)**

- Fácil agregar nuevos estados sin modificar el BLoC
- Fácil agregar nuevos eventos

### **5. Arquitectura Hexagonal**

- Core (Domain) independiente de infraestructura
- Puertos (Interfaces) y Adaptadores (Implementaciones)
- Fácil testear cada capa por separado

---

## 🚀 Módulos Pendientes de Refactorizar

Aplica la misma estructura a:

1. **features/pedidos/** (Alta prioridad)
2. **features/productos/** (Alta prioridad)
3. **features/atencion/**
4. **features/cliente/**
5. **features/cocina/**
6. **features/motorizado/**
7. **features/limpieza/**

---

## 📊 Beneficios Obtenidos

✅ **Código más limpio y mantenible**
✅ **Fácil de testear** (cada capa independiente)
✅ **Reutilización** de widgets y lógica
✅ **Escalabilidad** (fácil agregar funcionalidades)
✅ **Separación clara** entre UI, lógica y datos
✅ **State management reactivo** con BLoC
✅ **Código autodocumentado** con tipos y dataclasses

---

## 🔍 Ejemplo de Uso del BLoC

```python
# En la vista
ADMIN_BLOC.AGREGAR_EVENTO(CargarDashboard())

# El BLoC procesa
def AGREGAR_EVENTO(self, evento):
    if isinstance(evento, CargarDashboard):
        self._MANEJAR_CARGAR_DASHBOARD()

# Ejecuta caso de uso
async def _MANEJAR_CARGAR_DASHBOARD(self):
    self._CAMBIAR_ESTADO(AdminCargando())
    dashboard = self._cargar_estadisticas.EJECUTAR()
    self._CAMBIAR_ESTADO(AdminCargado(dashboard=dashboard))

# Notifica a la vista
def _CAMBIAR_ESTADO(self, nuevo_estado):
    self._estado = nuevo_estado
    self._NOTIFICAR_LISTENERS()

# La vista reacciona
def _ON_ESTADO_CAMBIO(self, estado):
    if isinstance(estado, AdminCargado):
        self._ACTUALIZAR_UI_CON_DATOS(estado.dashboard)
```

---

## 📚 Recursos y Referencias

- **Clean Architecture:** Robert C. Martin
- **BLoC Pattern:** Felix Angelov (bloc.dev)
- **Hexagonal Architecture:** Alistair Cockburn
- **SOLID Principles:** Robert C. Martin

---

**Autor:** Refactorización del módulo Admin
**Fecha:** 2026-01-25
**Versión:** 1.0
