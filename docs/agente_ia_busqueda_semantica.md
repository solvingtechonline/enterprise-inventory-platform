# Agente de IA: búsqueda semántica

*Complementa `docs/agente_ia_decision_proveedor.md` y
`docs/agente_ia_ingesta_embeddings.md`.*

## Dominio (regla de negocio de relevancia)

- **`EmbeddingProductoRepository.buscar_similares`** (puerto) devuelve
  `list[tuple[EmbeddingProducto, float]]`: cada candidato viene con su
  distancia coseno.
- **Entidad `ResultadoBusquedaProducto`**
  (`domain/.../entities/resultado_busqueda_producto.py`): par
  (código de producto, texto fuente, distancia), con una propiedad
  `similitud` de conveniencia. Pura, sin pgvector ni HTTP.
- **`EmbeddingProductoService.UMBRAL_DISTANCIA_RELEVANTE`** (constante
  de dominio, `0.8`): la regla de negocio que responde "¿qué es un
  resultado relevante?". `cosine_distance` de pgvector va de 0
  (idéntico) a 2 (opuesto); 1 es ortogonalidad. Un candidato con
  distancia mayor al umbral se descarta, así haya sido de los
  `limite` más cercanos disponibles en la tabla: el `ORDER BY ... LIMIT`
  de pgvector solo ordena por cercanía, no decide si el resultado tiene
  relación semántica real con la consulta. Esa decisión vive en el
  dominio (`EmbeddingProductoService.buscar_semanticamente`), no en el
  adaptador SQLAlchemy ni en el endpoint de FastAPI.
- **`EmbeddingProductoService.buscar_semanticamente(texto_consulta, limite)`**:
  genera el embedding de la consulta (mismo puerto
  `GeneradorEmbeddings` que la ingesta), trae candidatos vía
  `buscar_similares` y aplica el umbral de relevancia. Devuelve lista
  vacía si ningún candidato es relevante (no es un error).
- Cubierto por pruebas unitarias: `test_resultado_busqueda_producto.py`
  y casos dedicados en `test_embedding_producto_service.py`
  (candidatos relevantes vs. descartados, lista vacía, consulta vacía,
  propagación de error del proveedor). Total del paquete de dominio:
  **43 pruebas, todas en verde** (`poetry run pytest` /
  `python -m pytest` desde `domain/`).

## FastAPI (infraestructura/API)

- **`SQLAlchemyEmbeddingProductoRepository.buscar_similares`**: selecciona
  también la columna de distancia
  (`ProductoEmbeddingModel.vector.cosine_distance(vector).label("distancia")`)
  y devuelve `(entidad, distancia)` por fila. Es la única pieza de
  infraestructura que conoce pgvector.
- **`django_client.obtener_todos_los_productos(token)`**: GET
  `/api/productos/` sin filtro de `empresa`, reutilizando el parámetro
  ya opcional del `ProductoViewSet` existente (`get_queryset`), sin
  requerir cambios en `apps.productos` de Django.
- **`GET /api/ia/buscar`** (`backend-fastapi/app/api/ia.py`, requiere
  rol Administrador, mismo criterio que el resto del módulo de IA):
  - Query params: `consulta` (obligatorio) y `limite` (opcional,
    default 5, 1–20).
  - Llama a `EmbeddingProductoService.buscar_semanticamente` (ya
    filtrado por relevancia).
  - Enriquece cada `producto_codigo` relevante con nombre,
    características y NIT de empresa, resueltos contra Django en un
    único `GET /api/productos/` (`_enriquecer_resultados`). Si un
    código ya no existe en Django (caso borde), se devuelve igual con
    esos campos en `null`, en vez de romper toda la respuesta.
  - Si el proveedor de embeddings falla al generar el vector de la
    consulta → `502 Bad Gateway` (mismo criterio que la ingesta).

## Decisiones de alcance

- La integración visual del buscador en el frontend (`BusquedaSemanticaProductos`,
  panel "Búsqueda con IA" en la vista Productos) y el re-embeddado
  automático al crear/editar un producto en Django (ver
  `docs/agente_ia_ingesta_embeddings.md`) ya están implementados; ambos
  quedaron fuera del alcance en una primera versión de este documento y
  se agregaron después sin requerir cambios en este endpoint
  (`GET /api/ia/buscar` no se modificó).

## Prueba manual documentada

**Contexto de la prueba:** el entorno de desarrollo usado para construir
este proyecto no tiene una instancia real de PostgreSQL+pgvector
corriendo, ni salida de red habilitada hacia el proveedor de embeddings real. Por lo
tanto, la prueba de punta a punta contra el stack real
(`FastAPI + Postgres/pgvector + proveedor de embeddings real`) no se pudo ejecutar en ese
entorno. En su lugar, se documentan **dos cosas**:

1. Una prueba manual reproducible del **caso de uso de dominio real**
   (`EmbeddingProductoService`, la misma clase que usa el endpoint),
   con un generador de vectores determinístico (bolsa de palabras) en
   vez de una llamada real al proveedor de embeddings, y un repositorio en memoria en vez
   de pgvector. Script incluido en
   `docs/simulacion_busqueda_semantica.py`. Esto valida que la regla de
   negocio (ingesta → búsqueda → filtro de relevancia) funciona de
   punta a punta con datos coherentes, sin mockear el servicio bajo
   prueba.
2. Los comandos `curl` exactos para repetir la misma prueba contra el
   endpoint real, una vez desplegado con credenciales del proveedor de embeddings y una
   base de datos con pgvector.

### 1. Evidencia obtenida (simulación de dominio)

Comando ejecutado: `python docs/simulacion_busqueda_semantica.py`

```
=== 1. Ingesta de productos ===
  Ingresado P-001: dimension=21  texto='Laptop 15 pulgadas para diseño grafico. 16GB RAM, tarjeta gr...'
  Ingresado P-002: dimension=21  texto='Teclado mecanico inalambrico para oficina y productividad. P...'
  Ingresado P-003: dimension=21  texto='Cafe en grano origen Colombia, bebida de tueste medio. Preci...'

=== 2. Busqueda semantica: 'laptop para diseño' ===
  P-001  distancia=0.1835  similitud=0.8165  texto='Laptop 15 pulgadas para diseño grafico. 16GB RAM, tarjeta gr...'

=== 3. Busqueda semantica: 'teclado para la oficina' ===
  P-002  distancia=0.3675  similitud=0.6325  texto='Teclado mecanico inalambrico para oficina y productividad. P...'

=== 4. Busqueda semantica sin relacion: 'boleto de avion a Miami' ===
  (sin resultados relevantes -- correctamente filtrado por UMBRAL_DISTANCIA_RELEVANTE)
```

**Qué se buscó y qué devolvió (resumen):**

| Consulta | Producto ingerido más cercano | ¿Relevante? | Resultado |
|---|---|---|---|
| "laptop para diseño" | P-001 (Laptop 15", diseño gráfico) | Sí (similitud 0.82) | Devuelve P-001, correcto |
| "teclado para la oficina" | P-002 (Teclado mecánico, oficina) | Sí (similitud 0.63) | Devuelve P-002, correcto |
| "boleto de avión a Miami" | (ninguno con relación real) | No | Lista vacía, el umbral de relevancia descarta correctamente los 3 productos ingeridos, ninguno relacionado con viajes |

Esto confirma dos cosas a la vez: (a) el flujo ingesta → búsqueda
devuelve el producto correcto cuando existe relación semántica, y (b)
la regla de relevancia de dominio evita devolver "el menos malo" cuando
ningún producto tiene relación real con la consulta.

### 2. Cómo repetir la prueba contra el stack real (FastAPI + pgvector + proveedor de embeddings)

Con el proyecto desplegado (Postgres con pgvector habilitado, Django y
FastAPI corriendo, `OPENAI_API_KEY` configurada) y un token de
Administrador obtenido de `POST /api/auth/login/` en Django:

```bash
# 1. Ingestar 2-3 productos ya creados en Django (ver docs/agente_ia_ingesta_embeddings.md)
curl -X POST http://localhost:8001/api/ia/embeddings \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"empresa_nit": "900123456", "producto_codigo": "P-001"}'

curl -X POST http://localhost:8001/api/ia/embeddings \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"empresa_nit": "900123456", "producto_codigo": "P-002"}'

# 2. Buscar semánticamente
curl -G http://localhost:8001/api/ia/buscar \
  -H "Authorization: Bearer $TOKEN" \
  --data-urlencode "consulta=laptop para diseño gráfico" \
  --data-urlencode "limite=5"
```

Respuesta esperada (forma, no valores exactos: dependen de los
productos reales cargados):

```json
{
  "consulta": "laptop para diseño gráfico",
  "resultados": [
    {
      "producto_codigo": "P-001",
      "nombre": "Laptop 15 pulgadas",
      "caracteristicas": "16GB RAM, tarjeta gráfica dedicada",
      "empresa_nit": "900123456",
      "distancia": 0.18,
      "similitud": 0.82
    }
  ]
}
```

## Estado del agente de IA

- [x] pgvector habilitado en PostgreSQL, con tabla de embeddings de
      productos.
- [x] Endpoint del agente de IA que genera embeddings
      (`POST /api/ia/embeddings`).
- [x] Endpoint del agente de IA que responde búsquedas semánticas
      (`GET /api/ia/buscar`).
- [x] El criterio de relevancia es una regla de dominio, no una
      consulta SQL suelta (`EmbeddingProductoService.UMBRAL_DISTANCIA_RELEVANTE`).
- [x] Prueba manual documentada (arriba).

La integración visual del buscador en el frontend
(`BusquedaSemanticaProductos`) y el re-embeddado automático al
crear/editar un producto en Django ya están implementados; ver
`docs/agente_ia_ingesta_embeddings.md` y la sección "Decisiones de
alcance" arriba.
