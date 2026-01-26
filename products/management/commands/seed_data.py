from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import Category, Product
from decimal import Decimal
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')

        # Create users
        seller1, _ = User.objects.get_or_create(
            username='seller1',
            defaults={
                'email': 'seller1@example.com',
                'user_type': 'seller',
                'first_name': 'John',
                'last_name': 'Farmer'
            }
        )
        seller1.set_password('password123')
        seller1.save()

        customer1, _ = User.objects.get_or_create(
            username='customer1',
            defaults={
                'email': 'customer1@example.com',
                'user_type': 'customer',
                'first_name': 'Jane',
                'last_name': 'Smith'
            }
        )
        customer1.set_password('password123')
        customer1.save()

        # Create categories
        categories_data = [
            {'name': 'Vegetables', 'description': 'Fresh organic vegetables'},
            {'name': 'Fruits', 'description': 'Seasonal fresh fruits'},
            {'name': 'Dairy', 'description': 'Fresh dairy products'},
            {'name': 'Grains', 'description': 'Whole grains and cereals'},
            {'name': 'Herbs', 'description': 'Fresh and dried herbs'},
        ]

        categories = []
        for cat_data in categories_data:
            cat, _ = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories.append(cat)

        # Create products
        products_data = [
            {'name': 'Fresh Tomatoes', 'category': 0, 'price': '5.99', 'quantity': 100},
            {'name': 'Organic Carrots', 'category': 0, 'price': '3.49', 'quantity': 80},
            {'name': 'Green Lettuce', 'category': 0, 'price': '2.99', 'quantity': 60},
            {'name': 'Fresh Apples', 'category': 1, 'price': '4.99', 'quantity': 120},
            {'name': 'Ripe Bananas', 'category': 1, 'price': '2.49', 'quantity': 150},
            {'name': 'Strawberries', 'category': 1, 'price': '6.99', 'quantity': 40},
            {'name': 'Fresh Milk', 'category': 2, 'price': '3.99', 'quantity': 50},
            {'name': 'Farm Eggs', 'category': 2, 'price': '5.49', 'quantity': 70},
            {'name': 'Cheddar Cheese', 'category': 2, 'price': '7.99', 'quantity': 30},
            {'name': 'Brown Rice', 'category': 3, 'price': '8.99', 'quantity': 90},
            {'name': 'Whole Wheat', 'category': 3, 'price': '6.49', 'quantity': 100},
            {'name': 'Fresh Basil', 'category': 4, 'price': '2.99', 'quantity': 25},
            {'name': 'Oregano', 'category': 4, 'price': '3.49', 'quantity': 20},
        ]

        for prod_data in products_data:
            Product.objects.get_or_create(
                name=prod_data['name'],
                defaults={
                    'seller': seller1,
                    'category': categories[prod_data['category']],
                    'description': f"High quality {prod_data['name'].lower()} from local farm",
                    'price': Decimal(prod_data['price']),
                    'quantity': prod_data['quantity'],
                    'is_active': True
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded database!'))
        self.stdout.write(f'Created users: seller1/customer1 (password: password123)')
        self.stdout.write(f'Created {len(categories)} categories')
        self.stdout.write(f'Created {len(products_data)} products')
