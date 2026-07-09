"""
Puerto de repositorio de EmbeddingProducto (interfaz de persistencia).

Define el contrato que cualquier infraestructura de persistencia debe
cumplir para que el dominio pueda operar sobre embeddings de Producto,
sin conocer pgvector, SQLAlchemy ni ningún driver (Arquitectura Limpia,
mismo patrón que InventarioRepository).

La implementación concreta (SQLAlchemy + pgvector) vive en el
microservicio FastAPI, dueño de esta tabla igual que de Inventario.

Nota sobre búsqueda semántica: `buscar_similares` devuelve, junto
a cada embedding, la distancia coseno calculada por pgvector frente al
vector de consulta. La interfaz expone ese dato crudo porque decidir
qué distancia es "relevante" es una regla de negocio (ver
`EmbeddingProductoService.buscar_semanticamente`), no algo que deba
resolverse dentro del adaptador de persistencia ni quedar implícito en
el simple orden de un `ORDER BY ... LIMIT`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from lite_thinking_domain.entities.embedding_producto import EmbeddingProducto


class EmbeddingProductoRepository(ABC):
    """Puerto de persistencia para la entidad EmbeddingProducto."""

    @abstractmethod
    def guardar(self, embedding: EmbeddingProducto) -> EmbeddingProducto:
        """Crea el embedding de un producto, o reemplaza el vigente, y lo devuelve persistido."""

    @abstractmethod
    def buscar_por_producto(self, producto_codigo: str) -> EmbeddingProducto | None:
        """Busca el embedding vigente de un producto por su código."""

    @abstractmethod
    def buscar_similares(
        self, vector: list[float], limite: int = 5
    ) -> list[tuple[EmbeddingProducto, float]]:
        """
        Devuelve hasta `limite` pares (embedding, distancia_coseno),
        ordenados del más cercano al más lejano frente a `vector`.

        No filtra por relevancia: solo trae los `limite` más cercanos
        que existan en la tabla, aunque estén semánticamente lejos. El
        filtrado de relevancia es responsabilidad del dominio, no de
        este puerto (ver nota de módulo).
        """

    @abstractmethod
    def eliminar(self, producto_codigo: str) -> bool:
        """Elimina el embedding de un producto. Devuelve True si existía y fue eliminado."""
