from rest_framework_simplejwt.views import TokenObtainPairView

from apps.autenticacion.serializers import LoginSerializer


class LoginView(TokenObtainPairView):
    """
    POST /api/auth/login/
    Body: {"correo": "admin@example.com", "password": "..."}
    Respuesta: {"access": "...", "refresh": "..."}
    El access token incluye el claim "rol".
    """

    serializer_class = LoginSerializer
