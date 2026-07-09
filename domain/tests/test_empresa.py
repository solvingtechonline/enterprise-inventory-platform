"""Pruebas unitarias de la entidad de dominio Empresa."""
import pytest
from lite_thinking_domain.entities.empresa import Empresa
from lite_thinking_domain.value_objects.nit import Nit


def test_empresa_valida_se_construye_con_nit_como_value_object():
    empresa = Empresa(
        nit="900123456-7",
        nombre="Lite Thinking S.A.S.",
        direccion="Calle 1 # 2-3",
        telefono="+573001234567",
    )
    assert isinstance(empresa.nit, Nit)
    assert str(empresa.nit) == "900123456-7"


def test_empresa_con_nit_invalido_lanza_error():
    with pytest.raises(ValueError):
        Empresa(nit="abc", nombre="X", direccion="Y", telefono="123")


def test_empresa_con_nombre_vacio_lanza_error():
    with pytest.raises(ValueError):
        Empresa(nit="900123456", nombre="   ", direccion="Y", telefono="123")
