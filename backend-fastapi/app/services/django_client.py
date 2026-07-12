"""
Cliente HTTP hacia la API REST de Django.

FastAPI necesita datos de Empresa y Productos para armar el PDF de
Inventario, pero esas tablas son administradas exclusivamente por el
ORM de Django. En lugar de leerlas directamente desde SQLAlchemy (lo
que fusionaría la persistencia), este módulo las consulta vía la API
REST de Django que ya existe, reenviando el mismo token del
Administrador que llegó a FastAPI (un único emisor de autenticación,
válido en ambos backends).
"""

from __future__ import annotations

import httpx
from fastapi import HTTPException, status

from app.core.config import settings

_TIMEOUT_SEGUNDOS = 5.0


def _encabezados(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def obtener_empresa(nit: str, token: str) -> dict:
    """GET /api/empresas/{nit}/ en Django (lectura pública, pero se reenvía el token igual)."""
    url = f"{settings.DJANGO_API_URL}/empresas/{nit}/"
    try:
        respuesta = httpx.get(url, headers=_encabezados(token), timeout=_TIMEOUT_SEGUNDOS)
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No se pudo conectar con el servicio de Empresas (Django).",
        ) from exc

    if respuesta.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe la empresa con NIT {nit}.",
        )
    if respuesta.status_code >= status.HTTP_400_BAD_REQUEST:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="El servicio de Empresas (Django) respondió con un error inesperado.",
        )
    return respuesta.json()


def obtener_productos_por_empresa(nit: str, token: str) -> list[dict]:
    """GET /api/productos/?empresa={nit} en Django (requiere rol Administrador)."""
    url = f"{settings.DJANGO_API_URL}/productos/"
    try:
        respuesta = httpx.get(
            url,
            params={"empresa": nit},
            headers=_encabezados(token),
            timeout=_TIMEOUT_SEGUNDOS,
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No se pudo conectar con el servicio de Productos (Django).",
        ) from exc

    if respuesta.status_code >= status.HTTP_400_BAD_REQUEST:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="El servicio de Productos (Django) respondió con un error inesperado.",
        )
    return respuesta.json()


def obtener_todos_los_productos(token: str) -> list[dict]:
    """
    GET /api/productos/ en Django, sin filtro de empresa.

    Reutiliza el mismo endpoint de `ProductoViewSet` que ya usa
    `obtener_productos_por_empresa`: el filtro `empresa` ya es opcional
    en ese ViewSet (ver `apps.productos.views.ProductoViewSet.get_queryset`
    en Django), así que no se agrega ni modifica nada en ese módulo. Se
    usa para resolver, en un solo llamado, los datos completos
    (nombre, precios, empresa) de los productos que la búsqueda
    semántica del agente de IA devuelve por código (`app.api.ia`).
    """
    url = f"{settings.DJANGO_API_URL}/productos/"
    try:
        respuesta = httpx.get(
            url, headers=_encabezados(token), timeout=_TIMEOUT_SEGUNDOS
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No se pudo conectar con el servicio de Productos (Django).",
        ) from exc

    if respuesta.status_code >= status.HTTP_400_BAD_REQUEST:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="El servicio de Productos (Django) respondió con un error inesperado.",
        )
    return respuesta.json()
