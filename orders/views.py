from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Order
from .serializers import OrderSerializer

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_seller:
            return Order.objects.filter(product__seller=user)
        else:
            return Order.objects.filter(customer=user)

    def perform_create(self, serializer):
        order = serializer.save()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.customer != request.user and not request.user.is_seller:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        if order.status != 'pending':
            return Response({'error': 'Only pending orders can be cancelled.'}, status=status.HTTP_400_BAD_REQUEST)
        order.cancel()
        return Response(OrderSerializer(order).data)
