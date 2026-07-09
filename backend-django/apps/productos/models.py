"""
Modelo Producto:
Código, Nombre, Características, Precio en varias monedas, Empresa.

Administrado por el ORM de Django, igual que Empresa.

El precio "en varias monedas" se modela como una tabla relacionada
(PrecioProducto) en vez de columnas fijas por moneda, para poder
registrar cualquier combinación de monedas por producto sin rediseñar
el esquema — sin introducir conversión de tasas en tiempo real, que
no es un requisito y sería sobreingeniería.
"""

from django.core.validators import MinValueValidator
from django.db import models
from lite_thinking_domain.value_objects.precio import PRECIO_MINIMO

from apps.empresas.models import Empresa


class Producto(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=200)
    caracteristicas = models.TextField(blank=True)
    empresa = models.ForeignKey(
        Empresa, on_delete=models.CASCADE, related_name="productos"
    )

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "producto"
        verbose_name_plural = "productos"
        ordering = ["nombre"]

    def __str__(self) -> str:
        return f"{self.codigo} - {self.nombre}"


class PrecioProducto(models.Model):
    class Moneda(models.TextChoices):
        COP = "COP", "Peso colombiano"
        USD = "USD", "Dólar estadounidense"
        EUR = "EUR", "Euro"

    producto = models.ForeignKey(
        Producto, on_delete=models.CASCADE, related_name="precios"
    )
    moneda = models.CharField(max_length=3, choices=Moneda.choices)
    valor = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        # Límite delegado al dominio (Precio): no puede ser negativo.
        validators=[MinValueValidator(PRECIO_MINIMO)],
    )

    class Meta:
        verbose_name = "precio de producto"
        verbose_name_plural = "precios de producto"
        constraints = [
            models.UniqueConstraint(
                fields=["producto", "moneda"], name="precio_unico_por_moneda"
            )
        ]

    def __str__(self) -> str:
        return f"{self.producto.codigo}: {self.valor} {self.moneda}"
