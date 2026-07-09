# Agente de IA — Ingesta de embeddings

*Complementa `docs/agente_ia_decision_proveedor.md`. El agente de IA está
implementado dentro de FastAPI, reutilizando la conexión ya existente a
PostgreSQL.*

## Piezas implementadas

- **Puerto de dominio `GeneradorEmbeddings`**
  (`domain/src/lite_thinking_domain/repositories/generador_embeddings.py`):
  contrato `generar(texto: str) -> list[float]`, sin dependencia de
  ningún proveedor concreto ni de su SDK (Arquitectura Limpia, mismo
  patrón que los repositorios de persistencia).
- **Excepción de dominio `ErrorGeneracionEmbedding`**
  (`domain/src/lite_thinking_domain/exceptions.py`): pura, sin conocer
  HTTP ni el SDK de ningún proveedor; permite que un fallo del
  proveedor de IA se traduzca a un error HTTP puntual sin tumbar el
  microservicio.
- **Servicio de dominio `EmbeddingProductoService`**
  (`domain/src/lite_thinking_domain/services/embedding_producto_service.py`):
  la regla de "cómo se genera y se guarda un embedding" vive aquí, no
  suelta en un endpoint de FastAPI. Orquesta el puerto de generación y el
  puerto de persistencia (ambos inyectados); si ya existe un embedding
  para el producto, lo reemplaza en vez de duplicarlo.
- **Adaptador de persistencia `SQLAlchemyEmbeddingProductoRepository`**
  (`backend-fastapi/app/repositories/sqlalchemy_embedding_producto_repository.py`):
  implementa el puerto sobre la tabla `producto_embedding`, incluida
  `buscar_similares` (con el operador de distancia coseno de pgvector),
  usada por el endpoint de búsqueda semántica — ver
  `docs/agente_ia_busqueda_semantica.md`.
- **Adaptador del proveedor por defecto `GeminiGeneradorEmbeddings`**
  (`backend-fastapi/app/services/gemini_embeddings_provider.py`): llama
  a `gemini-embedding-001` (Google) vía `httpx`, sin agregar un SDK
  nuevo. Traduce timeouts, errores de conexión, credenciales rechazadas
  (401/403), límite de tasa (429) y una dimensión de vector inesperada
  a `ErrorGeneracionEmbedding`.
- **Adaptador alternativo `OpenAIGeneradorEmbeddings`**
  (`backend-fastapi/app/services/openai_embeddings_provider.py`): llama a
  `text-embedding-3-small` (OpenAI), seleccionable con
  `EMBEDDINGS_PROVIDER=openai`. Traduce
  `AuthenticationError`, `APITimeoutError`, `APIConnectionError`,
  `RateLimitError`, `APIStatusError` y una dimensión de vector inesperada
  a `ErrorGeneracionEmbedding`.
- **Endpoint `POST /api/ia/embeddings`**
  (`backend-fastapi/app/api/ia.py`, requiere rol Administrador): recibe
  `empresa_nit` + `producto_codigo`, busca el producto reutilizando el
  filtro ya existente `GET /api/productos/?empresa=<nit>` de Django (sin
  agregar un endpoint nuevo en ese módulo), arma el texto fuente
  (nombre + características + monedas de precio) y genera/guarda el
  embedding vigente. Si el proveedor de IA falla, responde
  `502 Bad Gateway` con el detalle, sin afectar el resto del servicio
  (Inventario, PDF, correo siguen funcionando).

## Decisiones de alcance

- La ingesta de embeddings es explícita: se dispara llamando al endpoint
  con el código del producto, no automáticamente al crear/editar un
  Producto en Django.
- La respuesta HTTP no expone el vector completo; devuelve solo su
  dimensión, como evidencia de que se generó correctamente.
