"""
Servicio de dominio: EmbeddingProductoService.

Contiene la regla de "cómo se genera y se guarda el embedding vigente
de un Producto": no es una llamada suelta a un SDK de IA dentro de un
endpoint de FastAPI, sino un caso de uso de dominio que orquesta el
puerto de generación (`GeneradorEmbeddings`) y el puerto de
persistencia (`EmbeddingProductoRepository`), ambos inyectados:
mismo patrón que `InventarioService` con `InventarioRepository`.

Regla de negocio (ya establecida en la entidad `EmbeddingProducto`):
cada producto tiene un único embedding vigente; volver a generarlo
reemplaza el vector y el texto fuente anteriores en vez de crear un
duplicado.
"""

from __future__ import annotations

from lite_thinking_domain.entities.embedding_producto import EmbeddingProducto
from lite_thinking_domain.entities.resultado_busqueda_producto import (
    ResultadoBusquedaProducto,
)
from lite_thinking_domain.repositories.embedding_producto_repository import (
    EmbeddingProductoRepository,
)
from lite_thinking_domain.repositories.generador_embeddings import GeneradorEmbeddings

LIMITE_BUSQUEDA_POR_DEFECTO = 5


class EmbeddingProductoService:
    """
    Caso de uso: generar (o regenerar) el embedding vigente de un
    Producto, y buscar productos por similitud semántica.
    """

    # Regla de negocio: qué distancia coseno se considera "relevante".
    #
    # pgvector's `cosine_distance` va de 0 (vectores idénticos) a 2
    # (vectores opuestos); 1 equivale a ortogonalidad (sin relación
    # semántica). Un resultado con distancia mayor a este umbral se
    # descarta como ruido, aunque pgvector lo haya devuelto por estar
    # entre los `limite` más cercanos disponibles en la tabla: la
    # consulta SQL solo ordena por cercanía, no juzga si el resultado
    # tiene relación real con la búsqueda. Esa evaluación vive aquí,
    # en el dominio, no en el adaptador de persistencia ni en el
    # endpoint de FastAPI.
    #
    # Valor calibrado a partir de un caso real observado: una consulta
    # claramente no relacionada ("tostadora") contra un producto no
    # relacionado (un portátil, descrito con muy poco texto) devolvió
    # 0.51 de distancia y pasaba el umbral anterior (0.8), que estaba
    # demasiado cerca de la ortogonalidad (1.0) para descartar nada. Se
    # bajó a 0.45 para excluir ese caso con margen real, no al límite.
    # Es un valor conservador de partida, no calibrado con un dataset
    # de evaluación del catálogo real; si en producción resulta
    # demasiado estricto (descarta productos que sí deberían aparecer)
    # o demasiado laxo, es la primera constante a ajustar, ya que toda
    # la regla de relevancia vive en esta única línea.
    UMBRAL_DISTANCIA_RELEVANTE: float = 0.45

    def __init__(
        self,
        repositorio: EmbeddingProductoRepository,
        generador: GeneradorEmbeddings,
    ) -> None:
        self._repositorio = repositorio
        self._generador = generador

    def generar_y_guardar(
        self, producto_codigo: str, texto_fuente: str
    ) -> EmbeddingProducto:
        """
        Genera el vector para `texto_fuente` (vía el puerto
        `GeneradorEmbeddings`) y lo guarda como el embedding vigente de
        `producto_codigo`.

        Si ya existía un embedding para ese producto, reemplaza su
        vector y texto fuente (misma identidad de negocio: no se
        duplica la fila). Si el proveedor de IA falla, el adaptador de
        `generador` lanza `ErrorGeneracionEmbedding`; este servicio no
        la atrapa, la deja propagar para que la capa de API decida el
        código de respuesta (así una falla del proveedor no tumba el
        proceso de FastAPI, solo esta operación puntual).
        """
        vector = self._generador.generar(texto_fuente)

        existente = self._repositorio.buscar_por_producto(producto_codigo)
        if existente is not None:
            existente.reemplazar_vector(vector, texto_fuente)
            return self._repositorio.guardar(existente)

        nuevo = EmbeddingProducto(
            producto_codigo=producto_codigo,
            texto_fuente=texto_fuente,
            vector=vector,
        )
        return self._repositorio.guardar(nuevo)

    def buscar_semanticamente(
        self,
        texto_consulta: str,
        limite: int = LIMITE_BUSQUEDA_POR_DEFECTO,
    ) -> list[ResultadoBusquedaProducto]:
        """
        Caso de uso: búsqueda semántica de productos (literal k del PDF).

        1. Genera el embedding de `texto_consulta` (mismo puerto
           `GeneradorEmbeddings` que usa la ingesta).
        2. Trae hasta `limite` candidatos ordenados por cercanía en
           pgvector (puerto `EmbeddingProductoRepository.buscar_similares`).
        3. Aplica la regla de negocio de relevancia
           (`UMBRAL_DISTANCIA_RELEVANTE`): descarta los candidatos cuya
           distancia sea mayor al umbral, para no devolver productos sin
           relación semántica real solo porque eran "los menos lejanos"
           entre lo que hubiera en la tabla.

        Si no hay ningún candidato relevante, devuelve una lista vacía
        (no es un error: es una búsqueda sin resultados coherentes).
        """
        if not texto_consulta or not texto_consulta.strip():
            raise ValueError("El texto de la consulta es obligatorio.")
        if limite < 1:
            raise ValueError("El límite de resultados debe ser al menos 1.")

        vector_consulta = self._generador.generar(texto_consulta)
        candidatos = self._repositorio.buscar_similares(vector_consulta, limite)

        resultados = [
            ResultadoBusquedaProducto(
                producto_codigo=embedding.producto_codigo,
                texto_fuente=embedding.texto_fuente,
                distancia=distancia,
            )
            for embedding, distancia in candidatos
        ]
        return [
            resultado
            for resultado in resultados
            if resultado.distancia <= self.UMBRAL_DISTANCIA_RELEVANTE
        ]

    def eliminar(self, producto_codigo: str) -> bool:
        """
        Elimina el embedding vigente de un producto (si existía).

        Caso de uso complementario a `generar_y_guardar`: cuando un
        Producto se borra en Django, su embedding en pgvector queda
        huérfano si nadie lo limpia (ver `app.api.ia`, endpoint
        `DELETE /api/ia/embeddings/{producto_codigo}`). Delega
        directamente en el puerto de repositorio, mismo patrón que
        `InventarioService.eliminar`.
        """
        return self._repositorio.eliminar(producto_codigo)
