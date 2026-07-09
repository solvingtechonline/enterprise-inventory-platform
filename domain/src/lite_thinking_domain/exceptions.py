"""
Excepciones de dominio.

Puras: no dependen de FastAPI, HTTPException, ni de ningún SDK de
proveedor de IA. La capa de infraestructura (FastAPI) las traduce al
código de estado HTTP que corresponda (ej. 502 Bad Gateway); el
dominio solo necesita señalar que un caso de uso falló, sin conocer
HTTP.
"""

from __future__ import annotations


class ErrorGeneracionEmbedding(Exception):
    """
    Se lanza cuando el proveedor de embeddings (infraestructura) no pudo
    generar un vector para un texto dado: timeout, credenciales inválidas,
    error de red, límite de tasa, o una respuesta con una dimensión
    distinta a la esperada.

    El dominio solo conoce que la generación falló; el detalle técnico
    del proveedor concreto (OpenAI u otro) queda en el mensaje, nunca en
    el tipo de excepción, para no acoplar el dominio a un SDK específico.
    """
