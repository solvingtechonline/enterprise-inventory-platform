"""
Prueba minima de verificacion de instalacion aislada del paquete de dominio.
Este paquete NO debe depender de Django, FastAPI ni de ningun framework web.
"""
import lite_thinking_domain


def test_domain_package_is_importable():
    """El paquete de dominio debe poder importarse sin ninguna dependencia externa."""
    assert lite_thinking_domain is not None
