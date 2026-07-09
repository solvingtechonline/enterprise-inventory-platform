"""
Modelo de usuario para autenticación.

Solo el rol Administrador se autentica: el Externo accede como
visitante de solo lectura, sin usuario ni contraseña. Por eso este
modelo únicamente representa administradores; el campo `rol` se
mantiene porque el token emitido debe incluir el rol, para que
FastAPI pueda validarlo sin volver a autenticar.

La contraseña se almacena encriptada mediante el hasher por defecto de
Django (PBKDF2), heredado de AbstractBaseUser.set_password().
"""

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class UsuarioManager(BaseUserManager):
    """Manager personalizado: el identificador de login es el correo, no un username."""

    def create_user(self, correo: str, password: str | None = None, **extra_fields):
        if not correo:
            raise ValueError("El usuario debe tener un correo electrónico.")
        correo = self.normalize_email(correo)
        extra_fields.setdefault("rol", Usuario.Rol.ADMINISTRADOR)
        usuario = self.model(correo=correo, **extra_fields)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, correo: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("rol", Usuario.Rol.ADMINISTRADOR)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("El superusuario debe tener is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("El superusuario debe tener is_superuser=True.")

        return self.create_user(correo, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """
    Usuario Administrador del sistema.

    El rol Externo no tiene representación en base de datos: no se
    autentica.
    """

    class Rol(models.TextChoices):
        ADMINISTRADOR = "administrador", "Administrador"

    correo = models.EmailField(unique=True, verbose_name="correo electrónico")
    nombre = models.CharField(max_length=150, blank=True)
    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.ADMINISTRADOR)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UsuarioManager()

    USERNAME_FIELD = "correo"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

    def __str__(self) -> str:
        return self.correo
