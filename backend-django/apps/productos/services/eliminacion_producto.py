"""
Lógica compartida para borrar un Producto de forma segura.

Se usa tanto desde `ProductoViewSet.perform_destroy` (borrado directo)
como desde `EmpresaViewSet.perform_destroy` (borrado en cascada al
eliminar una Empresa) para no duplicar esta regla en dos lugares.

Se divide en dos pasos independientes (`verificar_sin_stock` y
`limpiar_embedding`) en vez de una sola función todo-en-uno, porque
`EmpresaViewSet` necesita poder ejecutar el paso de verificación para
TODOS los productos de la empresa antes de ejecutar el paso de
limpieza para cualquiera de ellos (ver su `perform_destroy`): si un
producto de los últimos en la lista tiene stock, no queremos haber
limpiado ya el embedding de los primeros.
"""

from __future__ import annotations

from apps.productos.models import Producto
from apps.productos.services.fastapi_ia_client import eliminar_embedding_async_seguro
from apps.productos.services.fastapi_inventario_client import (
    obtener_cantidad_en_inventario,
)
from rest_framework.exceptions import ValidationError


def verificar_sin_stock(producto: Producto, token: str) -> None:
    """
    Lanza `ValidationError` (400) si el producto tiene stock registrado
    en Inventario. No modifica nada; solo verifica.
    """
    cantidad = obtener_cantidad_en_inventario(
        empresa_nit=producto.empresa.nit,
        producto_codigo=producto.codigo,
        token=token,
    )
    if cantidad > 0:
        raise ValidationError(
            f"No se puede eliminar el producto '{producto.codigo}': "
            f"tiene {cantidad} unidades en inventario. "
            "Ajusta el inventario a 0 antes de eliminarlo."
        )


def limpiar_embedding(producto: Producto, token: str) -> None:
    """Dispara la limpieza best-effort del embedding del producto en FastAPI."""
    eliminar_embedding_async_seguro(producto_codigo=producto.codigo, token=token)


def preparar_eliminacion_producto(producto: Producto, token: str) -> None:
    """
    Verifica que el producto no tenga stock y, si pasa, limpia su
    embedding. Se debe llamar ANTES de borrar el producto de la base
    de datos. Usado por `ProductoViewSet.perform_destroy` (verificación
    y limpieza de un único producto, juntas).
    """
    verificar_sin_stock(producto, token)
    limpiar_embedding(producto, token)
