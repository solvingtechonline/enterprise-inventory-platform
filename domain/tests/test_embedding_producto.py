"""Pruebas unitarias de la entidad de dominio EmbeddingProducto."""
import pytest
from lite_thinking_domain.entities.embedding_producto import EmbeddingProducto


def test_embedding_valido_se_construye():
    embedding = EmbeddingProducto(
        producto_codigo="P-001",
        texto_fuente="Laptop 15 pulgadas, 16GB RAM",
        vector=[0.1, 0.2, 0.3],
    )
    assert embedding.producto_codigo == "P-001"
    assert embedding.vector == [0.1, 0.2, 0.3]


def test_embedding_sin_producto_codigo_lanza_error():
    with pytest.raises(ValueError):
        EmbeddingProducto(producto_codigo="", texto_fuente="X", vector=[0.1])


def test_embedding_sin_texto_fuente_lanza_error():
    with pytest.raises(ValueError):
        EmbeddingProducto(producto_codigo="P-001", texto_fuente="  ", vector=[0.1])


def test_embedding_con_vector_vacio_lanza_error():
    with pytest.raises(ValueError):
        EmbeddingProducto(producto_codigo="P-001", texto_fuente="X", vector=[])


def test_reemplazar_vector_actualiza_vector_y_texto():
    embedding = EmbeddingProducto(
        producto_codigo="P-001", texto_fuente="Texto viejo", vector=[0.1]
    )
    embedding.reemplazar_vector([0.9, 0.8], "Texto nuevo")
    assert embedding.vector == [0.9, 0.8]
    assert embedding.texto_fuente == "Texto nuevo"


def test_reemplazar_vector_vacio_lanza_error():
    embedding = EmbeddingProducto(
        producto_codigo="P-001", texto_fuente="Texto", vector=[0.1]
    )
    with pytest.raises(ValueError):
        embedding.reemplazar_vector([], "Texto nuevo")
