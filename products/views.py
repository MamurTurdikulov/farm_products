from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product, ProductImage
from .serializers import (CategorySerializer, ProductSerializer,
                          ProductCreateSerializer, ProductImageSerializer)
from .permissions import IsSellerOrReadOnly


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'seller']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'quantity']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductCreateSerializer
        return ProductSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by seller's own products if requested
        if self.request.query_params.get('my_products'):
            queryset = queryset.filter(seller=self.request.user)
        return queryset

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_stock(self, request, pk=None):
        product = self.get_object()
        if product.seller != request.user:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)

        quantity = request.data.get('quantity', 0)
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError
        except ValueError:
            return Response({'error': 'Invalid quantity'}, status=status.HTTP_400_BAD_REQUEST)

        product.quantity += quantity
        product.save()
        return Response({'message': 'Stock updated', 'new_quantity': product.quantity})

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_products(self, request):
        products = Product.objects.filter(seller=request.user)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        if not request.user.is_authenticated or request.user.user_type != 'seller':
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)

        products = Product.objects.filter(seller=request.user, quantity__lte=10, quantity__gt=0)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)