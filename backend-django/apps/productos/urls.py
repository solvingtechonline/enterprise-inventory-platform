from rest_framework.routers import DefaultRouter

from apps.productos.views import ProductoViewSet

router = DefaultRouter()
router.register(r"productos", ProductoViewSet, basename="producto")

urlpatterns = router.urls
