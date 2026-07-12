"""
Puerto de dominio: GeneradorEmbeddings.

Define el contrato para convertir un texto en un vector de embedding,
sin que el dominio conozca el proveedor concreto (OpenAI, Anthropic,
LangChain o un modelo local) ni su SDK. Mismo patrón de Arquitectura
Limpia que los repositorios de persistencia: el requisito funcional
(generar embeddings) es lo que importa al dominio, no el proveedor.

La implementación concreta (llamada real a la API de OpenAI, según
docs/agente_ia_decision_proveedor.md) vive en el microservicio FastAPI,
igual que las implementaciones de los repositorios de persistencia.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class GeneradorEmbeddings(ABC):
    """Puerto de infraestructura: genera el vector de embedding de un texto."""

    @abstractmethod
    def generar(self, texto: str) -> list[float]:
        """
        Convierte `texto` en un vector de embedding.

        La implementación debe lanzar
        `lite_thinking_domain.exceptions.ErrorGeneracionEmbedding` si el
        proveedor falla (timeout, credenciales, red, límite de tasa,
        etc.), en vez de dejar escapar la excepción específica del SDK
        usado. Así el dominio y la capa de API no quedan acoplados a
        un proveedor concreto.
        """
