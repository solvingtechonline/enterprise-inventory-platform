from rest_framework.viewsets import ModelViewSet

from apps.autenticacion.permissions import EsAdministrador
from apps.productos.models import Producto
from apps.productos.serializers import ProductoSerializer


class ProductoViewSet(ModelViewSet):
    """
    CRUD de Producto, asociado a Empresa.

    Supuesto documentado: la especificación solo exime de
    autenticación la visualización de Empresas por el rol Externo; no
    menciona a Externo respecto de Productos. Por lo tanto, Productos
    requiere rol Administrador para todas las operaciones, incluida la
    lectura, siguiendo el principio de seguridad por defecto.

    Filtro opcional por Empresa: /api/productos/?empresa=<nit>
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
