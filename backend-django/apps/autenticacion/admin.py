from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.autenticacion.models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario
    ordering = ["correo"]
    list_display = ["correo", "nombre", "rol", "is_active", "is_staff"]
    search_fields = ["correo", "nombre"]
    fieldsets = (
        (None, {"fields": ("correo", "password")}),
        ("Información personal", {"fields": ("nombre", "rol")}),
        ("Permisos", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("correo", "nombre", "rol", "password1", "password2", "is_staff", "is_active"),
            },
        ),
    )
