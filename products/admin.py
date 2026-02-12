from django.contrib import admin
from .models import Category, Product, ProductImage

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']
    readonly_fields = ['created_at']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'seller', 'category', 'price', 'quantity', 'is_active', 'created_at']
    list_filter = ['is_active', 'category', 'seller', 'created_at']
    search_fields = ['name', 'description', 'seller__username']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_active', 'price', 'quantity']
    date_hierarchy = 'created_at'

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'created_at']
    list_filter = ['created_at']
    search_fields = ['product__name']