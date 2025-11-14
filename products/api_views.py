from rest_framework import viewsets, status, filters
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction

from .models import Category, Product, Customer, Order
from .serializers import CategorySerializer, ProductSerializer, CustomerSerializer, OrderSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ("category",)
    search_fields = ("name", "description")
    ordering_fields = ("price", "available_kilos", "created_at")


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all().order_by("name", "surname")
    serializer_class = CustomerSerializer
    permission_classes = [AllowAny]
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("name", "surname", "phone", "email")
    ordering_fields = ("name",)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related("product", "customer").all().order_by("-created_at")
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ("status", "customer", "product")
    search_fields = ("customer__name", "product__name", "note")
    ordering_fields = ("created_at",)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = serializer.validated_data["product"]
        kilos = serializer.validated_data["kilos_ordered"]

        if product.available_kilos < kilos:
            return Response({"detail": "Not enough stock available."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # For Postgres it's better to select_for_update; but atomic block helps for SQLite too
            product.available_kilos = product.available_kilos - kilos
            product.save(update_fields=["available_kilos"])
            order = serializer.save()

        out = self.get_serializer(order)
        return Response(out.data, status=status.HTTP_201_CREATED)
