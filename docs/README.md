# 📚 Documentación - Cony Chips

## 📖 Documentación Principal

### Arquitectura y Sistema

- **[ARQUITECTURA_SEGURIDAD.md](ARQUITECTURA_SEGURIDAD.md)** - Arquitectura completa del sistema de seguridad con JWT RS256, PostgreSQL y Redis
- **[SISTEMA_COMPLETO.md](SISTEMA_COMPLETO.md)** - Guía completa del sistema instalado y cómo ejecutarlo
- **[FLUJO_APLICACION.md](FLUJO_APLICACION.md)** - Flujo completo de la aplicación y navegación entre módulos
- **[CHANGELOG.md](CHANGELOG.md)** - Historial de cambios y versiones del sistema

## 📘 Guías de Usuario y Desarrollo

- **[guias/GUIA_REFACTORIZACION_BLOC.md](guias/GUIA_REFACTORIZACION_BLOC.md)** - Guía completa del patrón BLoC y arquitectura hexagonal
- **[guias/GUIA_RAPIDA_ADMIN.md](guias/GUIA_RAPIDA_ADMIN.md)** - Guía rápida de uso del panel de administración
- **[guias/NUEVAS_FUNCIONALIDADES.md](guias/NUEVAS_FUNCIONALIDADES.md)** - Documentación de funcionalidades recientes
- **[guias/SISTEMA_CONFIGURACION.md](guias/SISTEMA_CONFIGURACION.md)** - Sistema de configuración dinámica
- **[guias/VERIFICACION_SISTEMA.md](guias/VERIFICACION_SISTEMA.md)** - Guía de verificación del sistema

## 🏗️ Arquitectura del Proyecto

El proyecto sigue una arquitectura hexagonal (Clean Architecture) con patrón BLoC:

```
features/
├── autenticacion/     # Módulo de autenticación JWT
├── admin/             # Panel de administración
│   ├── domain/        # Entidades y casos de uso
│   ├── data/          # Repositorios y fuentes de datos
│   └── presentation/  # BLoCs, widgets y páginas
├── pedidos/           # Gestión de pedidos
├── finanzas/          # Módulo financiero
└── ...
```

## 🔑 Características Principales

### Seguridad
- JWT RS256 con claves asimétricas de 4096 bits
- Sistema de tokens de dos capas (App Token + Access Token)
- Refresh tokens con renovación automática
- Blacklist de tokens en Redis

### Base de Datos
- PostgreSQL 16+ con connection pooling
- Redis para cache y sesiones
- SQLAlchemy 2.0 con soporte thread-safe

### Frontend
- Flet framework para UI multiplataforma
- Patrón BLoC para gestión de estado
- Componentes reutilizables

## 🚀 Inicio Rápido

Ver [SISTEMA_COMPLETO.md](SISTEMA_COMPLETO.md) para instrucciones de instalación y ejecución.

## 📝 Convenciones de Código

- **Nombres de clases**: PascalCase (ej: `UsuariosBloc`)
- **Nombres de funciones**: SNAKE_CASE_MAYÚSCULAS (ej: `CARGAR_USUARIOS`)
- **Constantes**: MAYÚSCULAS (ej: `MODELO_USUARIO`)
- **Variables privadas**: Prefijo `_` (ej: `_estado_actual`)

## 🤝 Contribución

1. Seguir la arquitectura hexagonal existente
2. Usar el patrón BLoC para nuevas features
3. Mantener separación de responsabilidades (domain/data/presentation)
4. Escribir documentación para nuevas funcionalidades

---

**Última actualización**: Enero 2026  
**Versión**: 2.0.0
