from django.db import models
from django.core.exceptions import ValidationError
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys


def validate_jpeg(image):
    try:
        img = Image.open(image)
        if img.format not in ["JPEG", "JPG"]:
            raise ValidationError("Only JPEG/JPG images are allowed.")
    except Exception:
        raise ValidationError("Invalid or corrupted image file.")


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.PositiveIntegerField(default=0)
    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True,
        validators=[validate_jpeg]
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("name", "category")

    def __str__(self):
        return f"{self.name} (×{self.amount})"

    def save(self, *args, **kwargs):
        if self.image:
            img = Image.open(self.image)
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.thumbnail((800, 800), Image.Resampling.LANCZOS)
            output = BytesIO()
            img.save(output, format="JPEG", quality=85)
            output.seek(0)
            self.image = InMemoryUploadedFile(
                output, "ImageField",
                f"{self.image.name.split('.')[0]}.jpg",
                "image/jpeg",
                sys.getsizeof(output),
                None
            )
        super().save(*args, **kwargs)


class Customer(models.Model):
    name = models.CharField(max_length=150)
    surname = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=50, unique=True)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Customers"

    def __str__(self):
        return f"{self.name} {self.surname}".strip()


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, null=True, blank=True)
    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("shipped", "Shipped"),
        ("canceled", "Canceled"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    note = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.id}"

    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    def total_cost(self):
        return sum(item.line_total() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def line_total(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.product.name} × {self.quantity}"