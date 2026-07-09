"""
Validación del token JWT emitido por Django.

Django es la única fuente de autenticación; FastAPI únicamente valida
el token (mismo algoritmo y clave de firma, compartidos vía variables
de entorno) y lee el claim `rol`. FastAPI NO emite tokens, NO tiene su
propia tabla de usuarios y NO reintroduce un flujo de login.
"""

from __future__ import annotations

from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import settings

_bearer_scheme = HTTPBearer(auto_error=False)


def decodificar_token(token: str) -> dict[str, Any]:
    """Decodifica y valida la firma/expiración del JWT emitido por Django."""
    try:
        return jwt.decode(
            token,
            settings.JWT_SIGNING_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


class UsuarioToken:
    """Datos del usuario, extraídos del claim del token de Django."""

    def __init__(self, correo: str | None, rol: str | None, token: str) -> None:
        self.correo = correo
        self.rol = rol
        self.token = token

    @property
    def es_administrador(self) -> bool:
        return self.rol == "administrador"


def obtener_usuario_actual(
    credenciales: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> UsuarioToken:
    """Extrae y valida el usuario a partir del header Authorization: Bearer <token>."""
    if credenciales is None or not credenciales.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere un token de autenticación (emitido por Django).",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decodificar_token(credenciales.credentials)
    return UsuarioToken(
        correo=payload.get("correo"),
        rol=payload.get("rol"),
        token=credenciales.credentials,
    )
