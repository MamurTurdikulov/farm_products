from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    )

    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='customer')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.user_type})"

    @property
    def is_seller(self):
        return self.user_type == 'seller'

    @property
    def is_customer(self):
        return self.user_type == 'customer'