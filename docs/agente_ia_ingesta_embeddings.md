# Agente de IA: ingesta de embeddings

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
  usada por el endpoint de búsqueda semántica. Ver
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
- **Cliente `fastapi_ia_client`**
  (`backend-django/apps/productos/services/fastapi_ia_client.py`):
  dispara `POST /api/ia/embeddings` desde Django, reenviando el token
  del Administrador de la petición actual (mismo emisor de
  autenticación en ambos backends; ver
  `backend-fastapi/app/services/django_client.py` para el sentido
  inverso). Enganchado en `ProductoViewSet.perform_create` /
  `perform_update` (`backend-django/apps/productos/views.py`).

## Ingesta automática al crear/editar un Producto

Desde Django, `ProductoViewSet` dispara la ingesta justo después de
guardar el Producto (creación o edición), sin que el usuario tenga que
llamar al endpoint de FastAPI a mano:

1. El Administrador crea o edita un Producto vía `POST`/`PUT`/`PATCH
   /api/productos/` en Django (ya autenticado con su JWT).
2. Tras guardar el Producto en la base de datos, `ProductoViewSet`
   llama a `fastapi_ia_client.ingestar_embedding_async_seguro(...)`,
   reenviando `empresa.nit`, `producto.codigo` y el mismo token JWT de
   la petición.
3. Esa llamada golpea `POST /api/ia/embeddings` en FastAPI, que genera
   y guarda el embedding vigente exactamente igual que si se hubiera
   llamado manualmente.

**Es "best-effort", a propósito:** si FastAPI no responde, está caído,
o el proveedor de embeddings configurado falla (por ejemplo, sin
`GEMINI_API_KEY`), el Producto en Django **igual queda guardado**; el
cliente solo registra un `warning` en el log y no propaga el error.
Guardar un Producto no debe depender de la disponibilidad del agente
de IA: mismo criterio de "no tumbar el resto del servicio" que ya
usa el propio endpoint de FastAPI ante un fallo del proveedor.

El endpoint manual `POST /api/ia/embeddings` **se mantiene disponible**
para dos casos que la ingesta automática no cubre:

- Reingestar en bloque los productos que ya existían antes de esta
  automatización.
- Reintentar manualmente un producto puntual cuyo embedding no se
  generó porque el agente de IA estaba caído en el momento del
  guardado.

## Decisiones de alcance

- La respuesta HTTP del endpoint no expone el vector completo; devuelve
  solo su dimensión, como evidencia de que se generó correctamente.
- La ingesta automática se dispara de forma síncrona (con un timeout
  corto) dentro del mismo request-response de Django, no vía una cola
  de eventos o un job en background; se consideró suficiente para el
  volumen de este proyecto, y queda documentado como posible mejora
  futura si el volumen de escrituras creciera.
