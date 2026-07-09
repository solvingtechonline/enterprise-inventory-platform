"""
Endpoints REST del agente de IA con pgvector.

Ingesta de embeddings: dado un producto (consultado vía la API REST de
Django), generar su embedding con el proveedor configurado (Gemini por
defecto, gratuito; OpenAI como alternativa de pago) y
guardarlo como el vigente para ese producto.

Búsqueda semántica: dada una consulta en lenguaje natural, generar su
embedding, traer los productos más similares vía
`EmbeddingProductoService.buscar_semanticamente` (que ya aplica la
regla de relevancia de dominio) y enriquecerlos con sus datos de
negocio (nombre, características, empresa) consultados en Django. Ver
docs/agente_ia_busqueda_semantica.md.

Requiere rol Administrador: la especificación solo exime de
autenticación la visualización de Empresas por el rol Externo; no
menciona a Externo respecto del agente de IA. Se aplica el mismo
criterio de seguridad por defecto ya usado en Inventario
(`app.api.deps.requerir_administrador`).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from lite_thinking_domain.exceptions import ErrorGeneracionEmbedding
from lite_thinking_domain.services.embedding_producto_service import (
    LIMITE_BUSQUEDA_POR_DEFECTO,
    EmbeddingProductoService,
)

from app.api.deps import obtener_embedding_producto_service, requerir_administrador
from app.core.security import UsuarioToken
from app.schemas.ia import (
    BusquedaSemanticaRead,
    EmbeddingIngestarInput,
    EmbeddingRead,
    ProductoResultadoBusqueda,
)
from app.services import django_client

router = APIRouter(
    prefix="/api/ia",
    tags=["agente-ia"],
    dependencies=[Depends(requerir_administrador)],
)


def _construir_texto_fuente(producto: dict) -> str:
    """
    Arma el texto que se embebe, a partir de los campos de negocio del
    producto (nombre, características y monedas de precio disponibles).

    Vive en esta capa (no en el dominio) porque traduce un dict crudo
    devuelto por la API de Django a un texto plano; el dominio solo
    recibe el texto ya armado (`EmbeddingProductoService.generar_y_guardar`
    no conoce la forma del JSON de Django).
    """
    nombre = (producto.get("nombre") or "").strip()
    caracteristicas = (producto.get("caracteristicas") or "").strip()
    monedas = ", ".join(
        precio.get("moneda", "")
        for precio in producto.get("precios", [])
        if precio.get("moneda")
    )

    partes = [parte for parte in (nombre, caracteristicas) if parte]
    texto = ". ".join(partes)
    if monedas:
        texto = f"{texto}. Precios disponibles en: {monedas}." if texto else (
            f"Precios disponibles en: {monedas}."
        )
    return texto


def _buscar_producto_por_codigo(
    empresa_nit: str, producto_codigo: str, token: str
) -> dict:
    """
    Reutiliza el filtro por empresa ya existente en Django
    (`GET /api/productos/?empresa=<nit>`, ya consumido por
    `app.api.inventario`) y busca el producto por código en memoria.

    Se hace así, en vez de agregar un endpoint de detalle por código en
    Django, para no introducir cambios innecesarios en ese módulo.
    """
    productos = django_client.obtener_productos_por_empresa(empresa_nit, token)
    for producto in productos:
        if producto.get("codigo") == producto_codigo:
            return producto

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=(
            f"No existe el producto con código '{producto_codigo}' "
            f"para la empresa con NIT {empresa_nit}."
        ),
    )


@router.post(
    "/embeddings",
    response_model=EmbeddingRead,
    status_code=status.HTTP_201_CREATED,
    summary="Generar (o regenerar) el embedding vigente de un producto",
)
def ingestar_embedding(
    body: EmbeddingIngestarInput,
    usuario: UsuarioToken = Depends(requerir_administrador),
    servicio: EmbeddingProductoService = Depends(obtener_embedding_producto_service),
) -> EmbeddingRead:
    producto = _buscar_producto_por_codigo(
        body.empresa_nit, body.producto_codigo, usuario.token
    )
    texto_fuente = _construir_texto_fuente(producto)

    if not texto_fuente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "El producto no tiene nombre ni características con las "
                "que construir un texto para embeber."
            ),
        )

    try:
        embedding = servicio.generar_y_guardar(body.producto_codigo, texto_fuente)
    except ErrorGeneracionEmbedding as exc:
        # El proveedor de IA falló (timeout/credenciales/red/dimensión
        # inesperada): se informa como error de dependencia externa, sin
        # tumbar el microservicio — el resto de endpoints (Inventario,
        # PDF, correo) sigue funcionando con normalidad.
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"No se pudo generar el embedding: {exc}",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc

    return EmbeddingRead(
        producto_codigo=embedding.producto_codigo,
        texto_fuente=embedding.texto_fuente,
        dimension=len(embedding.vector),
        actualizado_en=embedding.actualizado_en,
    )


def _enriquecer_resultados(
    resultados: list, token: str
) -> list[ProductoResultadoBusqueda]:
    """
    Resuelve cada `producto_codigo` devuelto por el dominio contra la
    lista completa de productos de Django (un único GET, sin filtro de
    empresa — `django_client.obtener_todos_los_productos`), para
    devolver nombre/características/empresa además de la
    distancia/similitud ya calculadas por
    `EmbeddingProductoService.buscar_semanticamente`.

    Si un producto fue borrado en Django después de embeberse (caso
    borde, no cubierto por la ingesta), se omite del resultado en vez
    de romper la respuesta completa: la búsqueda semántica no es dueña
    de la consistencia de esa tabla.
    """
    if not resultados:
        return []

    productos_por_codigo = {
        producto.get("codigo"): producto
        for producto in django_client.obtener_todos_los_productos(token)
    }

    enriquecidos: list[ProductoResultadoBusqueda] = []
    for resultado in resultados:
        producto = productos_por_codigo.get(resultado.producto_codigo)
        enriquecidos.append(
            ProductoResultadoBusqueda(
                producto_codigo=resultado.producto_codigo,
                nombre=producto.get("nombre") if producto else None,
                caracteristicas=producto.get("caracteristicas") if producto else None,
                empresa_nit=(
                    producto.get("empresa") if producto else None
                ),
                distancia=resultado.distancia,
                similitud=resultado.similitud,
            )
        )
    return enriquecidos


@router.get(
    "/buscar",
    response_model=BusquedaSemanticaRead,
    summary="Búsqueda semántica de productos por consulta en lenguaje natural",
)
def buscar_productos(
    consulta: str = Query(
        ..., min_length=1, description="Consulta en lenguaje natural, ej. 'laptop para diseño'."
    ),
    limite: int = Query(
        LIMITE_BUSQUEDA_POR_DEFECTO,
        ge=1,
        le=20,
        description="Máximo de candidatos a evaluar antes de filtrar por relevancia.",
    ),
    usuario: UsuarioToken = Depends(requerir_administrador),
    servicio: EmbeddingProductoService = Depends(obtener_embedding_producto_service),
) -> BusquedaSemanticaRead:
    try:
        resultados = servicio.buscar_semanticamente(consulta, limite)
    except ErrorGeneracionEmbedding as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"No se pudo generar el embedding de la consulta: {exc}",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc

    return BusquedaSemanticaRead(
        consulta=consulta,
        resultados=_enriquecer_resultados(resultados, usuario.token),
    )
