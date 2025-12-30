from django.db import models
from accounts.models import User
from products.models import Product

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('fulfilled', 'Fulfilled'),
        ('cancelled', 'Cancelled'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    requested_quantity_kg = models.DecimalField(max_digits=10, decimal_places=2)
    fulfilled_quantity_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Only on first save (creation)
        if not self.pk:
            available = self.product.total_quantity_kg
            self.fulfilled_quantity_kg = min(self.requested_quantity_kg, available)
            # Deduct from product stock
            self.product.total_quantity_kg -= self.fulfilled_quantity_kg
            self.product.save()
            if self.fulfilled_quantity_kg == 0:
                self.status = 'cancelled'  # auto-cancel if no stock
        super().save(*args, **kwargs)

    def cancel(self):
        if self.status == 'pending':
            # Return stock
            self.product.total_quantity_kg += self.fulfilled_quantity_kg
            self.product.save()
            self.status = 'cancelled'
            self.save()

    def __str__(self):
        return f"Order {self.id}: {self.customer.username} → {self.product.name} ({self.fulfilled_quantity_kg} kg)"