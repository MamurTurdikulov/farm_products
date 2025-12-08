from rest_framework import serializers
from products.models import Category, Product, Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class ProductSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "name", "description", "price", "amount", "image", "category_id"
        ]

    def create(self, validated_data):
        category_id = validated_data.pop("category_id")
        category = Category.objects.get(pk=category_id)
        return Product.objects.create(category=category, **validated_data)

    def update(self, instance, validated_data):
        if "category_id" in validated_data:
            category_id = validated_data.pop("category_id")
            instance.category = Category.objects.get(pk=category_id)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product_name", "quantity", "price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer_full_name = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id", "customer_name", "customer_phone", "status",
            "note", "created_at", "items", "customer_full_name"
        ]

    def get_customer_full_name(self, obj):
        return f"{obj.customer_name} {obj.customer_phone}"


class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["status", "note"]