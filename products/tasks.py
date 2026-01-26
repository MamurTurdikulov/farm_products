from celery import shared_task
from django.core.mail import send_mail
from .models import Product

@shared_task
def check_low_stock():
    """Check for low stock products and notify sellers"""
    low_stock_products = Product.objects.filter(
        quantity__lte=10,
        quantity__gt=0,
        is_active=True
    )

    for product in low_stock_products:
        # Send email to seller (if email is configured)
        message = f'Your product "{product.name}" is running low on stock. Current quantity: {product.quantity}'
        try:
            send_mail(
                'Low Stock Alert',
                message,
                'noreply@farmproducts.com',
                [product.seller.email],
            )
            print(f"Low stock alert sent: {message}")
        except Exception as e:
            print(f"Failed to send email: {e}")

    return f"Checked {low_stock_products.count()} low stock products"

@shared_task
def update_product_stock(product_id, quantity):
    """Update product stock (background task)"""
    try:
        product = Product.objects.get(id=product_id)
        product.quantity += quantity
        product.save()
        return f"Stock updated for {product.name}"
    except Product.DoesNotExist:
        return "Product not found"