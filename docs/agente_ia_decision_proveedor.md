# Decisión de proveedor de embeddings del Agente de IA

## Proveedor por defecto: Google Gemini (`gemini-embedding-001`, 1536 dimensiones)

El proveedor es **configurable** vía la variable `EMBEDDINGS_PROVIDER`
(`gemini` u `openai`) en `backend-fastapi/.env`, gracias a que el
dominio solo depende del puerto `GeneradorEmbeddings`
(`domain/src/lite_thinking_domain/repositories/generador_embeddings.py`),
sin conocer qué proveedor concreto lo implementa.

## Por qué Gemini por defecto

- **Tiene una capa gratuita real**: la API de Gemini permite generar
  embeddings sin tarjeta de crédito, limitada por tasa de solicitudes
  (suficiente para el volumen de productos de este proyecto). OpenAI,
  en cambio, exige una compra prepagada mínima antes de poder llamar a
  su API de embeddings.
- **Mismo modelo (1536 dimensiones) que ya usaba la tabla
  `producto_embedding`** vía Matryoshka Representation Learning
  (`outputDimensionality=1536`), así que no requirió ningún cambio de
  esquema al agregarlo.
- **No requiere un SDK adicional**: se llama vía HTTP directo con
  `httpx`, que ya era dependencia del proyecto (usada por
  `django_client`), en vez de agregar el SDK oficial de Google para una
  sola operación (generar un embedding a partir de un texto).

## Por qué no Anthropic ni LangChain

- **Anthropic no ofrece una API de embeddings.** El catálogo de
  Anthropic (Claude) está orientado a generación de texto/mensajes, no
  a modelos de embeddings; usarlo obligaría a un rodeo (ej. pedirle a
  un LLM que genere un vector, algo que no es su diseño) que sería
  sobreingeniería innecesaria y menos confiable que un modelo de
  embeddings dedicado.
- **LangChain no es un proveedor, es una capa de orquestación.** Para
  un caso de uso tan acotado (un texto de producto → un vector → una
  búsqueda por similitud en pgvector), introducir LangChain agregaría
  una dependencia y una capa de abstracción adicional sin resolver nada
  que no resuelva ya una llamada directa al proveedor.

## Alternativa de pago: OpenAI (`text-embedding-3-small`)

Sigue disponible como adaptador completo
(`backend-fastapi/app/services/openai_embeddings_provider.py`),
seleccionable con `EMBEDDINGS_PROVIDER=openai`. Es la opción a usar si
se prefiere no depender de Google, o si se necesita mayor throughput
que el permitido por la capa gratuita de Gemini.

## Qué implementa esta decisión

- Extensión `pgvector` habilitada en `lite_thinking_db` (`docs/postgres_setup.sql`).
- Tabla `producto_embedding` (SQLAlchemy, `backend-fastapi/app/models/producto_embedding.py`):
  `producto_codigo`, `texto_fuente`, `vector` (`Vector(1536)`), timestamps.
  Se registra en `Base.metadata` (mismo patrón que `InventarioModel`) para
  que `create_all` la cree al iniciar el microservicio.
- Puerto de dominio `EmbeddingProductoRepository`
  (`domain/src/lite_thinking_domain/repositories/embedding_producto_repository.py`):
  `guardar`, `buscar_por_producto`, `buscar_similares`, `eliminar`. Sin
  ninguna dependencia de pgvector/SQLAlchemy: es dominio puro.
- Entidad de dominio `EmbeddingProducto`
  (`domain/src/lite_thinking_domain/entities/embedding_producto.py`), con
  el vector como `list[float]` puro.
- Adaptador concreto `SQLAlchemyEmbeddingProductoRepository`
  (`backend-fastapi/app/repositories/sqlalchemy_embedding_producto_repository.py`),
  que implementa el puerto usando pgvector.
- Dos adaptadores del puerto `GeneradorEmbeddings`:
  `GeminiGeneradorEmbeddings` (por defecto, gratuito) y
  `OpenAIGeneradorEmbeddings` (alternativa de pago), seleccionables vía
  `EMBEDDINGS_PROVIDER` sin tocar el dominio ni el endpoint.
- Endpoints del agente de IA (`backend-fastapi/app/api/ia.py`): ingesta de
  embeddings y búsqueda semántica. Ver `docs/agente_ia_ingesta_embeddings.md` y
  `docs/agente_ia_busqueda_semantica.md` para el detalle de cada uno.
- Variables de entorno en `backend-fastapi` (`.env.example` y `core/config.py`):
  `EMBEDDINGS_PROVIDER`, `GEMINI_API_KEY`, `GEMINI_EMBEDDINGS_MODEL`,
  `OPENAI_API_KEY`, `OPENAI_EMBEDDINGS_MODEL`, `EMBEDDINGS_DIMENSION`.
- Librerías agregadas a `backend-fastapi/requirements.txt`: `pgvector` (tipo
  de columna) y `openai` (SDK del proveedor de pago alternativo; Gemini
  no necesita SDK propio, usa `httpx`).
