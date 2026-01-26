from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from products.models import Product, Category
from orders.models import Order, OrderItem

User = get_user_model()


class DashboardTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.seller = User.objects.create_user(
            username='seller_test',
            password='test123',
            user_type='seller'
        )
        self.customer = User.objects.create_user(
            username='customer_test',
            password='test123',
            user_type='customer'
        )

        # Create test category
        self.category = Category.objects.create(name='Test Category')

        # Create test product
        self.product = Product.objects.create(
            seller=self.seller,
            category=self.category,
            name='Test Product',
            description='Test Description',
            price=10.00,
            quantity=100
        )

    def test_seller_can_access_dashboard(self):
        self.client.force_authenticate(user=self.seller)
        response = self.client.get('/api/dashboard/seller/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('products', response.data)
        self.assertIn('sales', response.data)

    def test_customer_cannot_access_dashboard(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/api/dashboard/seller/')
        self.assertEqual(response.status_code, 403)
