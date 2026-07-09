"""
Serializers de autenticación.

El token emitido por Django incluye el claim `rol`, para que FastAPI lo
valide sin necesidad de una autenticación propia.
"""

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class LoginSerializer(TokenObtainPairSerializer):
    """
    Login con correo y contraseña.

    El campo de usuario se toma automáticamente de Usuario.USERNAME_FIELD
    ("correo"), por lo que el payload esperado es:
        {"correo": "...", "password": "..."}
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["rol"] = user.rol
        token["correo"] = user.correo
        return token
