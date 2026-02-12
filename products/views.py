from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter products based on user type:
        - Sellers: See only their own products
        - Customers: See only active products from all sellers
        - Admins: See all products
        """
        user = self.request.user

        if user.is_seller:
            return Product.objects.filter(seller=user)
        elif user.is_staff:
            return Product.objects.all()
        else:
            return Product.objects.filter(is_active=True)

    def get_permissions(self):
        """
        Set permissions based on action:
        - Create: Only sellers and admins
        - Update/Delete: Only product owner or admin
        - Read: All authenticated users
        """
        if self.action == 'create':
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        """
        Create a new product.
        Only sellers can create products.
        """
        # Check if user is a seller
        if not hasattr(request.user, 'is_seller') or not request.user.is_seller:
            return Response(
                {"error": "Only sellers can create products"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Add seller to the request data
        request.data['seller'] = request.user.id

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Save the product
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        """Set the seller to the current user"""
        serializer.save(seller=self.request.user)

    def update(self, request, *args, **kwargs):
        """
        Update a product.
        Only the product owner or admin can update.
        """
        instance = self.get_object()

        # Check if user owns this product or is admin
        if not (request.user == instance.seller or request.user.is_staff):
            return Response(
                {"error": "You don't have permission to modify this product"},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a product.
        Only the product owner or admin can delete.
        """
        instance = self.get_object()

        # Check if user owns this product or is admin
        if not (request.user == instance.seller or request.user.is_staff):
            return Response(
                {"error": "You don't have permission to delete this product"},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='my-products')
    def my_products(self, request):
        """
        Get seller's own products.
        """
        if not hasattr(request.user, 'is_seller') or not request.user.is_seller:
            return Response(
                {"error": "Only sellers can view their products"},
                status=status.HTTP_403_FORBIDDEN
            )

        products = Product.objects.filter(seller=request.user)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_stock(self, request, pk=None):
        """
        Add stock to a product.
        Only the product owner or admin can add stock.
        """
        product = get_object_or_404(Product, pk=pk)

        # Check if user owns this product or is admin
        if not (request.user == product.seller or request.user.is_staff):
            return Response(
                {"error": "You don't have permission to modify this product"},
                status=status.HTTP_403_FORBIDDEN
            )

        quantity = int(request.data.get('quantity', 0))
        if quantity <= 0:
            return Response(
                {"error": "Quantity must be positive"},
                status=status.HTTP_400_BAD_REQUEST
            )

        product.quantity += quantity
        product.save()

        serializer = self.get_serializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)