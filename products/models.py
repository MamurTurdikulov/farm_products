from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone

def validate_jpeg(file):
    """Validator that ensures uploaded file has a .jpeg extension."""
    name = str(getattr(file, 'name', '')).lower()
    if not name.endswith('.jpeg'):
        raise ValidationError("Only .jpeg images are allowed.")


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products"
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    available_kilos = models.FloatField(default=0.0)

    image = models.ImageField(
        upload_to="product_images/",
        validators=[validate_jpeg],
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "name"]

    def __str__(self):
        return f"{self.name} ({self.available_kilos} kg)"

    def get_absolute_url(self):
        return reverse("products:detail", kwargs={"pk": self.pk})


class Customer(models.Model):
    name = models.CharField(max_length=200)
    surname = models.CharField(max_length=200, blank=True, default="")
    phone = models.CharField(max_length=40, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True, default=timezone.now)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        full = f"{self.name} {self.surname}".strip()
        return full or (self.phone or self.email or "Customer")


class Order(models.Model):
    STATUS_PENDING = "Pending"
    STATUS_COMPLETED = "Completed"
    STATUS_CANCELLED = "Cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="orders"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="orders"
    )
    kilos_ordered = models.FloatField(default=0.0)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    note = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk or 'N/A'} — {self.kilos_ordered}kg of {self.product.name} for {self.customer}"

    def total_price(self):
        return (self.product.price or 0) * (self.kilos_ordered or 0)
