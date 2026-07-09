"""Pruebas unitarias de la entidad de dominio ResultadoBusquedaProducto."""
import pytest
from lite_thinking_domain.entities.resultado_busqueda_producto import (
    ResultadoBusquedaProducto,
)


def test_resultado_valido_se_construye():
    resultado = ResultadoBusquedaProducto(
        producto_codigo="P-001", texto_fuente="Laptop 15 pulgadas", distancia=0.2
    )
    assert resultado.producto_codigo == "P-001"
    assert resultado.distancia == 0.2


def test_resultado_sin_producto_codigo_lanza_error():
    with pytest.raises(ValueError):
        ResultadoBusquedaProducto(producto_codigo="", texto_fuente="X", distancia=0.1)


def test_resultado_con_distancia_negativa_lanza_error():
    with pytest.raises(ValueError):
        ResultadoBusquedaProducto(producto_codigo="P-001", texto_fuente="X", distancia=-0.1)


def test_similitud_es_uno_menos_distancia():
    resultado = ResultadoBusquedaProducto(
        producto_codigo="P-001", texto_fuente="X", distancia=0.3
    )
    assert resultado.similitud == pytest.approx(0.7)
