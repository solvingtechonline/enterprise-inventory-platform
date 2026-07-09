from rest_framework.viewsets import ModelViewSet

from apps.autenticacion.permissions import EsAdministrador
from apps.productos.models import Producto
from apps.productos.serializers import ProductoSerializer
from apps.productos.services.fastapi_ia_client import ingestar_embedding_async_seguro


class ProductoViewSet(ModelViewSet):
    """
    CRUD de Producto, asociado a Empresa.

    Supuesto documentado: la especificación solo exime de
    autenticación la visualización de Empresas por el rol Externo; no
    menciona a Externo respecto de Productos. Por lo tanto, Productos
    requiere rol Administrador para todas las operaciones, incluida la
    lectura, siguiendo el principio de seguridad por defecto.

    Filtro opcional por Empresa: /api/productos/?empresa=<nit>

    Ingesta automática de embeddings: al crear o editar un Producto,
    se dispara `POST /api/ia/embeddings` en FastAPI (ver
    `perform_create`/`perform_update` y
    `apps.productos.services.fastapi_ia_client`) para que el agente de
    IA quede con el embedding vigente sin requerir una llamada manual
    aparte. El endpoint manual se mantiene disponible para
    reingestar histórico o para recuperarse de un fallo puntual del
    agente de IA en el momento del guardado.
    """

    queryset = Producto.objects.select_related("empresa").prefetch_related("precios")
    serializer_class = ProductoSerializer
    permission_classes = [EsAdministrador]

    def get_queryset(self):
        queryset = super().get_queryset()
        nit_empresa = self.request.query_params.get("empresa")
        if nit_empresa:
            queryset = queryset.filter(empresa__nit=nit_empresa)
        return queryset

    def _token_actual(self) -> str:
        """
        Extrae el JWT crudo del header `Authorization` de la petición
        entrante, para reenviarlo a FastAPI (mismo emisor de
        autenticación en ambos backends; ver
        `apps.productos.services.fastapi_ia_client`).
        """
        encabezado = self.request.headers.get("Authorization", "")
        return encabezado.removeprefix("Bearer ").strip()

    def _disparar_ingesta_embedding(self, producto: Producto) -> None:
        ingestar_embedding_async_seguro(
            empresa_nit=producto.empresa.nit,
            producto_codigo=producto.codigo,
            token=self._token_actual(),
        )

    def perform_create(self, serializer):
        producto = serializer.save()
        self._disparar_ingesta_embedding(producto)

    def perform_update(self, serializer):
        producto = serializer.save()
        self._disparar_ingesta_embedding(producto)
