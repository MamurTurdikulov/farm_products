from rest_framework import serializers
from .models import Order, OrderItem, Cart, CartItem
from products.models import Product


# Minimal inline product serializer
class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'quantity']


class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'quantity', 'price']


class OrderItemCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating order items"""

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']
        read_only_fields = ['price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total_amount', 'created_at', 'updated_at', 'items']
        read_only_fields = ['user', 'total_amount', 'created_at', 'updated_at']


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating orders with items"""
    items = OrderItemCreateSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = ['status', 'items']
        read_only_fields = ['total_amount']

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Order must have at least one item.")
        return value

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        request = self.context.get('request')

        # Calculate total amount
        total_amount = 0
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']

            # Validate stock
            if product.quantity < quantity:
                raise serializers.ValidationError(
                    f"Insufficient stock for {product.name}. Available: {product.quantity}, Requested: {quantity}"
                )

            # Set price from product
            item_data['price'] = product.price
            total_amount += float(product.price) * quantity

        # Create order
        order = Order.objects.create(
            user=request.user,
            total_amount=total_amount,
            **validated_data
        )

        # Create order items
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        return order


class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'updated_at']
        read_only_fields = ['user']