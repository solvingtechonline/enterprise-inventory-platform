"""
Pruebas unitarias del servicio de dominio EmbeddingProductoService.

Usan un repositorio y un generador de embeddings falsos (en memoria),
sin SQLAlchemy, pgvector ni red: el dominio se prueba de forma
totalmente aislada (mismo criterio que domain/tests/test_installation.py).
"""

from __future__ import annotations

import pytest
from lite_thinking_domain.entities.embedding_producto import EmbeddingProducto
from lite_thinking_domain.exceptions import ErrorGeneracionEmbedding
from lite_thinking_domain.repositories.embedding_producto_repository import (
    EmbeddingProductoRepository,
)
from lite_thinking_domain.repositories.generador_embeddings import GeneradorEmbeddings
from lite_thinking_domain.services.embedding_producto_service import (
    EmbeddingProductoService,
)


class _RepositorioEmbeddingFalso(EmbeddingProductoRepository):
    """Repositorio en memoria, solo para probar el servicio de dominio."""

    def __init__(self) -> None:
        self.por_codigo: dict[str, EmbeddingProducto] = {}
        self.distancias: dict[str, float] = {}
        self._siguiente_id = 1

    def guardar(self, embedding: EmbeddingProducto) -> EmbeddingProducto:
        if embedding.id is None:
            embedding.id = self._siguiente_id
            self._siguiente_id += 1
        self.por_codigo[embedding.producto_codigo] = embedding
        return embedding

    def buscar_por_producto(self, producto_codigo: str) -> EmbeddingProducto | None:
        return self.por_codigo.get(producto_codigo)

    def buscar_similares(
        self, vector: list[float], limite: int = 5
    ) -> list[tuple[EmbeddingProducto, float]]:
        # Distancia falsa y determinística: permite a las pruebas del
        # servicio controlar cuáles candidatos quedan dentro/fuera del
        # umbral de relevancia, sin depender de pgvector real.
        pares = [
            (embedding, self.distancias.get(embedding.producto_codigo, 0.0))
            for embedding in self.por_codigo.values()
        ]
        pares.sort(key=lambda par: par[1])
        return pares[:limite]

    def eliminar(self, producto_codigo: str) -> bool:
        return self.por_codigo.pop(producto_codigo, None) is not None


class _GeneradorEmbeddingsFalso(GeneradorEmbeddings):
    """Generador en memoria: vector determinístico o falla simulada, sin red."""

    def __init__(self, vector: list[float] | None = None, falla: bool = False) -> None:
        self._vector = vector if vector is not None else [0.1, 0.2, 0.3]
        self._falla = falla

    def generar(self, texto: str) -> list[float]:
        if self._falla:
            raise ErrorGeneracionEmbedding("Fallo simulado del proveedor de IA.")
        return self._vector


def test_generar_y_guardar_crea_embedding_nuevo():
    repositorio = _RepositorioEmbeddingFalso()
    servicio = EmbeddingProductoService(repositorio, _GeneradorEmbeddingsFalso([0.5, 0.6]))

    resultado = servicio.generar_y_guardar("P-001", "Laptop 15 pulgadas, 16GB RAM")

    assert resultado.producto_codigo == "P-001"
    assert resultado.vector == [0.5, 0.6]
    assert resultado.id is not None
    assert repositorio.buscar_por_producto("P-001") is resultado


def test_generar_y_guardar_reemplaza_embedding_existente_sin_duplicar():
    repositorio = _RepositorioEmbeddingFalso()
    primero = EmbeddingProductoService(
        repositorio, _GeneradorEmbeddingsFalso([0.1, 0.1])
    ).generar_y_guardar("P-001", "Texto viejo")

    segundo = EmbeddingProductoService(
        repositorio, _GeneradorEmbeddingsFalso([0.9, 0.9])
    ).generar_y_guardar("P-001", "Texto nuevo")

    assert primero.id == segundo.id
    assert segundo.vector == [0.9, 0.9]
    assert segundo.texto_fuente == "Texto nuevo"
    assert len(repositorio.por_codigo) == 1


def test_generar_y_guardar_propaga_error_del_proveedor_de_ia():
    repositorio = _RepositorioEmbeddingFalso()
    servicio = EmbeddingProductoService(repositorio, _GeneradorEmbeddingsFalso(falla=True))

    with pytest.raises(ErrorGeneracionEmbedding):
        servicio.generar_y_guardar("P-001", "Texto")

    # La falla del proveedor no debe dejar un registro a medias.
    assert repositorio.buscar_por_producto("P-001") is None


def test_buscar_semanticamente_devuelve_solo_los_candidatos_relevantes():
    repositorio = _RepositorioEmbeddingFalso()
    for codigo, distancia in (("P-001", 0.10), ("P-002", 0.30), ("P-003", 0.95)):
        repositorio.por_codigo[codigo] = EmbeddingProducto(
            id=None, producto_codigo=codigo, texto_fuente=f"texto {codigo}", vector=[0.1]
        )
        repositorio.distancias[codigo] = distancia

    servicio = EmbeddingProductoService(repositorio, _GeneradorEmbeddingsFalso([0.1]))

    resultados = servicio.buscar_semanticamente("laptop para diseño", limite=5)

    # P-003 (distancia 0.95) queda fuera: supera UMBRAL_DISTANCIA_RELEVANTE (0.45).
    codigos = [r.producto_codigo for r in resultados]
    assert codigos == ["P-001", "P-002"]
    assert resultados[0].distancia == 0.10
    assert resultados[0].similitud == pytest.approx(0.90)


def test_buscar_semanticamente_sin_candidatos_relevantes_devuelve_lista_vacia():
    repositorio = _RepositorioEmbeddingFalso()
    repositorio.por_codigo["P-009"] = EmbeddingProducto(
        id=None, producto_codigo="P-009", texto_fuente="texto lejano", vector=[0.9]
    )
    repositorio.distancias["P-009"] = 1.7

    servicio = EmbeddingProductoService(repositorio, _GeneradorEmbeddingsFalso([0.9]))

    assert servicio.buscar_semanticamente("consulta sin relación") == []


def test_buscar_semanticamente_rechaza_consulta_vacia():
    repositorio = _RepositorioEmbeddingFalso()
    servicio = EmbeddingProductoService(repositorio, _GeneradorEmbeddingsFalso())

    with pytest.raises(ValueError):
        servicio.buscar_semanticamente("   ")


def test_buscar_semanticamente_propaga_error_del_proveedor_de_ia():
    repositorio = _RepositorioEmbeddingFalso()
    servicio = EmbeddingProductoService(repositorio, _GeneradorEmbeddingsFalso(falla=True))

    with pytest.raises(ErrorGeneracionEmbedding):
        servicio.buscar_semanticamente("laptop")
