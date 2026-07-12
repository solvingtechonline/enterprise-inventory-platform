"""
Cliente HTTP hacia el módulo de Inventario del microservicio FastAPI.

A diferencia de `fastapi_ia_client.py` (best-effort: un fallo ahí nunca
debe impedir guardar/borrar un Producto), este cliente respalda una
verificación de seguridad antes de un borrado: si no podemos confirmar
que un producto no tiene stock, NO es seguro dejarlo borrar. Por eso,
ante cualquier fallo de conexión o respuesta inesperada de FastAPI,
`obtener_cantidad_en_inventario` lanza `ErrorVerificacionInventario`
en vez de tragarse el error con un `logger.warning`: es fail-safe, no
fail-open.
"""

from __future__ import annotations

import logging

import httpx
from django.conf import settings
from rest_framework.exceptions import APIException

logger = logging.getLogger(__name__)

_TIMEOUT_SEGUNDOS = 5.0


class ErrorVerificacionInventario(APIException):
    """
    No se pudo confirmar contra FastAPI si un producto tiene stock.

    Se usa en vez de dejar pasar el borrado "por si acaso": la
    verificación de inventario es una medida de seguridad, no una
    conveniencia, así que un fallo de conectividad debe bloquear la
    operación en vez de ignorarse.
    """

    status_code = 503
    default_detail = (
        "No se pudo verificar el inventario del producto. Intenta de nuevo."
    )
    default_code = "error_verificacion_inventario"


def obtener_cantidad_en_inventario(empresa_nit: str, producto_codigo: str, token: str) -> int:
    """
    Devuelve la cantidad en inventario de un producto en una empresa
    (0 si no hay registro). Llama a
    `GET /api/inventario/verificar-producto` en FastAPI.
    """
    url = f"{settings.FASTAPI_API_URL}/inventario/verificar-producto"
    encabezados = {"Authorization": f"Bearer {token}"}
    parametros = {"empresa_nit": empresa_nit, "producto_codigo": producto_codigo}

    try:
        respuesta = httpx.get(
            url, params=parametros, headers=encabezados, timeout=_TIMEOUT_SEGUNDOS
        )
    except httpx.RequestError as exc:
        logger.error(
            "No se pudo conectar con el agente de Inventario (FastAPI) para "
            "verificar stock del producto '%s'. Se bloquea el borrado por "
            "seguridad.",
            producto_codigo,
        )
        raise ErrorVerificacionInventario() from exc

    if respuesta.status_code == httpx.codes.NOT_FOUND:
        return 0

    if respuesta.status_code >= httpx.codes.BAD_REQUEST:
        logger.error(
            "El agente de Inventario (FastAPI) respondió %s al verificar "
            "stock del producto '%s'. Se bloquea el borrado por seguridad. "
            "Detalle: %s",
            respuesta.status_code,
            producto_codigo,
            respuesta.text,
        )
        raise ErrorVerificacionInventario()

    return respuesta.json()["cantidad"]
