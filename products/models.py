from django.db import models

class Category(models.Model):
    """Represents a product category (e.g. Fruits, Vegetables, Dairy)."""
    title = models.CharField(max_length=100, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.title

class Product(models.Model):
    """Represents a product with price, description, and image."""
    title = models.CharField(max_length=100, null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products'
    )
    cost = models.IntegerField(null=False, blank=False, help_text="Purchase cost (in local currency)")
    price = models.IntegerField(null=False, blank=False, help_text="Selling price (in local currency)")
    image = models.ImageField(upload_to='products')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class Customer(models.Model):
    """Represents a customer placing orders."""
    first_name = models.CharField(max_length=100, null=False, blank=False)
    last_name = models.CharField(max_length=100, null=False, blank=False)
    phone_number = models.CharField(max_length=100, unique=True, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Order(models.Model):
    """Represents a customer's order."""
    PAYMENT_CHOICES = (
        (1, "Cash"),
        (2, "Card"),
        (3, "Transfer"),
    )

    STATUS_CHOICES = (
        (1, "New"),
        (2, "In Progress"),
        (3, "Delivered"),
        (4, "Cancelled"),
    )

    payment_type = models.IntegerField(choices=PAYMENT_CHOICES, default=1)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    address = models.CharField(max_length=250, null=False, blank=False)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} ({self.customer})"

class OrderProduct(models.Model):
    """Links products to orders (many-to-many through model)."""
    count = models.IntegerField(null=False, blank=False)
    price = models.IntegerField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        related_name='order_items'
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        related_name='order_products'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product} × {self.count}"