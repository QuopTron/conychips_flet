# Arquitectura de Seguridad - Cony Chips

## Índice

1. [Stack Tecnológico](#stack-tecnológico)
2. [Sistema de Tokens JWT](#sistema-de-tokens-jwt)
3. [Arquitectura de Dos Capas](#arquitectura-de-dos-capas)
4. [Flujos de Autenticación](#flujos-de-autenticación)
5. [Gestión de Sesiones con Redis](#gestión-de-sesiones-con-redis)
6. [Base de Datos PostgreSQL](#base-de-datos-postgresql)
7. [Configuración](#configuración)

---

## Stack Tecnológico

### Backend

- **PostgreSQL 16+**: Base de datos relacional con connection pooling
- **Redis 7+**: Cache, sesiones, blacklist de tokens
- **SQLAlchemy 2.0**: ORM con soporte async
- **Cryptography**: Generación y manejo de claves RSA

### Seguridad

- **JWT RS256**: Tokens con firma asimétrica (4096-bit RSA)
- **PyJWT**: Librería para manejo de tokens
- **Argon2**: Hash de contraseñas (via PassLib)

### Frontend

- **Flet**: UI multiplataforma
- **WebSockets**: Notificaciones en tiempo real

---

## Sistema de Tokens JWT

### Algoritmo: RS256 (Firma Asimétrica)

```
┌─────────────────┐         ┌─────────────────┐
│  Clave Privada  │────────▶│  Firma Token    │
│  (4096-bit RSA) │         │  (Solo Server)  │
└─────────────────┘         └─────────────────┘
                                      │
                                      ▼
┌─────────────────┐         ┌─────────────────┐
│  Clave Pública  │────────▶│ Verifica Token  │
│  (Cualquiera)   │         │ (Server/Client) │
└─────────────────┘         └─────────────────┘
```

**Ventajas de RS256 vs HS256:**

- ✅ Clave privada nunca sale del servidor
- ✅ Clave pública puede distribuirse
- ✅ Tokens no se pueden falsificar sin clave privada
- ✅ Permite verificación distribuida

### Tipos de Tokens

#### 1. Token de Aplicación (App Token)

**Duración:** 30 días  
**Propósito:** Identificar dispositivo/instalación  
**Sobrevive:** Cierre de sesión de usuario

```json
{
    "tipo": "app",
    "dispositivo_id": "uuid-del-dispositivo",
    "metadata": {
        "plataforma": "linux",
        "version_app": "1.0.0"
    },
    "jti": "uuid-token-único",
    "exp": 1234567890,
    "iat": 1234567890,
    "nbf": 1234567890,
    "iss": "conychips-api",
    "aud": "conychips-app"
}
```

#### 2. Token de Acceso (Access Token)

**Duración:** 15 minutos  
**Propósito:** Autenticación de usuario  
**Contiene:** Roles, permisos, datos de usuario

```json
{
    "tipo": "access",
    "usuario_id": 123,
    "email": "usuario@ejemplo.com",
    "roles": ["cajero", "admin"],
    "permisos": ["ver_productos", "crear_pedidos"],
    "app_token_id": "jti-del-app-token",
    "jti": "uuid-token-único",
    "exp": 1234567890,
    "iat": 1234567890,
    "nbf": 1234567890,
    "iss": "conychips-api",
    "aud": "conychips-app"
}
```

#### 3. Token de Refresco (Refresh Token)

**Duración:** 7 días  
**Propósito:** Renovar access token sin re-autenticación

```json
{
    "tipo": "refresh",
    "usuario_id": 123,
    "app_token_id": "jti-del-app-token",
    "jti": "uuid-token-único",
    "exp": 1234567890,
    "iat": 1234567890,
    "nbf": 1234567890,
    "iss": "conychips-api",
    "aud": "conychips-app"
}
```

---

## Arquitectura de Dos Capas

### Capa 1: Aplicación (Dispositivo)

```
Instalación de App
        │
        ▼
App Token (30 días) ─────┐
        │                │
        │                │ Persiste
        ▼                │
Usuario Inicia Sesión    │
        │                │
        ▼                │
Access + Refresh Token   │
        │                │
        ▼                │
Usuario Cierra Sesión    │
        │                │
        ▼                │
Tokens de Usuario        │
Revocados                │
        │                │
        ▼                │
App Token ───────────────┘
Sigue Válido
```

### Capa 2: Usuario (Sesión)

```
Login Exitoso
        │
        ▼
┌───────────────────┐
│  Access Token     │ ◀─── Usado en cada request
│  (15 minutos)     │      Bearer eyJhbGc...
└───────────────────┘
        │
        │ Expira
        ▼
┌───────────────────┐
│  Refresh Token    │ ◀─── Renovar sin login
│  (7 días)         │      POST /auth/refresh
└───────────────────┘
        │
        │ Renueva
        ▼
Nuevos Access + Refresh Tokens
```

---

## Flujos de Autenticación

### Flujo 1: Primera Instalación

```mermaid
sequenceDiagram
    participant App
    participant API
    participant Redis
    participant DB

    App->>API: POST /app/register {dispositivo_info}
    API->>API: Generar App Token (30d)
    API->>Redis: Guardar metadata dispositivo
    API-->>App: {app_token}
    App->>App: Guardar en LocalStorage
```

### Flujo 2: Login de Usuario

```mermaid
sequenceDiagram
    participant App
    participant API
    participant Redis
    participant DB

    App->>API: POST /auth/login {email, password, app_token}
    API->>API: Verificar App Token
    API->>DB: Validar credenciales
    API->>API: Generar Access Token (15m)
    API->>API: Generar Refresh Token (7d)
    API->>Redis: Guardar sesión
    API-->>App: {access_token, refresh_token}
    App->>App: Guardar en memoria/cookie segura
```

### Flujo 3: Request Autenticado

```mermaid
sequenceDiagram
    participant App
    participant API
    participant Redis

    App->>API: GET /pedidos (Header: Bearer access_token)
    API->>API: Verificar firma RS256
    API->>Redis: ¿Token en blacklist?
    Redis-->>API: No
    API->>API: Extraer usuario_id, roles, permisos
    API-->>App: {pedidos}
```

### Flujo 4: Renovación de Token

```mermaid
sequenceDiagram
    participant App
    participant API
    participant Redis

    App->>API: POST /auth/refresh {refresh_token}
    API->>API: Verificar Refresh Token
    API->>Redis: ¿Token en blacklist?
    Redis-->>API: No
    API->>Redis: Revocar tokens anteriores
    API->>API: Generar nuevos Access + Refresh
    API->>Redis: Guardar nueva sesión
    API-->>App: {access_token, refresh_token}
```

### Flujo 5: Logout de Usuario

```mermaid
sequenceDiagram
    participant App
    participant API
    participant Redis

    App->>API: POST /auth/logout {access_token}
    API->>Redis: Agregar JTI a blacklist
    API->>Redis: Eliminar sesión de usuario
    API->>Redis: Mantener App Token válido
    API-->>App: {success: true}
    Note over App: App Token sigue válido
    Note over App: Usuario puede hacer login de nuevo
```

---

## Gestión de Sesiones con Redis

### Estructura de Keys

```
session:usuario:123:jti-access-token  → datos de sesión
cache:productos:lista                 → cache de datos
blacklist:jti-token-revocado          → tokens revocados
```

### Sesiones de Usuario

```python
# Guardar sesión en Redis
{
    "usuario_id": 123,
    "email": "usuario@ejemplo.com",
    "roles": ["cajero"],
    "ultima_actividad": "2024-01-15T10:30:00",
    "ip": "192.168.1.100",
    "dispositivo_id": "uuid-dispositivo"
}
# TTL: 7 días (duración del refresh token)
```

### Blacklist de Tokens

```python
# Al revocar un token
blacklist:jti-abc123 → "revocado"
# TTL: tiempo restante hasta expiración original
```

### Cache de Aplicación

```python
# Cache de productos
cache:productos:lista → [...productos]
# TTL: 1 hora

# Cache de configuración
cache:config:general → {...config}
# TTL: 24 horas
```

---

## Base de Datos PostgreSQL

### Connection Pooling

```python
pool_size = 20          # Conexiones base
max_overflow = 40       # Conexiones adicionales
pool_recycle = 3600     # Reciclar cada hora
pool_pre_ping = True    # Verificar conexión antes de usar
```

### Configuración Óptima

```sql
-- postgresql.conf
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 10MB
maintenance_work_mem = 64MB
```

### Índices Críticos

```sql
-- Usuarios
CREATE INDEX idx_usuarios_email ON usuarios(email);
CREATE INDEX idx_usuarios_activo ON usuarios(activo);

-- Pedidos
CREATE INDEX idx_pedidos_fecha ON pedidos(fecha_creacion);
CREATE INDEX idx_pedidos_estado ON pedidos(estado);
CREATE INDEX idx_pedidos_usuario ON pedidos(usuario_id);

-- Sesiones
CREATE INDEX idx_sesiones_usuario ON sesiones_activas(usuario_id);
CREATE INDEX idx_sesiones_token ON sesiones_activas(jti);
```

---

## Configuración

### Archivo .env

```bash
# Base de datos
DATABASE_URL=postgresql://conychips_user:password@localhost:5432/conychips_db
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
DB_POOL_TIMEOUT=30

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=50
REDIS_DECODE_RESPONSES=True

# JWT
JWT_ALGORITHM=RS256
JWT_PRIVATE_KEY_PATH=config/keys/jwt_private.pem
JWT_PUBLIC_KEY_PATH=config/keys/jwt_public.pem
JWT_ACCESS_TOKEN_EXPIRES=900      # 15 minutos
JWT_REFRESH_TOKEN_EXPIRES=604800  # 7 días
JWT_APP_TOKEN_EXPIRES=2592000     # 30 días
JWT_ISSUER=conychips-api
JWT_AUDIENCE=conychips-app

# Seguridad
SECRET_KEY=tu-clave-secreta-aquí
HASH_ALGORITHM=argon2
BCRYPT_ROUNDS=12

# WebSocket
WS_SERVER_URL=ws://localhost:8765
WS_RECONNECT_DELAY=5
WS_MAX_RETRIES=10
```

### Generación de Claves RSA

```bash
# Ejecutar el script
python generar_claves_jwt.py

# O manualmente con openssl
openssl genrsa -out config/keys/jwt_private.pem 4096
openssl rsa -in config/keys/jwt_private.pem -pubout -out config/keys/jwt_public.pem
chmod 600 config/keys/jwt_private.pem
chmod 644 config/keys/jwt_public.pem
```

---

## Seguridad Adicional

### Cookies Seguras (Futuro)

```python
# HttpOnly: No accesible desde JavaScript
# Secure: Solo HTTPS
# SameSite=Lax: Protección CSRF

response.set_cookie(
    "access_token",
    value=token,
    httponly=True,
    secure=True,
    samesite="lax",
    max_age=900
)
```

### Rate Limiting (Futuro)

```python
# Con Redis
@rate_limit(max_requests=100, window=60)  # 100 requests/minuto
def ENDPOINT_PROTEGIDO():
    pass
```

### Validaciones Obligatorias

```python
# Cada request debe validar:
1. Firma del token (RS256)
2. Expiración (exp)
3. Not Before (nbf)
4. Issued At (iat)
5. Issuer (iss)
6. Audience (aud)
7. Blacklist (Redis)
8. Tipo de token correcto
```

---

## Monitoreo

### Métricas Clave

```python
# Redis
- Sesiones activas: COUNT session:*
- Tokens en blacklist: COUNT blacklist:*
- Hit rate de cache: INFO stats

# PostgreSQL
- Conexiones activas: SELECT count(*) FROM pg_stat_activity
- Queries lentas: pg_stat_statements
- Tamaño de tablas: pg_total_relation_size

# Aplicación
- Tokens generados/hora
- Tokens revocados/hora
- Fallos de autenticación/hora
- Tiempo de respuesta promedio
```

---

## Migraciones

### De SQLite a PostgreSQL

```bash
# 1. Backup SQLite
sqlite3 sistema.db .dump > backup.sql

# 2. Migrar estructura
python migrar_nuevas_tablas.py

# 3. Migrar datos (si es necesario)
# Script personalizado dependiendo de los datos
```

---

## Troubleshooting

### PostgreSQL no conecta

```bash
# Verificar servicio
sudo systemctl status postgresql
sudo systemctl start postgresql

# Verificar puerto
sudo netstat -plnt | grep 5432

# Logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

### Redis no responde

```bash
# Verificar servicio
sudo systemctl status redis
sudo systemctl start redis

# Test de conexión
redis-cli ping

# Logs
sudo tail -f /var/log/redis/redis-server.log
```

### Tokens inválidos

```bash
# Verificar claves RSA
ls -la config/keys/

# Regenerar claves
python generar_claves_jwt.py

# Limpiar blacklist
redis-cli FLUSHDB
```

---

## Referencias

- [JWT Best Practices](https://datatracker.ietf.org/doc/html/rfc8725)
- [RS256 vs HS256](https://auth0.com/blog/rs256-vs-hs256-whats-the-difference/)
- [PostgreSQL Connection Pooling](https://www.postgresql.org/docs/current/runtime-config-connection.html)
- [Redis Best Practices](https://redis.io/docs/management/optimization/)
