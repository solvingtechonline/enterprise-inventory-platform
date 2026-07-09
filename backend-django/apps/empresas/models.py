"""
Modelo Empresa: NIT (PK), Nombre, Dirección, Teléfono.

Administrado por el ORM de Django. Nunca por SQLAlchemy.
"""

from django.core.validators import RegexValidator
from django.db import models
from lite_thinking_domain.value_objects.nit import PATRON_NIT

# El patrón vive únicamente en el dominio (lite_thinking_domain.value_objects.nit);
# este validador de Django lo reutiliza en vez de reimplementarlo, para no
# duplicar la regla de negocio.
validador_nit = RegexValidator(
    regex=PATRON_NIT,
    message="El NIT debe contener solo dígitos, con un dígito de verificación opcional (ej. 900123456-7).",
)

validador_telefono = RegexValidator(
    regex=r"^\+?\d{7,15}$",
    message="El teléfono debe contener entre 7 y 15 dígitos, con un '+' opcional al inicio.",
)


class Empresa(models.Model):
    nit = models.CharField(
        max_length=20,
        primary_key=True,
        validators=[validador_nit],
        verbose_name="NIT",
    )
    nombre = models.CharField(max_length=200)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20, validators=[validador_telefono])

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "empresa"
        verbose_name_plural = "empresas"
        ordering = ["nombre"]

    def __str__(self) -> str:
        return f"{self.nombre} ({self.nit})"
