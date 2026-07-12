"""
Script de mantenimiento: backfill y limpieza de embeddings de Producto.

NO es parte de la API: no se ejecuta en cada request ni en el startup
de FastAPI. Es una herramienta manual para:

1. Detectar productos que existen en Django pero no tienen embedding
   en `producto_embedding` (por ejemplo, productos creados antes de
   que existiera la ingesta automática, o casos donde falló el
   best-effort de `ingestar_embedding_async_seguro` en Django).
2. Detectar embeddings huérfanos: filas de `producto_embedding` cuyo
   `producto_codigo` ya no existe en Django (el caso que motivó la
   Conversación 4, productos borrados antes de que existiera la
   limpieza automática, o los que se colaron por el borrado en
   cascada de Empresa antes de la Conversación 10).

Reutiliza la infraestructura real del proyecto, no la duplica:
- La conexión a base de datos: `app.db.session.SessionLocal` (misma
  configuración que usa FastAPI, vía `app.core.config.settings`).
- El ensamblaje del caso de uso de embeddings (repositorio SQLAlchemy +
  proveedor Gemini/OpenAI según `EMBEDDINGS_PROVIDER`):
  `app.api.deps.obtener_embedding_producto_service`, la misma factory
  que usa el endpoint `POST /api/ia/embeddings`.
- La construcción del texto que se embebe: `app.api.ia._construir_texto_fuente`,
  la misma función que usa ese endpoint (no se reimplementa la lógica
  de qué texto se le manda al proveedor de IA).
- El cliente HTTP hacia Django: `app.services.django_client.obtener_todos_los_productos`,
  ya existente, sin filtro de empresa.

La única pieza que este script sí resuelve directamente (no había un
método de dominio para esto, ni falta hacía uno para un script de
mantenimiento puntual) es "listar todos los producto_codigo que tienen
fila en producto_embedding": una consulta de solo lectura, directa
contra `ProductoEmbeddingModel`, sin pasar por el puerto de
repositorio del dominio (ese puerto expone operaciones de negocio,
"listar todo" no es una de ellas).

USO:

    cd backend-fastapi
    python scripts/mantenimiento_embeddings.py --token <JWT_ADMIN>

    (modo solo lectura por defecto, no modifica nada)

    python scripts/mantenimiento_embeddings.py --token <JWT_ADMIN> --reingestar
    python scripts/mantenimiento_embeddings.py --token <JWT_ADMIN> --eliminar-huerfanos
    python scripts/mantenimiento_embeddings.py --token <JWT_ADMIN> --eliminar-huerfanos --confirmar

Ver el resto de flags con --help.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sqlalchemy import select

# Permite ejecutar el script desde cualquier directorio (no solo si se
# hizo `cd backend-fastapi` primero): inserta la raíz de backend-fastapi
# (el padre de esta carpeta scripts/) en sys.path, para que `import app...`
# resuelva igual que cuando corre `uvicorn app.main:app` desde ahí.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.api.deps import obtener_embedding_producto_service  # noqa: E402
from app.api.ia import _construir_texto_fuente  # noqa: E402
from app.core.config import settings  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.models.producto_embedding import ProductoEmbeddingModel  # noqa: E402
from app.services import django_client  # noqa: E402
from fastapi import HTTPException  # noqa: E402
from lite_thinking_domain.exceptions import ErrorGeneracionEmbedding  # noqa: E402


def _imprimir_encabezado() -> None:
    print("=" * 70)
    print("Script de mantenimiento de embeddings")
    print(f"  POSTGRES_DB   = {settings.POSTGRES_DB}")
    print(f"  POSTGRES_HOST = {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}")
    print(f"  DJANGO_API_URL = {settings.DJANGO_API_URL}")
    print("=" * 70)


def _detectar(token: str) -> tuple[dict[str, dict], set[str], set[str], set[str]]:
    """
    Devuelve (productos_por_codigo, codigos_django, faltantes, huerfanos).

    - productos_por_codigo: dict completo de Django, código -> producto
      (se necesita completo, no solo el código, para reingestar: hace
      falta nombre/características/precios para construir el texto).
    - faltantes: en Django, sin fila en producto_embedding.
    - huerfanos: fila en producto_embedding, sin producto en Django.
    """
    try:
        productos = django_client.obtener_todos_los_productos(token)
    except HTTPException as exc:
        print(f"\nERROR: no se pudo consultar Django ({exc.status_code}): {exc.detail}")
        sys.exit(1)

    productos_por_codigo = {p["codigo"]: p for p in productos}
    codigos_django = set(productos_por_codigo.keys())

    db = SessionLocal()
    try:
        codigos_embedding = set(
            db.execute(select(ProductoEmbeddingModel.producto_codigo)).scalars().all()
        )
    finally:
        db.close()

    faltantes = codigos_django - codigos_embedding
    huerfanos = codigos_embedding - codigos_django
    return productos_por_codigo, codigos_django, faltantes, huerfanos


def _reportar_deteccion(faltantes: set[str], huerfanos: set[str]) -> None:
    print(f"\nProductos en Django SIN embedding ({len(faltantes)}):")
    for codigo in sorted(faltantes):
        print(f"  - {codigo}")
    if not faltantes:
        print("  (ninguno)")

    print(f"\nEmbeddings HUÉRFANOS, sin producto en Django ({len(huerfanos)}):")
    for codigo in sorted(huerfanos):
        print(f"  - {codigo}")
    if not huerfanos:
        print("  (ninguno)")


def _reingestar(productos_por_codigo: dict[str, dict], faltantes: set[str]) -> None:
    if not faltantes:
        print("\nNada que reingestar.")
        return

    db = SessionLocal()
    try:
        servicio = next(obtener_embedding_producto_service(db))
        exitos: list[str] = []
        fallos: list[tuple[str, str]] = []

        for codigo in sorted(faltantes):
            producto = productos_por_codigo[codigo]
            texto_fuente = _construir_texto_fuente(producto)
            try:
                servicio.generar_y_guardar(codigo, texto_fuente)
                exitos.append(codigo)
                print(f"  OK    {codigo}")
            except ErrorGeneracionEmbedding as exc:
                fallos.append((codigo, str(exc)))
                print(f"  FALLO {codigo}: {exc}")
            except Exception as exc:  # noqa: BLE001 - se reporta y se sigue con el resto
                fallos.append((codigo, str(exc)))
                print(f"  FALLO {codigo}: {exc}")
        # No hace falta db.commit() aquí: SQLAlchemyEmbeddingProductoRepository.guardar
        # ya comitea internamente en cada llamada (ver su código), fila por fila.
    finally:
        db.close()

    print(f"\nReingesta: {len(exitos)} exitosos, {len(fallos)} fallidos.")
    for codigo, motivo in fallos:
        print(f"  - {codigo}: {motivo}")


def _eliminar_huerfanos(huerfanos: set[str], confirmar_flag: bool) -> None:
    if not huerfanos:
        print("\nNo hay huérfanos que eliminar.")
        return

    if not confirmar_flag:
        respuesta = input(
            f"\n¿Eliminar {len(huerfanos)} embedding(s) huérfano(s)? "
            "Esta acción no se puede deshacer. Escribe 'si' para confirmar: "
        )
        if respuesta.strip().lower() != "si":
            print("Cancelado. No se eliminó nada.")
            return

    db = SessionLocal()
    try:
        servicio = next(obtener_embedding_producto_service(db))
        eliminados = 0
        for codigo in sorted(huerfanos):
            if servicio.eliminar(codigo):
                eliminados += 1
                print(f"  ELIMINADO {codigo}")
        # Mismo caso que en _reingestar: SQLAlchemyEmbeddingProductoRepository.eliminar
        # ya comitea internamente, no hace falta un db.commit() aparte aquí.
    finally:
        db.close()

    print(f"\nEliminados: {eliminados} de {len(huerfanos)} huérfanos.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Backfill y limpieza de embeddings de Producto (herramienta manual)."
    )
    parser.add_argument(
        "--token",
        required=True,
        help="JWT de un usuario Administrador de Django (mismo que usa la app; "
        "requerido porque este script consulta la API de Django).",
    )
    parser.add_argument(
        "--reingestar",
        action="store_true",
        help="Genera y guarda el embedding de los productos detectados sin uno.",
    )
    parser.add_argument(
        "--eliminar-huerfanos",
        action="store_true",
        help="Elimina las filas de producto_embedding sin producto correspondiente en Django.",
    )
    parser.add_argument(
        "--confirmar",
        action="store_true",
        help="Salta la confirmación interactiva al usar --eliminar-huerfanos "
        "(para uso no interactivo, ej. cron/CI).",
    )
    args = parser.parse_args()

    _imprimir_encabezado()
    productos_por_codigo, _codigos_django, faltantes, huerfanos = _detectar(args.token)
    _reportar_deteccion(faltantes, huerfanos)

    if not args.reingestar and not args.eliminar_huerfanos:
        print("\nModo solo lectura (por defecto). Nada fue modificado.")
        print("Usa --reingestar y/o --eliminar-huerfanos para actuar sobre lo detectado.")
        return

    if args.reingestar:
        print("\n--- Reingestando productos faltantes ---")
        _reingestar(productos_por_codigo, faltantes)

    if args.eliminar_huerfanos:
        print("\n--- Eliminando embeddings huérfanos ---")
        _eliminar_huerfanos(huerfanos, args.confirmar)


if __name__ == "__main__":
    main()
