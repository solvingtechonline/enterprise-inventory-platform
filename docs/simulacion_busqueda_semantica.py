"""
Simulación reproducible del flujo de ingesta + búsqueda semántica,
usando el mismo EmbeddingProductoService de dominio (sin mocks del
propio servicio: se prueba el objeto real), con un generador de
vectores determinístico basado en superposición de palabras clave (en
vez de una llamada real al proveedor de embeddings) y un repositorio en memoria (en vez
de pgvector real).

Por qué así: para ejecutar este script no se requiere una instancia de
PostgreSQL+pgvector corriendo ni una OPENAI_API_KEY real. Esta
simulación deja documentado que la regla de dominio (ingesta ->
búsqueda -> filtro de relevancia) funciona de punta a punta con datos
coherentes. `docs/agente_ia_busqueda_semantica.md` incluye, además, los
comandos curl exactos para repetir la misma prueba contra el stack real
(FastAPI + Postgres/pgvector + proveedor de embeddings) una vez desplegado.
"""
from __future__ import annotations

import os
import sys

_RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_RAIZ_PROYECTO, "domain", "src"))

from lite_thinking_domain.entities.embedding_producto import EmbeddingProducto
from lite_thinking_domain.repositories.embedding_producto_repository import (
    EmbeddingProductoRepository,
)
from lite_thinking_domain.repositories.generador_embeddings import GeneradorEmbeddings
from lite_thinking_domain.services.embedding_producto_service import (
    EmbeddingProductoService,
)

VOCABULARIO = [
    "laptop", "portatil", "computador", "diseño", "grafico", "gaming",
    "juegos", "oficina", "productividad", "teclado", "mecanico",
    "inalambrico", "mouse", "monitor", "pantalla", "silla", "ergonomica",
    "escritorio", "cafe", "grano", "bebida",
]


def vectorizar(texto: str) -> list[float]:
    """Bolsa de palabras normalizada sobre VOCABULARIO (determinístico, sin red)."""
    texto = texto.lower()
    vector = [float(texto.count(palabra)) for palabra in VOCABULARIO]
    norma = sum(v * v for v in vector) ** 0.5
    if norma == 0:
        return [0.0] * len(VOCABULARIO)
    return [v / norma for v in vector]


class GeneradorSimulado(GeneradorEmbeddings):
    def generar(self, texto: str) -> list[float]:
        return vectorizar(texto)


class RepositorioEnMemoria(EmbeddingProductoRepository):
    def __init__(self) -> None:
        self._por_codigo: dict[str, EmbeddingProducto] = {}
        self._siguiente_id = 1

    def guardar(self, embedding: EmbeddingProducto) -> EmbeddingProducto:
        if embedding.id is None:
            embedding.id = self._siguiente_id
            self._siguiente_id += 1
        self._por_codigo[embedding.producto_codigo] = embedding
        return embedding

    def buscar_por_producto(self, producto_codigo: str) -> EmbeddingProducto | None:
        return self._por_codigo.get(producto_codigo)

    def buscar_similares(self, vector, limite=5):
        def distancia_coseno(a, b):
            punto = sum(x * y for x, y in zip(a, b))
            return 1 - punto  # ambos vectores ya están normalizados

        pares = [
            (emb, distancia_coseno(vector, emb.vector))
            for emb in self._por_codigo.values()
        ]
        pares.sort(key=lambda par: par[1])
        return pares[:limite]

    def eliminar(self, producto_codigo: str) -> bool:
        return self._por_codigo.pop(producto_codigo, None) is not None


def main() -> None:
    repositorio = RepositorioEnMemoria()
    generador = GeneradorSimulado()
    servicio = EmbeddingProductoService(repositorio, generador)

    productos = [
        ("P-001", "Laptop 15 pulgadas para diseño grafico. 16GB RAM, tarjeta grafica dedicada. Precios disponibles en: USD, COP."),
        ("P-002", "Teclado mecanico inalambrico para oficina y productividad. Precios disponibles en: USD."),
        ("P-003", "Cafe en grano origen Colombia, bebida de tueste medio. Precios disponibles en: COP."),
    ]

    print("=== 1. Ingesta de productos ===")
    for codigo, texto in productos:
        embedding = servicio.generar_y_guardar(codigo, texto)
        print(f"  Ingresado {codigo}: dimension={len(embedding.vector)}  texto='{texto[:60]}...'")

    print()
    print("=== 2. Busqueda semantica: 'laptop para diseño' ===")
    resultados = servicio.buscar_semanticamente("laptop para diseño", limite=5)
    for r in resultados:
        print(f"  {r.producto_codigo}  distancia={r.distancia:.4f}  similitud={r.similitud:.4f}  texto='{r.texto_fuente[:60]}...'")
    if not resultados:
        print("  (sin resultados relevantes)")

    print()
    print("=== 3. Busqueda semantica: 'teclado para la oficina' ===")
    resultados = servicio.buscar_semanticamente("teclado para la oficina", limite=5)
    for r in resultados:
        print(f"  {r.producto_codigo}  distancia={r.distancia:.4f}  similitud={r.similitud:.4f}  texto='{r.texto_fuente[:60]}...'")
    if not resultados:
        print("  (sin resultados relevantes)")

    print()
    print("=== 4. Busqueda semantica sin relacion: 'boleto de avion a Miami' ===")
    resultados = servicio.buscar_semanticamente("boleto de avion a Miami", limite=5)
    for r in resultados:
        print(f"  {r.producto_codigo}  distancia={r.distancia:.4f}  similitud={r.similitud:.4f}")
    if not resultados:
        print("  (sin resultados relevantes -- correctamente filtrado por UMBRAL_DISTANCIA_RELEVANTE)")


if __name__ == "__main__":
    main()
