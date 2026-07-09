"""
Adaptador de infraestructura: implementa el puerto de dominio
`GeneradorEmbeddings` llamando a la API de OpenAI (proveedor elegido
en docs/agente_ia_decision_proveedor.md: `text-embedding-3-small`,
1536 dimensiones).

Traduce cualquier falla del SDK de OpenAI (timeout, credenciales,
red, límite de tasa, respuesta con dimensión inesperada) a
`ErrorGeneracionEmbedding` (excepción pura de dominio): ni el dominio
ni la capa de endpoints necesitan conocer las excepciones específicas
del SDK `openai`. Esto es lo que permite que un fallo del proveedor de
IA se traduzca a un error HTTP puntual (ver `app.api.ia`) sin tumbar
el resto del microservicio.
"""

from __future__ import annotations

import logging

import openai
from lite_thinking_domain.exceptions import ErrorGeneracionEmbedding
from lite_thinking_domain.repositories.generador_embeddings import GeneradorEmbeddings

from app.core.config import settings

logger = logging.getLogger("inventario.embeddings")

_TIMEOUT_SEGUNDOS = 15.0


class OpenAIGeneradorEmbeddings(GeneradorEmbeddings):
    """Genera embeddings vía la API de OpenAI (proveedor elegido para el proyecto)."""

    def __init__(self) -> None:
        # El cliente se crea aunque OPENAI_API_KEY esté vacío: el error de
        # credenciales se produce recién al llamar `generar` (más abajo),
        # no aquí. Así el microservicio sigue arrancando sin la clave
        # configurada; solo esta operación puntual fallará con un 502.
        self._cliente = openai.OpenAI(api_key=settings.OPENAI_API_KEY or "sk-no-configurada")

    def generar(self, texto: str) -> list[float]:
        if not settings.OPENAI_API_KEY:
            raise ErrorGeneracionEmbedding(
                "No hay una OPENAI_API_KEY configurada; no se puede generar el embedding."
            )

        try:
            respuesta = self._cliente.embeddings.create(
                model=settings.OPENAI_EMBEDDINGS_MODEL,
                input=texto,
                timeout=_TIMEOUT_SEGUNDOS,
            )
        except openai.AuthenticationError as exc:
            logger.error("OpenAI rechazó las credenciales configuradas: %s", exc)
            raise ErrorGeneracionEmbedding(
                "OpenAI rechazó las credenciales configuradas (OPENAI_API_KEY)."
            ) from exc
        except openai.APITimeoutError as exc:
            logger.error("Timeout llamando a OpenAI para generar el embedding: %s", exc)
            raise ErrorGeneracionEmbedding(
                "Se agotó el tiempo de espera al llamar a OpenAI para generar el embedding."
            ) from exc
        except openai.APIConnectionError as exc:
            logger.error("No se pudo conectar con OpenAI: %s", exc)
            raise ErrorGeneracionEmbedding(
                "No se pudo conectar con OpenAI para generar el embedding."
            ) from exc
        except openai.RateLimitError as exc:
            logger.error("OpenAI respondió límite de tasa: %s", exc)
            raise ErrorGeneracionEmbedding(
                "OpenAI rechazó la solicitud por límite de tasa (rate limit)."
            ) from exc
        except openai.APIStatusError as exc:
            logger.error("OpenAI respondió un error inesperado: %s", exc)
            raise ErrorGeneracionEmbedding(
                f"OpenAI respondió con un error inesperado (status {exc.status_code})."
            ) from exc

        vector = list(respuesta.data[0].embedding)
        if len(vector) != settings.EMBEDDINGS_DIMENSION:
            raise ErrorGeneracionEmbedding(
                "El proveedor devolvió un vector de dimensión distinta a la "
                f"esperada ({len(vector)} != {settings.EMBEDDINGS_DIMENSION})."
            )
        return vector
