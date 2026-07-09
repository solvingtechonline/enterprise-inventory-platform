"""
Esquemas Pydantic (contrato de la API REST de Inventario).

Son responsabilidad exclusiva de FastAPI (capa de infraestructura/API):
el dominio no conoce Pydantic, solo la entidad `Inventario` pura.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class InventarioRegistrar(BaseModel):
    """Body para registrar (o incrementar) stock de un producto en una empresa."""

    empresa_nit: str = Field(..., min_length=1, max_length=20, description="NIT de la empresa.")
    producto_codigo: str = Field(
        ..., min_length=1, max_length=50, description="Código único del producto."
    )
    cantidad: int = Field(..., gt=0, description="Unidades a registrar (debe ser mayor a 0).")


class InventarioActualizarCantidad(BaseModel):
    """Body para corregir la cantidad absoluta de un registro existente."""

    cantidad: int = Field(..., ge=0, description="Nueva cantidad absoluta (no negativa).")


class InventarioRead(BaseModel):
    """Representación de salida de un registro de inventario."""

    id: int
    empresa_nit: str
    producto_codigo: str
    cantidad: int
    actualizado_en: datetime | None = None

    model_config = {"from_attributes": True}


class ReporteEnviarInput(BaseModel):
    """Body para enviar por correo el PDF de inventario de una empresa."""

    empresa_nit: str = Field(..., min_length=1, max_length=20, description="NIT de la empresa.")
    destinatario: EmailStr = Field(..., description="Correo que recibirá el PDF adjunto.")


class ReporteEnviarRead(BaseModel):
    """Confirmación del envío (o simulación) del reporte por correo."""

    mensaje: str
    modo: str
