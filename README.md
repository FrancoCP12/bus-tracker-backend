# 🚌 Bus Tracker Backend

Sistema de seguimiento de autobuses en tiempo real con FastAPI, PostgreSQL/PostGIS y Redis.

---

## 📁 Estructura del Proyecto

```
bus-tracker-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Punto de entrada FastAPI
│   ├── api/                    # Endpoints REST y WebSockets
│   │   ├── __init__.py
│   │   ├── buses.py            # CRUD autobuses
│   │   ├── locations.py        # Búsqueda por ubicación
│   │   ├── realtime.py         # WebSockets GPS
│   │   └── route.py           # Carga GeoJSON
│   ├── core/                   # Configuración central
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── security.py
│   ├── db/                     # Conexión PostgreSQL
│   │   ├── __init__.py
│   │   └── base.py
│   ├── models/                 # Modelos SQLAlchemy
│   │   ├── __init__.py
│   │   ├── bus.py
│   │   ├── bus_stop.py
│   │   ├── route.py
│   │   └── user.py
│   ├── schemas/                # Esquemas Pydantic
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── bus.py
│   │   ├── location.py
│   │   └── user.py
│   └── services/               # Lógica de negocio
│       ├── __init__.py
│       ├── eta_service.py
│       ├── location_service.py
│       └── route_service.py
├── alembic/                    # Migraciones DB
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── alembic.ini
├── compose.yaml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología |
|------------|------------|
| Framework | FastAPI (Python 3.11+) |
| Base de Datos | PostgreSQL + PostGIS |
| Cache/Mensajería | Redis |
| ORM | SQLAlchemy 2.0 |
| Migraciones | Alembic |
| Validación | Pydantic |
| Contenedores | Docker |

---

## 🚀 Instalación

### Con Docker (Recomendado)

```bash
docker compose up --build
```

### Manual

```bash
# 1. Crear .env
DATABASE_URL=postgresql://user:pass@localhost:5432/bustracker
HOST_REDIS=localhost
PORT_REDIS=6379

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Migraciones
alembic upgrade head

# 4. Ejecutar
uvicorn app.main:app --reload
```

**Acceso:** `http://localhost:8000`  
**Swagger:** `http://localhost:8000/docs`  
**ReDoc:** `http://localhost:8000/redoc`

---

## 📊 Modelos de Datos

### Bus
```
┌────────────┬─────────────────┬─────────────────────────────────┐
│ Campo      │ Tipo            │ Descripción                     │
├────────────┼─────────────────┼─────────────────────────────────┤
│ id_bus     │ INT (PK)        │ Identificador único             │
│ id_route   │ INT (FK)        │ Ruta asignada                   │
│ patent     │ VARCHAR(7)      │ Patente única del vehículo      │
│ identifier │ VARCHAR(10)     │ Identificador público           │
│ company    │ VARCHAR(10)     │ Empresa propietaria             │
│ is_active  │ BOOLEAN         │ Estado activo/inactivo          │
└────────────┴─────────────────┴─────────────────────────────────┘
```

### Route
```
┌────────────┬─────────────────┬─────────────────────────────────┐
│ Campo      │ Tipo            │ Descripción                     │
├────────────┼─────────────────┼─────────────────────────────────┤
│ id_route   │ INT (PK)        │ Identificador único             │
│ position   │ GEOMETRY        │ Línea de ruta (PostGIS)         │
│            │ (LINESTRING)    │ SRID: 4326                      │
└────────────┴─────────────────┴─────────────────────────────────┘
```

### BusStop
```
┌────────────┬─────────────────┬─────────────────────────────────┐
│ Campo      │ Tipo            │ Descripción                     │
├────────────┼─────────────────┼─────────────────────────────────┤
│ id_bus_stop│ INT (PK)        │ Identificador único             │
│ id_route   │ INT (FK)        │ Ruta asociada                   │
│ position   │ GEOMETRY        │ Ubicación (POINT)              │
│            │ (POINT)         │ SRID: 4326                      │
└────────────┴─────────────────┴─────────────────────────────────┘
```

**Relación:** Route ←→ BusStop (muchos a muchos)

---

## 🌐 API Endpoints

### Buses (CRUD)

| Método | Ruta | Descripción | Filtros |
|--------|------|-------------|---------|
| `GET` | `/buses/` | Listar todos | `?id=`, `?patent=`, `?identifier=`, `?company=`, `?is_active=` |
| `POST` | `/buses/` | Crear autobús | Body: `{patent, identifier, company, is_active}` |
| `PATCH` | `/buses/{id}` | Actualizar | Body (parcial): campos a modificar |

**Ejemplo POST:**
```json
{
  "patent": "AB123CD",
  "identifier": "BUS-001",
  "company": "EMPRESA1",
  "is_active": true
}
```

### Rutas

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/geojson/` | Cargar ruta desde GeoJSON |
| `GET` | `/busStop/{lat}/{lon}` | Paradas cercanas a coordenadas |

### Ubicación

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/loadBus/` | Buscar rutas entre dos puntos |

**Parámetros:**
- `lat_origen`, `lon_origen` - Coordenadas de origen
- `lat_destiny`, `lon_destiny` - Coordenadas de destino

---

## 📡 WebSockets (Tiempo Real)

### Recibir GPS del autobús
```
WS /buses/{id}/location/
```
**Payload esperado:**
```json
{
  "id": "bus123",
  "company": "empresa1",
  "coord": [-58.1234, -34.5678]
}
```

### Suscribirse a actualizaciones
```
WS /buses/connect/{id}/{company}
```
**Respuesta:**
```json
{
  "type": "update",
  "buses": {
    "id": "bus123",
    "company": "empresa1",
    "coord": [-58.1234, -34.5678],
    "timestamp": 1710000000
  }
}
```

---

## ⚙️ Configuración

| Variable | Descripción | Default |
|----------|-------------|---------|
| `DATABASE_URL` | URL PostgreSQL | `postgresql://user:pass@localhost:5432/bustracker` |
| `HOST_REDIS` | Host Redis | `localhost` |
| `PORT_REDIS` | Puerto Redis | `6379` |

---

## 🔧 Comandos Útiles

```bash
# Migraciones
alembic revision --autogenerate -m "descripcion"
alembic upgrade head
alembic downgrade -1

# Servidor desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Docker
docker compose up --build
docker compose down
docker compose logs -f
```

---

## 📋 Convenciones de Código

- **Nomenclatura:** `snake_case` para variables/funciones, `PascalCase` para clases
- **Imports:** stdlib → third-party → local (ordenados alfabéticamente)
- **Tipado:** Anotaciones de tipo en todas las funciones públicas
- **Docstrings:** Google style para funciones públicas
