from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema, extend_schema_view
from rest_framework.viewsets import ModelViewSet

from apps.autenticacion.permissions import LecturaLibreEscrituraAdministrador
from apps.empresas.models import Empresa
from apps.empresas.serializers import EmpresaSerializer
from apps.productos.services.eliminacion_producto import (
    limpiar_embedding,
    verificar_sin_stock,
)

_EJEMPLO_EMPRESA = OpenApiExample(
    "Empresa de ejemplo",
    value={
        "nit": "900123456-7",
        "nombre": "Los Asociados S.A.S.",
        "direccion": "Cra 8g #90",
        "telefono": "3004444430",
    },
    request_only=False,
    response_only=False,
)


@extend_schema_view(
    list=extend_schema(
        tags=["Empresas"],
        summary="Listar empresas",
        description=(
            "Devuelve todas las empresas registradas. No requiere "
            "autenticación: es el punto de acceso del rol Externo, "
            "que solo puede consultar, nunca escribir."
        ),
        examples=[_EJEMPLO_EMPRESA],
        auth=[],
    ),
    retrieve=extend_schema(
        tags=["Empresas"],
        summary="Consultar una empresa por NIT",
        description="Devuelve una empresa puntual. Público, sin autenticación.",
        examples=[_EJEMPLO_EMPRESA],
        auth=[],
    ),
    create=extend_schema(
        tags=["Empresas"],
        summary="Registrar una empresa",
        description=(
            "Requiere rol Administrador (header "
            "`Authorization: Bearer <access>`). El NIT es la llave "
            "primaria: debe ser único y cumplir el formato "
            "`dígitos[-dígito de verificación]`, por ejemplo "
            "`900123456-7`."
        ),
        examples=[_EJEMPLO_EMPRESA],
    ),
    update=extend_schema(
        tags=["Empresas"],
        summary="Editar una empresa (reemplazo completo)",
        description="Requiere rol Administrador. Reemplaza todos los campos editables.",
        examples=[_EJEMPLO_EMPRESA],
    ),
    partial_update=extend_schema(
        tags=["Empresas"],
        summary="Editar una empresa (campos parciales)",
        description="Requiere rol Administrador. Solo actualiza los campos enviados.",
    ),
    destroy=extend_schema(
        tags=["Empresas"],
        summary="Eliminar una empresa",
        description=(
            "Requiere rol Administrador. Elimina en cascada todos los "
            "productos de la empresa **siempre que ninguno tenga stock "
            "registrado en Inventario** (microservicio FastAPI); si "
            "alguno tiene stock, la eliminación se rechaza por completo "
            "y no se borra nada."
        ),
    ),
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
