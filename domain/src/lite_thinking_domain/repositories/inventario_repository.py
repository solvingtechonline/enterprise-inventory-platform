"""
Puerto de repositorio de Inventario (interfaz de persistencia).

Define el contrato que cualquier infraestructura de persistencia debe
cumplir para que el dominio pueda operar sobre Inventario, sin conocer
SQLAlchemy ni ningún detalle técnico (Arquitectura Limpia).

La implementación concreta (SQLAlchemy) vive en el microservicio
FastAPI, que es el dueño exclusivo de la tabla Inventario.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from lite_thinking_domain.entities.inventario import Inventario


class InventarioRepository(ABC):
    """Puerto de persistencia para la entidad Inventario."""

    @abstractmethod
    def obtener_por_id(self, inventario_id: int) -> Inventario | None:
        """Busca un registro de inventario por su identificador."""

    @abstractmethod
    def buscar_por_empresa_y_producto(
        self, empresa_nit: str, producto_codigo: str
    ) -> Inventario | None:
        """Busca el registro único de inventario para una empresa y un producto."""

    @abstractmethod
    def listar_por_empresa(self, empresa_nit: str) -> list[Inventario]:
        """Lista todos los registros de inventario de una empresa."""

    @abstractmethod
    def guardar(self, inventario: Inventario) -> Inventario:
        """Crea o actualiza un registro de inventario y devuelve la entidad persistida."""

    @abstractmethod
    def eliminar(self, inventario_id: int) -> bool:
        """Elimina un registro de inventario. Devuelve True si existía y fue eliminado."""
