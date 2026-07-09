"""Pruebas unitarias del objeto de valor Precio."""
from decimal import Decimal

import pytest
from lite_thinking_domain.value_objects.precio import Precio


@pytest.mark.parametrize("valor", [0, "0", 10.5, "1500000", Decimal("99.99")])
def test_precio_valido_se_construye(valor):
    precio = Precio(valor)
    assert precio.valor >= 0


@pytest.mark.parametrize("valor", [-1, "-0.01", -1500000])
def test_precio_negativo_lanza_error(valor):
    with pytest.raises(ValueError):
        Precio(valor)


def test_precio_no_numerico_lanza_error():
    with pytest.raises(ValueError):
        Precio("no-es-un-numero")
