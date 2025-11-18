from django.contrib import admin
from .models import Category, Product, Customer, Order

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "price", "available_kilos", "created_at")
    list_filter = ("category",)
    search_fields = ("name", "description")


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "surname", "phone", "email")
    search_fields = ("name", "surname", "phone", "email")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "product", "kilos_ordered", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("customer__name", "product__name")
