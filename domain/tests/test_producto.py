"""Pruebas unitarias de la entidad de dominio Producto."""
import pytest
from lite_thinking_domain.entities.producto import Producto
from lite_thinking_domain.value_objects.precio import Precio


def test_producto_valido_se_construye_con_precios_como_value_objects():
    producto = Producto(
        codigo="P-001",
        nombre="Laptop",
        empresa_nit="900123456-7",
        precios=[1500000, 400],
    )
    assert all(isinstance(precio, Precio) for precio in producto.precios)


def test_producto_con_precio_negativo_lanza_error():
    with pytest.raises(ValueError):
        Producto(
            codigo="P-002",
            nombre="Mouse",
            empresa_nit="900123456-7",
            precios=[-10],
        )


def test_producto_sin_codigo_lanza_error():
    with pytest.raises(ValueError):
        Producto(codigo="", nombre="Mouse", empresa_nit="900123456-7", precios=[10])
