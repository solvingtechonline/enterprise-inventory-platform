"""
Cliente HTTP hacia el agente de IA del microservicio FastAPI.

Django es dueño de Producto (ORM, tabla `productos_producto`), pero el
embedding vigente de ese producto vive en FastAPI/pgvector
(`producto_embedding`), administrado por
`EmbeddingProductoService` en el dominio. En vez de que Django hable
directamente con pgvector o con el proveedor de embeddings (lo que
duplicaría esa lógica en dos backends), este módulo dispara la ingesta
llamando a `POST /api/ia/embeddings`, que ya existe y ya la resuelve.

Es el mismo patrón que `backend-fastapi/app/services/django_client.py`,
pero en sentido inverso: reenvía el mismo token del Administrador que
llegó a la petición de Django, porque ese endpoint de FastAPI exige
rol Administrador (`requerir_administrador`) y no hay un emisor de
autenticación distinto entre los dos backends.

Este cliente se usa de forma "best-effort" desde
`apps.productos.views.ProductoViewSet`: si FastAPI no responde, está
caído, o el proveedor de embeddings falla, el Producto en Django ya
quedó guardado de todas formas: un fallo aquí no debe tumbar el
guardado del producto, solo dejarlo temporalmente sin embedder (se
puede reintentar más tarde llamando a `POST /api/ia/embeddings`
manualmente, que se mantiene disponible para ese caso).

Mismo criterio best-effort aplica a `eliminar_embedding_async_seguro`
(ver `ProductoViewSet.perform_destroy`): si FastAPI no responde al
intentar borrar el embedding, el Producto se elimina en Django de
todas formas y el embedding queda huérfano hasta que se limpie
manualmente (ver el script de mantenimiento de embeddings).
"""

from __future__ import annotations

import logging

import httpx
from django.conf import settings

logger = logging.getLogger(__name__)

_TIMEOUT_SEGUNDOS = 5.0


def ingestar_embedding_async_seguro(
    empresa_nit: str, producto_codigo: str, token: str
) -> None:
    """
    Llama a `POST /api/ia/embeddings` en FastAPI para generar (o
    regenerar) el embedding vigente de un producto.

    No lanza excepciones: cualquier fallo (conexión, timeout, 4xx/5xx
    de FastAPI, proveedor de IA sin configurar) se registra como
    warning y se descarta, para que crear/editar un Producto en Django
    nunca falle por una causa ajena a Empresa/Producto. Ver el
    docstring del módulo.
    """
    url = f"{settings.FASTAPI_API_URL}/ia/embeddings"
    cuerpo = {"empresa_nit": empresa_nit, "producto_codigo": producto_codigo}
    encabezados = {"Authorization": f"Bearer {token}"}

    try:
        respuesta = httpx.post(
            url, json=cuerpo, headers=encabezados, timeout=_TIMEOUT_SEGUNDOS
        )
    except httpx.RequestError:
        logger.warning(
            "No se pudo conectar con el agente de IA (FastAPI) para "
            "generar el embedding del producto '%s'. El producto se "
            "guardó correctamente; el embedding puede regenerarse más "
            "tarde con POST /api/ia/embeddings.",
            producto_codigo,
        )
        return

    if respuesta.status_code >= httpx.codes.BAD_REQUEST:
        logger.warning(
            "El agente de IA (FastAPI) respondió %s al intentar generar "
            "el embedding del producto '%s'. El producto se guardó "
            "correctamente; el embedding puede regenerarse más tarde "
            "con POST /api/ia/embeddings. Detalle: %s",
            respuesta.status_code,
            producto_codigo,
            respuesta.text,
        )


def eliminar_embedding_async_seguro(producto_codigo: str, token: str) -> None:
    """
    Llama a `DELETE /api/ia/embeddings/{producto_codigo}` en FastAPI
    para eliminar el embedding vigente de un producto que se acaba de
    borrar en Django.

    No recibe `empresa_nit`: a diferencia de `ingestar_embedding_async_seguro`
    (que lo necesita para resolver el producto en la API de Django),
    aquí `producto_codigo` ya identifica de forma única la fila a
    borrar en `producto_embedding` (columna con `UniqueConstraint`, ver
    `app.models.producto_embedding.ProductoEmbeddingModel`), así que no
    hace falta.

    No lanza excepciones: mismo criterio best-effort que
    `ingestar_embedding_async_seguro` (ver docstring del módulo). Un
    404 de FastAPI (embedding inexistente) es un caso válido, no un
    error, y no se registra como warning.
    """
    url = f"{settings.FASTAPI_API_URL}/ia/embeddings/{producto_codigo}"
    encabezados = {"Authorization": f"Bearer {token}"}

    try:
        respuesta = httpx.delete(url, headers=encabezados, timeout=_TIMEOUT_SEGUNDOS)
    except httpx.RequestError:
        logger.warning(
            "No se pudo conectar con el agente de IA (FastAPI) para "
            "eliminar el embedding del producto '%s'. El producto se "
            "elimina en Django de todas formas; el embedding quedará "
            "huérfano hasta limpiarse manualmente.",
            producto_codigo,
        )
        return

    if (
        respuesta.status_code >= httpx.codes.BAD_REQUEST
        and respuesta.status_code != httpx.codes.NOT_FOUND
    ):
        logger.warning(
            "El agente de IA (FastAPI) respondió %s al intentar eliminar "
            "el embedding del producto '%s'. El producto se elimina en "
            "Django de todas formas; el embedding quedará huérfano hasta "
            "limpiarse manualmente. Detalle: %s",
            respuesta.status_code,
            producto_codigo,
            respuesta.text,
        )
