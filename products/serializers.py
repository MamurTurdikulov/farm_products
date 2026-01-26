from rest_framework import serializers
from .models import Category, Product, ProductImage

class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = '__all__'

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('seller', 'created_at', 'updated_at')

class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('category', 'name', 'description', 'price', 'quantity', 'image', 'is_active')
        extra_kwargs = {
            'image': {'required': False}
        }

    def validate_category(self, value):
        if not value:
            raise serializers.ValidationError("Category is required.")
        return value

    def create(self, validated_data):
        validated_data['seller'] = self.context['request'].user
        return super().create(validated_data)