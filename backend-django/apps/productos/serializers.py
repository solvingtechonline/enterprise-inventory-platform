from lite_thinking_domain.value_objects.precio import Precio
from rest_framework import serializers

from apps.productos.models import PrecioProducto, Producto


class PrecioProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrecioProducto
        fields = ["moneda", "valor"]

    def validate_valor(self, value):
        """Delega la regla 'precio no negativo' al dominio (Precio)."""
        try:
            Precio(value)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc
        return value


class ProductoSerializer(serializers.ModelSerializer):
    precios = PrecioProductoSerializer(many=True)

    class Meta:
        model = Producto
        fields = [
            "id",
            "codigo",
            "nombre",
            "caracteristicas",
            "empresa",
            "precios",
            "creado_en",
            "actualizado_en",
        ]
        read_only_fields = ["id", "creado_en", "actualizado_en"]

    def validate_precios(self, value):
        if not value:
            raise serializers.ValidationError(
                "El producto debe tener al menos un precio en alguna moneda."
            )
        monedas = [item["moneda"] for item in value]
        if len(monedas) != len(set(monedas)):
            raise serializers.ValidationError(
                "No se puede repetir la misma moneda más de una vez por producto."
            )
        return value

    def create(self, validated_data):
        precios_data = validated_data.pop("precios")
        producto = Producto.objects.create(**validated_data)
        PrecioProducto.objects.bulk_create(
            [PrecioProducto(producto=producto, **precio) for precio in precios_data]
        )
        return producto

    def update(self, instance, validated_data):
        precios_data = validated_data.pop("precios", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if precios_data is not None:
            instance.precios.all().delete()
            PrecioProducto.objects.bulk_create(
                [PrecioProducto(producto=instance, **precio) for precio in precios_data]
            )

        return instance
