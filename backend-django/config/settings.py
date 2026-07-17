"""
Configuración base de Django para el proyecto Lite Thinking 2026.

Este proyecto es la capa de aplicación/infraestructura para:
- Empresa (CRUD Administrador / lectura Externo)
- Productos
- Login y autenticación (emisión de token con rol)
"""

from datetime import timedelta
from pathlib import Path

from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------
# Seguridad / entorno
# --------------------------------------------------------------------------
SECRET_KEY = config("DJANGO_SECRET_KEY", default="dev-insecure-secret-key-change-in-env")
DEBUG = config("DJANGO_DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config("DJANGO_ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

# --------------------------------------------------------------------------
# Aplicaciones
# --------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "drf_spectacular",
]

LOCAL_APPS: list[str] = [
    "apps.autenticacion",
    "apps.empresas",
    "apps.productos",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --------------------------------------------------------------------------
# Base de datos: PostgreSQL (única base de datos del sistema)
# --------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB", default="lite_thinking_db"),
        "USER": config("POSTGRES_USER", default="lite_thinking_user"),
        "PASSWORD": config("POSTGRES_PASSWORD", default="lite_thinking_password"),
        "HOST": config("POSTGRES_HOST", default="localhost"),
        "PORT": config("POSTGRES_PORT", default="5432"),
        "OPTIONS": {
            "client_encoding": "UTF8",
        },
    }
}

# --------------------------------------------------------------------------
# Validación de contraseñas (el Administrador se autentica con contraseña
# encriptada)
# --------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --------------------------------------------------------------------------
# Internacionalización
# --------------------------------------------------------------------------
LANGUAGE_CODE = "es"
TIME_ZONE = "America/Bogota"
USE_I18N = True
USE_TZ = True

# --------------------------------------------------------------------------
# Archivos estáticos
# --------------------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --------------------------------------------------------------------------
# Django REST Framework
# --------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Lite Thinking 2026 — API de Empresas, Productos y Autenticación",
    "DESCRIPTION": (
        "API REST de Django para la gestión de Empresas y Productos, y para "
        "la autenticación del rol Administrador (login por correo y "
        "contraseña, con JWT). El registro de Inventario, la generación de "
        "PDF y la búsqueda semántica con IA viven en un microservicio "
        "aparte (FastAPI), documentado en su propio /docs.\n\n"
        "### Roles\n"
        "- **Administrador** (autenticado con JWT): acceso completo a "
        "Empresas y Productos (crear, editar, eliminar).\n"
        "- **Externo** (sin autenticación): solo puede listar y consultar "
        "Empresas (`GET /api/empresas/`). No tiene acceso a Productos.\n\n"
        "### Autenticación\n"
        "1. `POST /api/auth/login/` con `correo` y `password` devuelve un "
        "par de tokens (`access`, `refresh`). El `access` incluye el rol "
        "del usuario como claim.\n"
        "2. Envía el token en cada petición protegida como "
        "`Authorization: Bearer <access>`.\n"
        "3. Cuando expire, pide uno nuevo con `POST /api/auth/refresh/` "
        "usando el `refresh`.\n\n"
        "Usa el botón **Authorize** de esta página: pega `Bearer <access>` "
        "y todos los endpoints protegidos quedarán autenticados en las "
        "pruebas que hagas desde aquí."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": "/api/",
    "TAGS": [
        {"name": "Autenticación", "description": "Login y renovación de tokens JWT para el rol Administrador."},
        {"name": "Empresas", "description": "Alta, consulta, edición y eliminación de empresas."},
        {"name": "Productos", "description": "Alta, consulta, edición y eliminación de productos asociados a una empresa."},
    ],
}

# --------------------------------------------------------------------------
# JWT: Django es la única fuente de autenticación. El token emitido aquí
# incluye el rol y es validado por FastAPI sin re-autenticar.
# --------------------------------------------------------------------------
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=config("JWT_ACCESS_TOKEN_LIFETIME_HOURS", default=8, cast=int)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=config("JWT_REFRESH_TOKEN_LIFETIME_DAYS", default=1, cast=int)),
    "ALGORITHM": config("JWT_ALGORITHM", default="HS256"),
    "SIGNING_KEY": config("JWT_SIGNING_KEY", default=SECRET_KEY),
}

# --------------------------------------------------------------------------
# Modelo de usuario personalizado (correo + contraseña)
# --------------------------------------------------------------------------
AUTH_USER_MODEL = "autenticacion.Usuario"

# --------------------------------------------------------------------------
# CORS: el frontend Next.js consume esta API
# --------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:3000",
    cast=Csv(),
)

# --------------------------------------------------------------------------
# Integración con FastAPI: Django dispara la ingesta de embeddings del
# agente de IA (POST /api/ia/embeddings) al crear/editar un Producto,
# reenviando el token del Administrador que llegó a esta misma petición
# (mismo criterio que ya usa FastAPI en sentido inverso para leer
# Empresa/Productos vía la API de Django). Ver
# apps.productos.services.fastapi_ia_client.
# --------------------------------------------------------------------------
FASTAPI_API_URL = config("FASTAPI_API_URL", default="http://localhost:8001/api")
