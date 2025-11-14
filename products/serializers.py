from rest_framework import serializers
from .models import Category, Product, Customer, Order


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source="category",
        queryset=Category.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "category",
            "category_id",
            "description",
            "price",
            "available_kilos",
            "image",
            "created_at",
        ]


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "name", "surname", "phone", "email"]


class OrderSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    customer_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source="customer",
        queryset=Customer.objects.all()
    )

    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source="product",
        queryset=Product.objects.all()
    )

    total_price = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "customer_id",
            "product",
            "product_id",
            "kilos_ordered",
            "note",
            "status",
            "total_price",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("status",)

    def get_total_price(self, obj):
        return obj.total_price()
