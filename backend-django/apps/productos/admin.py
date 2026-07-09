from django.contrib import admin

from apps.productos.models import PrecioProducto, Producto


class PrecioProductoInline(admin.TabularInline):
    model = PrecioProducto
    extra = 1


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ["codigo", "nombre", "empresa"]
    search_fields = ["codigo", "nombre"]
    list_filter = ["empresa"]
    inlines = [PrecioProductoInline]
