from rest_framework import serializers
from .models import Product
from accounts.models import User

class ProductSerializer(serializers.ModelSerializer):
    seller_username = serializers.ReadOnlyField(source='seller.username')

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price_per_kg', 'total_quantity_kg', 'seller', 'seller_username']
        read_only_fields = ['seller']

    def validate_total_quantity_kg(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative.")
        return value