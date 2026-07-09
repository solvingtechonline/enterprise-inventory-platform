"""
Dependencias compartidas por los endpoints de Inventario.

Nota sobre permisos: la especificación solo exime de
autenticación la visualización de Empresas por el rol Externo; no
menciona a Externo respecto de Inventario. Siguiendo el mismo criterio
ya aplicado a Productos en Django (seguridad por defecto), Inventario
requiere rol Administrador para todas las operaciones, incluida la
consulta.
"""

from __future__ import annotations

from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from lite_thinking_domain.services.embedding_producto_service import (
    EmbeddingProductoService,
)
from lite_thinking_domain.services.inventario_service import InventarioService
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import UsuarioToken, obtener_usuario_actual
from app.db.session import get_db
from app.repositories.sqlalchemy_embedding_producto_repository import (
    SQLAlchemyEmbeddingProductoRepository,
)
from app.repositories.sqlalchemy_inventario_repository import (
    SQLAlchemyInventarioRepository,
)
from app.services.gemini_embeddings_provider import GeminiGeneradorEmbeddings
from app.services.openai_embeddings_provider import OpenAIGeneradorEmbeddings


def requerir_administrador(
    usuario: UsuarioToken = Depends(obtener_usuario_actual),
) -> UsuarioToken:
    if not usuario.es_administrador:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta acción requiere rol Administrador.",
        )
    return usuario


def obtener_inventario_service(
    db: Session = Depends(get_db),
) -> Generator[InventarioService, None, None]:
    repositorio = SQLAlchemyInventarioRepository(db)
    yield InventarioService(repositorio)


def obtener_embedding_producto_service(
    db: Session = Depends(get_db),
) -> Generator[EmbeddingProductoService, None, None]:
    """
    Ensambla el caso de uso de ingesta de embeddings: adaptador de
    persistencia (SQLAlchemy + pgvector) y adaptador del proveedor de
    IA (Gemini por defecto, u OpenAI si se configura
    `EMBEDDINGS_PROVIDER=openai`), ambos inyectados en el servicio de
    dominio puro. El dominio no conoce cuál de los dos se está usando.
    """
    repositorio = SQLAlchemyEmbeddingProductoRepository(db)
    if settings.EMBEDDINGS_PROVIDER == "openai":
        generador = OpenAIGeneradorEmbeddings()
    else:
        generador = GeminiGeneradorEmbeddings()
    yield EmbeddingProductoService(repositorio, generador)
