from rest_framework import generics, status
from rest_framework.response import Response
from .models import Category, Product, Customer, Order, OrderItem
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    OrderCreateSerializer,
)


class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.filter(amount__gt=0).select_related("category")
    serializer_class = ProductSerializer


class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.select_related("category")
    serializer_class = ProductSerializer


class OrderCreateAPIView(generics.CreateAPIView):
    serializer_class = OrderCreateSerializer

    def perform_create(self, serializer):
        order = serializer.save()
        # Update product stock
        for item in order.items.all():
            product = item.product
            product.amount -= item.quantity
            product.save()