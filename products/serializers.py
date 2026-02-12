from rest_framework import serializers
from .models import Product, Category
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    seller = UserSerializer(read_only=True)
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    in_stock = serializers.BooleanField(read_only=True)
    low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'seller', 'seller_name', 'category', 'category_name',
            'name', 'description', 'price', 'quantity', 'image',
            'is_active', 'created_at', 'updated_at', 'in_stock', 'low_stock'
        ]
        read_only_fields = ['seller', 'created_at', 'updated_at']

    def create(self, validated_data):
        """Create product with current user as seller"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['seller'] = request.user
        return super().create(validated_data)

    def validate_price(self, value):
        """Validate price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value

    def validate_quantity(self, value):
        """Validate quantity is non-negative"""
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative")
        return value

    def validate(self, data):
        """Validate category exists"""
        category = data.get('category')
        if category and not Category.objects.filter(id=category.id).exists():
            raise serializers.ValidationError({"category": "Category does not exist"})
        return data