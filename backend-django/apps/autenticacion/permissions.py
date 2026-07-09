"""
Permisos basados en rol (los permisos de rol se validan siempre en el
backend, nunca solo en el frontend).
"""

from rest_framework.permissions import SAFE_METHODS, BasePermission


def es_administrador(request) -> bool:
    usuario = request.user
    return bool(
        usuario
        and usuario.is_authenticated
        and getattr(usuario, "rol", None) == "administrador"
    )


class EsAdministrador(BasePermission):
    """Requiere un usuario autenticado con rol Administrador para cualquier método."""

    message = "Esta acción requiere rol Administrador."

    def has_permission(self, request, view) -> bool:
        return es_administrador(request)


class LecturaLibreEscrituraAdministrador(BasePermission):
    """
    Lectura (GET/HEAD/OPTIONS) permitida a cualquiera, incluido el usuario
    Externo sin autenticación. Escritura reservada al
    Administrador autenticado.
    """

    message = "Esta acción requiere rol Administrador."

    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return es_administrador(request)
