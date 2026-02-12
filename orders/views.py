from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Order, OrderItem, Cart, CartItem
from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    CartSerializer,
    CartItemSerializer
)
from products.models import Product


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        # Only show user's own orders
        return Order.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """Get single order with items"""
        instance = self.get_object()
        if instance.user != request.user:
            return Response(
                {"error": "You don't have permission to view this order."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Create order from cart items
        Automatically moves cart items to order and clears cart
        """
        # Get or create cart
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Check if cart has items
        cart_items = cart.items.all()
        if not cart_items.exists():
            return Response(
                {"error": "Cart is empty. Add items to cart first."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Prepare items data for order
        items_data = []
        for cart_item in cart_items:
            items_data.append({
                'product': cart_item.product.id,
                'quantity': cart_item.quantity,
                'price': cart_item.product.price
            })

        # Create serializer with items
        serializer = self.get_serializer(data={'status': 'pending', 'items': items_data})
        serializer.is_valid(raise_exception=True)

        # Save order (stock will be reduced via signals)
        order = serializer.save()

        # Clear cart items
        cart_items.delete()

        # Return order details
        order_serializer = OrderSerializer(order)
        return Response(
            order_serializer.data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Update order status (seller or admin only)"""
        order = self.get_object()

        # Only seller of products or admin can update status
        if not request.user.is_staff and not request.user.is_seller:
            return Response(
                {"error": "Only sellers or admins can update order status."},
                status=status.HTTP_403_FORBIDDEN
            )

        new_status = request.data.get('status')
        if not new_status:
            return Response(
                {"error": "Status is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        valid_statuses = dict(Order.STATUS_CHOICES)
        if new_status not in valid_statuses:
            return Response(
                {"error": f"Invalid status. Must be one of: {', '.join(valid_statuses.keys())}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = new_status
        order.save()

        return Response({
            "message": "Order status updated successfully",
            "order_id": order.id,
            "new_status": new_status
        })


class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Get user's cart with items"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Add item to cart"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        if quantity <= 0:
            return Response(
                {"error": "Quantity must be positive"},
                status=status.HTTP_400_BAD_REQUEST
            )

        product = get_object_or_404(Product, id=product_id)

        if product.quantity < quantity:
            return Response(
                {"error": f"Insufficient stock. Available: {product.quantity} kg"},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            # Update quantity if item already in cart
            cart_item.quantity += quantity
            cart_item.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        """Remove item from cart"""
        item_id = request.data.get('item_id')
        cart = get_object_or_404(Cart, user=request.user)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        item.delete()

        # Return updated cart
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def update_item(self, request):
        """Update item quantity in cart"""
        item_id = request.data.get('item_id')
        quantity = int(request.data.get('quantity', 1))

        if quantity <= 0:
            return Response(
                {"error": "Quantity must be positive"},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart = get_object_or_404(Cart, user=request.user)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

        # Check stock
        if cart_item.product.quantity < quantity:
            return Response(
                {"error": f"Insufficient stock. Available: {cart_item.product.quantity} kg"},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item.quantity = quantity
        cart_item.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """Clear entire cart"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()

        return Response(
            {"message": "Cart cleared successfully"},
            status=status.HTTP_200_OK
        )