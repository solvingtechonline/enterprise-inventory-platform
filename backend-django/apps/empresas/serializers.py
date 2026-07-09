from lite_thinking_domain.value_objects.nit import Nit
from rest_framework import serializers

from apps.empresas.models import Empresa


class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = ["nit", "nombre", "direccion", "telefono", "creado_en", "actualizado_en"]
        read_only_fields = ["creado_en", "actualizado_en"]

    def validate_nit(self, value: str) -> str:
        """Delega el formato del NIT al dominio (Nit), única fuente de la regla."""
        try:
            Nit(value)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc
        return value

    def validate_nombre(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError("El nombre no puede estar vacío.")
        return value.strip()

    def validate_direccion(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError("La dirección no puede estar vacía.")
        return value.strip()
