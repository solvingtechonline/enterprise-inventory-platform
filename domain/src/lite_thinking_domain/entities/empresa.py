"""
Entidad de dominio: Empresa.

Representa una Empresa del negocio: NIT, Nombre, Dirección, Teléfono.
Entidad pura: no conoce Django, FastAPI, SQLAlchemy ni HTTP.

La identidad de negocio de una Empresa es su NIT, validado por el
objeto de valor Nit.
"""

from __future__ import annotations

from dataclasses import dataclass

from lite_thinking_domain.value_objects.nit import Nit


@dataclass
class Empresa:
    """Entidad Empresa. El NIT se valida mediante el objeto de valor Nit."""

    nit: Nit
    nombre: str
    direccion: str
    telefono: str

    def __post_init__(self) -> None:
        # Garantiza que 'nit' siempre sea el objeto de valor, incluso si
        # el llamador pasó un str crudo.
        if not isinstance(self.nit, Nit):
            self.nit = Nit(str(self.nit))
        if not self.nombre or not self.nombre.strip():
            raise ValueError("El nombre de la empresa es obligatorio.")
        if not self.direccion or not self.direccion.strip():
            raise ValueError("La dirección de la empresa es obligatoria.")
