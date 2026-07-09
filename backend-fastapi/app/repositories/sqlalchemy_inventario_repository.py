"""
Adaptador de infraestructura: implementa el puerto `InventarioRepository`
(definido en el dominio) usando SQLAlchemy sobre la tabla `inventario`.

Esta clase es la única pieza que traduce entre la entidad de dominio
`Inventario` (pura) y el modelo físico `InventarioModel` (SQLAlchemy).
Ningún otro módulo debe conocer SQLAlchemy más allá de este archivo y
`app.models.inventario`.
"""

from __future__ import annotations

from lite_thinking_domain.entities.inventario import Inventario
from lite_thinking_domain.repositories.inventario_repository import (
    InventarioRepository,
)
from lite_thinking_domain.value_objects.cantidad import Cantidad
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventario import InventarioModel


def _a_entidad(modelo: InventarioModel) -> Inventario:
    return Inventario(
        id=modelo.id,
        empresa_nit=modelo.empresa_nit,
        producto_codigo=modelo.producto_codigo,
        cantidad=Cantidad(modelo.cantidad),
        actualizado_en=modelo.actualizado_en,
    )


class SQLAlchemyInventarioRepository(InventarioRepository):
    """Implementación concreta del puerto de dominio, vía SQLAlchemy."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def obtener_por_id(self, inventario_id: int) -> Inventario | None:
        modelo = self._db.get(InventarioModel, inventario_id)
        return _a_entidad(modelo) if modelo else None

    def buscar_por_empresa_y_producto(
        self, empresa_nit: str, producto_codigo: str
    ) -> Inventario | None:
        stmt = select(InventarioModel).where(
            InventarioModel.empresa_nit == empresa_nit,
            InventarioModel.producto_codigo == producto_codigo,
        )
        modelo = self._db.execute(stmt).scalar_one_or_none()
        return _a_entidad(modelo) if modelo else None

    def listar_por_empresa(self, empresa_nit: str) -> list[Inventario]:
        stmt = (
            select(InventarioModel)
            .where(InventarioModel.empresa_nit == empresa_nit)
            .order_by(InventarioModel.producto_codigo)
        )
        modelos = self._db.execute(stmt).scalars().all()
        return [_a_entidad(m) for m in modelos]

    def guardar(self, inventario: Inventario) -> Inventario:
        if inventario.id is not None:
            modelo = self._db.get(InventarioModel, inventario.id)
            if modelo is None:
                raise ValueError(
                    f"No existe el registro de inventario id={inventario.id}."
                )
            modelo.cantidad = int(inventario.cantidad)
        else:
            modelo = InventarioModel(
                empresa_nit=inventario.empresa_nit,
                producto_codigo=inventario.producto_codigo,
                cantidad=int(inventario.cantidad),
            )
            self._db.add(modelo)

        self._db.commit()
        self._db.refresh(modelo)
        return _a_entidad(modelo)

    def eliminar(self, inventario_id: int) -> bool:
        modelo = self._db.get(InventarioModel, inventario_id)
        if modelo is None:
            return False
        self._db.delete(modelo)
        self._db.commit()
        return True
