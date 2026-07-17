"""
Configuración de URLs raíz del proyecto.
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    # Documentación de la API (equivalente a /docs y /redoc de FastAPI):
    # - /api/schema/       -> el spec OpenAPI crudo (YAML)
    # - /api/docs/         -> Swagger UI interactivo
    # - /api/redoc/        -> ReDoc (formato de lectura)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/auth/", include("apps.autenticacion.urls")),
    path("api/", include("apps.empresas.urls")),
    path("api/", include("apps.productos.urls")),
]
