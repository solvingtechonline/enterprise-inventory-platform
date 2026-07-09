"""
Modelo SQLAlchemy de la tabla `inventario`.

FastAPI/SQLAlchemy es dueño EXCLUSIVO de esta tabla. No se declara una
ForeignKey real hacia las tablas `empresa` / `producto` porque esas
tablas son administradas por el ORM de Django en el mismo Postgres:
Inventario guarda solo la referencia por valor (NIT, código), nunca
fusiona ni importa los modelos de Django.

Este es un detalle de infraestructura: no debe filtrarse a la capa de
dominio (`lite_thinking_domain`), que solo conoce la entidad `Inventario`
pura y el puerto `InventarioRepository`.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class InventarioModel(Base):
    """Fila física de la tabla `inventario`."""

    __tablename__ = "inventario"
    __table_args__ = (
        UniqueConstraint(
            "empresa_nit", "producto_codigo", name="uq_inventario_empresa_producto"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    empresa_nit: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    producto_codigo: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
