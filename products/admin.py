from django.contrib import admin
from .models import Category, Product, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_count', 'created_at')
    search_fields = ('name',)

    def product_count(self, obj):
        return obj.products.count()

    product_count.short_description = 'Products'


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'seller', 'category', 'price', 'quantity', 'is_active', 'created_at')
    list_filter = ('is_active', 'category', 'seller')
    search_fields = ('name', 'description')
    inlines = [ProductImageInline]
    readonly_fields = ('created_at', 'updated_at')