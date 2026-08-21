from rest_framework import serializers

from .models import Product, Order


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = 'pk', 'name', 'description', 'price', 'archive', 'preview'


class OrderSerializer(serializers.ModelSerializer):
    # Указываем, что для связи "многие ко многим" нужно брать текстовое поле 'name'
    products = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'  # Поле из модели Product
    )

    class Meta:
        model = Order
        fields = 'pk', 'delivery_address', 'promocode', 'products', 'is_done', 'created_at'