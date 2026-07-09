"""
Configuración de URLs raíz del proyecto.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.autenticacion.urls")),
    path("api/", include("apps.empresas.urls")),
    path("api/", include("apps.productos.urls")),
]
