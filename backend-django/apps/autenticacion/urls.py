from django.urls import path
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import TokenRefreshView

from apps.autenticacion.views import LoginView

TokenRefreshView = extend_schema(
    tags=["Autenticación"],
    summary="Renovar el access token",
    description="Recibe un `refresh` válido y devuelve un nuevo `access`.",
)(TokenRefreshView)

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
