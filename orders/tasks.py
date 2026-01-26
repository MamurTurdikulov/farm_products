from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Cart

@shared_task
def cleanup_old_carts():
    '''Delete carts that haven't been updated in 30 days'''
    thirty_days_ago = timezone.now() - timedelta(days=30)
    old_carts = Cart.objects.filter(updated_at__lt=thirty_days_ago)
    count = old_carts.count()
    old_carts.delete()
    return f"Deleted {count} old carts"

@shared_task
def send_order_confirmation(order_id):
    '''Send order confirmation email'''
    from .models import Order
    try:
        order = Order.objects.get(id=order_id)
        # Send email logic here
        print(f"Order confirmation sent for order #{order.id}")
        return f"Confirmation sent for order #{order.id}"
    except Order.DoesNotExist:
        return "Order not found"