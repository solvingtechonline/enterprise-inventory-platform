# Lite Thinking 2026: Gestión de Empresas, Productos e Inventario

## 1. Nombre del proyecto

**Lite Thinking 2026**: Prueba técnica para Desarrollador Python / Django / React.

## 2. Descripción general

El sistema permite gestionar **Empresas** y los **Productos** asociados a cada una, controlar el **Inventario** de esos productos por empresa, y generar/enviar por correo un **reporte en PDF** del inventario. Tiene dos roles de usuario: un **Administrador** con control total sobre el sistema, y un usuario **Externo** que solo puede consultar el listado de empresas, sin necesidad de iniciar sesión.

El objetivo de la prueba técnica era evaluar, más allá de la funcionalidad, la capacidad de diseñar una solución con **separación real de responsabilidades**: una capa de dominio desacoplada de los frameworks web, dos backends con responsabilidades distintas comunicándose entre sí, y un frontend organizado bajo un sistema de diseño consistente (Atomic Design).

El problema que resuelve es el de una pequeña organización que necesita centralizar el catálogo de empresas cliente/proveedoras, sus productos con precios en distintas monedas, y llevar un control simple de existencias por empresa, con la posibilidad de compartir ese inventario en PDF por correo.

## 3. Tecnologías utilizadas

### Backend
- **Django 6 + Django REST Framework**: capa de aplicación para Empresa, Productos, Login y autenticación. Se eligió por su ORM maduro, su sistema de permisos y por ser una de las tecnologías exigidas por la prueba.
- **djangorestframework-simplejwt**: emisión y validación de tokens JWT con claims personalizados (rol, correo).
- **FastAPI**: microservicio independiente, dueño exclusivo de la tabla Inventario (registro, consulta, generación de PDF y envío por correo). Se eligió por su tipado con Pydantic, su velocidad de desarrollo y porque también era una tecnología exigida por la prueba.
- **SQLAlchemy**: ORM del microservicio de Inventario; administra únicamente la tabla `inventario`, nunca las tablas de Django.

### Frontend
- **React 19 + Next.js 16**: las cuatro vistas del sistema (Login, Empresas, Productos, Inventario), consumiendo ambas APIs vía REST.
- **Atomic Design**: los componentes de React están organizados en `atoms/`, `molecules/`, `organisms/` y `templates/`, para mantener una jerarquía de reutilización clara.
- **Tailwind CSS v4**: utilidades de estilos.

### Base de datos
- **PostgreSQL**: única base de datos del sistema. Django administra las tablas de Empresa, Productos y Usuarios; SQLAlchemy administra exclusivamente la tabla Inventario y la tabla `producto_embedding` del agente de IA. Todas conviven en la misma instancia de Postgres sin mezclarse a nivel de ORM.
- **pgvector**: extensión de PostgreSQL que agrega el tipo de columna `Vector` y operadores de distancia (coseno) usados por el agente de IA para la búsqueda semántica.

### Agente de IA (búsqueda semántica)
- **Gemini (`gemini-embedding-001`)**: proveedor de embeddings por defecto para el agente de IA, elegido por tener una capa gratuita real (sin tarjeta de crédito). Es configurable: `EMBEDDINGS_PROVIDER=openai` cambia a `text-embedding-3-small` de OpenAI como alternativa de pago. La justificación completa, y por qué no Anthropic (no ofrece API de embeddings) ni LangChain (capa de orquestación innecesaria para este caso de uso), está en `docs/agente_ia_decision_proveedor.md`.

### Librerías principales
- **ReportLab**: generación del PDF de inventario en el microservicio FastAPI.
- **curl** (invocado vía `subprocess` desde `app.services.email_service`): envío del PDF por correo consumiendo directamente la API HTTP de Brevo (`https://api.brevo.com/v3/smtp/email`), sin SMTP. Se eligió así porque el plan gratuito de Render bloquea/falla en los puertos SMTP salientes (25/587/465), mientras que la API de Brevo viaja por HTTPS (443) como cualquier otra llamada REST del proyecto.
- **python-jose**: validación (decodificación y verificación de firma) del JWT emitido por Django, del lado de FastAPI.
- **httpx**: cliente HTTP usado tanto por FastAPI (para consultar la API de Django al construir el reporte y al enriquecer los resultados de búsqueda semántica) como por Django (para disparar automáticamente `POST /api/ia/embeddings` en FastAPI al crear/editar un Producto).

### Herramientas
- **Poetry**: gestiona las dependencias del paquete de dominio (`domain/`), que se instala como dependencia editable (`-e ../domain`) tanto en Django como en FastAPI.
- **python-decouple**: lectura de variables de entorno en Django.
- **pydantic-settings**: lectura de variables de entorno en FastAPI.
- **ruff** y **ESLint**: análisis estático de calidad de código (Python y frontend, respectivamente), como herramientas de desarrollo — nunca como dependencias de producción. Ver `docs/indicadores_calidad.md`.

## 4. Arquitectura

El proyecto sigue una variante de **Arquitectura Limpia** con dos backends independientes que comparten una única capa de dominio:

```
                     ┌───────────────────────────┐
                     │   Frontend (Next.js)      │
                     │   Atomic Design            │
                     └─────────────┬─────────────┘
                                   │ REST (fetch)
              ┌────────────────────┴────────────────────┐
              │                                          │
   ┌──────────▼──────────┐                  ┌────────────▼────────────────┐
   │  Django + DRF        │                  │  FastAPI                    │
   │  Empresa, Productos, │                  │  Inventario, PDF, correo,   │
   │  Login (emite JWT)   │                  │  Agente de IA (pgvector)    │
   │                       │◄─── REST ────────┤  (valida el JWT de         │
   │                       │  (para leer      │   Django, no emite         │
   │                       │  Empresa/Prod.)  │   tokens propios)          │
   └──────────┬───────────┘                  └────────────┬────────────────┘
              │ Django ORM                                │ SQLAlchemy
              │                                            │
              ▼                                            ▼
   ┌───────────────────────────── PostgreSQL (única BD) ─────────────────────────┐
   │  Tablas Empresa / Producto / Usuario   Tabla Inventario   Tabla             │
   │                                                            producto_embedding│
   │                                                            (pgvector)       │
   └──────────────────────────────────────────────────────────────────────────┘
                                                                     ▲
                                                                     │ embeddings
                                                        ┌────────────┴────────────┐
                                                        │  Gemini (por defecto)    │
                                                        │  o OpenAI (alternativa)  │
                                                        └─────────────────────────┘

                     ┌────────────────────────────────┐
                     │  domain/ (paquete Poetry)       │
                     │  Entidades: Inventario, Empresa,│
                     │  Producto, EmbeddingProducto,   │
                     │  ResultadoBusquedaProducto       │
                     │  VOs: Cantidad, Nit, Precio      │
                     │  Puertos: InventarioRepository,  │
                     │  EmbeddingProductoRepository,    │
                     │  GeneradorEmbeddings             │
                     │  Servicios: InventarioService,   │
                     │  EmbeddingProductoService         │
                     │  (sin Django/FastAPI/HTTP)        │
                     └────────────────────────────────┘
```

Puntos clave:

- **Django** es la única fuente de autenticación: emite el JWT con el claim `rol`. **FastAPI no tiene tabla de usuarios ni flujo de login propio**; solo valida la firma del mismo token (misma clave y algoritmo compartidos por variables de entorno).
- Cuando FastAPI necesita construir el PDF de inventario, no lee las tablas de Django directamente: **reenvía el token del usuario y consulta la API REST de Django** para obtener los datos de Empresa y Productos. Esto evita mezclar la persistencia de los dos ORMs. El agente de IA sigue el mismo criterio: resuelve nombre/características/empresa de cada resultado consultando la API de Django, en vez de duplicar esos datos en la tabla de embeddings.
- La comunicación entre backends va **en ambos sentidos**: además de que FastAPI reenvía el token para leer Empresa/Productos de Django, **Django reenvía el mismo token en sentido contrario** hacia FastAPI (`apps.productos.services.fastapi_ia_client`) para disparar automáticamente la ingesta de embeddings al crear/editar un Producto, sin que el usuario tenga que llamarla a mano.
- El envío del PDF de inventario por correo consume directamente la API HTTP de Brevo con `curl` (`app.services.email_service`), no SMTP: el plan gratuito de Render bloquea/falla en los puertos SMTP salientes, mientras que la API de Brevo viaja por HTTPS igual que cualquier otra llamada REST del proyecto.
- El **dominio** (`domain/`) es un paquete Python instalable de forma aislada (sin Django, FastAPI ni HTTP). Cubre las entidades del negocio de forma general, no solo Inventario:
  - `Inventario` + VO `Cantidad` (no negativa): registrar de nuevo un producto ya existente en el inventario de una empresa **suma** a la cantidad existente en vez de duplicar el registro.
  - `Empresa` + VO `Nit` (formato validado: solo dígitos, con dígito de verificación opcional).
  - `Producto` + VO `Precio` (no puede ser negativo, uno por moneda).
  - `EmbeddingProducto` + `ResultadoBusquedaProducto`, y el servicio `EmbeddingProductoService`: la regla de qué tan cerca debe estar un resultado para considerarse relevante (`UMBRAL_DISTANCIA_RELEVANTE`) vive aquí, no en una consulta SQL suelta ni en el endpoint de FastAPI.
  - FastAPI implementa los puertos `InventarioRepository` y `EmbeddingProductoRepository` con SQLAlchemy/pgvector, y `GeneradorEmbeddings` con Gemini u OpenAI (configurable); el dominio no conoce SQLAlchemy, pgvector, Gemini ni OpenAI.

## 5. Estructura del proyecto

```
lite-thinking-2026/
├── domain/                    # Paquete de dominio (Poetry), aislado de frameworks web
│   └── src/lite_thinking_domain/
│       ├── entities/          # Inventario, Empresa, Producto, EmbeddingProducto,
│       │                      # ResultadoBusquedaProducto
│       ├── value_objects/     # Cantidad (no negativa), Nit (formato), Precio (no negativo)
│       ├── repositories/      # Puertos: InventarioRepository, EmbeddingProductoRepository,
│       │                      # GeneradorEmbeddings (interfaces)
│       ├── services/          # InventarioService, EmbeddingProductoService (reglas de negocio,
│       │                      # incluye el umbral de relevancia de la búsqueda semántica)
│       └── exceptions.py      # ErrorGeneracionEmbedding (error de dominio, sin conocer HTTP/proveedor)
│
├── backend-django/            # Empresa, Productos, Login/Auth
│   ├── config/                 # settings, urls, wsgi/asgi
│   └── apps/
│       ├── autenticacion/      # Usuario (correo+password), login JWT, permisos por rol
│       ├── empresas/           # CRUD Empresa (lectura pública, escritura Administrador)
│       └── productos/          # CRUD Producto con precios multi-moneda (solo Administrador)
│           └── services/        # fastapi_ia_client: dispara la ingesta automática de
│                                 # embeddings en FastAPI tras crear/editar un Producto
│
├── backend-fastapi/            # Inventario, PDF, envío de correo, Agente de IA
│   └── app/
│       ├── api/                # Endpoints REST de Inventario e IA + dependencias de auth
│       │   └── ia.py            # POST /api/ia/embeddings, GET /api/ia/buscar
│       ├── core/                # Configuración y validación del JWT de Django
│       ├── db/                  # Sesión de SQLAlchemy
│       ├── models/              # InventarioModel, ProductoEmbeddingModel (SQLAlchemy + pgvector)
│       ├── repositories/        # Adaptadores SQLAlchemy de los puertos de dominio
│       ├── schemas/              # Contratos Pydantic de la API (incluye schemas/ia.py)
│       └── services/             # Cliente hacia Django, PDF, correo (API de Brevo vía curl), proveedores de embeddings (Gemini/OpenAI)
│
├── frontend/                   # Next.js + React, Atomic Design
│   ├── app/                     # Rutas: /, /login, /empresas, /productos, /inventario
│   ├── components/
│   │   ├── atoms/               # Button, Input, Select, Badge, Spinner, etc.
│   │   ├── molecules/           # Alert, FormField, Modal, ConfirmDialog, etc.
│   │   ├── organisms/           # Formularios y tablas de cada vista, Navbar
│   │   └── templates/           # AuthGate (protección de rutas), PageShell
│   └── lib/
│       ├── api/                  # Clientes REST hacia Django y FastAPI
│       ├── auth/                 # AuthContext, decodificación del JWT
│       ├── types/                 # Tipos TypeScript compartidos
│       └── utils/                  # Descarga de archivos (PDF)
│
├── requirements-dev.txt        # Herramienta de análisis estático (ruff), solo desarrollo/evaluación
│
└── docs/
    ├── postgres_setup.sql                    # Creación de BD/usuario + extensión pgvector
    ├── agente_ia_decision_proveedor.md        # Por qué Gemini (gratis) por defecto, OpenAI como alternativa
    ├── agente_ia_ingesta_embeddings.md             # Ingesta de embeddings (POST /api/ia/embeddings)
    ├── agente_ia_busqueda_semantica.md            # Búsqueda semántica (GET /api/ia/buscar) + prueba manual
    ├── simulacion_busqueda_semantica.py       # Script reproducible de la prueba manual del agente de IA
    └── indicadores_calidad.md                 # Evidencia de Lighthouse / análisis estático / GTmetrix
```

## 6. Requisitos previos

| Herramienta | Versión mínima |
|---|---|
| Python | 3.11 |
| Node.js | 20 LTS (requerido por Next.js 16) |
| PostgreSQL | 14 |
| Poetry | 1.8 (o compatible con `pyproject.toml` formato 2.x) |
| npm | 10 (la que acompaña a Node 20) |

## 7. Instalación

### 7.1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd lite-thinking-2026
```

### 7.2. Crear la base de datos (incluye la extensión pgvector)

**Requisito previo:** la extensión `pgvector` debe estar instalada a nivel de sistema operativo antes de este paso (paquete `postgresql-<versión>-pgvector` en Debian/Ubuntu, `pgvector` en Homebrew, o la imagen `pgvector/pgvector` si se usa Docker). Sin este paquete de sistema, el `CREATE EXTENSION` del siguiente script falla.

Con PostgreSQL corriendo localmente, y conectado como superusuario:

```bash
psql -U postgres -f docs/postgres_setup.sql
```

Esto crea la base `lite_thinking_db` y el usuario `lite_thinking_user`, compartidos por Django y FastAPI (misma base de datos, tablas administradas por ORMs distintos), **y habilita la extensión `vector`** dentro de `lite_thinking_db` (requerida por la tabla `producto_embedding` del agente de IA). La tabla en sí no se crea aquí: FastAPI la crea automáticamente al arrancar (mismo mecanismo que la tabla `inventario`, ver sección 7.6).

### 7.3. Capa de dominio (verificación de instalación aislada)

```bash
cd domain
poetry install
poetry run pytest
cd ..
```

Este paso confirma que el paquete de dominio se instala y se importa sin depender de Django ni de FastAPI.

### 7.4. Variables de entorno

Copiar los archivos de ejemplo y ajustar si es necesario (ver sección 8):

```bash
cp backend-django/.env.example backend-django/.env
cp backend-fastapi/.env.example backend-fastapi/.env
cp frontend/.env.local.example frontend/.env.local
```

> **Importante:** `JWT_SIGNING_KEY` y `JWT_ALGORITHM` deben ser **idénticos** en `backend-django/.env` y `backend-fastapi/.env`. Django emite el token; FastAPI solo lo valida.

> **Nota para Windows (PowerShell):** por defecto, PowerShell restringe la ejecución de scripts, lo que impide activar los entornos virtuales de Django y FastAPI (`.venv\Scripts\Activate.ps1`). Si al activarlos aparece un error de política de ejecución, habilita los scripts firmados localmente antes de continuar:
>
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
>
> Esto solo necesita ejecutarse una vez por usuario. Alternativamente, puedes usar el Símbolo del sistema (`cmd.exe`) y activar los entornos con `.venv\Scripts\activate.bat`, que no está sujeto a esta restricción.

### 7.5. Backend Django (Empresa, Productos, Login)

```bash
cd backend-django
python3 -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
```

Crear un usuario Administrador (no existe endpoint de registro; se crea por línea de comandos):

```bash
python manage.py createsuperuser
# Pedirá: correo, nombre (opcional) y contraseña
```

Levantar el servidor:

```bash
python manage.py runserver 0.0.0.0:8000
```

### 7.6. Microservicio FastAPI (Inventario, PDF, correo)

En otra terminal:

```bash
cd backend-fastapi
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

Al arrancar, FastAPI crea automáticamente las tablas `inventario` y `producto_embedding` si no existen (no se usa Alembic). Verificación rápida:

```bash
curl http://localhost:8001/health
```

> **Agente de IA:** el módulo de búsqueda semántica (`POST /api/ia/embeddings`, `GET /api/ia/buscar`) requiere una clave del proveedor de embeddings configurado en `backend-fastapi/.env` — por defecto `GEMINI_API_KEY` (gratis, ver sección 8), o `OPENAI_API_KEY` si cambias `EMBEDDINGS_PROVIDER=openai`. Sin esa clave, el resto del servicio (Inventario, PDF, correo) sigue funcionando con normalidad; solo esos dos endpoints responderán `502 Bad Gateway` al intentar generar un embedding.

### 7.7. Frontend (Next.js)

En otra terminal:

```bash
cd frontend
npm install
npm run dev
```

Disponible en `http://localhost:3000`.

## 8. Variables de entorno

### `backend-django/.env`

| Variable | Descripción |
|---|---|
| `DJANGO_SECRET_KEY` | Clave secreta interna de Django. |
| `DJANGO_DEBUG` | `True`/`False`. Modo de depuración. |
| `DJANGO_ALLOWED_HOSTS` | Hosts permitidos, separados por coma. |
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_HOST` / `POSTGRES_PORT` | Conexión a la base de datos única del sistema. |
| `JWT_ALGORITHM` | Algoritmo de firma del token (`HS256`). |
| `JWT_SIGNING_KEY` | Clave de firma del JWT. **Debe coincidir con la de FastAPI.** |
| `JWT_ACCESS_TOKEN_LIFETIME_HOURS` | Duración del access token. |
| `JWT_REFRESH_TOKEN_LIFETIME_DAYS` | Duración del refresh token. |
| `CORS_ALLOWED_ORIGINS` | Orígenes permitidos (el frontend Next.js). |
| `FASTAPI_API_URL` | URL base de la API de FastAPI, usada para disparar automáticamente `POST /api/ia/embeddings` al crear/editar un Producto (ver `apps.productos.services.fastapi_ia_client`). |

### `backend-fastapi/.env`

| Variable | Descripción |
|---|---|
| `APP_NAME` / `DEBUG` | Metadatos del servicio. |
| `POSTGRES_*` | Misma base de datos que Django. |
| `JWT_ALGORITHM` / `JWT_SIGNING_KEY` | **Deben coincidir exactamente con Django**; FastAPI no emite tokens, solo los valida. |
| `DJANGO_API_URL` | URL base de la API de Django, usada para leer Empresa/Productos al construir el PDF. |
| `BREVO_API_KEY` | Clave de la API HTTP de Brevo (`https://app.brevo.com/settings/keys/api`). Si queda vacía, el envío de correo se simula en modo consola (se registra en el log en vez de enviarse). El envío se hace con `curl` (ver `app.services.email_service`), no SMTP, precisamente para evitar el bloqueo de puertos SMTP salientes en el plan gratuito de Render. |
| `BREVO_FROM_EMAIL` / `BREVO_FROM_NAME` | Remitente del correo con el PDF adjunto. |
| `CORS_ALLOWED_ORIGINS` | Orígenes permitidos. |
| `EMBEDDINGS_PROVIDER` | Proveedor de embeddings del agente de IA: `gemini` (por defecto, gratis) u `openai` (alternativa de pago). Ver `docs/agente_ia_decision_proveedor.md` para la comparación completa. Sin la clave del proveedor seleccionado, `POST /api/ia/embeddings` y `GET /api/ia/buscar` responden `502 Bad Gateway`; el resto del servicio no se ve afectado. |
| `GEMINI_API_KEY` / `GEMINI_EMBEDDINGS_MODEL` | Clave y modelo de Gemini (proveedor por defecto). Clave gratuita en https://aistudio.google.com/apikey. |
| `OPENAI_API_KEY` / `OPENAI_EMBEDDINGS_MODEL` | Clave y modelo de OpenAI, solo si `EMBEDDINGS_PROVIDER=openai`. |
| `EMBEDDINGS_DIMENSION` | Dimensión del vector generado (1536, tanto para Gemini como para OpenAI); debe coincidir con la columna `Vector(...)` de la tabla `producto_embedding`. |

### `frontend/.env.local`

| Variable | Descripción |
|---|---|
| `NEXT_PUBLIC_DJANGO_API_URL` | URL base de la API de Django (por defecto `http://localhost:8000/api`). |
| `NEXT_PUBLIC_FASTAPI_API_URL` | URL base de la API de FastAPI (por defecto `http://localhost:8001`). |

## 9. Ejecución

Con la base de datos ya creada y las variables de entorno configuradas, se requieren **tres procesos corriendo en paralelo**, cada uno en su propia terminal:

```bash
# Terminal 1: Django (puerto 8000)
cd backend-django && source .venv/bin/activate && python manage.py runserver 0.0.0.0:8000

# Terminal 2: FastAPI (puerto 8001)
cd backend-fastapi && source .venv/bin/activate && uvicorn app.main:app --reload --port 8001

# Terminal 3: Frontend (puerto 3000)
cd frontend && npm run dev
```

| Servicio | Puerto | URL |
|---|---|---|
| Django (Empresa, Productos, Login) | 8000 | http://localhost:8000/api |
| FastAPI (Inventario, PDF, correo) | 8001 | http://localhost:8001 |
| Next.js (Frontend) | 3000 | http://localhost:3000 |
| PostgreSQL | 5432 | N/A |

El detalle de todos los endpoints de Django, con ejemplos `curl`, está en `backend-django/docs_verificacion_endpoints.md`.

## 10. Funcionalidades implementadas

- [x] Vista Empresa: NIT (PK), Nombre, Dirección, Teléfono.
- [x] CRUD completo de Empresa para el Administrador; lectura sin autenticación para el usuario Externo.
- [x] Vista Productos: Código, Nombre, Características, Precio en varias monedas (COP/USD/EUR), Empresa asociada.
- [x] CRUD de Productos, restringido al Administrador (incluida la lectura).
- [x] Vista Login: autenticación con correo y contraseña, emisión de JWT con el rol embebido.
- [x] Contraseña del Administrador encriptada (hasher PBKDF2 por defecto de Django).
- [x] Vista Inventario: registro y consulta de existencias por Empresa. Registrar un producto ya existente incrementa la cantidad en vez de duplicar el registro.
- [x] Descarga del PDF de inventario de una empresa.
- [x] Envío del PDF de inventario por correo consumiendo directamente la API HTTP de Brevo con `curl` (con modo "consola" de respaldo si no hay `BREVO_API_KEY` configurada), sin SMTP, para evitar el bloqueo de puertos SMTP salientes del plan gratuito de Render.
- [x] Permisos de rol (Administrador/Externo) validados siempre en el backend (Django y FastAPI), nunca solo en el frontend.
- [x] Capa de dominio (`domain/`) desacoplada de Django/FastAPI/HTTP, instalable de forma aislada, cubriendo las entidades del negocio de forma general: `Inventario` (VO `Cantidad`), `Empresa` (VO `Nit`) y `Producto` (VO `Precio`) — no solo Inventario. Verificada con una suite de pruebas automatizadas (`pytest`, 43 pruebas en verde).
- [x] `pyproject.toml` del paquete de dominio, gestionado con Poetry.
- [x] FastAPI valida el JWT emitido por Django sin tener autenticación propia.
- [x] Frontend organizado bajo Atomic Design (`atoms/`, `molecules/`, `organisms/`, `templates/`).
- [x] Uso efectivo de las 7 tecnologías obligatorias: Python, Django, FastAPI, React, PostgreSQL, SQLAlchemy y Next.js.
- [x] **Agente de IA con pgvector:** PostgreSQL con la extensión `pgvector` habilitada, tabla `producto_embedding`, generación de embeddings con Gemini por defecto (u OpenAI como alternativa, configurable) vía `POST /api/ia/embeddings`, y búsqueda semántica vía `GET /api/ia/buscar`, con el criterio de relevancia (umbral de distancia coseno) resuelto como regla de dominio, no como consulta SQL suelta. Ver `docs/agente_ia_decision_proveedor.md`, `docs/agente_ia_ingesta_embeddings.md` y `docs/agente_ia_busqueda_semantica.md`.
- [x] **Integración visual del buscador semántico en la vista Productos:** panel plegable "Búsqueda con IA" (`BusquedaSemanticaProductos`) que consulta `GET /api/ia/buscar` en lenguaje natural y muestra código, nombre, características y porcentaje de similitud de cada resultado; cada resultado permite ubicar la empresa asociada directamente en el filtro de la tabla de Productos.
- [x] **Re-embeddado automático del agente de IA al crear/editar un Producto en Django:** `ProductoViewSet` dispara `POST /api/ia/embeddings` en FastAPI (reenviando el token del Administrador de la petición actual) justo después de guardar el Producto, vía `apps.productos.services.fastapi_ia_client`. Es "best-effort": si el agente de IA no responde o el proveedor de embeddings falla, el Producto queda guardado igual y solo se registra un warning; el endpoint manual `POST /api/ia/embeddings` se mantiene disponible para reingestar histórico o recuperar ese caso puntual. Con esto, el panel "Búsqueda con IA" queda siempre al día sin pasos manuales adicionales. Ver `docs/agente_ia_ingesta_embeddings.md`.
- [x] Filtro por Empresa en el listado de Productos (`GET /api/productos/?empresa=<nit>`), reutilizado tanto por el frontend como por el propio agente de IA para resolver los datos de negocio de cada resultado.
- [x] **Indicadores de rendimiento y calidad:** análisis estático de código (`ruff`, equivalente a SonarQube) sobre los tres paquetes Python, y ESLint sobre el frontend, ambos como herramientas de desarrollo (no dependencias de producción); build de producción del frontend verificado (6/6 rutas estáticas). Ver `docs/indicadores_calidad.md` para el detalle completo, incluida la justificación de por qué Lighthouse no pudo ejecutarse en el entorno de desarrollo usado y por qué GTmetrix no aplica sin despliegue público.

## 11. Conclusión

El proyecto cumple los requisitos obligatorios planteados: gestión de Empresas y Productos con roles diferenciados, un flujo completo de Inventario con generación y envío de PDF, autenticación segura con JWT compartido entre dos backends, una capa de dominio desacoplada bajo Poetry que cubre las entidades del negocio (Empresa, Producto e Inventario), un agente de IA con pgvector para búsqueda semántica de productos, y evidencia documentada de indicadores de calidad y rendimiento. La arquitectura prioriza la simplicidad y la separación de responsabilidades por encima de la sobreingeniería, dejando explícitamente fuera del alcance lo que no era necesario para el objetivo del proyecto.