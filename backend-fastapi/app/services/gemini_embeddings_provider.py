"""
Adaptador de infraestructura: implementa el puerto de dominio
`GeneradorEmbeddings` llamando a la API de embeddings de Google Gemini
(`gemini-embedding-001`), usando `httpx` (ya es dependencia del
proyecto para `django_client`) en vez de agregar el SDK oficial de
Google, evitando así una dependencia nueva para una sola llamada REST.

Se eligió como proveedor por defecto porque el Gemini API tiene una
capa gratuita real (limitada por tasa, sin tarjeta de crédito), a
diferencia de OpenAI, que exige una compra prepagada mínima. Ver
docs/agente_ia_decision_proveedor.md para la comparación completa.

Traduce cualquier falla de la API (timeout, credenciales, red, límite
de tasa, respuesta con dimensión inesperada) a `ErrorGeneracionEmbedding`
(excepción pura de dominio), igual que el adaptador de OpenAI.
"""

from __future__ import annotations

import logging

import httpx
from lite_thinking_domain.exceptions import ErrorGeneracionEmbedding
from lite_thinking_domain.repositories.generador_embeddings import GeneradorEmbeddings

from app.core.config import settings

logger = logging.getLogger("inventario.embeddings")

_TIMEOUT_SEGUNDOS = 15.0
_URL_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


class GeminiGeneradorEmbeddings(GeneradorEmbeddings):
    """Genera embeddings vía la API de Gemini (proveedor gratuito por defecto)."""

    def generar(self, texto: str) -> list[float]:
        if not settings.GEMINI_API_KEY:
            raise ErrorGeneracionEmbedding(
                "No hay una GEMINI_API_KEY configurada; no se puede generar el embedding."
            )

        url = f"{_URL_BASE}/{settings.GEMINI_EMBEDDINGS_MODEL}:embedContent"
        payload = {
            "content": {"parts": [{"text": texto}]},
            "outputDimensionality": settings.EMBEDDINGS_DIMENSION,
        }

        try:
            respuesta = httpx.post(
                url,
                params={"key": settings.GEMINI_API_KEY},
                json=payload,
                timeout=_TIMEOUT_SEGUNDOS,
            )
            respuesta.raise_for_status()
        except httpx.TimeoutException as exc:
            logger.error("Timeout llamando a Gemini para generar el embedding: %s", exc)
            raise ErrorGeneracionEmbedding(
                "Se agotó el tiempo de espera al llamar a Gemini para generar el embedding."
            ) from exc
        except httpx.ConnectError as exc:
            logger.error("No se pudo conectar con Gemini: %s", exc)
            raise ErrorGeneracionEmbedding(
                "No se pudo conectar con Gemini para generar el embedding."
            ) from exc
        except httpx.HTTPStatusError as exc:
            codigo = exc.response.status_code
            if codigo == 401 or codigo == 403:
                logger.error("Gemini rechazó las credenciales configuradas: %s", exc)
                raise ErrorGeneracionEmbedding(
                    "Gemini rechazó las credenciales configuradas (GEMINI_API_KEY)."
                ) from exc
            if codigo == 429:
                logger.error("Gemini respondió límite de tasa: %s", exc)
                raise ErrorGeneracionEmbedding(
                    "Gemini rechazó la solicitud por límite de tasa (rate limit)."
                ) from exc
            logger.error("Gemini respondió un error inesperado: %s", exc)
            raise ErrorGeneracionEmbedding(
                f"Gemini respondió con un error inesperado (status {codigo})."
            ) from exc

        cuerpo = respuesta.json()
        vector = list(cuerpo.get("embedding", {}).get("values", []))
        if len(vector) != settings.EMBEDDINGS_DIMENSION:
            raise ErrorGeneracionEmbedding(
                "El proveedor devolvió un vector de dimensión distinta a la "
                f"esperada ({len(vector)} != {settings.EMBEDDINGS_DIMENSION})."
            )
        return vector
