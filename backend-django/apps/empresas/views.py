from rest_framework.viewsets import ModelViewSet

from apps.autenticacion.permissions import LecturaLibreEscrituraAdministrador
from apps.empresas.models import Empresa
from apps.empresas.serializers import EmpresaSerializer


class EmpresaViewSet(ModelViewSet):
    """
    CRUD de Empresa.

    - Lectura (GET): pública, sin autenticación (rol Externo).
    - Escritura (POST/PUT/PATCH/DELETE): solo Administrador autenticado.
    """

    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer
    permission_classes = [LecturaLibreEscrituraAdministrador]
    lookup_field = "nit"
