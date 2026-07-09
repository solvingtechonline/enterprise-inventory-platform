from django.contrib import admin

from apps.empresas.models import Empresa


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ["nit", "nombre", "telefono"]
    search_fields = ["nit", "nombre"]
