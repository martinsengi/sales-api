from rest_framework import serializers

from ..models import Product


class ProductSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='uuid')

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'category',
        ]
