"""
Servicio de dominio: InventarioService.

Contiene la única regla de negocio no trivial del módulo de Inventario:
si una empresa ya tiene un registro para un producto, registrar de nuevo
ese producto SUMA a la cantidad existente en lugar de crear un duplicado
(la identidad de negocio es empresa_nit + producto_codigo). Esta regla
vive en el dominio para que sea independiente de FastAPI/SQLAlchemy.
"""

from __future__ import annotations

from lite_thinking_domain.entities.inventario import Inventario
from lite_thinking_domain.repositories.inventario_repository import (
    InventarioRepository,
)
from lite_thinking_domain.value_objects.cantidad import Cantidad


class InventarioService:
    """Casos de uso de Inventario, sobre el puerto de repositorio (inyectado)."""

    def __init__(self, repositorio: InventarioRepository) -> None:
        self._repositorio = repositorio

    def registrar_producto(
        self, empresa_nit: str, producto_codigo: str, cantidad: int
    ) -> Inventario:
        """
        Registra unidades de un producto en el inventario de una empresa.

        Si ya existe un registro para esa combinación empresa+producto,
        incrementa la cantidad existente. Si no existe, crea uno nuevo.
        """
        existente = self._repositorio.buscar_por_empresa_y_producto(
            empresa_nit, producto_codigo
        )
        if existente is not None:
            existente.incrementar(cantidad)
            return self._repositorio.guardar(existente)

        nuevo = Inventario(
            empresa_nit=empresa_nit,
            producto_codigo=producto_codigo,
            cantidad=Cantidad(cantidad),
        )
        return self._repositorio.guardar(nuevo)

    def actualizar_cantidad(self, inventario_id: int, nueva_cantidad: int) -> Inventario:
        """Corrige la cantidad de un registro existente a un valor absoluto."""
        registro = self._repositorio.obtener_por_id(inventario_id)
        if registro is None:
            raise ValueError(f"No existe un registro de inventario con id={inventario_id}.")
        registro.establecer_cantidad(nueva_cantidad)
        return self._repositorio.guardar(registro)

    def listar_por_empresa(self, empresa_nit: str) -> list[Inventario]:
        return self._repositorio.listar_por_empresa(empresa_nit)

    def obtener_por_id(self, inventario_id: int) -> Inventario | None:
        return self._repositorio.obtener_por_id(inventario_id)

    def eliminar(self, inventario_id: int) -> bool:
        return self._repositorio.eliminar(inventario_id)
