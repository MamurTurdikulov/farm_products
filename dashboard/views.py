from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import timedelta
from products.models import Product
from orders.models import Order, OrderItem


class SellerDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.user_type != 'seller':
            return Response({'error': 'Only sellers can access dashboard'}, status=403)

        # Product statistics
        products = Product.objects.filter(seller=user)
        total_products = products.count()
        active_products = products.filter(is_active=True).count()
        out_of_stock = products.filter(quantity=0).count()
        low_stock = products.filter(quantity__lte=10, quantity__gt=0).count()

        # Sales statistics
        sold_items = OrderItem.objects.filter(seller=user)
        total_sales = sold_items.aggregate(total=Sum('subtotal'))['total'] or 0
        total_orders = sold_items.values('order').distinct().count()
        total_items_sold = sold_items.aggregate(total=Sum('quantity'))['total'] or 0

        # Recent orders (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_sales = sold_items.filter(
            order__created_at__gte=thirty_days_ago
        ).aggregate(total=Sum('subtotal'))['total'] or 0

        # Top selling products
        top_products = sold_items.values('product__name').annotate(
            total_sold=Sum('quantity'),
            revenue=Sum('subtotal')
        ).order_by('-total_sold')[:5]

        # Monthly sales data (last 6 months)
        monthly_sales = []
        for i in range(6):
            month_start = timezone.now() - timedelta(days=30 * (i + 1))
            month_end = timezone.now() - timedelta(days=30 * i)
            sales = sold_items.filter(
                order__created_at__gte=month_start,
                order__created_at__lt=month_end
            ).aggregate(total=Sum('subtotal'))['total'] or 0
            monthly_sales.append({
                'month': month_start.strftime('%B'),
                'sales': float(sales)
            })

        # Order status distribution
        order_statuses = Order.objects.filter(
            items__seller=user
        ).values('status').annotate(count=Count('id')).order_by('status')

        return Response({
            'products': {
                'total': total_products,
                'active': active_products,
                'out_of_stock': out_of_stock,
                'low_stock': low_stock,
            },
            'sales': {
                'total_revenue': float(total_sales),
                'total_orders': total_orders,
                'items_sold': total_items_sold,
                'recent_sales_30_days': float(recent_sales),
            },
            'top_products': list(top_products),
            'monthly_sales': monthly_sales[::-1],
            'order_statuses': list(order_statuses),
        })


class SellerRevenueView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.user_type != 'seller':
            return Response({'error': 'Only sellers can access this'}, status=403)

        # Get date range from query params
        days = int(request.GET.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)

        # Daily revenue
        daily_revenue = OrderItem.objects.filter(
            seller=user,
            order__created_at__gte=start_date
        ).values('order__created_at__date').annotate(
            revenue=Sum('subtotal'),
            orders=Count('order', distinct=True)
        ).order_by('order__created_at__date')

        return Response({
            'period_days': days,
            'daily_revenue': list(daily_revenue)
        })
