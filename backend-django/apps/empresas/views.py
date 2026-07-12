from rest_framework.viewsets import ModelViewSet

from apps.autenticacion.permissions import LecturaLibreEscrituraAdministrador
from apps.empresas.models import Empresa
from apps.empresas.serializers import EmpresaSerializer
from apps.productos.services.eliminacion_producto import (
    limpiar_embedding,
    verificar_sin_stock,
)


class EmpresaViewSet(ModelViewSet):
    """
    CRUD de Empresa.

    - Lectura (GET): pública, sin autenticación (rol Externo).
    - Escritura (POST/PUT/PATCH/DELETE): solo Administrador autenticado.

    Borrado en cascada de Productos: al eliminar una Empresa, Django
    cascadea el borrado de sus Productos (`Producto.empresa` es
    `on_delete=CASCADE`). Ese borrado en cascada NO pasa por
    `ProductoViewSet.perform_destroy` (es un borrado a nivel de ORM,
    no una petición HTTP a `/api/productos/{id}/`), así que
    `perform_destroy` de este ViewSet reimplementa las mismas dos
    reglas que ya aplican a un Producto individual, en dos pasadas:

    1. Verifica TODOS los productos de la empresa antes de tocar nada.
       Si cualquiera tiene stock, se aborta todo sin haber borrado ni
       limpiado nada (ver `eliminacion_producto.verificar_sin_stock`).
    2. Si todos pasan, limpia el embedding de cada uno (ver
       `eliminacion_producto.limpiar_embedding`) y recién ahí se
       ejecuta el borrado de la Empresa, que dispara el cascade.
    """

    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer
    permission_classes = [LecturaLibreEscrituraAdministrador]
    lookup_field = "nit"

    def _token_actual(self) -> str:
        """
        Extrae el JWT crudo del header `Authorization` de la petición
        entrante, para reenviarlo a FastAPI. Mismo método que
        `ProductoViewSet._token_actual` (se mantiene por-ViewSet, sin
        extraer a un utilitario compartido, siguiendo el mismo patrón
        ya usado en ese ViewSet).
        """
        encabezado = self.request.headers.get("Authorization", "")
        return encabezado.removeprefix("Bearer ").strip()

    def perform_destroy(self, instance):
        token = self._token_actual()
        productos = list(instance.productos.select_related("empresa").all())

        # Pasada 1: verificar TODOS antes de actuar sobre cualquiera.
        for producto in productos:
            verificar_sin_stock(producto, token)

        # Pasada 2: ya verificados sin stock, limpiar embeddings.
        for producto in productos:
            limpiar_embedding(producto, token)

        instance.delete()
