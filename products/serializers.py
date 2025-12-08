from rest_framework import serializers
from .models import Category, Product, Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = ["id", "name", "description", "price", "amount", "image", "category"]


class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ["product_id", "quantity", "price"]

    def validate(self, data):
        product_id = data["product_id"]
        qty = data["quantity"]
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError({"product_id": "Product not found."})
        if qty > product.amount:
            raise serializers.ValidationError(
                {"quantity": f"Only {product.amount} available for '{product.name}'."}
            )
        data["product"] = product
        data["price"] = product.price
        return data


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    customer_name = serializers.CharField(max_length=255)
    customer_phone = serializers.CharField(max_length=50)

    class Meta:
        model = Order
        fields = ["customer_name", "customer_phone", "note", "items"]

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            product = item_data.pop("product")
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item_data["quantity"],
                price=item_data["price"],
            )
        return order