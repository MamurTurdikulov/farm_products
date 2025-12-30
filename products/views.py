from rest_framework import viewsets, permissions
from .models import Product
from .serializers import ProductSerializer
from django_filters.rest_framework import DjangoFilterBackend

class IsSeller(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_seller

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['seller']

    def get_queryset(self):
        # Sellers see all their products (even 0-kg)
        # Customers see only products with stock > 0
        user = self.request.user
        if user.is_seller:
            return Product.objects.filter(seller=user)
        else:
            return Product.objects.filter(total_quantity_kg__gt=0)

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsSeller]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]