from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.autenticacion.serializers import LoginSerializer


@extend_schema(
    tags=["Autenticación"],
    summary="Iniciar sesión (rol Administrador)",
    description=(
        "Autentica con correo y contraseña. Solo existen usuarios con "
        "rol Administrador; el rol Externo consulta Empresas sin "
        "autenticarse. El `access` devuelto incluye el claim `rol` y "
        "es válido tanto para esta API (Django) como para el "
        "microservicio de Inventario/IA (FastAPI)."
    ),
    examples=[
        OpenApiExample(
            "Credenciales",
            value={"correo": "admin@example.com", "password": "contraseña-segura"},
            request_only=True,
        ),
        OpenApiExample(
            "Tokens emitidos",
            value={
                "refresh": "eyJhbGciOiJIUzI1NiIs...",
                "access": "eyJhbGciOiJIUzI1NiIs...",
            },
            response_only=True,
        ),
    ],
)
class LoginView(TokenObtainPairView):
    """
    POST /api/auth/login/
    Body: {"correo": "admin@example.com", "password": "..."}
    Respuesta: {"access": "...", "refresh": "..."}
    El access token incluye el claim "rol".
    """

    serializer_class = LoginSerializer
