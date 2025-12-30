from rest_framework import serializers
from .models import Order
from products.models import Product

class OrderSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    customer_username = serializers.ReadOnlyField(source='customer.username')
    warning = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'product', 'product_name',
            'requested_quantity_kg', 'fulfilled_quantity_kg',
            'status', 'customer_username', 'created_at', 'warning'
        ]
        read_only_fields = ['customer', 'fulfilled_quantity_kg', 'status']

    def get_warning(self, obj):
        if obj.fulfilled_quantity_kg < obj.requested_quantity_kg:
            return "We do not have that much"
        return None

    def validate_product(self, product):
        if product.total_quantity_kg <= 0:
            raise serializers.ValidationError("This product is currently out of stock.")
        return product

    def validate_requested_quantity_kg(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be positive.")
        return value

    def create(self, validated_data):
        validated_data['customer'] = self.context['request'].user
        return super().create(validated_data)