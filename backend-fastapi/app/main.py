"""
Microservicio FastAPI — dueño de la tabla Inventario.

Responsabilidades implementadas:
- Registro y consulta de Inventario por Empresa (CRUD completo).
- Validación del token JWT emitido por Django (sin autenticación propia).
- Generación del PDF de Inventario y envío por correo (integrado con la
  API de Empresas/Productos de Django vía `app.services.django_client`).
- Agente de IA con pgvector: ingesta de embeddings de Producto
  (`app.api.ia`) — generar y guardar el vector vigente de un
  producto con el proveedor de embeddings configurado (Gemini por
  defecto, gratuito; OpenAI como alternativa) — y
  búsqueda semántica (`GET /api/ia/buscar`) sobre esos embeddings, con
  el criterio de relevancia resuelto en el dominio
  (`EmbeddingProductoService.buscar_semanticamente`). Ver
  docs/agente_ia_busqueda_semantica.md.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.ia import router as ia_router
from app.api.inventario import router as inventario_router
from app.core.config import settings
from app.db.session import Base, engine

# Modelos importados para que Base.metadata los conozca antes de create_all.
from app.models import InventarioModel, ProductoEmbeddingModel  # noqa: F401

app = FastAPI(
    title=settings.APP_NAME,
    description="Microservicio de Inventario (registro, PDF, envío por correo).",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CORS_ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

app.include_router(inventario_router)
app.include_router(ia_router)

_logger = logging.getLogger("inventario.errores")


@app.exception_handler(Exception)
async def manejar_error_no_controlado(request: Request, exc: Exception) -> JSONResponse:
    """
    Convierte cualquier excepción no controlada en una respuesta JSON normal.

    Sin este manejador, un error inesperado (por ejemplo, al invocar
    curl contra la API de Brevo) escapa del middleware de CORS y el
    navegador lo reporta como un falso bloqueo de CORS, ocultando el
    error real.
    """
    _logger.exception("Error no controlado en %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Ocurrió un error inesperado en el servidor. Revisa los logs de FastAPI."},
    )


@app.on_event("startup")
def crear_tablas() -> None:
    """
    Crea las tablas `inventario` y `producto_embedding` si no existen.

    No se usa Alembic; `create_all` es suficiente para el alcance
    actual y no afecta las tablas de Django (Base solo conoce los
    modelos de este microservicio).
    """
    Base.metadata.create_all(bind=engine)


@app.get("/health", tags=["infraestructura"])
def health_check() -> dict:
    """Verificación de que el servicio está en ejecución (no valida la BD)."""
    return {"status": "ok", "service": settings.APP_NAME}
