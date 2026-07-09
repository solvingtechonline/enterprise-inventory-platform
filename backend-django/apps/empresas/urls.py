from rest_framework.routers import DefaultRouter

from apps.empresas.views import EmpresaViewSet

router = DefaultRouter()
router.register(r"empresas", EmpresaViewSet, basename="empresa")

urlpatterns = router.urls
