from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import OrderItem, Order
from products.models import Product

@receiver(post_save, sender=OrderItem)
def reduce_product_stock(sender, instance, created, **kwargs):
    '''Automatically reduce product stock when order item is created'''
    if created:
        product = instance.product
        if product.quantity >= instance.quantity:
            product.quantity -= instance.quantity
            product.save()
        else:
            # Handle insufficient stock (shouldn't happen due to validation)
            raise ValueError(f"Insufficient stock for {product.name}")

@receiver(post_delete, sender=OrderItem)
def restore_product_stock(sender, instance, **kwargs):
    '''Restore product stock when order item is deleted (cancelled)'''
    product = instance.product
    product.quantity += instance.quantity
    product.save()

@receiver(post_save, sender=Order)
def send_order_notification(sender, instance, created, **kwargs):
    '''Send notifications when order is created or updated'''
    if created:
        # Trigger email task
        from .tasks import send_order_confirmation
        send_order_confirmation.delay(instance.id)
        print(f"Order #{instance.id} created - notification sent")
    else:
        # Order updated (status changed)
        print(f"Order #{instance.id} status changed to {instance.status}")
