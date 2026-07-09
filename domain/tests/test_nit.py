"""Pruebas unitarias del objeto de valor Nit."""
import pytest
from lite_thinking_domain.value_objects.nit import Nit


@pytest.mark.parametrize(
    "valor",
    ["900123456", "900123456-7", "12345", "123456789012345"],
)
def test_nit_valido_se_construye(valor):
    nit = Nit(valor)
    assert str(nit) == valor


@pytest.mark.parametrize(
    "valor",
    [
        "",
        "abc",
        "123",  # menos de 5 dígitos
        "1234567890123456",  # más de 15 dígitos
        "900123456-77",  # dígito de verificación de más de un dígito
        "900-123456",
    ],
)
def test_nit_invalido_lanza_error(valor):
    with pytest.raises(ValueError):
        Nit(valor)
