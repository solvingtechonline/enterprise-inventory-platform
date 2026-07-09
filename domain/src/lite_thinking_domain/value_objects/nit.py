"""
Objeto de valor: Nit.

Encapsula el formato válido del NIT de una Empresa: solo dígitos, con
un dígito de verificación opcional. Inmutable por diseño (frozen
dataclass), igual que Cantidad.

`PATRON_NIT` es la única fuente de verdad del patrón: tanto el modelo
de Django (validación a nivel de ORM/base de datos) como el serializer
(validación a nivel de API) deben derivar de esta constante o de esta
clase, en vez de reimplementar el patrón cada uno por su lado.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

PATRON_NIT = r"^\d{5,15}(-\d)?$"
_NIT_REGEX = re.compile(PATRON_NIT)


@dataclass(frozen=True)
class Nit:
    """NIT de una Empresa, validado contra `PATRON_NIT`."""

    valor: str

    def __post_init__(self) -> None:
        if not isinstance(self.valor, str) or not _NIT_REGEX.match(self.valor):
            raise ValueError(
                "El NIT debe contener solo dígitos, con un dígito de "
                "verificación opcional (ej. 900123456-7)."
            )

    def __str__(self) -> str:
        return self.valor
